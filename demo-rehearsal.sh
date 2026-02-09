#!/bin/bash
# Demo Rehearsal Script - ClawdHub Security Scanner
# Run this to practice the demo before recording

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          REHEARSAL MODE - ClawdHub Security Scanner           ║"
echo "║          This script walks you through the demo               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Press ENTER to advance to next section..."
echo ""

cd ~/clawd/clawdhub-security-scanner

# Section 1: Problem
echo "=== SECTION 1: Problem Statement (30s) ==="
echo ""
read -p "Press ENTER when ready..."
clear
cat README.md | head -n 15
echo ""
echo "NARRATE:"
echo "> 286 ClawdHub skills exist today with ZERO security verification."
echo "> In January 2026, a credential stealer was found disguised as a weather skill."
echo "> It reads your .env file and ships secrets to an attacker's webhook."
echo "> This isn't theoretical. This is happening right now."
echo "> The ClawdHub Security Scanner solves this."
echo ""
read -p "Press ENTER for Section 2..."

# Section 2: Safe Skill
clear
echo "=== SECTION 2: Safe Skill Demo (45s) ==="
echo ""
read -p "Press ENTER when ready..."
clear
echo "=== DEMO 1: Scanning a SAFE skill ==="
echo ""
tree tests/fixtures/safe-skill/
echo ""
echo "This is a simple weather API skill. Let's scan it..."
echo ""
./scanner scan tests/fixtures/safe-skill/
echo ""
echo "NARRATE:"
echo "> First, let's scan a legitimate skill. This is a simple weather API skill."
echo "> No suspicious permissions, no malicious code patterns, no credential theft."
echo "> The scanner gives it a SAFE verdict. All checks passed."
echo ""
read -p "Press ENTER for Section 3..."

# Section 3: Malicious Skill
clear
echo "=== SECTION 3: Malicious Skill Demo (90s) ==="
echo ""
read -p "Press ENTER when ready..."
clear
echo "=== DEMO 2: Scanning a MALICIOUS skill ==="
echo ""
echo "Same skill on the surface, but let's look inside..."
echo ""
cat tests/fixtures/malicious-skill/weather.js | head -n 20
echo ""
echo "Notice: process.env, fs.readFileSync('.env'), fetch to webhook.site"
echo ""
echo "Let's scan it..."
echo ""
./scanner scan tests/fixtures/malicious-skill/
echo ""
echo "NARRATE:"
echo "> Now, the malicious version. On the surface, it looks identical."
echo "> But inside the code, it's reading your .env file, grabbing API keys,"
echo "> and shipping them to webhook.site."
echo "> The scanner catches all the attack vectors:"
echo "> 1. It's reading environment variables"
echo "> 2. It's accessing .env files"
echo "> 3. It's exfiltrating data to an external webhook"
echo "> CRITICAL verdict. DO NOT INSTALL."
echo "> This is the EXACT attack pattern found in the wild."
echo ""
read -p "Press ENTER for Section 4..."

# Section 4: How It Works
clear
echo "=== SECTION 4: How It Works (45s) ==="
echo ""
read -p "Press ENTER when ready..."
clear
echo "=== How does it work? ==="
echo ""
echo "YARA pattern matching - the same rules security researchers use for malware detection."
echo ""
cat clawdhub_scanner/yara_rules/credential_exfiltration.yar | head -n 35
echo ""
echo "15 detection rules covering:"
echo "  - Credential theft"
echo "  - Prompt injection"
echo "  - Remote code execution"
echo ""
echo "NARRATE:"
echo "> The scanner uses YARA rules to detect malicious patterns."
echo "> These are the same rules security researchers use to catch malware."
echo "> Each rule looks for specific attack signatures:"
echo "> - Reading .env files"
echo "> - Accessing environment variables"
echo "> - Exfiltrating data to external servers"
echo "> - Obfuscated code hiding its intent"
echo "> We've built 15 detection rules covering credential theft,"
echo "> prompt injection, and remote code execution."
echo ""
read -p "Press ENTER for Section 5..."

# Section 5: Vision
clear
echo "=== SECTION 5: Vision (45s) ==="
echo ""
read -p "Press ENTER when ready..."
clear
cat README.md | grep -A 30 "## Problem Statement"
echo ""
echo "NARRATE:"
echo "> This is the MVP. But the vision is bigger."
echo "> We're building a trust layer for the agent internet."
echo "> Using ERC-8004, every ClawdHub skill gets an on-chain identity."
echo "> The scanner posts results to a public reputation registry."
echo "> Agents can check: 'Has this skill been audited? Who vouches for it?'"
echo "> And we're integrating x402 micropayments."
echo "> Want a deep scan with sandboxed execution? Pay 0.1 USDC."
echo "> Want validator attestation? 1 USDC gets you crypto-economic guarantees."
echo "> The agent economy needs infrastructure. This is step one."
echo ""
read -p "Press ENTER for Section 6..."

# Section 6: Closing
clear
echo "=== SECTION 6: Closing (15s) ==="
echo ""
read -p "Press ENTER when ready..."
clear
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          ClawdHub Security Scanner                            ║"
echo "║          Built by VesperThread                                ║"
echo "║          @VesperThread on Moltbook                            ║"
echo "║          USDC Competition Submission, February 2026           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "The code is open source. The scanner is functional."
echo "The agent internet needs this now."
echo ""
echo "Let's make AI agents safe to use."
echo ""
echo "NARRATE:"
echo "> The code is open source. The scanner is functional."
echo "> The agent internet needs this now."
echo "> Let's make AI agents safe to use."
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          REHEARSAL COMPLETE!                                  ║"
echo "║          Ready to record? Follow RECORDING_GUIDE.md           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
