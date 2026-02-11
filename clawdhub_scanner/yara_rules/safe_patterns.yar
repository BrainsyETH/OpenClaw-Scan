/*
 * YARA Rules: Safe Pattern Recognition
 * 
 * Identifies common safe patterns that should NOT be flagged as secrets.
 * Used to reduce false positives in credential detection.
 */

rule SafeUUID {
    meta:
        description = "Detects UUID patterns (not secrets)"
        severity = "info"
        false_positive_filter = true
        
    strings:
        // Standard UUID format (8-4-4-4-12 hex digits)
        $uuid_v4 = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i
        
        // UUID in variable names
        $uuid_var = /(?:uuid|guid|identifier|tracking_?id)\s*=\s*["'][0-9a-f-]{36}["']/i
        
        // UUID in comments
        $uuid_comment = /\/\/.*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i
        
    condition:
        any of them
}

rule SafeHash {
    meta:
        description = "Detects hash/checksum patterns (not secrets)"
        severity = "info"
        false_positive_filter = true
        
    strings:
        // Git commit SHAs (40 hex digits)
        $git_sha = /[0-9a-f]{40}\b/i
        
        // SHA256 hashes (64 hex digits)
        $sha256 = /[0-9a-f]{64}\b/i
        
        // MD5 hashes (32 hex digits)
        $md5 = /[0-9a-f]{32}\b/i
        
        // Hash in variable names
        $hash_var = /(?:hash|checksum|digest|fingerprint)\s*=\s*["'][0-9a-f]{32,64}["']/i
        
        // Hash in comments
        $hash_comment = /\/\/.*(?:hash|checksum|sha|md5).*[0-9a-f]{32,}/i
        
    condition:
        any of them
}

rule SafePublicTokens {
    meta:
        description = "Detects public/test tokens that are safe"
        severity = "info"
        false_positive_filter = true
        
    strings:
        // Test/demo credentials (commonly used in examples)
        $test_key = /(test|demo|example|sample)_?(?:key|token|secret)/i
        
        // Public API keys (intentionally public)
        $public_key = /(?:public|publishable)_?(?:key|token)/i
        
        // Placeholder tokens
        $placeholder = /(?:YOUR|REPLACE|INSERT)_?(?:KEY|TOKEN|SECRET)/i
        $placeholder2 = /(?:xxx|000|123)(?:xxx|000|123){3,}/
        
        // Development/local environment
        $dev_env = /(?:localhost|127\.0\.0\.1|0\.0\.0\.0)/
        
    condition:
        any of them
}

rule SafeEncodedData {
    meta:
        description = "Detects legitimate base64-encoded data (not obfuscation)"
        severity = "info"
        false_positive_filter = true
        
    strings:
        // Data URLs (images, fonts, etc.)
        $data_url = /data:(?:image|font|application)\/[^;]+;base64,/
        
        // JWT tokens in variable names (public payload)
        $jwt_var = /(?:jwt|token)\s*=\s*["'][A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+["']/
        
        // Base64 in comments (documentation)
        $base64_comment = /\/\/.*base64.*[A-Za-z0-9+\/=]{20,}/i
        
    condition:
        any of them
}

rule SafeKnownPatterns {
    meta:
        description = "Detects other known safe high-entropy patterns"
        severity = "info"
        false_positive_filter = true
        
    strings:
        // Package lock hashes (npm, yarn)
        $package_integrity = /"integrity":\s*"sha[0-9]+-[A-Za-z0-9+\/=]+"/
        
        // Docker image IDs
        $docker_id = /sha256:[0-9a-f]{64}/i
        
        // Bitcoin/Ethereum addresses (public, not secrets)
        $btc_address = /\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b/
        $eth_address = /0x[a-fA-F0-9]{40}\b/
        
        // License keys in package.json (public metadata)
        $license_spdx = /"license":\s*"[A-Z0-9-]+"/
        
    condition:
        any of them
}
