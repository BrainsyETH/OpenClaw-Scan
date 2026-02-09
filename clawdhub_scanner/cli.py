#!/usr/bin/env python3
"""
ClawdHub Security Scanner CLI
Command-line interface for scanning ClawdHub skills for security vulnerabilities.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from .manifest_parser import ManifestParser
from .yara_scanner import YaraScanner, ScanSeverity


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner():
    """Print scanner banner"""
    banner = f"""
{Colors.BLUE}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║          ClawdHub Security Scanner v0.1.0                     ║
║          Protecting agents from supply chain attacks          ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)


def format_severity(severity: str) -> str:
    """Color-code severity levels"""
    colors = {
        'CRITICAL': Colors.RED,
        'HIGH': Colors.YELLOW,
        'MEDIUM': Colors.BLUE,
        'LOW': Colors.GREEN,
        'SAFE': Colors.GREEN,
    }
    color = colors.get(severity, '')
    return f"{color}{severity}{Colors.END}"


def scan_skill(skill_path: Path, verbose: bool = False) -> int:
    """
    Scan a ClawdHub skill for security issues.
    
    Args:
        skill_path: Path to skill directory
        verbose: Show detailed scan output
        
    Returns:
        Exit code (0 = pass, 1 = warnings, 2 = critical issues)
    """
    if not skill_path.exists():
        print(f"{Colors.RED}Error:{Colors.END} Skill path does not exist: {skill_path}")
        return 2
    
    if not skill_path.is_dir():
        print(f"{Colors.RED}Error:{Colors.END} Skill path is not a directory: {skill_path}")
        return 2
    
    print(f"\n{Colors.BOLD}Scanning:{Colors.END} {skill_path.name}")
    print("─" * 70)
    
    # Step 1: Manifest validation
    print(f"\n{Colors.BOLD}[1/2] Validating manifest...{Colors.END}")
    manifest_path = skill_path / "skill.json"
    
    if not manifest_path.exists():
        print(f"{Colors.YELLOW}Warning:{Colors.END} No skill.json found")
        manifest_risk = "MEDIUM"
        manifest_issues = ["Missing manifest file"]
    else:
        parser = ManifestParser()
        result_obj = parser.parse(str(manifest_path))
        result = result_obj.to_dict()  # Convert dataclass to dict for CLI
        
        if result['valid']:
            manifest_risk = result.get('risk_level', 'UNKNOWN')
            manifest_issues = result.get('warnings', [])
            permissions = result.get('permissions', {})
            
            print(f"  ✓ Manifest valid")
            print(f"  Risk level: {format_severity(manifest_risk)}")
            
            if verbose and permissions:
                print(f"\n  Declared permissions:")
                for perm_type, perm_list in permissions.items():
                    print(f"    • {perm_type}: {', '.join(perm_list)}")
        else:
            manifest_risk = "HIGH"
            manifest_issues = result.get('errors', [])
            print(f"  {Colors.RED}✗ Manifest validation failed{Colors.END}")
    
    # Step 2: YARA pattern scanning
    print(f"\n{Colors.BOLD}[2/2] Scanning for malicious patterns...{Colors.END}")
    
    scanner = YaraScanner()
    scan_result = scanner.scan_skill(skill_path)  # Returns YaraScanResult object
    yara_matches = scan_result.matches  # Get the list of matches
    
    if not yara_matches:
        print(f"  ✓ No malicious patterns detected")
        yara_risk = "SAFE"
    else:
        print(f"  {Colors.RED}✗ Found {len(yara_matches)} suspicious patterns{Colors.END}\n")
        yara_risk = "CRITICAL" if any(m.severity in [ScanSeverity.CRITICAL, ScanSeverity.HIGH] for m in yara_matches) else "MEDIUM"
        
        for match in yara_matches:
            severity = format_severity(match.severity.value)
            print(f"  [{severity}] {match.rule_name}")
            print(f"      File: {match.file_path}")
            print(f"      Description: {match.description}")
            
            if verbose and match.matched_strings:
                for matched_str in match.matched_strings[:3]:  # Show first 3 matches
                    print(f"      Match: {matched_str}")
            print()
    
    # Overall risk assessment
    print("\n" + "═" * 70)
    print(f"{Colors.BOLD}OVERALL ASSESSMENT{Colors.END}")
    print("─" * 70)
    
    # Determine final risk level
    risk_levels = {'SAFE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
    final_risk_score = max(
        risk_levels.get(manifest_risk, 0),
        risk_levels.get(yara_risk, 0)
    )
    final_risk = [k for k, v in risk_levels.items() if v == final_risk_score][0]
    
    print(f"Risk Level: {format_severity(final_risk)}")
    
    if manifest_issues:
        print(f"\nManifest Issues ({len(manifest_issues)}):")
        for issue in manifest_issues:
            print(f"  • {issue}")
    
    if yara_matches:
        print(f"\nSecurity Findings ({len(yara_matches)}):")
        for match in yara_matches:
            print(f"  • {match.rule_name} ({match.severity.value})")
    
    # Recommendation
    print(f"\n{Colors.BOLD}RECOMMENDATION:{Colors.END}")
    if final_risk in ['SAFE', 'LOW']:
        print(f"  {Colors.GREEN}✓ Skill appears safe to install{Colors.END}")
        exit_code = 0
    elif final_risk == 'MEDIUM':
        print(f"  {Colors.YELLOW}⚠ Review findings before installing{Colors.END}")
        exit_code = 1
    else:
        print(f"  {Colors.RED}✗ DO NOT INSTALL - Critical security issues detected{Colors.END}")
        exit_code = 2
    
    print("─" * 70 + "\n")
    
    return exit_code


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Scan ClawdHub skills for security vulnerabilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a skill before installing
  clawdhub-scanner scan ./my-skill
  
  # Scan with verbose output
  clawdhub-scanner scan ./my-skill --verbose
  
  # Scan all skills in a directory
  clawdhub-scanner scan ./skills --recursive
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ClawdHub Security Scanner v0.1.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan a skill for security issues')
    scan_parser.add_argument(
        'skill_path',
        type=Path,
        help='Path to skill directory'
    )
    scan_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed scan output'
    )
    scan_parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Scan all subdirectories as skills'
    )
    scan_parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Suppress banner output'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'scan':
        if not args.no_banner:
            print_banner()
        
        if args.recursive:
            # Scan all subdirectories
            exit_code = 0
            skill_dirs = [d for d in args.skill_path.iterdir() if d.is_dir()]
            
            if not skill_dirs:
                print(f"{Colors.RED}Error:{Colors.END} No skill directories found in {args.skill_path}")
                return 2
            
            print(f"Found {len(skill_dirs)} skills to scan\n")
            
            for skill_dir in skill_dirs:
                result = scan_skill(skill_dir, args.verbose)
                exit_code = max(exit_code, result)
            
            return exit_code
        else:
            # Scan single skill
            return scan_skill(args.skill_path, args.verbose)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
