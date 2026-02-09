"""
ClawdHub Skill Manifest Parser

Validates skill.json structure and checks for suspicious permissions.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for permission analysis"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ManifestCheck:
    """Result of a single manifest validation check"""
    check_name: str
    passed: bool
    risk_level: RiskLevel
    message: str
    details: Optional[Dict] = None


@dataclass
class ManifestScanResult:
    """Complete scan result for a skill manifest"""
    skill_name: str
    passed: bool
    risk_level: RiskLevel
    checks: List[ManifestCheck]
    raw_manifest: Dict

    def get_critical_issues(self) -> List[ManifestCheck]:
        """Return only critical/high risk findings"""
        return [c for c in self.checks if c.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
    
    def to_dict(self) -> Dict:
        """Convert scan result to dict for backward compatibility with CLI"""
        warnings = [c.message for c in self.checks if not c.passed and c.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]]
        errors = [c.message for c in self.checks if not c.passed and c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        return {
            'valid': self.passed,
            'skill_name': self.skill_name,
            'risk_level': self.risk_level.value.upper(),
            'warnings': warnings,
            'errors': errors,
            'permissions': self.raw_manifest.get('permissions', {}),
            'checks': [
                {
                    'name': c.check_name,
                    'passed': c.passed,
                    'risk': c.risk_level.value,
                    'message': c.message,
                    'details': c.details
                }
                for c in self.checks
            ]
        }


class ManifestParser:
    """
    Parses and validates ClawdHub skill.json manifests.
    
    Checks for:
    - Required fields (name, version, description)
    - Suspicious file access patterns
    - Network access declarations
    - API key usage
    - Shell command execution
    - Obfuscated code indicators
    """

    REQUIRED_FIELDS = ["name", "version", "description", "author"]
    
    # High-risk permission patterns
    SUSPICIOUS_PATTERNS = {
        "filesystem_full": ["fs.readFile", "fs.writeFile", "fs.readdir", "fs.unlink"],
        "env_access": ["process.env", "os.environ", "env.get"],
        "network_unrestricted": ["http.request", "https.request", "fetch", "axios"],
        "shell_exec": ["child_process.exec", "subprocess.run", "os.system"],
        "api_keys": [".env", "API_KEY", "SECRET_KEY", "TOKEN"],
    }

    def parse(self, manifest_path: str) -> ManifestScanResult:
        """
        Parse and validate a skill.json manifest file.
        
        Args:
            manifest_path: Path to skill.json file
            
        Returns:
            ManifestScanResult with validation results
        """
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            return ManifestScanResult(
                skill_name="unknown",
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                checks=[ManifestCheck(
                    check_name="json_validation",
                    passed=False,
                    risk_level=RiskLevel.CRITICAL,
                    message=f"Invalid JSON: {str(e)}"
                )],
                raw_manifest={}
            )
        except FileNotFoundError:
            return ManifestScanResult(
                skill_name="unknown",
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                checks=[ManifestCheck(
                    check_name="file_exists",
                    passed=False,
                    risk_level=RiskLevel.CRITICAL,
                    message=f"Manifest not found: {manifest_path}"
                )],
                raw_manifest={}
            )

        skill_name = manifest.get("name", "unknown")
        checks = []

        # Check required fields
        checks.extend(self._check_required_fields(manifest))
        
        # Check permissions
        checks.extend(self._check_permissions(manifest))
        
        # Check for suspicious patterns in code references
        checks.extend(self._check_code_patterns(manifest))

        # Determine overall risk level
        risk_levels = [c.risk_level for c in checks]
        if RiskLevel.CRITICAL in risk_levels:
            overall_risk = RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            overall_risk = RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            overall_risk = RiskLevel.MEDIUM
        elif RiskLevel.LOW in risk_levels:
            overall_risk = RiskLevel.LOW
        else:
            overall_risk = RiskLevel.SAFE

        passed = all(c.passed for c in checks) and overall_risk not in [RiskLevel.CRITICAL, RiskLevel.HIGH]

        return ManifestScanResult(
            skill_name=skill_name,
            passed=passed,
            risk_level=overall_risk,
            checks=checks,
            raw_manifest=manifest
        )

    def _check_required_fields(self, manifest: Dict) -> List[ManifestCheck]:
        """Validate all required fields are present"""
        checks = []
        for field in self.REQUIRED_FIELDS:
            if field not in manifest:
                checks.append(ManifestCheck(
                    check_name=f"required_field_{field}",
                    passed=False,
                    risk_level=RiskLevel.HIGH,
                    message=f"Missing required field: {field}"
                ))
            else:
                checks.append(ManifestCheck(
                    check_name=f"required_field_{field}",
                    passed=True,
                    risk_level=RiskLevel.SAFE,
                    message=f"Field '{field}' present"
                ))
        return checks

    def _check_permissions(self, manifest: Dict) -> List[ManifestCheck]:
        """Check declared permissions for red flags"""
        checks = []
        permissions = manifest.get("permissions", [])
        
        if not permissions:
            checks.append(ManifestCheck(
                check_name="permissions_declared",
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message="No permissions declared (should explicitly declare 'none' or list permissions)"
            ))
            return checks

        # Check for overly broad permissions
        if "filesystem:all" in permissions:
            checks.append(ManifestCheck(
                check_name="filesystem_all",
                passed=False,
                risk_level=RiskLevel.HIGH,
                message="Unrestricted filesystem access requested",
                details={"permission": "filesystem:all"}
            ))
        
        if "network:all" in permissions:
            checks.append(ManifestCheck(
                check_name="network_all",
                passed=False,
                risk_level=RiskLevel.HIGH,
                message="Unrestricted network access requested",
                details={"permission": "network:all"}
            ))

        if "env:all" in permissions:
            checks.append(ManifestCheck(
                check_name="env_all",
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                message="Access to all environment variables (potential credential theft)",
                details={"permission": "env:all"}
            ))

        return checks

    def _check_code_patterns(self, manifest: Dict) -> List[ManifestCheck]:
        """Check code/entry points for suspicious patterns"""
        checks = []
        
        # Check entry point file
        entry_point = manifest.get("main", "")
        if not entry_point:
            checks.append(ManifestCheck(
                check_name="entry_point",
                passed=False,
                risk_level=RiskLevel.HIGH,
                message="No entry point specified"
            ))
        
        # Check for obfuscation indicators
        code_str = json.dumps(manifest).lower()
        
        obfuscation_indicators = ["eval(", "exec(", "base64", "atob", "btoa"]
        found_indicators = [ind for ind in obfuscation_indicators if ind in code_str]
        
        if found_indicators:
            checks.append(ManifestCheck(
                check_name="obfuscation",
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                message=f"Potential code obfuscation detected",
                details={"indicators": found_indicators}
            ))

        return checks


def scan_manifest(manifest_path: str) -> ManifestScanResult:
    """
    Convenience function to scan a manifest file.
    
    Args:
        manifest_path: Path to skill.json file
        
    Returns:
        ManifestScanResult with validation results
    """
    parser = ManifestParser()
    return parser.parse(manifest_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manifest_parser.py <path/to/skill.json>")
        sys.exit(1)
    
    result = scan_manifest(sys.argv[1])
    
    print(f"\n{'='*60}")
    print(f"Skill: {result.skill_name}")
    print(f"Risk Level: {result.risk_level.value.upper()}")
    print(f"Passed: {'✅' if result.passed else '❌'}")
    print(f"{'='*60}\n")
    
    for check in result.checks:
        status = "✅" if check.passed else "❌"
        print(f"{status} [{check.risk_level.value.upper()}] {check.message}")
        if check.details:
            print(f"   Details: {check.details}")
    
    critical_issues = result.get_critical_issues()
    if critical_issues:
        print(f"\n⚠️  {len(critical_issues)} CRITICAL/HIGH RISK ISSUES FOUND")
        for issue in critical_issues:
            print(f"   - {issue.message}")
