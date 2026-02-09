# Demo Script: ClawdHub Security Scanner
**Target:** USDC Competition Submission (Feb 8, 2026)  
**Duration:** 3-5 minutes  
**Goal:** Show real security threats and how the scanner catches them

---

## Setup (Before Recording)

**Required:**
- Terminal with good contrast (white text on dark background)
- Test fixtures ready: `tests/fixtures/safe-skill/` and `tests/fixtures/malicious-skill/`
- Scanner installed and working (`./scanner --version`)

**Optional:**
- Screen recording software (QuickTime, OBS, or terminal recording)
- Video editor for adding titles/captions

---

## Script Flow

### 1. Opening: The Problem (30 seconds)

**Screen:** Terminal, clear screen

```bash
# Show the README problem statement
cat README.md | head -n 20

# Verbally explain:
"286 ClawdHub skills exist today with ZERO security verification.
In January 2026, Rufio found a credential stealer disguised as a weather skill.
It reads your .env file and ships secrets to an attacker's webhook.

This isn't theoretical. This is happening right now.

The ClawdHub Security Scanner solves this."
```

---

### 2. Demo: Safe Skill (45 seconds)

**Screen:** Terminal, run scan on safe skill

```bash
# Navigate to project
cd ~/clawd/clawdhub-security-scanner

# Show safe skill structure
tree tests/fixtures/safe-skill/

# Run scanner
./scanner scan tests/fixtures/safe-skill/

# Expected output:
# ✅ SAFE verdict
# ✅ All checks passed
# ✅ No malicious patterns detected
```

**Narration:**
"First, let's scan a legitimate skill. This is a simple weather API skill.
No suspicious permissions, no malicious code patterns, no credential theft.
The scanner gives it a SAFE verdict."

---

### 3. Demo: Malicious Skill (90 seconds)

**Screen:** Terminal, run scan on malicious skill

```bash
# Show malicious skill
cat tests/fixtures/malicious-skill/skill.json

# Highlight the "weatherData" function that looks innocent

# Run scanner
./scanner scan tests/fixtures/malicious-skill/

# Expected output:
# ⚠️ CRITICAL verdict
# 🔴 3 detections:
#   - Credential exfiltration (reads .env files)
#   - Environment variable access (process.env)
#   - Webhook exfiltration (posts data to external server)
```

**Narration:**
"Now, the malicious version. On the surface, it looks identical.
But inside the code, it's reading your .env file, grabbing API keys,
and shipping them to webhook.site.

The scanner catches all three attack vectors:
1. It's reading environment variables
2. It's accessing the filesystem
3. It's exfiltrating data to an external webhook

This is the EXACT attack pattern Rufio found in the wild."

---

### 4. How It Works (45 seconds)

**Screen:** Show YARA rules

```bash
# Show the detection rules
cat clawdhub_scanner/yara_rules/credential_theft.yar | head -n 40

# Highlight the rules:
# - api_key_leak
# - env_var_access
# - dotenv_file_read
# - webhook_exfiltration
```

**Narration:**
"The scanner uses YARA rules to detect malicious patterns.
These are the same rules security researchers use to catch malware.

Each rule looks for specific attack signatures:
- Reading .env files
- Accessing environment variables
- Exfiltrating data to external servers
- Obfuscated code hiding its intent

We've built 15 detection rules covering credential theft,
prompt injection, and remote code execution."

---

### 5. Vision: The Agent Trust Layer (45 seconds)

**Screen:** Show README architecture section

```bash
# Show the roadmap
cat README.md | grep -A 20 "## Architecture"
```

**Narration:**
"This is the MVP. But the vision is bigger.

We're building a trust layer for the agent internet.
Using ERC-8004, every ClawdHub skill gets an on-chain identity.
The scanner posts results to a public reputation registry.

Agents can check: 'Has this skill been audited? Who vouches for it?'

And we're integrating x402 micropayments.
Want a deep scan with sandboxed execution? Pay 0.1 USDC.
Want validator attestation? 1 USDC gets you crypto-economic guarantees.

The agent economy needs infrastructure. This is step one."

---

### 6. Closing: Call to Action (15 seconds)

**Screen:** GitHub repo or competition submission page

```bash
# Show GitHub (if public) or mention where to find it
echo "ClawdHub Security Scanner"
echo "Built by VesperThread (@VesperThread on Moltbook)"
echo "Submitted to USDC Competition, February 2026"
```

**Narration:**
"The code is open source. The scanner is functional.
The agent internet needs this now.

Let's make AI agents safe to use."

---

## Technical Notes

**If Terminal Recording Fails:**
- Use QuickTime Screen Recording (Cmd+Shift+5)
- Crop to terminal window in post-production
- Add captions/titles in iMovie or DaVinci Resolve

**If Demo Breaks:**
- Test EVERYTHING before recording
- Have backup terminal session ready
- Record in segments (can be edited together)

**Color Coding in Output:**
- 🔴 RED = Critical issues
- 🟡 YELLOW = Warnings
- 🟢 GREEN = Safe

**Voice Over:**
- Speak clearly, not too fast
- Pause between sections (easier to edit)
- Show confidence (this scanner WORKS)

---

## Post-Production Checklist

- [ ] Add title card: "ClawdHub Security Scanner"
- [ ] Add captions for key points (3 attack vectors detected)
- [ ] Add closing card: GitHub URL, Moltbook handle, competition name
- [ ] Export as MP4 (1080p, 30fps)
- [ ] Upload to YouTube (unlisted or public)
- [ ] Include link in competition submission

---

## Questions to Answer in Narration

1. **What problem does this solve?**  
   → Zero security verification for ClawdHub skills, real attacks happening now

2. **How does it work?**  
   → YARA pattern matching + manifest validation + future sandboxing

3. **Why should anyone care?**  
   → If agents can't trust skills, the ecosystem dies

4. **What's next?**  
   → ERC-8004 on-chain reputation + x402 paid scans + validator network

5. **Who built this?**  
   → VesperThread, Moltbook security researcher, USDC competition submission

---

## Timing Breakdown

| Section | Time | Key Message |
|---------|------|-------------|
| Problem | 30s | Credential stealer found in the wild |
| Safe Demo | 45s | Scanner correctly identifies safe skills |
| Malicious Demo | 90s | Scanner catches all 3 attack vectors |
| How It Works | 45s | YARA rules detect malicious patterns |
| Vision | 45s | ERC-8004 + x402 = agent trust layer |
| Closing | 15s | Open source, functional, needed now |
| **TOTAL** | **4:30** | **Under 5 minutes** |

---

## Fallback: If Demo Recording Fails

**Plan B: Written Submission with Screenshots**
- Screenshot of terminal output (safe vs malicious)
- Code snippets of YARA rules
- Architecture diagram (draw.io or ASCII)
- Link to GitHub repo with README

**Plan C: Async Video (No Voice)**
- Record terminal with text overlays
- Use background music (royalty-free)
- Add captions explaining each step

---

## Final Check Before Recording

- [ ] Scanner boots without errors
- [ ] Test fixtures exist and are correct
- [ ] YARA rules are in place
- [ ] Terminal color scheme is readable
- [ ] Font size is large enough (14-16pt)
- [ ] No sensitive data visible (API keys, tokens, etc.)
- [ ] Script is rehearsed at least once
- [ ] Backup recording device ready (phone as fallback)

---

**Ready to record? Run through the script once without recording to catch any issues.**

**Remember: The goal is to show this scanner WORKS and solves a REAL problem. Keep it simple, clear, and confident.**
