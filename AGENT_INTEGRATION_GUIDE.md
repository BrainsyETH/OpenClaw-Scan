# Agent Integration Guide: OpenClaw-Scan x402 API

**Target audience:** AI agents wanting to integrate ClawdHub security scanning into their workflows.

---

## Quick Start

**API Endpoint:** `https://openclaw-scan-api.fly.dev` (example - update after deployment)

**Two tiers:**
- 🆓 **Free:** Basic manifest validation
- 💳 **Paid:** Full security scan ($0.50 USDC via x402)

**Authentication:** None required (payment handled by x402 protocol)

---

## Free Tier: Manifest Scan

Validate a ClawdHub skill's `skill.json` manifest for structural issues and suspicious permissions.

### cURL Example

```bash
curl -X POST "https://openclaw-scan-api.fly.dev/api/v1/scan/manifest" \
  -F "skill_manifest=@skill.json"
```

### Python Example

```python
import requests

# Upload skill.json
with open("skill.json", "rb") as f:
    response = requests.post(
        "https://openclaw-scan-api.fly.dev/api/v1/scan/manifest",
        files={"skill_manifest": ("skill.json", f, "application/json")}
    )

result = response.json()
print(f"Risk Level: {result['risk_level']}")
print(f"Passed: {result['passed']}")
if result['warnings']:
    print(f"Warnings: {result['warnings']}")
```

### Response Format

```json
{
  "scan_id": "a1b2c3d4",
  "scan_type": "manifest",
  "skill_name": "example-skill",
  "passed": true,
  "risk_level": "SAFE",
  "warnings": [],
  "errors": [],
  "checks": {
    "has_required_fields": true,
    "valid_permissions": true,
    "suspicious_patterns": false
  },
  "payment_required": false
}
```

---

## Paid Tier: Deep Scan with x402

Full security analysis including manifest validation + YARA pattern matching for credential theft, code injection, and supply chain attacks.

**Price:** $0.50 USDC (launch special, normally $1.00)  
**Network:** Base mainnet (eip155:8453)  
**Protocol:** x402 (HTTP 402 Payment Required)

### How x402 Works

1. **Initial request** → Server returns `402 Payment Required`
2. **Payment details** → Response includes payment proof format
3. **Sign payment** → Use your EVM wallet to sign USDC transfer
4. **Retry with proof** → Include signed payment in `X-PAYMENT` header
5. **Scan completes** → Server verifies payment and runs scan

### Step-by-Step Integration

#### Step 1: Make Initial Request (Get 402 Response)

```bash
curl -X POST "https://openclaw-scan-api.fly.dev/api/v1/scan/deep" \
  -F "skill_archive=@skill.zip" \
  -v
```

**Response (402 Payment Required):**
```
HTTP/1.1 402 Payment Required
PAYMENT-REQUIRED: {
  "scheme": "exact",
  "network": "eip155:8453",
  "token": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
  "amount": "500000",
  "pay_to": "0x...",
  "expires_at": "2026-02-10T19:00:00Z"
}

{
  "error": "payment_required",
  "message": "This endpoint requires payment",
  "details": { ... }
}
```

#### Step 2: Sign USDC Payment

**Using ethers.js (JavaScript):**

```javascript
import { ethers } from 'ethers';

// Parse payment details from 402 response
const paymentDetails = JSON.parse(response.headers['payment-required']);

// Connect wallet (Base network)
const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// USDC contract on Base
const usdcContract = new ethers.Contract(
  paymentDetails.token,  // USDC address
  ['function transfer(address to, uint256 amount) returns (bool)'],
  wallet
);

// Sign and send payment
const tx = await usdcContract.transfer(
  paymentDetails.pay_to,
  paymentDetails.amount  // 500000 = $0.50 (6 decimals)
);
const receipt = await tx.wait();

// Payment proof = transaction hash
const paymentProof = receipt.hash;
```

**Using web3.py (Python):**

```python
from web3 import Web3
import os

# Connect to Base mainnet
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
account = w3.eth.account.from_key(os.environ['PRIVATE_KEY'])

# USDC contract ABI (simplified)
usdc_abi = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

# Create contract instance
usdc_contract = w3.eth.contract(
    address=payment_details['token'],
    abi=usdc_abi
)

# Build transaction
tx = usdc_contract.functions.transfer(
    payment_details['pay_to'],
    int(payment_details['amount'])
).build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 100000,
    'gasPrice': w3.eth.gas_price
})

# Sign and send
signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

payment_proof = receipt['transactionHash'].hex()
```

#### Step 3: Retry Request with Payment Proof

```bash
curl -X POST "https://openclaw-scan-api.fly.dev/api/v1/scan/deep" \
  -F "skill_archive=@skill.zip" \
  -H "X-PAYMENT: 0xabcdef1234567890..."  # Transaction hash
```

**Response (200 OK with scan results):**

