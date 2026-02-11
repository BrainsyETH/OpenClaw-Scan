#!/usr/bin/env python3
"""
Scanner Integration Module
Connects FastAPI server to the actual ClawdHub scanner CLI
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import subprocess
import logging

# Add parent directory to path to import clawdhub_scanner
sys.path.insert(0, str(Path(__file__).parent.parent))

from clawdhub_scanner.manifest_parser import ManifestParser
from clawdhub_scanner.yara_scanner import YaraScanner, ScanSeverity

logger = logging.getLogger(__name__)


class ScannerIntegration:
    """
    Integrates the ClawdHub scanner into the API server.
    Provides methods to scan skills and return structured results.
    """
    
    def __init__(self):
        self.manifest_parser = ManifestParser()
        self.yara_scanner = YaraScanner()
        
    def scan_skill(self, skill_path: str, tier: str = "free") -> Dict:
        """
        Scan a skill and return structured results.
        
        Args:
            skill_path: Path to skill directory or GitHub URL
            tier: "free" or "premium" (determines scan depth)
            
        Returns:
            dict: Scan results with verdict, findings, etc.
        """
        scan_id = self._generate_scan_id()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        try:
            # Download skill if GitHub URL
            if skill_path.startswith("http"):
                skill_dir = self._download_skill_from_url(skill_path)
            else:
                skill_dir = Path(skill_path)
            
            if not skill_dir.exists():
                return {
                    "scan_id": scan_id,
                    "skill": skill_path,
                    "verdict": "ERROR",
                    "findings": [{
                        "severity": "ERROR",
                        "message": f"Skill not found: {skill_path}"
                    }],
                    "timestamp": timestamp,
                    "scanner_version": "0.2.0",
                    "tier": tier
                }
            
            # Parse manifest
            manifest_path = skill_dir / "skill.json"
            if not manifest_path.exists():
                return {
                    "scan_id": scan_id,
                    "skill": skill_path,
                    "verdict": "ERROR",
                    "findings": [{
                        "severity": "ERROR",
                        "message": "skill.json not found"
                    }],
                    "timestamp": timestamp,
                    "scanner_version": "0.2.0",
                    "tier": tier
                }
            
            manifest_result = self.manifest_parser.parse(manifest_path)
            manifest_findings = self._extract_manifest_findings(manifest_result)
            
            # Run YARA scan
            yara_result = self.yara_scanner.scan_skill(skill_dir)
            
            # Combine findings
            all_findings = manifest_findings + self._format_yara_findings(yara_result.matches)
            
            # Determine overall verdict
            verdict = self._calculate_verdict(all_findings)
            
            results = {
                "scan_id": scan_id,
                "skill": skill_path,
                "verdict": verdict,
                "findings": all_findings,
                "timestamp": timestamp,
                "scanner_version": "0.2.0",
                "tier": tier,
                "manifest": {
                    "name": manifest_result.skill_name,
                    "version": manifest_result.raw_manifest.get("version", "unknown"),
                    "permissions": manifest_result.raw_manifest.get("permissions", [])
                },
                "stats": {
                    "total_findings": len(all_findings),
                    "critical": len([f for f in all_findings if f.get("severity") == "CRITICAL"]),
                    "high": len([f for f in all_findings if f.get("severity") == "HIGH"]),
                    "medium": len([f for f in all_findings if f.get("severity") == "MEDIUM"]),
                    "low": len([f for f in all_findings if f.get("severity") == "LOW"])
                }
            }
            
            # Add premium features if applicable
            if tier == "premium":
                results["sandbox_results"] = self._run_sandbox(skill_dir)
                results["behavioral_analysis"] = self._analyze_behavior(skill_dir)
            
            return results
            
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            return {
                "scan_id": scan_id,
                "skill": skill_path,
                "verdict": "ERROR",
                "findings": [{
                    "severity": "ERROR",
                    "message": f"Scan failed: {str(e)}"
                }],
                "timestamp": timestamp,
                "scanner_version": "0.2.0",
                "tier": tier
            }
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID"""
        import uuid
        return f"scan-{uuid.uuid4().hex[:12]}"
    
    def _download_skill_from_url(self, url: str) -> Path:
        """
        Download skill from GitHub URL to temp directory
        
        TODO: Implement actual git clone or API download
        For now, raise error
        """
        raise NotImplementedError("GitHub URL download not yet implemented. Please provide local path.")
    
    def _extract_manifest_findings(self, manifest_result) -> List[Dict]:
        """Extract security findings from manifest analysis"""
        findings = []
        
        # Convert manifest checks to findings
        for check in manifest_result.checks:
            if not check.passed or check.risk_level.value.upper() in ["MEDIUM", "HIGH", "CRITICAL"]:
                findings.append({
                    "severity": check.risk_level.value.upper(),
                    "category": "MANIFEST",
                    "message": check.message,
                    "details": check.details or {}
                })
        
        return findings
    
    def _format_yara_findings(self, yara_matches: List) -> List[Dict]:
        """Format YARA findings into standardized structure"""
        findings = []
        
        for match in yara_matches:
            findings.append({
                "severity": str(match.severity.value).upper() if hasattr(match.severity, 'value') else str(match.severity).upper(),
                "category": "YARA",
                "rule": match.rule_name,
                "message": match.description or f"YARA rule matched: {match.rule_name}",
                "details": {
                    "file": str(match.file_path),
                    "matched_strings": match.matched_strings if hasattr(match, 'matched_strings') else [],
                    "line_numbers": match.line_numbers if hasattr(match, 'line_numbers') else [],
                    "confidence": match.confidence if hasattr(match, 'confidence') else 1.0
                }
            })
        
        return findings
    
    def _calculate_verdict(self, findings: List[Dict]) -> str:
        """
        Calculate overall verdict based on findings
        
        Priority: CRITICAL > HIGH > MEDIUM > LOW > SAFE
        """
        if not findings:
            return "SAFE"
        
        severities = [f.get("severity", "UNKNOWN") for f in findings]
        
        if "CRITICAL" in severities:
            return "CRITICAL"
        elif "HIGH" in severities:
            return "HIGH"
        elif "MEDIUM" in severities:
            return "MEDIUM"
        elif "LOW" in severities:
            return "LOW"
        else:
            return "SAFE"
    
    def _run_sandbox(self, skill_dir: Path) -> Dict:
        """
        Run skill in Docker sandbox (premium feature)
        
        TODO: Implement actual Docker execution
        For MVP, return placeholder
        """
        logger.info("Sandbox execution (placeholder)")
        return {
            "exit_code": 0,
            "execution_time_ms": 0,
            "syscalls_detected": 0,
            "network_requests": 0,
            "file_writes": 0,
            "note": "Sandbox execution not yet implemented"
        }
    
    def _analyze_behavior(self, skill_dir: Path) -> Dict:
        """
        Analyze behavioral patterns (premium feature)
        
        TODO: Implement actual behavioral analysis
        For MVP, return placeholder
        """
        logger.info("Behavioral analysis (placeholder)")
        return {
            "anomalies_detected": 0,
            "confidence_score": 0,
            "risk_factors": [],
            "note": "Behavioral analysis not yet implemented"
        }


# Singleton instance
scanner_integration = ScannerIntegration()


def scan_skill(skill_path: str, tier: str = "free") -> Dict:
    """
    Convenience function to scan a skill.
    
    Args:
        skill_path: Path to skill directory or GitHub URL
        tier: "free" or "premium"
        
    Returns:
        dict: Scan results
    """
    return scanner_integration.scan_skill(skill_path, tier)
