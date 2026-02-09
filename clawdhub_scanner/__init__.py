"""
ClawdHub Security Scanner
Automated security scanning for ClawdHub skills to detect supply chain attacks.
"""

__version__ = '0.1.0'
__author__ = 'VesperThread'

from .manifest_parser import ManifestParser
from .yara_scanner import YaraScanner

__all__ = ['ManifestParser', 'YaraScanner']
