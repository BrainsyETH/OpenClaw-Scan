"""
x402 Monetization Configuration for ClawdHub Security Scanner.

Manages settings for x402 payment protocol integration including
wallet addresses, network selection, pricing, and facilitator URLs.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


# Network identifiers (CAIP-2 format)
BASE_SEPOLIA = "eip155:84532"
BASE_MAINNET = "eip155:8453"

# Default facilitator URLs
TESTNET_FACILITATOR = "https://x402.org/facilitator"

# Default pricing (in USD, paid as USDC)
DEFAULT_DEEP_SCAN_PRICE = "$0.01"
DEFAULT_MANIFEST_SCAN_PRICE = "$0.00"  # Free tier


@dataclass
class X402Config:
    """Configuration for x402 payment integration."""

    # Wallet address to receive payments (EVM address)
    pay_to_address: str = ""

    # Network for payment settlement
    network: str = BASE_SEPOLIA

    # Facilitator URL for payment verification/settlement
    facilitator_url: str = TESTNET_FACILITATOR

    # Pricing per scan type
    deep_scan_price: str = DEFAULT_DEEP_SCAN_PRICE
    manifest_scan_price: str = DEFAULT_MANIFEST_SCAN_PRICE

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8402

    # Upload directory for skill archives
    upload_dir: str = "/tmp/clawdhub_scans"

    @classmethod
    def from_env(cls) -> "X402Config":
        """Load configuration from environment variables."""
        return cls(
            pay_to_address=os.environ.get("PAY_TO_ADDRESS", ""),
            network=os.environ.get("X402_NETWORK", BASE_SEPOLIA),
            facilitator_url=os.environ.get(
                "X402_FACILITATOR_URL", TESTNET_FACILITATOR
            ),
            deep_scan_price=os.environ.get(
                "DEEP_SCAN_PRICE", DEFAULT_DEEP_SCAN_PRICE
            ),
            manifest_scan_price=os.environ.get(
                "MANIFEST_SCAN_PRICE", DEFAULT_MANIFEST_SCAN_PRICE
            ),
            host=os.environ.get("API_HOST", "0.0.0.0"),
            port=int(os.environ.get("API_PORT", "8402")),
            upload_dir=os.environ.get("UPLOAD_DIR", "/tmp/clawdhub_scans"),
        )

    @property
    def is_mainnet(self) -> bool:
        return self.network == BASE_MAINNET

    @property
    def is_configured(self) -> bool:
        """Check if payment receiving address is set."""
        return bool(self.pay_to_address)
