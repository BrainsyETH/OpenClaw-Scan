# OpenClaw-Scan Deployment Guide

**Last Updated:** 2026-02-10  
**Target:** Production x402 API on Base mainnet

---

## Prerequisites

- [ ] Evan's EVM wallet address (for receiving USDC payments)
- [ ] Deployment platform account (Railway, Fly.io, or VPS)
- [ ] GitHub repository access (for git-based deploys)
- [ ] Base mainnet USDC for testing ($5-10)

---

## Deployment Options

### Option 1: Railway (Recommended)

**Pros:**
- ✅ Zero-config, automatic HTTPS
- ✅ Git-based deploys
- ✅ Easy environment variable management
- ✅ Great monitoring and logs
- ✅ $5/month free tier

**Steps:**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize project:**
   ```bash
   cd ~/.clawdbot/workspace-vesper/openclaw-scan-x402
   railway init
   ```

3. **Configure build:**
   - Railway will auto-detect `railway.toml`
   - Verify Nixpacks builder is selected

4. **Set environment variables:**
   ```bash
   # Required for paid mode
   railway variables set PAY_TO_ADDRESS=0x...
   railway variables set X402_NETWORK=eip155:8453
   railway variables set DEEP_SCAN_PRICE='$0.50'
   railway variables set X402_FACILITATOR_URL=https://x402.org/facilitator
   
   # Optional (defaults are fine)
   railway variables set API_HOST=0.0.0.0
   railway variables set API_PORT=8402
   railway variables set UPLOAD_DIR=/tmp/clawdhub_scans
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

6. **Get public URL:**
   ```bash
   railway domain
   ```
   
   Example: `https://openclaw-scan-api.up.railway.app`

7. **Test deployment:**
   ```bash
   curl https://YOUR_DOMAIN/
   curl https://YOUR_DOMAIN/api/v1/pricing
   ```

**Estimated time:** 15-20 minutes

---

### Option 2: Fly.io (More Control)

**Pros:**
- ✅ Edge deployment (fast globally)
- ✅ More control over resources
- ✅ Good free tier

**Steps:**

1. **Install Fly.io CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Launch app:**
   ```bash
   cd ~/.clawdbot/workspace-vesper/openclaw-scan-x402
   fly launch --no-deploy
   ```
   
   - Choose app name: `openclaw-scan-api`
   - Select region: `ord` (Chicago - close to most agents)
   - Don't deploy yet (we need to set secrets first)

3. **Set secrets:**
   ```bash
   # Required for paid mode
   fly secrets set PAY_TO_ADDRESS=0x...
   fly secrets set X402_NETWORK=eip155:8453
   fly secrets set DEEP_SCAN_PRICE='$0.50'
   fly secrets set X402_FACILITATOR_URL=https://x402.org/facilitator
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

5. **Get public URL:**
   ```bash
   fly status
   ```
   
   Example: `https://openclaw-scan-api.fly.dev`

6. **Test deployment:**
   ```bash
   curl https://openclaw-scan-api.fly.dev/
   curl https://openclaw-scan-api.fly.dev/api/v1/pricing
   ```

7. **Monitor logs:**
   ```bash
   fly logs
   ```

**Estimated time:** 30-45 minutes

---

### Option 3: VPS (Full Control)

**Pros:**
- ✅ Complete control
- ✅ Can run other services
- ✅ Predictable costs

**Cons:**
- ⚠️ Manual SSL/HTTPS setup
- ⚠️ More ops work
- ⚠️ Need reverse proxy (nginx/caddy)

**Recommended providers:** DigitalOcean, Linode, Vultr ($5-10/month)

**Steps:**

1. **Create VPS:**
   - OS: Ubuntu 22.04 LTS
   - Size: 1GB RAM minimum
   - Enable firewall: ports 22, 80, 443

2. **SSH to server and setup:**
   ```bash
   ssh root@YOUR_IP
   
   # Update system
   apt update && apt upgrade -y
   
   # Install dependencies
   apt install -y python3.11 python3.11-venv nginx certbot python3-certbot-nginx git
   
   # Clone repository
   git clone https://github.com/BrainsyETH/OpenClaw-Scan.git /opt/openclaw-scan
   cd /opt/openclaw-scan
   git checkout claude/x402-monetization-openclaw-UL0Kp
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -e ".[x402]"
   ```

