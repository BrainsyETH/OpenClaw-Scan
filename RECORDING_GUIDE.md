# Recording Guide: ClawdHub Security Scanner Demo
**Created:** Feb 6, 2026, 15:40 CST  
**For:** USDC Competition Submission (Deadline: Feb 8, 14:00 CST)

---

## Quick Start

**EASIEST METHOD: macOS Screen Recording**
1. Press `Cmd + Shift + 5` to open screen recording controls
2. Select "Record Selected Portion" and choose your terminal window
3. Click "Record" and follow the script below
4. Press `Cmd + Control + Esc` to stop recording
5. Video saves to Desktop as "Screen Recording YYYY-MM-DD at HH.MM.SS.mov"

---

## Pre-Recording Checklist

- [ ] Terminal font size 14-16pt (readable on video)
- [ ] Terminal color scheme: white text on dark background (high contrast)
- [ ] Close all other windows (minimize distractions)
- [ ] Disable notifications (System Preferences → Notifications)
- [ ] Clear terminal history: `clear`
- [ ] Rehearse script at least once without recording
- [ ] Have water nearby (stay hydrated during narration)

---

## Full Script (4:30 duration)

### SECTION 1: Problem Statement (30 seconds)

**ACTION:**
```bash
cd ~/clawd/clawdhub-security-scanner
clear
cat README.md | head -n 15
```

**NARRATE:**
> "286 ClawdHub skills exist today with ZERO security verification.
> In January 2026, a credential stealer was found disguised as a weather skill.
> It reads your .env file and ships secrets to an attacker's webhook.
> 
> This isn't theoretical. This is happening right now.
> 
> The ClawdHub Security Scanner solves this."

**PAUSE:** 2 seconds

---

### SECTION 2: Safe Skill Demo (45 seconds)

**ACTION:**
```bash
clear
echo "=== DEMO 1: Scanning a SAFE skill ==="
echo ""
tree tests/fixtures/safe-skill/
echo ""
echo "This is a simple weather API skill. Let's scan it..."
echo ""
./scanner scan tests/fixtures/safe-skill/
```

**NARRATE:**
> "First, let's scan a legitimate skill. This is a simple weather API skill.
> No suspicious permissions, no malicious code patterns, no credential theft.
> 
> [Wait for scanner output]
> 
> The scanner gives it a SAFE verdict. All checks passed."

**PAUSE:** 2 seconds

---

### SECTION 3: Malicious Skill Demo (90 seconds)

**ACTION:**
```bash
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
```

**NARRATE:**
> "Now, the malicious version. On the surface, it looks identical.
> But inside the code, it's reading your .env file, grabbing API keys,
> and shipping them to webhook.site.
> 
> [Wait for scanner output]
> 
> The scanner catches all the attack vectors:
> 1. It's reading environment variables
> 2. It's accessing .env files
> 3. It's exfiltrating data to an external webhook
> 
> CRITICAL verdict. DO NOT INSTALL.
> 
> This is the EXACT attack pattern found in the wild."

**PAUSE:** 3 seconds

---

### SECTION 4: How It Works (45 seconds)

**ACTION:**
```bash
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
```

**NARRATE:**
> "The scanner uses YARA rules to detect malicious patterns.
> These are the same rules security researchers use to catch malware.
> 
> Each rule looks for specific attack signatures:
> - Reading .env files
> - Accessing environment variables
> - Exfiltrating data to external servers
> - Obfuscated code hiding its intent
> 
> We've built 15 detection rules covering credential theft,
> prompt injection, and remote code execution."

**PAUSE:** 2 seconds

---

### SECTION 5: Vision (45 seconds)

**ACTION:**
```bash
clear
cat README.md | grep -A 30 "## Problem Statement"
```

**NARRATE:**
> "This is the MVP. But the vision is bigger.
> 
> We're building a trust layer for the agent internet.
> Using ERC-8004, every ClawdHub skill gets an on-chain identity.
> The scanner posts results to a public reputation registry.
> 
> Agents can check: 'Has this skill been audited? Who vouches for it?'
> 
> And we're integrating x402 micropayments.
> Want a deep scan with sandboxed execution? Pay 0.1 USDC.
> Want validator attestation? 1 USDC gets you crypto-economic guarantees.
> 
> The agent economy needs infrastructure. This is step one."

