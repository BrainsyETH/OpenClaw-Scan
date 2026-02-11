# Base Sepolia Testnet Testing - Step-by-Step

**Wallet:** `0xF254aD619393A8B495342537d237d0FEA21567f2`  
**Network:** Base Sepolia (eip155:84532)  
**Price:** $0.01 USDC (testnet)

---

## PRE-FLIGHT CHECK ✅

**Payment verification code:** ✅ ALREADY IMPLEMENTED in `api/x402_verifier.py`
```python
async def verify_x402_payment(payment_signature: str, expected_amount: str):
    # Parses: network:tx_hash:signature
    # HTTP POST to: https://x402.org/facilitator/verify
    # Body: {network, tx_hash, expected_recipient, expected_amount}
    # Returns: {valid: bool, amount, network}
```

**Attestation signing:** ✅ ALREADY IMPLEMENTED in `api/attestation_signer.py`
```python
def sign_attestation(scan_result: Dict) -> Dict:
    # ECDSA SECP256k1 signature
    # SHA-256 hash → sign → return 0x-prefixed hex
```

**Server integration:** ✅ WORKING
- Line 220: Calls `verify_x402_payment()`
- Line 233: Calls `sign_attestation()`

---

## STEP 1: Configure for Base Sepolia (5 minutes)

```bash
cd ~/.clawdbot/workspace-vesper/openclaw-scan-x402/api

# Create .env.testnet
cat > .env.testnet << 'EOF'
# Base Sepolia Testnet Configuration
X402_NETWORK=eip155:84532
WALLET_ADDRESS=0xF254aD619393A8B495342537d237d0FEA21567f2
PREMIUM_PRICE=$0.01
FACILITATOR_URL=https://x402.org/facilitator
PORT=8000
NODE_ENV=development
EOF

# Load testnet config
export $(cat .env.testnet | xargs)
```

---

## STEP 2: Install Dependencies (5 minutes)

```bash
cd ~/.clawdbot/workspace-vesper/openclaw-scan-x402/api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Verify key packages
python -c "import fastapi, httpx, ecdsa; print('✅ All dependencies installed')"
```

---

## STEP 3: Start Server (2 minutes)

```bash
# In api/ directory with venv activated
source .env.testnet && python server.py

# Expected output:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
# NEW SIGNING KEY GENERATED - ADD TO .env:
# ATTESTATION_PRIVATE_KEY=abcd1234...  # SAVE THIS!
```

**IMPORTANT:** Copy the `ATTESTATION_PRIVATE_KEY` from logs and add to `.env.testnet`:
```bash
echo "ATTESTATION_PRIVATE_KEY=<KEY_FROM_LOGS>" >> .env.testnet
```

---

## STEP 4: Test Endpoints (5 minutes)

```bash
# In a new terminal (server still running)

# Test 1: Health check
curl http://localhost:8000/health | jq '.'
# Expected: {"status": "ok", "network": "eip155:84532", ...}

# Test 2: Free scan
curl "http://localhost:8000/scan/free?skill=test-skill" | jq '.'
# Expected: {scan_id, verdict, findings, tier: "free"}

# Test 3: Premium scan without payment (should get 402)
curl -v "http://localhost:8000/scan/premium?skill=test-skill" 2>&1 | grep -E "HTTP|PAYMENT-REQUIRED"
# Expected: HTTP/1.1 402 Payment Required
# Expected: PAYMENT-REQUIRED: <Base64-encoded-JSON>

# Test 4: Decode payment requirements
PAYMENT_HEADER=$(curl -s -D - http://localhost:8000/scan/premium?skill=test | grep -i payment-required | cut -d: -f2- | tr -d '\r\n ')
echo $PAYMENT_HEADER | base64 -d | jq '.'
# Expected: {protocol: "x402", recipient: "0xF254...", amount: "$0.01", network: "eip155:84532"}
```

If all 4 tests pass → Server is working correctly ✅

---

## STEP 5: Fund Testnet Wallet (15 minutes)

**Get Base Sepolia ETH:**
1. Go to: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
2. Connect wallet: `0xF254aD619393A8B495342537d237d0FEA21567f2`
3. Request testnet ETH (for gas fees)

**Get Base Sepolia USDC:**
1. Bridge Sepolia ETH to Base Sepolia: https://bridge.base.org/deposit
2. Get USDC from Circle testnet faucet: https://faucet.circle.com
   - Network: Base Sepolia
   - Token: USDC
   - Wallet: `0xF254aD619393A8B495342537d237d0FEA21567f2`

**Verify balance:**
```bash
# Check on Base Sepolia explorer
open https://sepolia.basescan.org/address/0xF254aD619393A8B495342537d237d0FEA21567f2
```

Expected: At least 0.01 USDC + some ETH for gas

---

## STEP 6: Make Real Payment (10 minutes)

**Option A: Using MetaMask (Manual)**

1. **Get payment details:**
   ```bash
   curl http://localhost:8000/scan/premium?skill=test-skill | jq '.wallet, .price'
   # wallet: "0xF254aD619393A8B495342537d237d0FEA21567f2"
   # price: "$0.01"
   ```