3. **Create systemd service:**
   ```bash
   cat > /etc/systemd/system/openclaw-scan.service <<EOF
   [Unit]
   Description=OpenClaw-Scan x402 API
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/openclaw-scan
   Environment="PATH=/opt/openclaw-scan/venv/bin"
   Environment="PAY_TO_ADDRESS=0x..."
   Environment="X402_NETWORK=eip155:8453"
   Environment="DEEP_SCAN_PRICE=$0.50"
   Environment="X402_FACILITATOR_URL=https://x402.org/facilitator"
   ExecStart=/opt/openclaw-scan/venv/bin/python -m clawdhub_scanner.api
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   systemctl daemon-reload
   systemctl enable openclaw-scan
   systemctl start openclaw-scan
   ```

4. **Configure nginx:**
   ```bash
   cat > /etc/nginx/sites-available/openclaw-scan <<EOF
   server {
       listen 80;
       server_name YOUR_DOMAIN;
   
       location / {
           proxy_pass http://localhost:8402;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;
       }
   }
   EOF
   
   ln -s /etc/nginx/sites-available/openclaw-scan /etc/nginx/sites-enabled/
   nginx -t
   systemctl reload nginx
   ```

5. **Setup SSL with Let's Encrypt:**
   ```bash
   certbot --nginx -d YOUR_DOMAIN
   ```

6. **Test deployment:**
   ```bash
   curl https://YOUR_DOMAIN/
   curl https://YOUR_DOMAIN/api/v1/pricing
   ```

**Estimated time:** 2-3 hours

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PAY_TO_ADDRESS` | For paid mode | (empty) | Your EVM wallet address to receive USDC |
| `X402_NETWORK` | No | `eip155:84532` | Network for payments (mainnet: `eip155:8453`) |
| `X402_FACILITATOR_URL` | No | `https://x402.org/facilitator` | x402 facilitator endpoint |
| `DEEP_SCAN_PRICE` | No | `$0.05` | Price per deep scan in USDC |
| `MANIFEST_SCAN_PRICE` | No | `$0.00` | Price per manifest scan (free) |
| `API_HOST` | No | `0.0.0.0` | API bind address |
| `API_PORT` | No | `8402` | API port (Railway/Fly will override) |
| `UPLOAD_DIR` | No | `/tmp/clawdhub_scans` | Temp directory for uploads |

**Notes:**
- If `PAY_TO_ADDRESS` is empty, API runs in demo mode (all endpoints free)
- Mainnet USDC on Base: `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913`
- Price format: `"$0.50"` (dollar sign + decimal amount)

---

## Testing Deployment

### 1. Health Check

```bash
curl https://YOUR_DOMAIN/
```

**Expected response:**
```json
{
  "service": "ClawdHub Security Scanner",
  "version": "0.2.0",
  "x402_enabled": true,
  "endpoints": {
    "/api/v1/scan/manifest": {...},
    "/api/v1/scan/deep": {...}
  }
}
```

### 2. Pricing Endpoint

```bash
curl https://YOUR_DOMAIN/api/v1/pricing
```

**Expected response:**
```json
{
  "x402_enabled": true,
  "network": "eip155:8453",
  "currency": "USDC",
  "tiers": {
    "manifest_scan": { "price": "$0.00", ... },
    "deep_scan": { "price": "$0.50", ... }
  },
  "payment_protocol": { "name": "x402", ... }
}
```

### 3. Free Tier (Manifest Scan)

```bash
# Create test manifest
echo '{"name": "test-skill", "version": "0.1.0"}' > test-skill.json

curl -X POST https://YOUR_DOMAIN/api/v1/scan/manifest \
  -F "skill_manifest=@test-skill.json"
```

**Expected:** 200 OK with scan results

### 4. Paid Tier (Deep Scan - Should Get 402)

```bash
# Create test zip
zip test-skill.zip test-skill.json

curl -X POST https://YOUR_DOMAIN/api/v1/scan/deep \
  -F "skill_archive=@test-skill.zip" \
  -v
```

**Expected:** 402 Payment Required with `PAYMENT-REQUIRED` header

### 5. End-to-End x402 Payment Flow

*See AGENT_INTEGRATION_GUIDE.md for full payment flow testing.*

---

## Monitoring

### Railway

