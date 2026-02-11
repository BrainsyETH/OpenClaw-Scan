# OpenClaw-Scan API

FastAPI server providing RESTful API for OpenClaw-Scan security scanner with x402 payment integration.

## Features

- **Free Tier:** Basic YARA scanning (no payment required)
- **Premium Tier ($0.75):** Runtime sandbox + behavioral analysis + signed attestation
- **x402 Payments:** Instant USDC micropayments on Base blockchain
- **Async Processing:** Non-blocking scan execution
- **Priority Queue:** Paid scans processed within 60s SLA

## Quick Start

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your wallet address and settings
```

### 3. Run Server

```bash
# Development (auto-reload)
python server.py

# Production (with uvicorn)
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Free scan
curl "http://localhost:8000/scan/free?skill=my-skill"

# Premium scan (will return 402 without payment)
curl "http://localhost:8000/scan/premium?skill=my-skill"
```

## API Documentation

Once the server is running, visit:
- **Interactive docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "scanner_version": "0.2.0",
  "x402_enabled": true,
  "network": "base-sepolia",
  "premium_price": "$0.75"
}
```

### `GET /scan/free?skill=<skill-name>`
Free tier security scan (no payment required).

**Features:**
- Manifest validation
- YARA pattern matching
- Static code analysis
- Risk scoring

**Response:**
```json
{
  "scan_id": "free-abc123",
  "skill": "my-skill",
  "verdict": "SAFE",
  "findings": [],
  "timestamp": "2026-02-10T12:34:56Z",
  "scanner_version": "0.2.0",
  "tier": "free"
}
```

### `GET /scan/premium?skill=<skill-name>`
Premium tier security scan (x402 payment required).

**Additional Features:**
- Runtime sandbox execution
- Behavioral analysis
- Signed attestation
- Priority queue (60s SLA)

**Without Payment:**
```http
HTTP/1.1 402 Payment Required
PAYMENT-REQUIRED: <base64 payment requirements>

{
  "error": "Payment required",
  "price": "$0.75",
  "network": "base-sepolia",
  "wallet": "0xYourWalletAddress"
}
```

**With Payment:**
```json
{
  "scan_id": "premium-xyz789",
  "skill": "my-skill",
  "verdict": "SAFE",
  "findings": [],
  "attestation": {
    "signature": "0x...",
    "skill_hash": "sha256:...",
    "timestamp": "2026-02-10T12:34:56Z"
  },
  "payment": {
    "tx_hash": "0x...",
    "amount": "$0.75",
    "network": "base-sepolia",
    "verified": true
  },
  "sandbox_results": {
    "exit_code": 0,
    "execution_time_ms": 1234,
    "syscalls_detected": 15,
    "network_requests": 0
  },
  "behavioral_analysis": {
    "anomalies_detected": 0,
    "confidence_score": 95
  }
}
```

### `POST /verify-attestation`
Verify a signed attestation (public, free).

**Request:**
```json
{
  "attestation": { ... },
  "signature": "0x..."
}
```

**Response:**
```json
{
  "valid": true,
  "signer": "OpenClaw-Scan",
  "reason": "Signature matches OpenClaw-Scan public key"
}
```

## Payment Flow (x402)

1. **Client requests premium scan:**
   ```bash
   GET /scan/premium?skill=my-skill
   ```

2. **Server returns 402 (no payment):**
   ```http
   HTTP/1.1 402 Payment Required
   PAYMENT-REQUIRED: <payment requirements>
   ```

3. **Client pays via x402-fetch (automatic):**
   ```javascript
   import { wrapFetchWithPayment } from 'x402-fetch';
   const response = await wrapFetchWithPayment(fetch)(
     'http://localhost:8000/scan/premium?skill=my-skill'
   );
   ```

4. **Server verifies payment and returns scan results**

## Development

### Project Structure

```
api/
├── server.py              # Main FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── README.md             # This file
└── modules/              # (to be created)
    ├── x402_middleware.py    # x402 payment verification
    ├── scanner_wrapper.py    # Scanner integration
    ├── attestation.py        # Signature generation/verification
    ├── sandbox.py            # Docker sandbox execution
    └── behavioral.py         # Behavioral analysis
```

### Next Steps

1. Implement x402 payment verification (`x402_middleware.py`)
2. Integrate existing scanner (`scanner_wrapper.py`)
3. Build Docker sandbox (`sandbox.py`)
4. Implement attestation signing (`attestation.py`)
5. Add behavioral analysis (`behavioral.py`)

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY api/requirements.txt .
RUN pip install -r requirements.txt
COPY api/ .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables (Production)

- `PORT`: Server port (default: 8000)
- `NODE_ENV`: `production`
- `WALLET_ADDRESS`: EVM wallet to receive payments (required)
- `NETWORK`: `base` (mainnet) or `base-sepolia` (testnet)
- `PREMIUM_PRICE`: `$0.75` (or custom price)
- `CDP_API_KEY_ID`: Coinbase CDP API key ID (for mainnet)
- `CDP_API_KEY_SECRET`: Coinbase CDP API secret (for mainnet)
- `ATTESTATION_PRIVATE_KEY`: ECC private key for signing (use secrets manager!)

## License

MIT
