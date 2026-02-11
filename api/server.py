#!/usr/bin/env python3
"""
OpenClaw-Scan API Server with x402 Payment Integration

Provides RESTful API for security scanning with premium features
protected by x402 micropayments.

Free tier: Basic YARA scan
Premium tier ($0.75): Runtime sandbox + behavioral analysis + signed attestation
"""

import os
import json
import logging
import base64
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from attestation_signer import sign_attestation, verify_attestation, get_public_key_hex
# Local imports
from scanner_integration import scan_skill
from x402_verifier import verify_x402_payment, generate_payment_requirements

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenClaw-Scan API",
    description="Security scanner for ClawdHub skills with x402 payments",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration (allow all origins for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to known origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")  # Wallet to receive payments
X402_NETWORK = os.getenv("X402_NETWORK", "eip155:8453")  # Base mainnet (was: base-sepolia)
PREMIUM_PRICE = os.getenv("PREMIUM_PRICE", "$0.75")  # Price per premium scan
FACILITATOR_URL = os.getenv("FACILITATOR_URL", "https://x402.org/facilitator")

# Legacy support
NETWORK = os.getenv("NETWORK", X402_NETWORK)

# Pydantic models
class ScanRequest(BaseModel):
    """Request model for scan endpoints"""
    skill: str  # Skill name or GitHub URL
    
class ScanResponse(BaseModel):
    """Response model for scan results"""
    scan_id: str
    skill: str
    verdict: str  # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    findings: list
    timestamp: str
    scanner_version: str
    tier: str  # "free" or "premium"
    
class PremiumScanResponse(ScanResponse):
    """Extended response for premium scans"""
    attestation: dict  # Signed attestation
    payment: dict  # Payment details
    sandbox_results: Optional[dict] = None
    behavioral_analysis: Optional[dict] = None

class AttestationVerifyRequest(BaseModel):
    """Request model for attestation verification"""
    attestation: dict
    signature: str

class AttestationVerifyResponse(BaseModel):
    """Response model for attestation verification"""
    valid: bool
    signer: Optional[str] = None
    reason: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status and server info
    """
    return {
        "status": "ok",
        "scanner_version": "0.2.0",
        "x402_enabled": True,
        "network": NETWORK,
        "premium_price": PREMIUM_PRICE
    }

# Free tier endpoint (no payment required)
@app.get("/scan/free", response_model=ScanResponse)
async def scan_free(
    skill: str = Query(..., description="Skill name or GitHub URL to scan")
):
    """
    Free tier security scan.
    
    Features:
    - Manifest validation
    - YARA pattern matching
    - Static code analysis
    - Basic risk scoring
    
    Args:
        skill: Skill name or GitHub URL
        
    Returns:
        ScanResponse: Scan results
        
    Raises:
        HTTPException: If scan fails
    """
    try:
        logger.info(f"Free scan requested for skill: {skill}")
        
        # Run actual scanner
        results = scan_skill(skill, tier="free")
        
        return ScanResponse(
            scan_id=results["scan_id"],
            skill=results["skill"],
            verdict=results["verdict"],
            findings=results["findings"],
            timestamp=results["timestamp"],
            scanner_version=results["scanner_version"],
            tier=results["tier"]
        )
    except Exception as e:
        logger.error(f"Free scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Premium tier endpoint (x402 payment required)
@app.get("/scan/premium", response_model=PremiumScanResponse)
async def scan_premium(
    request: Request,
    skill: str = Query(..., description="Skill name or GitHub URL to scan"),
    payment_signature: Optional[str] = Header(None, alias="X-PAYMENT-SIGNATURE")
):
    """
    Premium tier security scan with x402 payment.
    
    Features:
    - All free tier features
    - Runtime sandbox execution
    - Behavioral analysis
    - Signed attestation
    - Priority queue (60s SLA)
    
    Price: $0.75 per scan
    
    Args:
        skill: Skill name or GitHub URL
        payment_signature: x402 payment signature (from header)
        
    Returns:
        PremiumScanResponse: Full scan results with attestation
        
    Raises:
        HTTPException: 402 if no payment, 500 if scan fails
    """
    try:
        logger.info(f"Premium scan requested for skill: {skill}")
        
        # Check for payment signature
        if not payment_signature:
            # No payment provided - return 402 Payment Required
            logger.info("No payment signature, returning 402")
            
            # Build payment requirements
            payment_requirements = {
                "x402Version": 1,
                "scheme": "exact",
                "network": NETWORK,
                "price": PREMIUM_PRICE,
                "wallet": WALLET_ADDRESS,
                "description": f"Premium security scan for {skill}",
                "facilitator": FACILITATOR_URL
            }
            
            # Return 402 with payment requirements in header
            # Encode payment requirements as Base64 JSON per x402 spec
            payment_json = json.dumps(payment_requirements)
            payment_base64 = base64.b64encode(payment_json.encode('utf-8')).decode('utf-8')
            
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment required",
                    "price": PREMIUM_PRICE,
                    "network": NETWORK,
                    "wallet": WALLET_ADDRESS,
                    "message": "Premium scan requires payment via x402 protocol"
                },
                headers={
                    "PAYMENT-REQUIRED": payment_base64
                }
            )
        
        # Verify payment with facilitator
        # Verify x402 payment
        logger.info("Payment signature received, verifying...")
        payment_result = await verify_x402_payment(payment_signature, PREMIUM_PRICE)
        
        if not payment_result["valid"]:
            error_msg = payment_result.get("error", "Payment verification failed")
            raise HTTPException(status_code=402, detail=error_msg)
        
        logger.info("Payment verified, running premium scan...")
        
        # Run actual premium scanner
        scan_results = scan_skill(skill, tier="premium")
        
        # Add real signed attestation
        scan_results["attestation"] = sign_attestation(scan_results)
        
        # Add payment details
        scan_results["payment"] = {
            "tx_hash": payment_result["tx_hash"],
            "amount": payment_result["amount"] or PREMIUM_PRICE,
            "network": payment_result["network"] or NETWORK,
            "verified": True
        }
        
        # Settle payment asynchronously (don't block response)
        # TODO: Implement async payment settlement
        # asyncio.create_task(settle_x402_payment(payment_signature))
        
        logger.info(f"Premium scan complete for {skill}")
        return scan_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Premium scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Attestation verification endpoint (public, free)
@app.post("/verify-attestation", response_model=AttestationVerifyResponse)
async def verify_attestation_endpoint(request: AttestationVerifyRequest):
    """
    Verify a signed attestation from a premium scan.
    
    Public endpoint (no payment required) for anyone to verify
    that an attestation was genuinely issued by OpenClaw-Scan.
    
    Args:
        request: Attestation and signature to verify
        
    Returns:
        AttestationVerifyResponse: Verification result
    """
    try:
        logger.info("Attestation verification requested")
        
        # Verify the attestation signature
        is_valid = verify_attestation(request.attestation, request.signature)
        
        if is_valid:
            return AttestationVerifyResponse(
                valid=True,
                signer=get_public_key_hex(),
                reason="Signature matches OpenClaw-Scan public key"
            )
        else:
            return AttestationVerifyResponse(
                valid=False,
                signer=None,
                reason="Invalid signature or tampered attestation"
            )
    except Exception as e:
        logger.error(f"Attestation verification failed: {e}")
        return AttestationVerifyResponse(
            valid=False,
            reason=f"Verification error: {str(e)}"
        )

# Agent-facing endpoint (canonical)
@app.get("/api/v1/scan/deep", response_model=PremiumScanResponse)
async def scan_deep_v1(
    request: Request,
    skill: str = Query(..., description="Skill name or path to scan"),
    payment_signature: Optional[str] = Header(None, alias="X-PAYMENT-SIGNATURE")
):
    """
    Deep security scan with x402 payment (agent-facing endpoint).
    
    This is the canonical endpoint for AI agents with x402-compatible wallets.
    
    Features:
    - Full YARA pattern matching
    - Manifest validation
    - Runtime sandbox (premium)
    - Behavioral analysis (premium)
    - Signed attestation (premium)
    
    Price: $0.75 per scan (paid via x402 protocol)
    
    Usage:
        # With x402-fetch (automatic payment)
        const scan = await wrapFetchWithPayment(fetch)(
          'https://openclaw-scan.com/api/v1/scan/deep?skill=my-skill'
        );
    
    Args:
        skill: Skill name or GitHub URL to scan
        payment_signature: x402 payment signature (automatic with x402-fetch)
        
    Returns:
        PremiumScanResponse: Full scan results with attestation
    """
    # Delegate to premium scan endpoint
    return await scan_premium(request, skill, payment_signature)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "OpenClaw-Scan API",
        "version": "0.2.0",
        "description": "Security scanner for ClawdHub skills with x402 payments",
        "endpoints": {
            "health": "/health",
            "agent_scan": "/api/v1/scan/deep?skill=<skill-path>",
            "free_scan": "/scan/free?skill=<skill-name>",
            "premium_scan": "/scan/premium?skill=<skill-name>",
            "verify_attestation": "/verify-attestation",
            "docs": "/docs"
        },
        "pricing": {
            "free": "Basic YARA scan (no payment required)",
            "deep": f"{PREMIUM_PRICE} - Full security analysis (x402 payment)"
        },
        "network": X402_NETWORK,
        "wallet": WALLET_ADDRESS or "NOT_CONFIGURED"
    }

# Run server (for local development)
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
