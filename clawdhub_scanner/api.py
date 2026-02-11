"""
ClawdHub Security Scanner API with x402 Monetization.

Exposes the scanner as an HTTP API with tiered access:
- Free tier: Basic manifest validation
- Paid tier: Full deep scan (manifest + YARA pattern analysis) via x402 micropayments

Uses the x402 protocol (HTTP 402 Payment Required) for pay-per-scan pricing
settled in USDC on Base network.
"""

import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import X402Config
from .manifest_parser import ManifestParser
from .yara_scanner import YaraScanner, ScanSeverity


def create_app(config: Optional[X402Config] = None) -> FastAPI:
    """
    Create and configure the FastAPI application with x402 middleware.

    Args:
        config: x402 configuration. If None, loads from environment.

    Returns:
        Configured FastAPI application.
    """
    if config is None:
        config = X402Config.from_env()

    app = FastAPI(
        title="ClawdHub Security Scanner API",
        description=(
            "Pre-install security verification for ClawdHub skills. "
            "Detects supply chain attacks, credential theft, and malicious "
            "code patterns. Deep scans are monetized via x402 micropayments."
        ),
        version="0.2.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store config on app state for access in endpoints
    app.state.config = config

    # Ensure upload directory exists
    os.makedirs(config.upload_dir, exist_ok=True)

    # Register x402 payment middleware if configured
    _register_x402_middleware(app, config)

    # Register routes
    _register_routes(app)

    return app


def _register_x402_middleware(app: FastAPI, config: X402Config) -> None:
    """
    Register x402 payment middleware for paid endpoints.

    If the x402 SDK is installed and a pay_to_address is configured,
    the deep scan endpoint will require payment. Otherwise, endpoints
    operate in open/demo mode.
    """
    if not config.is_configured:
        print(
            "[x402] No PAY_TO_ADDRESS configured. "
            "Running in demo mode (all endpoints free)."
        )
        return

    try:
        from x402.http.middleware.fastapi import PaymentMiddlewareASGI
        from x402.http import HTTPFacilitatorClient, FacilitatorConfig, PaymentOption
        from x402.http.types import RouteConfig
        from x402.server import x402ResourceServer
        from x402.mechanisms.evm.exact import ExactEvmServerScheme

        facilitator_config = FacilitatorConfig(url=config.facilitator_url)
        facilitator_client = HTTPFacilitatorClient(facilitator_config)
        server = x402ResourceServer(facilitator_client)
        server.register(config.network, ExactEvmServerScheme())

        # Define which routes require payment
        routes = {}

        # Deep scan requires payment
        if config.deep_scan_price != "$0.00":
            routes["POST /api/v1/scan/deep"] = RouteConfig(
                accepts=[
                    PaymentOption(
                        scheme="exact",
                        price=config.deep_scan_price,
                        network=config.network,
                        pay_to=config.pay_to_address,
                    ),
                ]
            )

        if routes:
            app.add_middleware(
                PaymentMiddlewareASGI, routes=routes, server=server
            )
            print(
                f"[x402] Payment middleware active. "
                f"Deep scan price: {config.deep_scan_price} USDC "
                f"on {config.network}"
            )

    except ImportError:
        print(
            "[x402] x402 SDK not installed. "
            "Install with: pip install 'x402[fastapi,evm]'\n"
            "[x402] Running in demo mode (all endpoints free)."
        )


def _register_routes(app: FastAPI) -> None:
    """Register all API routes."""

    @app.get("/")
    async def root():
        """Health check and API information."""
        config: X402Config = app.state.config
        return {
            "service": "ClawdHub Security Scanner",
            "version": "0.2.0",
            "x402_enabled": config.is_configured,
            "endpoints": {
                "/api/v1/scan/manifest": {
                    "method": "POST",
                    "description": "Validate skill manifest (free)",
                    "price": "free",
                },
                "/api/v1/scan/deep": {
                    "method": "POST",
                    "description": "Full security scan with YARA patterns",
                    "price": config.deep_scan_price if config.is_configured else "free (demo mode)",
                    "payment": "x402 USDC" if config.is_configured else "none",
                },
            },
        }

    @app.post("/api/v1/scan/manifest")
    async def scan_manifest(skill_manifest: UploadFile = File(...)):
        """
        Free tier: Validate a skill.json manifest file.

        Checks for required fields, suspicious permissions, and
        obfuscation indicators. No payment required.

        Upload the skill.json file directly.
        """
        if not skill_manifest.filename or not skill_manifest.filename.endswith(".json"):
            raise HTTPException(
                status_code=400,
                detail="Upload must be a .json file (skill.json)",
            )

        content = await skill_manifest.read()
        try:
            manifest_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid JSON: {str(e)}"
            )

        # Write to temp file for the parser
        scan_id = str(uuid.uuid4())[:8]
        tmp_path = Path(tempfile.mkdtemp()) / "skill.json"
        tmp_path.write_text(content.decode("utf-8"))

        try:
            parser = ManifestParser()
            result = parser.parse(str(tmp_path))
            result_dict = result.to_dict()

            return {
                "scan_id": scan_id,
                "scan_type": "manifest",
                "skill_name": result_dict["skill_name"],
                "passed": result_dict["valid"],
                "risk_level": result_dict["risk_level"],
                "warnings": result_dict["warnings"],
                "errors": result_dict["errors"],
                "checks": result_dict["checks"],
                "payment_required": False,
            }
        finally:
            shutil.rmtree(tmp_path.parent, ignore_errors=True)

    @app.post("/api/v1/scan/deep")
    async def scan_deep(skill_archive: UploadFile = File(...)):
        """
        Paid tier: Full security scan with manifest validation and
        YARA pattern analysis.

        When x402 is enabled, this endpoint requires a USDC micropayment.
        The x402 middleware handles payment verification automatically --
        clients receive a 402 response with payment details, then retry
        with payment proof in the X-PAYMENT header.

        Upload a .zip archive of the skill directory.
        """
        if not skill_archive.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        scan_id = str(uuid.uuid4())[:8]
        config: X402Config = app.state.config
        work_dir = Path(config.upload_dir) / scan_id

        try:
            os.makedirs(work_dir, exist_ok=True)

            # Save uploaded archive
            archive_path = work_dir / skill_archive.filename
            content = await skill_archive.read()
            archive_path.write_bytes(content)

            # Extract if zip
            if skill_archive.filename.endswith(".zip"):
                import zipfile

                with zipfile.ZipFile(archive_path, "r") as zf:
                    # Security: check for path traversal
                    for info in zf.infolist():
                        if info.filename.startswith("/") or ".." in info.filename:
                            raise HTTPException(
                                status_code=400,
                                detail="Archive contains unsafe paths",
                            )
                    zf.extractall(work_dir / "skill")
                skill_dir = work_dir / "skill"
            else:
                # Treat as a directory of files (single file upload)
                skill_dir = work_dir
                archive_path.rename(work_dir / "index.js")

            # Phase 1: Manifest validation
            manifest_result = None
            manifest_path = skill_dir / "skill.json"
            if manifest_path.exists():
                parser = ManifestParser()
                manifest_obj = parser.parse(str(manifest_path))
                manifest_result = manifest_obj.to_dict()

            # Phase 2: YARA pattern scanning
            scanner = YaraScanner()
            yara_result = scanner.scan_skill(skill_dir)

            # Build response
            yara_matches_json = []
            for match in yara_result.matches:
                yara_matches_json.append({
                    "rule_name": match.rule_name,
                    "severity": match.severity.value,
                    "description": match.description,
                    "file_path": Path(match.file_path).name,
                    "matched_strings": match.matched_strings,
                    "line_numbers": match.line_numbers,
                })

            # Overall risk
            risk_levels = {"safe": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
            manifest_risk = risk_levels.get(
                (manifest_result or {}).get("risk_level", "SAFE").lower(), 0
            )
            yara_risk = 0
            if yara_result.matches:
                max_severity = max(
                    risk_levels.get(m.severity.value, 0)
                    for m in yara_result.matches
                )
                yara_risk = max_severity

            final_risk_score = max(manifest_risk, yara_risk)
            final_risk = [
                k for k, v in risk_levels.items() if v == final_risk_score
            ][0].upper()

            passed = final_risk_score <= 1  # SAFE or LOW

            return {
                "scan_id": scan_id,
                "scan_type": "deep",
                "passed": passed,
                "risk_level": final_risk,
                "manifest": manifest_result,
                "yara_scan": {
                    "passed": yara_result.passed,
                    "files_scanned": yara_result.files_scanned,
                    "matches": yara_matches_json,
                    "severity_summary": yara_result.get_severity_summary(),
                },
                "recommendation": (
                    "Skill appears safe to install"
                    if passed
                    else "DO NOT INSTALL - Security issues detected"
                ),
                "payment_settled": app.state.config.is_configured,
            }

        finally:
            # Clean up
            shutil.rmtree(work_dir, ignore_errors=True)

    @app.get("/api/v1/pricing")
    async def get_pricing():
        """Get current scan pricing and payment details."""
        config: X402Config = app.state.config
        return {
            "x402_enabled": config.is_configured,
            "network": config.network,
            "currency": "USDC",
            "tiers": {
                "manifest_scan": {
                    "price": config.manifest_scan_price,
                    "description": "Basic manifest validation",
                    "includes": [
                        "Required field validation",
                        "Permission analysis",
                        "Obfuscation detection",
                    ],
                },
                "deep_scan": {
                    "price": config.deep_scan_price,
                    "description": "Full security scan with YARA pattern matching",
                    "includes": [
                        "Everything in manifest scan",
                        "YARA pattern analysis (18 rules)",
                        "Credential theft detection",
                        "Malicious code detection",
                        "Prompt injection detection",
                    ],
                },
            },
            "payment_protocol": {
                "name": "x402",
                "spec": "https://www.x402.org",
                "flow": [
                    "1. POST to /api/v1/scan/deep",
                    "2. Receive 402 with payment details in PAYMENT-REQUIRED header",
                    "3. Sign USDC payment with your wallet",
                    "4. Retry request with PAYMENT-SIGNATURE header",
                    "5. Payment verified and settled, scan results returned",
                ],
            },
        }


def main():
    """Run the API server."""
    import uvicorn

    config = X402Config.from_env()
    app = create_app(config)

    print(f"\nStarting ClawdHub Scanner API on {config.host}:{config.port}")
    print(f"x402 payments: {'enabled' if config.is_configured else 'demo mode'}")
    if config.is_configured:
        print(f"Network: {config.network}")
        print(f"Deep scan price: {config.deep_scan_price} USDC")
    print()

    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