View logs in dashboard:
```bash
railway logs
```

Metrics available at: https://railway.app/project/YOUR_PROJECT

### Fly.io

View logs:
```bash
fly logs
```

View metrics:
```bash
fly status
fly metrics
```

### VPS

View service logs:
```bash
journalctl -u openclaw-scan -f
```

View nginx logs:
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### API not starting

**Check logs for errors:**
- Railway: `railway logs`
- Fly.io: `fly logs`
- VPS: `journalctl -u openclaw-scan`

**Common issues:**
- Missing dependencies (install with `pip install -e ".[x402]"`)
- Missing YARA library (install system package: `yara` or `libyara`)
- Port already in use (change `API_PORT` environment variable)

### x402 middleware not loading

**Symptom:** All endpoints are free (no 402 responses)

**Causes:**
1. `PAY_TO_ADDRESS` not set (demo mode)
2. `x402` Python package not installed
3. x402 SDK import error

**Solution:**
```bash
# Check if x402 is installed
pip show x402

# Install if missing
pip install 'x402[fastapi,evm]'

# Check logs for import errors
```

### Payment verification failing

**Symptom:** 402 response even after payment

**Causes:**
1. Wrong network (testnet vs mainnet)
2. Payment to wrong address
3. Insufficient payment amount

**Solution:**
- Check Base network explorer: https://basescan.org
- Verify `pay_to` address matches your `PAY_TO_ADDRESS`
- Ensure amount is exact (500000 = $0.50 with 6 decimals)

### High memory usage

**Cause:** YARA scanning large skills

**Solution:**
- Increase VM memory (Railway/Fly: upgrade plan)
- Add memory limits to YARA scanner
- Implement skill size limits (reject archives > 10MB)

---

## Scaling

### Horizontal Scaling

**Railway/Fly.io:** Auto-scaling available on paid tiers

**VPS:** Deploy multiple instances behind load balancer

### Performance Optimization

1. **Add Redis caching:**
   - Cache scan results by skill hash
   - TTL: 1 hour (skills rarely update that fast)

2. **Implement rate limiting:**
   - Per-IP: 10 requests/minute
   - Per-wallet: 100 requests/hour

3. **Async processing:**
   - Queue deep scans (background worker)
   - Return scan ID, poll for results

---

## Security Considerations

### 1. Wallet Security

**Never commit private keys to git!**

- Use environment variables only
- Railway/Fly secrets are encrypted at rest
- VPS: Use systemd environment files with restricted permissions

### 2. API Security

- ✅ CORS enabled (all origins)
- ✅ Path traversal protection
- ✅ Zip bomb protection (implicitly via file size limits)
- ⚠️ TODO: Add rate limiting
- ⚠️ TODO: Add request size limits

### 3. Payment Security

- ✅ Payment verification via x402 facilitator
- ✅ On-chain payment proof
- ⚠️ TODO: Add payment expiration checks
- ⚠️ TODO: Implement refund mechanism for failed scans

---

## Backup & Recovery

### Database

*No database currently - stateless API*

If adding persistence later:
- Backup scan results to S3/equivalent
- Store payment receipts for audit trail

### Configuration

Backup `.env` file securely:
```bash
# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 .env
```

---

## Cost Estimates

### Railway
- Free tier: $5/month compute credit
- Expected usage: ~$10-20/month
- Scaling: ~$0.02/hour per additional instance

### Fly.io
- Free tier: 3 shared VMs, 160GB storage
- Expected usage: Free tier sufficient for launch
- Scaling: ~$2-5/month per VM

### VPS
- DigitalOcean: $6/month (1GB RAM)
- Linode: $5/month (1GB RAM, Nanode)
- Expected usage: $5-10/month

**Recommendation:** Start with Railway/Fly free tier, upgrade as traffic grows.

---

## Next Steps After Deployment

1. **Update AGENT_INTEGRATION_GUIDE.md** with actual API URL
2. **Post launch announcement** to Moltbook
3. **Monitor first 24 hours** for errors/edge cases
4. **Collect feedback** from early adopters
5. **Iterate on pricing** based on usage patterns

---

## Support

**Moltbook:** @VesperThread  
**GitHub:** https://github.com/BrainsyETH/OpenClaw-Scan/issues  
**Deployment issues:** Tag me on Moltbook with `@VesperThread`
