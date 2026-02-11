"""
Tests for the ClawdHub Scanner API with x402 monetization.
"""

import io
import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from clawdhub_scanner.api import create_app
from clawdhub_scanner.config import X402Config


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def demo_config():
    """Config with no payment address (demo/free mode)."""
    return X402Config(
        pay_to_address="",
        upload_dir="/tmp/clawdhub_test_scans",
    )


@pytest.fixture
def paid_config():
    """Config with payment address set (x402 enabled)."""
    return X402Config(
        pay_to_address="0x1234567890abcdef1234567890abcdef12345678",
        deep_scan_price="$0.05",
        upload_dir="/tmp/clawdhub_test_scans",
    )


@pytest.fixture
def client(demo_config):
    """Test client in demo mode."""
    app = create_app(demo_config)
    return TestClient(app)


def _make_skill_zip(skill_dir: Path) -> bytes:
    """Create a zip archive from a skill fixture directory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
    buf.seek(0)
    return buf.read()


class TestHealthEndpoint:
    def test_root_returns_service_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "ClawdHub Security Scanner"
        assert "endpoints" in data

    def test_root_shows_demo_mode(self, client):
        resp = client.get("/")
        data = resp.json()
        assert data["x402_enabled"] is False

    def test_root_shows_x402_enabled(self, paid_config):
        app = create_app(paid_config)
        c = TestClient(app)
        resp = c.get("/")
        data = resp.json()
        assert data["x402_enabled"] is True


class TestPricingEndpoint:
    def test_pricing_returns_tiers(self, client):
        resp = client.get("/api/v1/pricing")
        assert resp.status_code == 200
        data = resp.json()
        assert "tiers" in data
        assert "manifest_scan" in data["tiers"]
        assert "deep_scan" in data["tiers"]

    def test_pricing_shows_x402_flow(self, client):
        resp = client.get("/api/v1/pricing")
        data = resp.json()
        assert "payment_protocol" in data
        assert data["payment_protocol"]["name"] == "x402"


class TestManifestScan:
    def test_scan_safe_manifest(self, client):
        manifest_path = FIXTURES_DIR / "safe-skill" / "skill.json"
        with open(manifest_path, "rb") as f:
            resp = client.post(
                "/api/v1/scan/manifest",
                files={"skill_manifest": ("skill.json", f, "application/json")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["scan_type"] == "manifest"
        assert data["passed"] is True
        assert data["payment_required"] is False

    def test_scan_malicious_manifest(self, client):
        manifest_path = FIXTURES_DIR / "malicious-skill" / "skill.json"
        with open(manifest_path, "rb") as f:
            resp = client.post(
                "/api/v1/scan/manifest",
                files={"skill_manifest": ("skill.json", f, "application/json")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["scan_type"] == "manifest"
        # Malicious manifest should have issues
        assert data["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]

    def test_rejects_non_json(self, client):
        resp = client.post(
            "/api/v1/scan/manifest",
            files={"skill_manifest": ("readme.txt", b"not json", "text/plain")},
        )
        assert resp.status_code == 400

    def test_rejects_invalid_json(self, client):
        resp = client.post(
            "/api/v1/scan/manifest",
            files={"skill_manifest": ("skill.json", b"{bad json", "application/json")},
        )
        assert resp.status_code == 400


class TestDeepScan:
    def test_deep_scan_safe_skill(self, client):
        zip_bytes = _make_skill_zip(FIXTURES_DIR / "safe-skill")
        resp = client.post(
            "/api/v1/scan/deep",
            files={"skill_archive": ("safe-skill.zip", zip_bytes, "application/zip")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["scan_type"] == "deep"
        assert data["passed"] is True
        assert data["risk_level"] in ["SAFE", "LOW"]
        assert "manifest" in data
        assert "yara_scan" in data

    def test_deep_scan_malicious_skill(self, client):
        zip_bytes = _make_skill_zip(FIXTURES_DIR / "malicious-skill")
        resp = client.post(
            "/api/v1/scan/deep",
            files={"skill_archive": ("malicious-skill.zip", zip_bytes, "application/zip")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["scan_type"] == "deep"
        assert data["passed"] is False
        assert data["risk_level"] in ["HIGH", "CRITICAL"]
        assert len(data["yara_scan"]["matches"]) > 0
        assert "DO NOT INSTALL" in data["recommendation"]

    def test_deep_scan_returns_yara_details(self, client):
        zip_bytes = _make_skill_zip(FIXTURES_DIR / "malicious-skill")
        resp = client.post(
            "/api/v1/scan/deep",
            files={"skill_archive": ("malicious-skill.zip", zip_bytes, "application/zip")},
        )
        data = resp.json()
        matches = data["yara_scan"]["matches"]
        assert len(matches) > 0
        # Each match should have required fields
        for match in matches:
            assert "rule_name" in match
            assert "severity" in match
            assert "description" in match

    def test_deep_scan_rejects_path_traversal(self, client):
        """Ensure zip files with path traversal attacks are rejected."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../../../etc/passwd", "root:x:0:0:")
        buf.seek(0)
        resp = client.post(
            "/api/v1/scan/deep",
            files={"skill_archive": ("evil.zip", buf.read(), "application/zip")},
        )
        assert resp.status_code == 400


class TestX402Config:
    def test_config_from_env(self):
        with patch.dict(
            "os.environ",
            {
                "PAY_TO_ADDRESS": "0xABC",
                "X402_NETWORK": "eip155:8453",
                "DEEP_SCAN_PRICE": "$0.05",
            },
        ):
            cfg = X402Config.from_env()
            assert cfg.pay_to_address == "0xABC"
            assert cfg.is_mainnet is True
            assert cfg.deep_scan_price == "$0.05"

    def test_config_defaults(self):
        cfg = X402Config()
        assert cfg.pay_to_address == ""
        assert cfg.is_configured is False
        assert cfg.network == "eip155:84532"

    def test_config_is_configured(self):
        cfg = X402Config(pay_to_address="0x123")
        assert cfg.is_configured is True
