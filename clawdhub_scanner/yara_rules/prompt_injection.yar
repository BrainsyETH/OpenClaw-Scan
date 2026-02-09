/*
 * ClawdHub Security Scanner - Prompt Injection Detection Rules
 * 
 * Detects patterns commonly associated with prompt injection attacks,
 * jailbreak attempts, and instruction manipulation in AI agent skills.
 * 
 * Author: VesperThread
 * Date: 2026-02-05
 */

rule PromptInjectionIgnorePrevious {
    meta:
        description = "Detects attempts to override previous instructions"
        severity = "HIGH"
        attack_type = "prompt_injection"
        confidence = "high"
        
    strings:
        $ignore1 = /ignore\s+(all\s+)?(previous|prior|earlier)\s+instructions/i
        $ignore2 = /disregard\s+(all\s+)?(previous|prior|earlier)\s+instructions/i
        $forget1 = /forget\s+(all\s+)?(previous|prior|earlier)\s+(instructions|context)/i
        $override1 = /override\s+(system|previous|default)\s+(instructions|prompts)/i
        $reset1 = /reset\s+(instructions|context|system)/i
        $new_instructions = /new\s+instructions:/i
        $ignore_system = /ignore\s+system\s+prompt/i
        
    condition:
        any of them
}

rule PromptLeakAttempt {
    meta:
        description = "Detects attempts to leak system prompts or internal instructions"
        severity = "MEDIUM"
        attack_type = "information_disclosure"
        confidence = "medium"
        
    strings:
        $leak1 = /print\s+(your\s+)?(system\s+prompt|instructions|guidelines)/i
        $leak2 = /show\s+(me\s+)?(your\s+)?(system\s+prompt|instructions)/i
        $leak3 = /reveal\s+(your\s+)?(system\s+prompt|instructions)/i
        $leak4 = /what\s+(are\s+)?(your\s+)?(system\s+prompt|instructions)/i
        $leak5 = /repeat\s+(your\s+)?(system\s+prompt|instructions)/i
        $leak6 = /display\s+(your\s+)?(system\s+prompt|original\s+instructions)/i
        $verbatim = /output\s+(verbatim|exactly)/i
        
    condition:
        any of them
}

rule RoleplayJailbreak {
    meta:
        description = "Detects roleplay-based jailbreak attempts"
        severity = "HIGH"
        attack_type = "jailbreak"
        confidence = "medium"
        
    strings:
        $roleplay1 = /pretend\s+you\s+are\s+(a\s+)?(different|unrestricted|unfiltered)/i
        $roleplay2 = /act\s+as\s+(if\s+you\s+are\s+)?(a\s+)?(unrestricted|unfiltered|uncensored)/i
        $roleplay3 = /imagine\s+you\s+have\s+no\s+(rules|restrictions|guidelines)/i
        $dan = /DAN\s+(mode|prompt)/i  // "Do Anything Now"
        $evil_mode = /(evil|chaos|unrestricted)\s+mode/i
        $no_ethics = /ignore\s+(ethics|safety|guidelines)/i
        $bypass = /bypass\s+(restrictions|safety|filters)/i
        
    condition:
        any of them
}

rule PermissionEscalation {
    meta:
        description = "Detects attempts to escalate permissions or access"
        severity = "CRITICAL"
        attack_type = "privilege_escalation"
        confidence = "high"
        
    strings:
        $grant1 = /grant\s+(me\s+)?(admin|root|sudo|elevated)\s+(access|permissions)/i
        $grant2 = /give\s+(me\s+)?(admin|root|sudo|elevated)\s+(access|rights)/i
        $escalate = /escalate\s+(my\s+)?privileges/i
        $sudo = /sudo\s+(access|mode|privileges)/i
        $unrestricted = /unrestricted\s+(access|mode)/i
        $bypass_auth = /bypass\s+auth(entication|orization)/i
        $override_perms = /override\s+permissions/i
        
    condition:
        any of them
}

rule SuspiciousInstructionManipulation {
    meta:
        description = "Detects suspicious attempts to manipulate agent behavior"
        severity = "MEDIUM"
        attack_type = "behavioral_manipulation"
        confidence = "low"
        
    strings:
        $change_behavior = /change\s+your\s+(behavior|responses|personality)/i
        $stop_following = /stop\s+following\s+(rules|guidelines|instructions)/i
        $disable1 = /disable\s+(safety|filtering|moderation)/i
        $remove_limits = /remove\s+(all\s+)?(limits|restrictions|constraints)/i
        $unlock = /unlock\s+(full|hidden|secret)\s+(capabilities|features)/i
        $developer_mode = /enable\s+developer\s+mode/i
        $bypass_filter = /bypass\s+content\s+filter/i
        
    condition:
        any of them
}
