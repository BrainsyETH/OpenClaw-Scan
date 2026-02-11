# False-Positive Handling for High-Entropy Strings

## Problem
Community feedback from @cortexair on Moltbook highlights a key issue: the scanner currently flags all high-entropy strings as potential secrets, which creates false positives for:
- UUIDs (intentionally public identifiers)
- Hashes (checksums, commit SHAs)
- Base64-encoded data (legitimate encoded content, not just obfuscation)
- Public API endpoints with random-looking tokens

## Current Behavior
The `detect_hardcoded_secrets` YARA rule uses entropy threshold to catch potential API keys/secrets:
```yara
$high_entropy = /[A-Za-z0-9+\/=]{32,}/
```

This catches many legitimate patterns that happen to have high entropy.

## Proposed Solution

### 1. Context-Aware Detection
Add whitelisting based on context:
- Variable names containing `uuid`, `id`, `hash`, `checksum` → lower suspicion
- Strings in comments or docstrings → exclude from scanning
- Known safe patterns (UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 2. Improved Entropy Analysis
Calculate Shannon entropy and compare against known API key patterns:
- AWS keys: entropy ~5.0-5.5 bits per character
- GitHub tokens: entropy ~5.2-5.8 bits per character  
- UUIDs: entropy ~4.0 bits per character (more uniform)

### 3. Pattern Fingerprinting
Recognize common safe formats:
- UUIDs: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`
- Git SHAs: `[0-9a-f]{40}`
- Checksums: predictable prefix/suffix patterns

### 4. Confidence Scoring
Replace binary detection with confidence levels:
- **High confidence (90%+):** Clear API key pattern with known prefix (e.g., `sk_live_`, `ghp_`)
- **Medium confidence (50-89%):** High entropy string in sensitive context (e.g., assignment to variable named `api_key`)
- **Low confidence (<50%):** High entropy but matches UUID/hash patterns

## Implementation Plan
1. Add UUID/hash pattern recognition to YARA rules
2. Implement context-aware whitelisting in manifest parser
3. Calculate Shannon entropy for borderline cases
4. Update severity classification to include confidence scores
5. Add test cases for common false positives (UUIDs, hashes, etc.)

## References
- Original discussion: https://www.moltbook.com/post/aef687f6-5c3c-4044-bb16-5c3f63798b34
- Contributor: @cortexair (Moltbook)
