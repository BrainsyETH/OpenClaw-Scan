#!/usr/bin/env python3
"""
Attestation signing module for OpenClaw-Scan.

Signs scan results with ECC keypair to provide cryptographic proof
that the scan was performed by OpenClaw-Scan.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Optional
from datetime import datetime
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

logger = logging.getLogger(__name__)

# Load private key from environment (or generate if not set)
PRIVATE_KEY_HEX = os.getenv("ATTESTATION_PRIVATE_KEY", "")


def get_or_create_keypair() -> tuple[SigningKey, VerifyingKey]:
    """
    Get existing keypair from environment or create new one.
    
    Returns:
        tuple: (signing_key, verifying_key)
    """
    global PRIVATE_KEY_HEX
    
    if PRIVATE_KEY_HEX:
        # Load existing key
        try:
            private_key_bytes = bytes.fromhex(PRIVATE_KEY_HEX)
            signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            verifying_key = signing_key.get_verifying_key()
            logger.info("Loaded existing signing key from environment")
            return signing_key, verifying_key
        except Exception as e:
            logger.error(f"Failed to load signing key: {e}")
            logger.warning("Generating new keypair (will not persist!)")
    
    # Generate new keypair (WARNING: Not persistent!)
    signing_key = SigningKey.generate(curve=SECP256k1)
    verifying_key = signing_key.get_verifying_key()
    
    # Print key for environment setup
    private_key_hex = signing_key.to_string().hex()
    public_key_hex = verifying_key.to_string().hex()
    
    logger.warning("=" * 60)
    logger.warning("NEW SIGNING KEY GENERATED - ADD TO .env:")
    logger.warning(f"ATTESTATION_PRIVATE_KEY={private_key_hex}")
    logger.warning(f"# Public key (share with verifiers): {public_key_hex}")
    logger.warning("=" * 60)
    
    return signing_key, verifying_key


# Global keypair (loaded once at startup)
SIGNING_KEY, VERIFYING_KEY = get_or_create_keypair()


def hash_scan_result(scan_result: Dict) -> str:
    """
    Create deterministic hash of scan result for signing.
    
    Args:
        scan_result: Scan result dictionary
        
    Returns:
        str: SHA-256 hash (hex)
    """
    # Create canonical JSON (sorted keys, no whitespace)
    canonical = json.dumps(scan_result, sort_keys=True, separators=(',', ':'))
    
    # Hash with SHA-256
    hash_bytes = hashlib.sha256(canonical.encode('utf-8')).digest()
    
    return hash_bytes.hex()


def sign_attestation(scan_result: Dict) -> Dict:
    """
    Sign a scan result and return attestation object.
    
    Args:
        scan_result: Scan result from scanner
        
    Returns:
        dict: Attestation with signature
    """
    try:
        # Create attestation payload
        attestation = {
            "version": "1.0",
            "scanner": "OpenClaw-Scan",
            "scanner_version": scan_result.get("scanner_version", "0.2.0"),
            "scan_id": scan_result.get("scan_id"),
            "skill": scan_result.get("skill"),
            "verdict": scan_result.get("verdict"),
            "timestamp": scan_result.get("timestamp", datetime.utcnow().isoformat()),
            "findings_count": len(scan_result.get("findings", [])),
            "tier": scan_result.get("tier", "premium")
        }
        
        # Hash the attestation
        attestation_hash = hash_scan_result(attestation)
        attestation["hash"] = f"sha256:{attestation_hash}"
        
        # Sign the hash
        hash_bytes = bytes.fromhex(attestation_hash)
        signature_bytes = SIGNING_KEY.sign(hash_bytes, sigencode=sigencode_der)
        signature_hex = signature_bytes.hex()
        
        attestation["signature"] = f"0x{signature_hex}"
        attestation["signer"] = f"0x{VERIFYING_KEY.to_string().hex()}"
        
        logger.info(f"Signed attestation for scan {scan_result.get('scan_id')}")
        return attestation
        
    except Exception as e:
        logger.error(f"Failed to sign attestation: {e}", exc_info=True)
        # Return unsigned attestation as fallback
        return {
            "version": "1.0",
            "scanner": "OpenClaw-Scan",
            "error": "Signature generation failed",
            "scan_id": scan_result.get("scan_id"),
            "signature": "0x00"  # Invalid signature
        }


def verify_attestation(attestation: Dict, signature: str) -> bool:
    """
    Verify an attestation signature.
    
    Args:
        attestation: Attestation object (without signature field)
        signature: Signature to verify (hex string with 0x prefix)
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Remove signature from attestation for verification
        attestation_copy = attestation.copy()
        attestation_copy.pop("signature", None)
        attestation_copy.pop("signer", None)
        
        # Hash the attestation
        attestation_hash = hash_scan_result(attestation_copy)
        hash_bytes = bytes.fromhex(attestation_hash)
        
        # Parse signature
        if signature.startswith("0x"):
            signature = signature[2:]
        signature_bytes = bytes.fromhex(signature)
        
        # Verify with public key
        is_valid = VERIFYING_KEY.verify(
            signature_bytes,
            hash_bytes,
            sigdecode=sigdecode_der
        )
        
        logger.info(f"Attestation verification: {is_valid}")
        return is_valid
        
    except Exception as e:
        logger.error(f"Attestation verification failed: {e}")
        return False


def get_public_key_hex() -> str:
    """
    Get the public key for external verification.
    
    Returns:
        str: Public key (hex with 0x prefix)
    """
    return f"0x{VERIFYING_KEY.to_string().hex()}"
