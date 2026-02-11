#!/bin/bash
# Quick Test Script - Run Server + Basic Tests
# Usage: ./quick_test.sh

set -e

echo "================================"
echo "OpenClaw-Scan Quick Test"
echo "================================"
echo ""

# Check if in api/ directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: Must run from api/ directory"
    echo "Run: cd api && ./quick_test.sh"
    exit 1
fi

# Step 1: Create testnet config
echo "[1/6] Creating testnet config..."
cat > .env.testnet << 'EOF'
X402_NETWORK=eip155:84532
WALLET_ADDRESS=0xF254aD619393A8B495342537d237d0FEA21567f2
PREMIUM_PRICE=$0.01
FACILITATOR_URL=https://x402.org/facilitator
PORT=8000
EOF
echo "✓ Config created"
echo ""

# Step 2: Check/create venv
echo "[2/6] Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 3: Install dependencies
echo "[3/6] Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 4: Start server in background
echo "[4/6] Starting server..."
export $(cat .env.testnet | xargs)
python server.py > /tmp/openclaw-server.log 2>&1 &
SERVER_PID=$!
echo "✓ Server started (PID: $SERVER_PID)"
echo "✓ Logs: tail -f /tmp/openclaw-server.log"
echo ""

# Wait for server to start
echo "Waiting for server to be ready..."
sleep 5

# Step 5: Run tests
echo "[5/6] Running tests..."
echo ""

# Test 1: Health
echo "Test 1: Health Check"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "ok"; then
    echo "✓ PASS - Server is healthy"
    echo "$HEALTH" | jq '.' | head -5
else
    echo "✗ FAIL - Health check failed"
    echo "$HEALTH"
fi
echo ""

# Test 2: Free scan
echo "Test 2: Free Tier Scan"
FREE=$(curl -s "http://localhost:8000/scan/free?skill=test")
if echo "$FREE" | grep -q "scan_id"; then
    echo "✓ PASS - Free scan works"
    echo "$FREE" | jq '.scan_id, .verdict, .tier' | head -3
else
    echo "✗ FAIL - Free scan failed"
    echo "$FREE"
fi
echo ""

# Test 3: Premium 402
echo "Test 3: Premium Scan (Expect 402)"
HTTP_CODE=$(curl -s -o /tmp/premium.json -w "%{http_code}" "http://localhost:8000/scan/premium?skill=test")
if [ "$HTTP_CODE" = "402" ]; then
    echo "✓ PASS - Got 402 Payment Required"
    cat /tmp/premium.json | jq '.wallet, .price, .network'
else
    echo "✗ FAIL - Expected 402, got $HTTP_CODE"
    cat /tmp/premium.json
fi
echo ""

# Test 4: Payment header
echo "Test 4: PAYMENT-REQUIRED Header"
HEADER=$(curl -s -D - http://localhost:8000/scan/premium?skill=test 2>&1 | grep -i "payment-required" | cut -d: -f2- | tr -d '\r\n ')
if [ -n "$HEADER" ]; then
    echo "✓ PASS - Header present (Base64)"
    echo "Raw: ${HEADER:0:50}..."
    echo ""
    echo "Decoded:"
    echo "$HEADER" | base64 -d 2>/dev/null | jq '.' || echo "(Invalid Base64)"
else
    echo "✗ FAIL - No PAYMENT-REQUIRED header"
fi
echo ""

# Test 5: Attestation endpoint
echo "Test 5: Attestation Verification Endpoint"
VERIFY=$(curl -s -X POST http://localhost:8000/verify-attestation \
    -H "Content-Type: application/json" \
    -d '{"attestation": {"version": "1.0", "scan_id": "test"}, "signature": "0x00"}')
if echo "$VERIFY" | grep -q "valid"; then
    echo "✓ PASS - Verification endpoint works"
    echo "$VERIFY" | jq '.valid, .reason' | head -2
else
    echo "✗ FAIL - Verification failed"
    echo "$VERIFY"
fi
echo ""

# Step 6: Summary
echo "================================"
echo "Test Summary"
echo "================================"
echo ""
echo "Server PID: $SERVER_PID"
echo "Logs: tail -f /tmp/openclaw-server.log"
echo ""
echo "NEXT STEPS:"
echo "1. All tests passed → Fund wallet with Base Sepolia USDC"
echo "2. Make payment → Get tx_hash"
echo "3. Test with payment signature:"
echo "   curl -H 'X-PAYMENT-SIGNATURE: eip155:84532:<TX_HASH>:0x00' \\"
echo "     http://localhost:8000/scan/premium?skill=test"
echo ""
echo "To stop server:"
echo "  kill $SERVER_PID"
echo ""
echo "To view attestation key (for production):"
echo "  grep 'ATTESTATION_PRIVATE_KEY' /tmp/openclaw-server.log"
echo ""