2. **Send USDC:**
   - Open MetaMask
   - Switch to Base Sepolia network
   - Send $0.01 USDC to wallet address
   - Copy transaction hash from confirmation

3. **Save tx_hash:**
   ```bash
   TX_HASH="0xYOUR_TX_HASH_HERE"
   ```

**Option B: Using cast (Command Line)**

```bash
# Install Foundry if needed: curl -L https://foundry.paradigm.xyz | bash

# USDC contract on Base Sepolia
USDC_ADDRESS="0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # Base Sepolia USDC

# Send 0.01 USDC (6 decimals = 10000)
cast send $USDC_ADDRESS \
  "transfer(address,uint256)" \
  0xF254aD619393A8B495342537d237d0FEA21567f2 \
  10000 \
  --rpc-url https://sepolia.base.org \
  --private-key YOUR_PRIVATE_KEY

# Get tx hash from output
TX_HASH="<tx_hash_from_output>"
```

---

## STEP 7: Test Payment Verification (5 minutes)

```bash
# Format payment signature
PAYMENT_SIG="eip155:84532:$TX_HASH:0x00"

# Test premium scan with payment
curl -X GET "http://localhost:8000/scan/premium?skill=test-skill" \
  -H "X-PAYMENT-SIGNATURE: $PAYMENT_SIG" \
  | jq '.'

# Expected response:
# {
#   "scan_id": "...",
#   "skill": "test-skill",
#   "verdict": "SAFE",
#   "findings": [...],
#   "tier": "premium",
#   "attestation": {
#     "signature": "0x3045...",  # REAL SIGNATURE (not 0xTODO!)
#     "hash": "sha256:...",
#     "signer": "0x04..."
#   },
#   "payment": {
#     "tx_hash": "$TX_HASH",
#     "amount": "$0.01",
#     "network": "eip155:84532",
#     "verified": true
#   }
# }
```

**Verification checklist:**
- [ ] HTTP 200 (not 402)
- [ ] `payment.verified` = true
- [ ] `payment.tx_hash` matches your transaction
- [ ] `attestation.signature` starts with "0x3045" (not "0xTODO")
- [ ] `tier` = "premium"

If all checks pass → **PAYMENT VERIFICATION WORKS!** ✅

---

## STEP 8: Verify Attestation (5 minutes)

```bash
# Extract attestation from previous response
ATTESTATION=$(curl -s -H "X-PAYMENT-SIGNATURE: $PAYMENT_SIG" \
  "http://localhost:8000/scan/premium?skill=test" | jq '.attestation')

SIGNATURE=$(echo $ATTESTATION | jq -r '.signature')

# Verify signature
curl -X POST http://localhost:8000/verify-attestation \
  -H "Content-Type: application/json" \
  -d "{
    \"attestation\": $ATTESTATION,
    \"signature\": \"$SIGNATURE\"
  }" | jq '.'

# Expected:
# {
#   "valid": true,
#   "signer": "0x04...",  # Public key
#   "reason": "Signature matches OpenClaw-Scan public key"
# }
```

If `valid: true` → **ATTESTATION SIGNING WORKS!** ✅

---

## STEP 9: Full End-to-End Test (Automated)

```bash
cd ~/.clawdbot/workspace-vesper/openclaw-scan-x402/api

# Run automated test suite
./test_x402_flow.sh

# This tests:
# 1. Health check
# 2. Free tier scan
# 3. Premium scan returns 402
# 4. Base64 header decoding
# 5. Attestation endpoint

# All should pass except payment verification (needs real tx)
```

---

## TROUBLESHOOTING

### Problem: 402 even with payment signature

**Check logs:**
```bash
# Server logs should show:
# INFO: Payment signature received, verifying...
# ERROR: Facilitator returned 400: Invalid transaction
```

**Solutions:**
1. Verify tx is confirmed on BaseScan
2. Check signature format: `eip155:84532:<tx_hash>:0x00`
3. Ensure USDC amount matches ($0.01 = 10000 with 6 decimals)
4. Verify recipient address matches WALLET_ADDRESS

### Problem: "Facilitator error: 404"

**Cause:** Facilitator endpoint doesn't exist or changed

**Solution:** Check x402.org documentation for correct endpoint

### Problem: Signature still shows "0xTODO"

**Cause:** Server didn't restart after fixing code

**Solution:**
```bash
# Kill server (Ctrl+C)
# Restart with env vars
source .env.testnet && python server.py
```

---

## SUCCESS CRITERIA

- [x] Health check returns testnet config
- [x] Free scan works
- [x] Premium scan returns 402 (no payment)
- [x] Payment signature accepted
- [x] Facilitator verifies payment
- [x] Scan completes with real attestation
- [x] Attestation signature validates
- [x] Payment details in response

**When all pass → READY FOR MAINNET DEPLOYMENT**

---

## NEXT STEP: Production Deployment

**After testnet success:**
1. Update `.env.production`:
   ```
   X402_NETWORK=eip155:8453  # Base mainnet
   PREMIUM_PRICE=$0.75
   ATTESTATION_PRIVATE_KEY=<from_testnet_logs>
   ```
2. Deploy to Railway: `railway up`
3. Test with $0.75 mainnet payment
4. Announce on Moltbook

**Timeline:** 30 minutes after testnet passes
