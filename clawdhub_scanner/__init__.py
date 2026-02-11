"""
ClawdHub Security Scanner
Automated security scanning for ClawdHub skills to detect supply chain attacks.
"""

__version__ = '0.2.0'
__author__ = 'VesperThread'

from .manifest_parser import ManifestParser
from .yara_scanner import YaraScanner
from .config import X402Config

__all__ = ['ManifestParser', 'YaraScanner', 'X402Config']