```json
{
  "scan_id": "e5f6g7h8",
  "scan_type": "deep",
  "passed": false,
  "risk_level": "CRITICAL",
  "manifest": {
    "skill_name": "suspicious-skill",
    "valid": false,
    "risk_level": "HIGH",
    "warnings": ["Requests excessive permissions"]
  },
  "yara_scan": {
    "passed": false,
    "files_scanned": 5,
    "matches": [
      {
        "rule_name": "credential_exfiltration",
        "severity": "CRITICAL",
        "description": "Detected credential theft pattern",
        "file_path": "index.js",
        "matched_strings": ["process.env", "https://webhook.site"],
        "line_numbers": [42, 56]
      }
    ],
    "severity_summary": {
      "CRITICAL": 1,
      "HIGH": 0,
      "MEDIUM": 0,
      "LOW": 0
    }
  },
  "recommendation": "DO NOT INSTALL - Security issues detected",
  "payment_settled": true
}
```

---

## Complete Integration Example (Python)

```python
import requests
import os
from web3 import Web3
from typing import Dict, Any

class OpenClawScanner:
    """Client for OpenClaw-Scan x402 API."""
    
    def __init__(self, api_url: str, private_key: str):
        self.api_url = api_url
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
        self.account = self.w3.eth.account.from_key(private_key)
    
    def scan_manifest(self, manifest_path: str) -> Dict[str, Any]:
        """Free tier: Scan skill.json manifest."""
        with open(manifest_path, 'rb') as f:
            response = requests.post(
                f"{self.api_url}/api/v1/scan/manifest",
                files={'skill_manifest': ('skill.json', f, 'application/json')}
            )
        response.raise_for_status()
        return response.json()
    
    def scan_deep(self, skill_zip_path: str) -> Dict[str, Any]:
        """Paid tier: Full security scan with x402 payment."""
        
        # Step 1: Initial request (get 402)
        with open(skill_zip_path, 'rb') as f:
            response = requests.post(
                f"{self.api_url}/api/v1/scan/deep",
                files={'skill_archive': ('skill.zip', f, 'application/zip')}
            )
        
        if response.status_code == 402:
            # Step 2: Pay with USDC
            payment_details = response.json()['details']
            tx_hash = self._pay_usdc(payment_details)
            
            # Step 3: Retry with payment proof
            with open(skill_zip_path, 'rb') as f:
                response = requests.post(
                    f"{self.api_url}/api/v1/scan/deep",
                    files={'skill_archive': ('skill.zip', f, 'application/zip')},
                    headers={'X-PAYMENT': tx_hash}
                )
        
        response.raise_for_status()
        return response.json()
    
    def _pay_usdc(self, payment_details: Dict[str, Any]) -> str:
        """Sign and send USDC payment, return tx hash."""
        usdc_abi = [...]  # Simplified for example
        usdc = self.w3.eth.contract(
            address=payment_details['token'],
            abi=usdc_abi
        )
        
        tx = usdc.functions.transfer(
            payment_details['pay_to'],
            int(payment_details['amount'])
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_hash.hex()

# Usage
scanner = OpenClawScanner(
    api_url="https://openclaw-scan-api.fly.dev",
    private_key=os.environ['PRIVATE_KEY']
)

# Free manifest scan
result = scanner.scan_manifest("skill.json")
print(f"Manifest risk: {result['risk_level']}")

# Paid deep scan
result = scanner.scan_deep("skill.zip")
print(f"Deep scan verdict: {result['recommendation']}")
```

---

## Troubleshooting

### "402 Payment Required" on Every Request

**Cause:** Payment proof not included or invalid.

**Solution:**
- Ensure `X-PAYMENT` header contains valid transaction hash
- Check transaction is confirmed on Base network
- Verify payment amount matches required price

### "Payment verification failed"

**Cause:** Payment didn't settle or went to wrong address.

**Solution:**
- Check Base network explorer: https://basescan.org/tx/YOUR_TX_HASH
- Verify recipient matches `pay_to` address from 402 response
- Ensure payment amount is exact (500000 = $0.50 USDC, 6 decimals)

### "Network mismatch"

**Cause:** Payment sent on wrong network (e.g., Sepolia testnet instead of mainnet).

**Solution:**
- Check API's `X402_NETWORK` setting in `/api/v1/pricing`
- Mainnet: `eip155:8453` (Base)
- Testnet: `eip155:84532` (Base Sepolia)

### Rate Limits

**Current limits:** None enforced, but be respectful.

**Best practice:** Cache scan results, don't re-scan same skill repeatedly.

---

## Support

**Moltbook:** @VesperThread  
**GitHub Issues:** https://github.com/BrainsyETH/OpenClaw-Scan/issues  
**Documentation:** https://github.com/BrainsyETH/OpenClaw-Scan

---

## Pricing

**Current (Launch Special):**
- Manifest scan: Free
- Deep scan: $0.50 USDC

**Regular pricing (after launch period):**
- Manifest scan: Free
- Deep scan: $1.00 USDC

Check `/api/v1/pricing` endpoint for current rates.

---

## What's Next?

**Roadmap:**
- ERC-8004 integration (on-chain skill reputation)
- Validator network (decentralized security audits)
- Continuous monitoring (alert on skill updates)
- MCP protocol support (native Claude integration)

**Community:** Join the discussion on Moltbook (m/security)
