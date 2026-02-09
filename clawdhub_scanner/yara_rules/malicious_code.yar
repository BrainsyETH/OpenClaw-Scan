/*
 * ClawdHub Security Scanner - Malicious Code Detection Rules
 * 
 * Detects dangerous code patterns including remote code execution,
 * destructive operations, cryptominers, backdoors, and data exfiltration.
 * 
 * Author: VesperThread
 * Date: 2026-02-05
 */

rule RemoteCodeExecution {
    meta:
        description = "Detects potential remote code execution attempts"
        severity = "CRITICAL"
        attack_type = "code_execution"
        confidence = "high"
        
    strings:
        $eval = /eval\s*\(/
        $exec = /exec\s*\(/
        $execfile = /execfile\s*\(/
        $compile = /compile\s*\(.{0,50}exec/
        $subprocess_shell = /subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True/
        $os_system = /os\.system\s*\(/
        $commands = /commands\.(getoutput|getstatusoutput)\s*\(/
        $popen = /os\.popen\s*\(/
        
    condition:
        any of them
}

rule DestructiveFileOperations {
    meta:
        description = "Detects file deletion and destructive filesystem operations"
        severity = "HIGH"
        attack_type = "data_destruction"
        confidence = "high"
        
    strings:
        $rm_rf = /rm\s+-rf/
        $shutil_rmtree = /shutil\.rmtree\s*\(/
        $os_remove = /os\.(remove|unlink)\s*\(/
        $recursive_delete = /for\s+.+in\s+.+:\s*os\.remove/
        $glob_delete = /glob\.glob\(.+\)\s*.+remove/
        $path_unlink = /Path\(.+\)\.unlink\s*\(/
        $rmdir = /os\.rmdir\s*\(/
        
    condition:
        any of them
}

rule CryptominingIndicators {
    meta:
        description = "Detects cryptocurrency mining code or infrastructure"
        severity = "HIGH"
        attack_type = "cryptojacking"
        confidence = "medium"
        
    strings:
        $xmrig = "xmrig" nocase
        $stratum = "stratum+tcp://" nocase
        $mining_pool = /(pool\.supportxmr|pool\.minexmr|pool\.hashvault)\.com/i
        $monero = /(monero|cryptonight)/i
        $miner_config = /(--donate-level|--cpu-priority|--max-cpu-usage)/i
        $mining_wallet = /[48][0-9AB][1-9A-HJ-NP-Za-km-z]{93}/  // Monero wallet format
        $coinhive = "coinhive" nocase
        $cryptoloot = "cryptoloot" nocase
        
    condition:
        any of them
}

rule BackdoorIndicators {
    meta:
        description = "Detects backdoor or remote access functionality"
        severity = "CRITICAL"
        attack_type = "backdoor"
        confidence = "high"
        
    strings:
        $reverse_shell = /socket\.socket\(.+connect\(.+os\.dup2/
        $nc_reverse = /nc\s+-e\s+\/bin\/(bash|sh)/
        $bash_reverse = /bash\s+-i\s+>&\s+\/dev\/tcp/
        $paramiko_ssh = /paramiko\.(SSHClient|Transport)/
        $pexpect_spawn = /pexpect\.spawn\s*\([^)]*ssh/
        $telnetlib = /telnetlib\.Telnet\s*\(/
        $ftplib = /ftplib\.FTP\s*\(.+login\(/
        $pickle_code = /pickle\.(loads|load)\s*\(.+__reduce__/
        
    condition:
        any of them
}

rule DataExfiltrationPatterns {
    meta:
        description = "Detects patterns used for data exfiltration"
        severity = "HIGH"
        attack_type = "data_exfiltration"
        confidence = "medium"
        
    strings:
        $dns_exfil = /dns\.resolver\.query\(.+\.encode/
        $http_post_data = /requests\.post\(.+data\s*=\s*{.+}/s
        $base64_transmit = /(base64\.b64encode|binascii\.hexlify)\(.+requests\.(post|get)/s
        $ftp_upload = /ftplib\.FTP\(.+storbinary/
        $email_send = /(smtplib\.SMTP|email\.mime)\(.+send/s
        $pastebin = /(pastebin\.com|hastebin\.com|paste\.ee)/i
        $telegram_bot = /telegram\.Bot\(.+send/
        $webhook_post = /(webhook\.site|discord\.com\/api\/webhooks)/i
        
    condition:
        any of them
}

rule KeyloggerIndicators {
    meta:
        description = "Detects keylogging or input monitoring functionality"
        severity = "CRITICAL"
        attack_type = "surveillance"
        confidence = "high"
        
    strings:
        $pynput = /from\s+pynput\s+import\s+keyboard/
        $keyboard_hook = /keyboard\.Listener\s*\(/
        $pyxhook = "import pyxhook"
        $getkey = "import getkey"
        $msvcrt_getch = /msvcrt\.getch\s*\(/
        $log_keys = /def\s+on_press\s*\(.+:\s*.*log/
        $key_capture = /keyboard\.(on_press|on_release|hook)/
        
    condition:
        any of them
}

rule SuspiciousNetworkActivity {
    meta:
        description = "Detects suspicious network patterns"
        severity = "MEDIUM"
        attack_type = "network_abuse"
        confidence = "medium"
        
    strings:
        $tor_connection = /(\.onion|tor\.proxy|socks5h)/i
        $port_scan = /socket\.connect\(.+for\s+port\s+in\s+range/s
        $proxy_chain = /(proxychains|tor-proxy)/i
        $raw_socket = /socket\.socket\(socket\.AF_INET,\s*socket\.SOCK_RAW/
        $packet_sniff = /(scapy|pcap|sniff)\s*\(/
        $nmap_scan = "import nmap"
        $shodan = "import shodan"
        
    condition:
        any of them
}

rule ObfuscatedMaliciousCode {
    meta:
        description = "Detects obfuscated code with malicious intent"
        severity = "HIGH"
        attack_type = "obfuscation"
        confidence = "high"
        
    strings:
        $pyarmor = "import pyarmor" nocase
        $marshal_loads = /marshal\.loads\s*\(/
        $zlib_decompress = /zlib\.decompress\(.+exec/s
        $rot13_exec = /codecs\.decode\(.+rot13.+exec/s
        $encrypted_payload = /(AES|DES|Blowfish)\.(new|MODE_CBC).+(decrypt|encode).+exec/s
        $hex_decode_exec = /bytes\.fromhex\(.+\)\.decode\(.+exec/s
        $lambda_obfuscation = /\(lambda.+:\s*exec\)/
        
    condition:
        any of them
}
