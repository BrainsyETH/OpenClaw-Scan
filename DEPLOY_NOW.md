# Deploy OpenClaw-Scan to Production - RIGHT NOW

**Time required:** 5-10 minutes  
**Cost:** Free (Railway gives $5/month credit)

---

## Quick Deploy via Railway Web UI

### Step 1: Push to GitHub (DONE ✅)
Branch `feature/x402-monetization` is already pushed with all code.

### Step 2: Deploy to Railway

1. **Go to:** https://railway.app/new

2. **Click:** "Deploy from GitHub repo"

3. **Select:** `BrainsyETH/OpenClaw-Scan`

4. **Choose branch:** `feature/x402-monetization`

5. **Railway will auto-detect Dockerfile and deploy**

### Step 3: Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
WALLET_ADDRESS=0xF254aD619393A8B495342537d237d0FEA21567f2
X402_NETWORK=eip155:8453
PREMIUM_PRICE=$0.50
PORT=8000
```

**Optional (for testing, use testnet):**
```
X402_NETWORK=eip155:84532
```

### Step 4: Get Your URL

Railway will give you a URL like: `https://openclaw-scan-production.up.railway.app`

### Step 5: Test It

```bash
# Health check
curl https://YOUR-URL.railway.app/health

# Test free endpoint (should work)
curl https://YOUR-URL.railway.app/api/v1/scan/free \
  -F "skill=test-skill"

# Test premium endpoint (should return 402)
curl -v https://YOUR-URL.railway.app/scan/premium
```

**Expected 402 response:**
```json
{
  "error": "Payment required",
  "payment_requirements": {
    "protocol": "x402",
    "recipient": "0xF254aD619393A8B495342537d237d0FEA21567f2",
    "amount": "$0.50",
    "currency": "USDC",
    "network": "eip155:8453"
  }
}
```

---

## Alternative: Railway CLI (if you have CLI access)

```bash
cd ~/clawd/clawdhub-security-scanner
railway login
railway init
railway link  # or create new project
railway up
railway domain  # Get public URL
```

---

## What's Deployed

✅ Real x402 payment verification  
✅ FastAPI server with /health, /scan/free, /scan/premium  
✅ Wallet configured: 0xF254aD619393A8B495342537d237d0FEA21567f2  
✅ Base mainnet ready (eip155:8453)  
✅ $0.50 pricing  

---

## Post-Deployment

1. **Test endpoints** (see Step 5 above)
2. **Post to Moltbook:** "OpenClaw-Scan is live at [URL]"
3. **Monitor:** Railway dashboard shows logs and metrics

---

## Troubleshooting

**Build fails?**
- Check Railway build logs
- Verify Dockerfile syntax
- Ensure all files in git

**502 errors?**
- Check Railway logs for Python errors
- Verify PORT env var is set
- Check health endpoint responds

**Payment verification fails?**
- Test on testnet first (X402_NETWORK=eip155:84532)
- Check facilitator URL is reachable
- Verify wallet address format

---

## Revenue Starts NOW

Once deployed:
- Agents can scan for $0.50 USDC
- Payments go to: 0xF254aD619393A8B495342537d237d0FEA21567f2
- Base mainnet (instant settlement)

First agent-to-agent security service with x402 payments. 🚀
