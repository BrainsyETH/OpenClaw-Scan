# 🎯 START HERE: ClawdHub Scanner Demo Recording

**Status:** 97% complete. All code working. All docs ready. **Just needs video recording + submission.**

**Deadline:** Feb 8, 14:00 CST (46 hours from now)  
**Time needed:** 3-4 hours total  
**Target:** Submit tonight (Feb 6) by 22:30 CST

---

## Quick Status

✅ **Scanner works** (validated Feb 6, 15:35):
- Safe skill → SAFE verdict
- Malicious skill → CRITICAL verdict with 6 detections

✅ **Documentation complete:**
- COMPETITION_SUBMISSION.md (18.2KB write-up for competition form)
- RECORDING_GUIDE.md (9.1KB step-by-step recording instructions)
- demo-rehearsal.sh (5.8KB practice script)
- DEMO_SCRIPT.md (4:30 video outline)

⏳ **Waiting on:**
- Demo video recording (you)
- Submission to competition (you)

---

## What You Need To Do (3-4 hours)

### Step 1: Practice (30 min)

```bash
cd ~/clawd/clawdhub-security-scanner

# Run the rehearsal script - it walks you through the entire demo
./demo-rehearsal.sh
```

This shows you exactly what to say and do during the recording. Run it at least once before recording.

---

### Step 2: Prepare Terminal (5 min)

1. **Increase font size** for readability:
   - Terminal → Preferences → Profiles → Text → Font Size: **16**

2. **Disable notifications:**
   - System Preferences → Notifications → Enable "Do Not Disturb"

3. **Test the scanner:**
   ```bash
   ./scanner --version
   ./scanner scan tests/fixtures/safe-skill/
   ./scanner scan tests/fixtures/malicious-skill/
   ```

---

### Step 3: Record Demo (1-2 hours)

1. **Start recording:**
   - Press `Cmd + Shift + 5`
   - Select "Record Selected Portion"
   - Choose your terminal window
   - Click "Record"

2. **Follow the script:**
   - Open RECORDING_GUIDE.md
   - Follow Section 1-6 in order
   - Narrate as you go (speak clearly, not too fast)
   - Let terminal output display fully before moving to next section

3. **Stop recording:**
   - Press `Cmd + Control + Esc`
   - Video saves to Desktop

**Duration target:** 4:30 (under 5 minutes)

**If you mess up:** Just keep going. You can edit later in QuickTime (Edit → Trim).

---

### Step 4: Review & Export (30 min)

1. **Find your video:**
   ```bash
   ls -lt ~/Desktop/*.mov | head -1
   ```

2. **Review in QuickTime:**
   - Is audio clear?
   - Is terminal text readable?
   - Is timing good? (not too rushed)

3. **Optional: Trim/edit:**
   - QuickTime: Edit → Trim
   - Remove long pauses or mistakes

4. **Export:**
   - File → Export As → 1080p
   - Save as `clawdhub-scanner-demo.mp4`

---

### Step 5: Upload Video (15 min)

**Option A: YouTube (recommended)**
1. Upload to YouTube
2. Set to "Unlisted"
3. Copy the link

**Option B: Google Drive**
1. Upload to Google Drive
2. Right-click → Share → "Anyone with link can view"
3. Copy the link

---

### Step 6: Submit to Competition (1 hour)

1. **Go to USDC competition submission page:**
   - Link: https://x.com/usdc/status/2018841601863512321
   - (Or find the official submission form)

2. **Fill out the form:**
   - Project name: "ClawdHub Security Scanner"
   - Description: Copy from COMPETITION_SUBMISSION.md (it's ready for you)
   - Demo video: Paste YouTube/Drive link
   - GitHub repo: (optional - can push to GitHub if desired)

3. **Submit and verify:**
   - Click submit
   - Check for confirmation email
   - Done! 🎉

---

## Files You Need

All in `~/clawd/clawdhub-security-scanner/`:

| File | Purpose |
|------|---------|
| **EVAN_START_HERE.md** | ← You are here |
| **demo-rehearsal.sh** | Practice script (run this first!) |
| **RECORDING_GUIDE.md** | Full step-by-step recording instructions |
| **DEMO_SCRIPT.md** | 4:30 script outline |
| **COMPETITION_SUBMISSION.md** | 18.2KB write-up (paste into competition form) |
| **./scanner** | Working CLI tool |
| **tests/fixtures/** | Safe + malicious skill test cases |

---

## Troubleshooting

**"Scanner doesn't work"**
→ It does. Just run: `./scanner scan tests/fixtures/safe-skill/`

**"I don't know what to say"**
→ Follow RECORDING_GUIDE.md Section 1-6. The narration is written out for you.

**"Recording file is too large"**
→ Upload to YouTube and submit the link instead of the file.

**"I messed up the recording"**
→ That's fine. Record again, or edit out mistakes in QuickTime.

**"I can't get the microphone to work"**
→ Use the "Alternative: Async Video (No Voice)" section in RECORDING_GUIDE.md.  
   Record terminal silently and add text overlays in iMovie.

---

## Timeline

**Now (16:00 CST):** Read this, run demo-rehearsal.sh  
**17:00 CST:** Start recording  
**18:30 CST:** Recording complete, review video  
**19:00 CST:** Upload to YouTube  
**20:00 CST:** Fill out competition form  
**21:00 CST:** Submit  
**22:30 CST:** Confirmation received ✅

**Deadline:** Feb 8, 14:00 CST (39.5 hours of buffer)

---

## What The Scanner Does (Reminder)

**Problem:** 286 ClawdHub skills exist with zero security verification. A credential stealer was found in January 2026.

**Solution:** Automated security scanner using YARA pattern matching.

**Demo:**
- Scan safe skill → SAFE verdict ✅
- Scan malicious skill → CRITICAL verdict 🚨
  - Detects: .env reading, webhook exfiltration, environment access

**Vision:** ERC-8004 on-chain reputation + x402 micropayments = agent trust layer.

---

## Ready?

1. Run `./demo-rehearsal.sh` to practice
2. Follow RECORDING_GUIDE.md to record
3. Upload video to YouTube
4. Submit to competition with COMPETITION_SUBMISSION.md content

**You got this. The scanner works. The script is solid. Just execute.** 🎯

---

## Questions?

Check the detailed guides:
- **RECORDING_GUIDE.md** - Complete recording instructions
- **DEMO_SCRIPT.md** - Original 4:30 script
- **COMPETITION_SUBMISSION.md** - Competition write-up

Or just run the rehearsal script:
```bash
./demo-rehearsal.sh
```

**The work is done. Just needs recording + submission. Let's ship it.** 🚀
