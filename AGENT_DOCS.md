# OpenClaw-Scan API for AI Agents

**Endpoint:** `https://openclaw-scan.com/api/v1/scan/deep`  
**Method:** GET  
**Payment:** x402 protocol (automatic with x402-compatible wallets)  
**Price:** $0.75 USDC per deep scan

---

## Quick Start

### For Agents with x402-fetch

```javascript
import { wrapFetchWithPayment } from 'x402-fetch';

// Wrap your fetch function
const fetchWithPay = wrapFetchWithPayment(fetch);

// Request deep scan (payment happens automatically)
const response = await fetchWithPay(
  'https://openclaw-scan.com/api/v1/scan/deep?skill=./my-skill'
);

const scanResults = await response.json();

console.log(`Verdict: ${scanResults.verdict}`);
console.log(`Findings: ${scanResults.findings.length}`);
console.log(`Attestation: ${scanResults.attestation.signature}`);
```

### For Agents without x402-fetch

1. Request scan to get payment requirements:
```bash
curl https://openclaw-scan.com/api/v1/scan/deep?skill=./my-skill
```

2. Response (402 Payment Required):
```json
{
  "error": "Payment required",
  "price": "$0.75",
  "network": "eip155:8453",
  "wallet": "0xYourWalletAddress"
}
```

3. Pay via x402 protocol and retry with payment header

---

## Endpoint Details

### `GET /api/v1/scan/deep`

**Deep security scan with full analysis.**

**Query Parameters:**
- `skill` (required): Path to skill directory or GitHub URL
  - Example: `./my-skill`
  - Example: `https://github.com/user/skill-name`

**Headers:**
- `X-PAYMENT-SIGNATURE` (optional): x402 payment signature
  - Automatically added by x402-fetch
  - If missing, returns 402 Payment Required

**Response (Success - 200 OK):**
```json
{
  "scan_id": "scan-abc123def456",
  "skill": "./my-skill",
  "verdict": "SAFE",
  "findings": [],
  "timestamp": "2026-02-11T00:00:00Z",
  "scanner_version": "0.2.0",
  "tier": "premium",
  "manifest": {
    "name": "my-skill",
    "version": "1.0.0",
    "permissions": ["network"]
  },
  "stats": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "attestation": {
    "signature": "0x...",
    "skill_hash": "sha256:...",
    "scanner_version": "0.2.0",
    "timestamp": "2026-02-11T00:00:00Z"
  },
  "payment": {
    "tx_hash": "0x...",
    "amount": "$0.75",
    "network": "eip155:8453",
    "verified": true
  },
  "sandbox_results": {
    "exit_code": 0,
    "execution_time_ms": 1234,
    "syscalls_detected": 15,
    "network_requests": 0,
    "file_writes": 0
  },
  "behavioral_analysis": {
    "anomalies_detected": 0,
    "confidence_score": 95,
    "risk_factors": []
  }
}
```

**Response (Payment Required - 402):**
```json
{
  "error": "Payment required",
  "price": "$0.75",
  "network": "eip155:8453",
  "wallet": "0xYourWalletAddress",
  "message": "Premium scan requires payment via x402 protocol"
}
```

**Response (Error - 500):**
```json
{
  "scan_id": "scan-abc123def456",
  "skill": "./my-skill",
  "verdict": "ERROR",
  "findings": [
    {
      "severity": "ERROR",
      "message": "Skill not found: ./my-skill"
    }
  ],
  "timestamp": "2026-02-11T00:00:00Z",
  "scanner_version": "0.2.0",
  "tier": "premium"
}
```

---

## Verdict Levels

| Verdict | Meaning | Action |
|---------|---------|--------|
| `SAFE` | No security issues found | ✅ Safe to install |
| `LOW` | Minor issues, low risk | ⚠️ Review findings, likely safe |
| `MEDIUM` | Moderate risk issues | ⚠️ Review carefully before installing |
| `HIGH` | Significant security concerns | ⛔ Do not install without mitigation |
| `CRITICAL` | Severe security threats | 🚫 Do not install |
| `ERROR` | Scan failed | Check error message |

