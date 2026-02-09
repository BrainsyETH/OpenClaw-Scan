"""
YARA-based pattern scanner for ClawdHub skills.

Scans JavaScript/TypeScript code for malicious patterns.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ScanSeverity(Enum):
    """Severity levels matching YARA rule metadata"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class YaraMatch:
    """A single YARA rule match"""
    rule_name: str
    severity: ScanSeverity
    description: str
    file_path: str
    matched_strings: List[str]
    line_numbers: List[int]


@dataclass
class YaraScanResult:
    """Complete YARA scan result for a skill"""
    skill_path: str
    passed: bool
    matches: List[YaraMatch]
    files_scanned: int
    
    def get_critical_matches(self) -> List[YaraMatch]:
        """Return only critical/high severity matches"""
        return [m for m in self.matches if m.severity in [ScanSeverity.CRITICAL, ScanSeverity.HIGH]]
    
    def get_severity_summary(self) -> Dict[str, int]:
        """Count matches by severity"""
        summary = {s.value: 0 for s in ScanSeverity}
        for match in self.matches:
            summary[match.severity.value] += 1
        return summary


class YaraScanner:
    """
    Scans ClawdHub skills using YARA rules.
    
    Note: This is a mock implementation for development.
    Production version will use python-yara library.
    """
    
    def __init__(self, rules_dir: Optional[Path] = None):
        """
        Initialize scanner with YARA rules.
        
        Args:
            rules_dir: Path to directory containing .yar files
        """
        if rules_dir is None:
            # Default to rules in same directory as this file
            rules_dir = Path(__file__).parent / "yara_rules"
        
        self.rules_dir = rules_dir
        self.rules_loaded = False
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load all .yar files from rules directory"""
        if not self.rules_dir.exists():
            raise FileNotFoundError(f"YARA rules directory not found: {self.rules_dir}")
        
        yar_files = list(self.rules_dir.glob("*.yar"))
        if not yar_files:
            raise ValueError(f"No .yar files found in {self.rules_dir}")
        
        # In production, this would compile YARA rules
        # For now, just verify files exist
        self.rules_loaded = True
        print(f"Loaded {len(yar_files)} YARA rule files")
    
    def scan_skill(self, skill_path: Path) -> YaraScanResult:
        """
        Scan a ClawdHub skill directory.
        
        Args:
            skill_path: Path to skill directory (containing skill.json)
            
        Returns:
            YaraScanResult with all matches
        """
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill path not found: {skill_path}")
        
        matches: List[YaraMatch] = []
        files_scanned = 0
        
        # Scan all JavaScript/TypeScript files
        for ext in ["*.js", "*.ts", "*.mjs"]:
            for file_path in skill_path.rglob(ext):
                if self._should_skip_file(file_path, skill_path):
                    continue
                
                file_matches = self._scan_file(file_path)
                matches.extend(file_matches)
                files_scanned += 1
        
        # Passed = no critical/high severity matches
        passed = len([m for m in matches if m.severity in [ScanSeverity.CRITICAL, ScanSeverity.HIGH]]) == 0
        
        return YaraScanResult(
            skill_path=str(skill_path),
            passed=passed,
            matches=matches,
            files_scanned=files_scanned
        )
    
    def _should_skip_file(self, file_path: Path, skill_root: Path) -> bool:
        """
        Skip common non-code files within the skill directory.
        
        Args:
            file_path: Full path to the file being checked
            skill_root: Root directory of the skill being scanned
            
        Returns:
            True if file should be skipped
        """
        skip_dirs = {"node_modules", "dist", "build", ".git"}
        
        # Only check path components WITHIN the skill directory
        # This prevents skipping test fixtures that are outside the skill
        try:
            relative_path = file_path.relative_to(skill_root)
            return any(part in skip_dirs for part in relative_path.parts)
        except ValueError:
            # file_path is not relative to skill_root (shouldn't happen)
            return False
    
    def _scan_file(self, file_path: Path) -> List[YaraMatch]:
        """
        Scan a single file with YARA rules.
        
        Note: This is a simplified mock for development.
        Production version will use python-yara library.
        """
        matches: List[YaraMatch] = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            return matches
        
        # Mock pattern detection (replace with real YARA in production)
        suspicious_patterns = {
            "webhook.site": (ScanSeverity.CRITICAL, "CredentialExfiltration", "Known exfiltration domain"),
            "process.env": (ScanSeverity.MEDIUM, "DangerousPermissions", "Environment variable access"),
            ".env": (ScanSeverity.HIGH, "CredentialExfiltration", "Reading .env file"),
            "eval(": (ScanSeverity.HIGH, "ObfuscatedCode", "Dynamic code execution"),
            "child_process": (ScanSeverity.HIGH, "DangerousPermissions", "Shell command execution"),
        }
        
        lines = content.split('\n')
        for pattern, (severity, rule_name, description) in suspicious_patterns.items():
            if pattern in content:
                # Find line numbers
                line_numbers = [i + 1 for i, line in enumerate(lines) if pattern in line]
                
                matches.append(YaraMatch(
                    rule_name=rule_name,
                    severity=severity,
                    description=description,
                    file_path=str(file_path),
                    matched_strings=[pattern],
                    line_numbers=line_numbers[:5]  # Limit to first 5 occurrences
                ))
        
        return matches
    
    def format_report(self, result: YaraScanResult) -> str:
        """Format scan result as human-readable report"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"YARA Scan Report: {Path(result.skill_path).name}")
        lines.append("=" * 70)
        lines.append(f"Files Scanned: {result.files_scanned}")
        lines.append(f"Status: {'✅ PASS' if result.passed else '❌ FAIL'}")
        lines.append("")
        
        if not result.matches:
            lines.append("No suspicious patterns detected.")
            return "\n".join(lines)
        
        # Group by severity
        severity_summary = result.get_severity_summary()
        lines.append("Severity Summary:")
        for severity in [ScanSeverity.CRITICAL, ScanSeverity.HIGH, ScanSeverity.MEDIUM, ScanSeverity.LOW]:
            count = severity_summary[severity.value]
            if count > 0:
                icon = "🔴" if severity in [ScanSeverity.CRITICAL, ScanSeverity.HIGH] else "🟡"
                lines.append(f"  {icon} {severity.value.upper()}: {count}")
        
        lines.append("")
        lines.append("Detailed Findings:")
        lines.append("-" * 70)
        
        # Sort matches by severity (critical first)
        severity_order = {ScanSeverity.CRITICAL: 0, ScanSeverity.HIGH: 1, ScanSeverity.MEDIUM: 2, ScanSeverity.LOW: 3}
        sorted_matches = sorted(result.matches, key=lambda m: severity_order[m.severity])
        
        for match in sorted_matches:
            lines.append(f"\n[{match.severity.value.upper()}] {match.rule_name}")
            lines.append(f"Description: {match.description}")
            lines.append(f"File: {Path(match.file_path).name}")
            lines.append(f"Lines: {', '.join(map(str, match.line_numbers))}")
            lines.append(f"Patterns: {', '.join(match.matched_strings)}")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    scanner = YaraScanner()
    
    # Example: scan a skill directory
    # result = scanner.scan_skill(Path("/path/to/skill"))
    # print(scanner.format_report(result))
    
    print("YARA Scanner initialized successfully")
    print(f"Rules directory: {scanner.rules_dir}")
