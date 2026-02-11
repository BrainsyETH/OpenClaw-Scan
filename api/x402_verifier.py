#!/usr/bin/env python3
"""
x402 Payment Verification Module
Implements HTTP-based payment verification with x402 facilitator
"""

import os
import logging
import httpx
from typing import Optional, Dict

logger = logging.getLogger(__name__)

FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "0xF254aD619393A8B495342537d237d0FEA21567f2")
X402_NETWORK = os.getenv("X402_NETWORK", "eip155:8453")  # Base mainnet


async def verify_x402_payment(
    payment_signature: str,
    expected_amount: str,
    timeout: int = 30
) -> Dict:
    """
    Verify x402 payment with facilitator.
    
    Args:
        payment_signature: PAYMENT-SIGNATURE header from client
        expected_amount: Expected payment amount (e.g., "$0.50")
        timeout: HTTP timeout in seconds
        
    Returns:
        dict: {
            "valid": bool,
            "tx_hash": str or None,
            "amount": str or None,
            "network": str or None,
            "error": str or None
        }
    """
    logger.info(f"Verifying x402 payment: {payment_signature[:20]}...")
    
    try:
        # Parse payment signature (format: <network>:<tx_hash>:<signature>)
        parts = payment_signature.split(":")
        if len(parts) < 2:
            return {
                "valid": False,
                "tx_hash": None,
                "amount": None,
                "network": None,
                "error": "Invalid payment signature format"
            }
        
        network = parts[0] if len(parts) >= 3 else X402_NETWORK
        tx_hash = parts[1] if len(parts) >= 2 else parts[0]
        
        # Verify with facilitator
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{FACILITATOR_URL}/verify",
                json={
                    "network": network,
                    "tx_hash": tx_hash,
                    "expected_recipient": WALLET_ADDRESS,
                    "expected_amount": expected_amount
                },
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": data.get("valid", False),
                    "tx_hash": tx_hash,
                    "amount": data.get("amount", expected_amount),
                    "network": network,
                    "error": None
                }
            else:
                logger.error(f"Facilitator returned {response.status_code}: {response.text}")
                return {
                    "valid": False,
                    "tx_hash": tx_hash,
                    "amount": None,
                    "network": network,
                    "error": f"Facilitator error: {response.status_code}"
                }
                
    except httpx.TimeoutException:
        logger.error("Payment verification timeout")
        return {
            "valid": False,
            "tx_hash": None,
            "amount": None,
            "network": None,
            "error": "Verification timeout"
        }
    except Exception as e:
        logger.error(f"Payment verification failed: {e}", exc_info=True)
        return {
            "valid": False,
            "tx_hash": None,
            "amount": None,
            "network": None,
            "error": str(e)
        }


def generate_payment_requirements(
    amount: str,
    wallet_address: str = WALLET_ADDRESS,
    network: str = X402_NETWORK
) -> Dict:
    """
    Generate x402 payment requirements for 402 response.
    
    Args:
        amount: Payment amount (e.g., "$0.50")
        wallet_address: Recipient wallet address
        network: EVM network identifier (e.g., "eip155:8453")
        
    Returns:
        dict: Payment requirements for PAYMENT-REQUIRED header
    """
    return {
        "protocol": "x402",
        "version": "1.0",
        "recipient": wallet_address,
        "amount": amount,
        "currency": "USDC",
        "network": network,
        "facilitator": FACILITATOR_URL
    }