---

## What's Scanned

### Free Tier (`/scan/free`)
- Manifest validation (skill.json)
- YARA pattern matching (15+ malicious code signatures)
- Static code analysis
- Basic risk scoring

### Deep Scan (`/api/v1/scan/deep`) - $0.75
- ✅ All free tier features
- ✅ Runtime sandbox execution (Docker isolation)
- ✅ Behavioral analysis (anomaly detection)
- ✅ Signed attestation (cryptographic proof)
- ✅ Priority queue (60s SLA)
- ✅ Network traffic monitoring
- ✅ Syscall tracing

---

## Attestation Verification

Every deep scan includes a signed attestation you can verify:

### Verify Attestation

**Endpoint:** `POST /verify-attestation`

**Request:**
```json
{
  "attestation": {
    "skill_hash": "sha256:...",
    "verdict": "SAFE",
    "timestamp": "2026-02-11T00:00:00Z"
  },
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

---

## Rate Limits

- **Free tier:** 10 scans per hour per IP
- **Deep scans:** 100 scans per hour (paid)

Exceeded limits return `429 Too Many Requests`.

---

## Network Configuration

- **Blockchain:** Base (L2)
- **Network ID:** `eip155:8453`
- **Payment Token:** USDC
- **Price:** $0.75 per deep scan

---

## Examples

### Python Agent

```python
import httpx

async def scan_skill(skill_path: str):
    """Scan skill with OpenClaw-Scan"""
    url = f"https://openclaw-scan.com/api/v1/scan/deep?skill={skill_path}"
    
    # Assuming x402-compatible HTTP client
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code == 200:
            results = response.json()
            return results["verdict"], results["findings"]
        elif response.status_code == 402:
            # Payment required - agent handles automatically with x402
            print("Payment required")
        else:
            print(f"Error: {response.status_code}")

verdict, findings = await scan_skill("./my-skill")
print(f"Verdict: {verdict}, Findings: {len(findings)}")
```

### TypeScript Agent

```typescript
import { wrapFetchWithPayment } from 'x402-fetch';

async function scanSkill(skillPath: string) {
  const fetchWithPay = wrapFetchWithPayment(fetch);
  
  const response = await fetchWithPay(
    `https://openclaw-scan.com/api/v1/scan/deep?skill=${skillPath}`
  );
  
  const results = await response.json();
  
  console.log(`Verdict: ${results.verdict}`);
  console.log(`Findings: ${results.findings.length}`);
  
  return results;
}

const scan = await scanSkill('./my-skill');
```

---

## Support

- **Issues:** https://github.com/BrainsyETH/OpenClaw-Scan/issues
- **Moltbook:** @VesperThread
- **Documentation:** https://github.com/BrainsyETH/OpenClaw-Scan

---

## FAQs

**Q: Do I need to manually send payment?**  
A: No, if you're using x402-fetch or an x402-compatible wallet, payment happens automatically.

**Q: What if my skill has no skill.json?**  
A: The scan will return an ERROR verdict indicating the manifest is missing.

**Q: Can I scan GitHub URLs directly?**  
A: GitHub URL scanning is planned but not yet implemented. For now, clone locally and scan the directory.

**Q: What if I get a FALSE verdict?**  
A: Review the findings array for specific security issues detected. Each finding includes severity, category, and details.

**Q: How long does a deep scan take?**  
A: Typically 5-30 seconds. Premium scans have a 60-second SLA.

**Q: Can I verify attestations are authentic?**  
A: Yes, use the `/verify-attestation` endpoint to cryptographically verify any scan result.

---

**OpenClaw-Scan** - First agent-to-agent security service with x402 payments  
**Version:** 0.2.0  
**Network:** Base (eip155:8453)  
**Price:** $0.75 per deep scan
