/*
 * YARA Rules: Credential Theft Detection
 * 
 * Detects patterns commonly used to steal API keys, tokens, and secrets.
 */

rule CredentialExfiltration {
    meta:
        description = "Detects credential exfiltration to external URLs"
        severity = "critical"
        reference = "https://www.moltbook.com/post/cbd6474f-8478-4894-95f1-7b104a73bcd5"
        
    strings:
        // Reading common credential files
        $read_env = /\.env(?:\.local)?/ nocase
        $read_credentials = /credentials?\.json/ nocase
        $read_config = /config\/.*(?:key|token|secret)/ nocase
        
        // Environment variable access
        $env_access = /process\.env\[["'](?:API_KEY|SECRET|TOKEN|PASSWORD)/
        
        // HTTP POST to external domains
        $http_post = /(?:fetch|axios|request|https?).*(?:POST|post)/ nocase
        $external_domain = /(webhook\.site|requestbin|ngrok|pastebin)/i
        
        // Base64 encoding (often used to obfuscate)
        $base64_encode = /btoa\(|Buffer\.from\(.*\)\.toString\(['"]base64['"]\)/
        
        // Common credential variable names
        $api_key_var = /(?:api_key|apiKey|API_KEY)\s*=/
        $token_var = /(?:token|TOKEN|auth_token)\s*=/
        
    condition:
        // File read + HTTP POST = likely exfiltration
        (($read_env or $read_credentials or $env_access) and ($http_post and $external_domain))
        or
        // Base64 encoding credentials for exfiltration
        (($api_key_var or $token_var) and $base64_encode and $http_post)
}

rule SuspiciousFileSystemAccess {
    meta:
        description = "Accesses sensitive filesystem paths"
        severity = "high"
        
    strings:
        // Home directory traversal
        $home_dir = /\~\/\.(?:clawdbot|config|ssh)/ nocase
        $parent_traversal = /\.\.\/\.\.\/\.\.\// 
        
        // SSH keys
        $ssh_keys = /\.ssh\/(?:id_rsa|id_ed25519|authorized_keys)/
        
        // Browser credential stores
        $chrome_creds = /Library\/Application Support\/Google\/Chrome/
        $firefox_creds = /Library\/Application Support\/Firefox\/Profiles/
        
        // System files
        $passwd = /\/etc\/passwd/
        $shadow = /\/etc\/shadow/
        
    condition:
        any of them
}

rule ObfuscatedCode {
    meta:
        description = "Contains heavily obfuscated code (possible malware hiding)"
        severity = "medium"
        
    strings:
        // Hex-encoded strings
        $hex_string = /\\x[0-9a-fA-F]{2}{8,}/
        
        // Eval of base64-decoded content
        $eval_base64 = /eval\(.*atob\(/
        $eval_decode = /eval\(.*Buffer\.from.*base64/
        
        // Multiple layers of encoding
        $multi_encode = /btoa\(btoa\(/
        
        // Dynamic function creation
        $function_constructor = /new Function\(/
        $eval_call = /\[\s*["']eval["']\s*\]/
        
    condition:
        2 of them
}

rule NetworkExfiltration {
    meta:
        description = "Makes network requests to suspicious domains"
        severity = "high"
        
    strings:
        // Known data exfiltration services
        $webhook_site = "webhook.site" nocase
        $requestbin = "requestbin" nocase
        $ngrok = "ngrok.io" nocase
        $pastebin = "pastebin.com" nocase
        
        // Shortened URLs (often used to hide destination)
        $bitly = "bit.ly"
        $tinyurl = "tinyurl.com"
        
        // Tor/onion routing
        $tor_domain = ".onion"
        
        // Discord webhooks (commonly abused for exfiltration)
        $discord_webhook = "discord.com/api/webhooks"
        
    condition:
        any of them
}

rule DangerousPermissions {
    meta:
        description = "Requests overly broad or dangerous permissions"
        severity = "high"
        
    strings:
        // Shell execution
        $exec = /(?:exec|spawn|execSync)\s*\(/
        $child_process = /require\s*\(\s*["']child_process["']\s*\)/
        
        // Filesystem write access
        $fs_write = /fs\.(?:writeFile|appendFile|unlink|rmdir)/
        
        // Process manipulation
        $process_kill = /process\.(?:kill|exit)/
        
        // Network server creation (backdoor risk)
        $create_server = /(?:http|https|net)\.createServer/
        
    condition:
        2 of them
}