**PAUSE:** 2 seconds

---

### SECTION 6: Closing (15 seconds)

**ACTION:**
```bash
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
```

**NARRATE:**
> "The code is open source. The scanner is functional.
> The agent internet needs this now.
> 
> Let's make AI agents safe to use."

**END RECORDING**

---

## Post-Recording Steps

1. **Find your recording:**
   - Check Desktop: `ls -lt ~/Desktop/*.mov | head -1`
   - Or in Downloads: `ls -lt ~/Downloads/*.mov | head -1`

2. **Review the video:**
   - Open in QuickTime Player
   - Check audio levels (narration clear?)
   - Check video quality (terminal readable?)

3. **Optional: Trim/Edit:**
   - QuickTime: Edit → Trim
   - Remove long pauses or mistakes
   - Keep under 5 minutes total

4. **Export:**
   - File → Export As → 1080p
   - Save as `clawdhub-scanner-demo.mov`

5. **Upload options:**
   - **YouTube (unlisted):** Upload and get shareable link
   - **Google Drive:** Upload and set sharing to "Anyone with link"
   - **Direct submission:** Include .mov file if competition allows

---

## Rehearsal Tips

**Before your first take:**
1. Run through the script WITHOUT recording
2. Practice narration timing (don't rush!)
3. Make sure all commands work as expected
4. Check that terminal output is readable

**Common mistakes:**
- ❌ Speaking too fast (viewers need time to read terminal output)
- ❌ Not pausing after scanner output (let them see the results)
- ❌ Terminal font too small (viewer can't read code)
- ❌ Forgetting to narrate (silence is awkward)

**Pro tips:**
- ✅ Pause 2-3 seconds between sections
- ✅ Speak clearly and confidently
- ✅ Let scanner output display fully before moving on
- ✅ If you make a mistake, just keep going (can edit later)

---

## Alternative: Async Video (No Voice)

If voice recording is difficult, create a **silent video with text overlays**:

1. Record terminal commands (no narration)
2. Use iMovie or DaVinci Resolve to add text overlays
3. Add royalty-free background music (YouTube Audio Library)
4. Export as MP4

**Text overlay template:**
- Section 1: "286 ClawdHub skills. Zero security. One credential stealer already found."
- Section 2: "Scanning a SAFE skill → All checks passed ✅"
- Section 3: "Scanning a MALICIOUS skill → CRITICAL: Credential theft detected 🚨"
- Section 4: "15 YARA rules detect attacks: .env reading, webhook exfiltration, prompt injection"
- Section 5: "Vision: ERC-8004 on-chain reputation + x402 micropayments = agent trust layer"
- Section 6: "Open source. Functional. Needed now. @VesperThread"

---

## Troubleshooting

**Problem:** Terminal text too small in recording  
**Solution:** Increase terminal font size to 16pt before recording

**Problem:** Scanner output too fast to read  
**Solution:** Add `sleep 3` after each scanner command

**Problem:** Narration sounds rushed  
**Solution:** Rehearse 2-3 times, focus on pausing between sections

**Problem:** Recording file too large (>100MB)  
**Solution:** Compress with HandBrake or upload to YouTube and submit link

**Problem:** Can't get microphone to work  
**Solution:** Use silent video + text overlays (see Alternative above)

---

## Time Check

**Target:** 4:30 total  
**Sections:**
- Problem: 30s
- Safe demo: 45s
- Malicious demo: 90s
- How it works: 45s
- Vision: 45s
- Closing: 15s

**Total:** 4:30 ✅

**Rehearsal run:** Add 30-60 seconds for natural pauses = ~5:30  
**Edited final:** Trim to 4:30-5:00 ✅

---

## Ready to Record?

**Pre-flight checklist:**
- [ ] Terminal font 14-16pt
- [ ] Dark background, white text
- [ ] Notifications disabled
- [ ] Scanner working (`./scanner --version`)
- [ ] Test fixtures present
- [ ] Script rehearsed at least once
- [ ] Water nearby
- [ ] Ready to narrate confidently

**When ready:**
1. Press `Cmd + Shift + 5`
2. Select terminal window
3. Click Record
4. Follow the script above
5. Press `Cmd + Control + Esc` to stop

**YOU GOT THIS. The scanner works. The script is solid. Just execute.** 🎯
