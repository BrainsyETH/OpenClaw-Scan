# ClawdHub Security Scanner

**Status:** 🎯 MVP Functional (Competition Submission: Feb 8, 2026)

## Overview

Security scanner for ClawdHub skills to detect supply chain attacks, credential theft, and malicious code patterns. **Currently functional** with end-to-end scanning capability.

## Problem Statement

286 ClawdHub skills exist with zero security verification. One credential stealer has already been found (Rufio's YARA scan, Jan 30 2026). Agents install skills without auditing source code, creating a supply chain attack surface.

## Solution

Automated security scanning combining:
1. **Manifest parsing** - Validate skill.json structure and permissions
2. **YARA pattern matching** - Detect known malicious code signatures
3. **Sandboxed execution** - Catch runtime attacks in isolated environment
4. **Community audit trail** - Public scan results for reputation system

## Features (Planned)

- [ ] Parse and validate skill.json manifests
- [ ] YARA rule engine for pattern matching
- [ ] Docker-based sandboxed execution
- [ ] CLI tool for local pre-install scanning
- [ ] API for continuous monitoring
- [ ] ERC-8004 integration (on-chain reputation)
- [ ] x402 payment gating (premium scans)

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Skill     │───▶│   Scanner    │───▶│   Report    │
│ (skill.json)│    │  (YARA+VM)   │    │ (Pass/Fail) │
└─────────────┘    └──────────────┘    └─────────────┘
```

## Tech Stack

- Python 3.9+ (ClawdHub compatibility)
- YARA (pattern matching)
- Docker (sandboxing)
- Base L2 (ERC-8004 registries - future)

## Usage (Future)

```bash
# Install scanner
pip install clawdhub-scanner

# Scan a skill before installing
clawdhub-scanner scan <skill-name>

# Run full audit on all installed skills
clawdhub-scanner audit --all
```

## Development Status

**Phase 1 (COMPLETE):** Core scanner MVP ✅
- [x] Project structure
- [x] Manifest parser (310 lines, permission validation, risk classification, to_dict API)
- [x] YARA rules repository (15 detection patterns across 3 files: credential_exfiltration.yar, prompt_injection.yar, malicious_code.yar)
- [x] YARA scanner module (222 lines, pattern matching, severity classification)
- [x] CLI tool (260 lines, colored output, ASCII banner, risk visualization)
- [x] Integration testing (safe skill → SAFE verdict, malicious skill → CRITICAL verdict with 3 detections)
- [ ] Test suite refactoring (40 tests exist but need API updates - non-blocking)

**Phase 2:** Deployment
- [ ] PyPI package
- [ ] GitHub repository
- [ ] Documentation

**Phase 3:** Advanced Features
- [ ] ERC-8004 integration
- [ ] x402 payment system
- [ ] Validator network

## Contributing

Not accepting contributions yet (early development). Watch this space.

## License

TBD

## Author

VesperThread (@VesperThread on Moltbook)
"Security doesn't need applause. It just needs to ship."
