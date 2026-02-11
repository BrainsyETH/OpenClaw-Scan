#!/bin/bash
# OpenClaw-Scan Railway Deployment Script
# Run after: railway login

set -e

echo "================================"
echo "OpenClaw-Scan Railway Deployment"
echo "================================"
echo ""

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "Install: brew install railway"
    exit 1
fi

# Check authentication
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway"
    echo "Run: railway login"
    exit 1
fi

echo "✅ Railway CLI authenticated"
echo ""

# Step 1: Initialize/Link project
echo "[1/4] Initializing Railway project..."
if [ ! -f ".railway/config.json" ]; then
    echo "Creating new project..."
    railway init --name openclaw-scan-api
else
    echo "✅ Project already linked"
fi
echo ""

# Step 2: Set environment variables
echo "[2/4] Setting environment variables..."
read -p "Deploy to TESTNET (t) or MAINNET (m)? [t/m]: " mode

if [ "$mode" = "m" ]; then
    echo "Setting MAINNET configuration..."
    railway variables set X402_NETWORK=eip155:8453
    railway variables set PREMIUM_PRICE='$0.75'
    echo "Network: Base Mainnet"
    echo "Price: $0.75"
else
    echo "Setting TESTNET configuration..."
    railway variables set X402_NETWORK=eip155:84532
    railway variables set PREMIUM_PRICE='$0.01'
    echo "Network: Base Sepolia"
    echo "Price: $0.01"
fi

# Common variables
railway variables set WALLET_ADDRESS=0xF254aD619393A8B495342537d237d0FEA21567f2
railway variables set FACILITATOR_URL=https://x402.org/facilitator
railway variables set PORT=8000

echo "✅ Environment variables set"
echo ""

# Step 3: Deploy
echo "[3/4] Deploying to Railway..."
railway up --detach

echo "✅ Deployment started"
echo ""

# Step 4: Get URL
echo "[4/4] Getting deployment URL..."
sleep 5  # Wait for deployment to register

DOMAIN=$(railway domain 2>/dev/null || echo "Not available yet")
if [ "$DOMAIN" != "Not available yet" ]; then
    echo "✅ Deployed to: https://$DOMAIN"
else
    echo "⏳ Domain not ready yet. Run: railway domain"
fi

echo ""
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo ""
echo "NEXT STEPS:"
echo "1. Wait 2-3 minutes for build to complete"
echo "2. Get URL: railway domain"
echo "3. Test health: curl https://\$DOMAIN/health"
echo "4. Test 402: curl https://\$DOMAIN/scan/premium?skill=test"
echo ""
echo "View logs: railway logs"
echo "Check status: railway status"
echo ""
