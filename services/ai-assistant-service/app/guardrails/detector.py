import re
from typing import Tuple, List, Dict, Any, Optional

class PromptInjectionDetector:
    """Detects adversarial attempts to hijack, bypass, or reveal LLM system instructions."""

    INJECTION_PATTERNS = [
        # Direct override attempts
        (r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts|rules)", "Direct Instruction Override"),
        (r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts|rules)", "Direct Instruction Disregard"),
        (r"forget\s+(everything|all)\s+you\s+(were\s+told|learned|know)", "Instruction Memory Erasure"),
        (r"bypass\s+(all\s+)?(safety|content|security)?\s*(filters|guardrails|policies|restrictions)", "Guardrail Bypass Attempt"),
        
        # System prompt leakage
        (r"(reveal|print|display|show|output|leak|repeat)\s+(your\s+)?(system\s+prompt|initial\s+prompt|secret\s+instructions|hidden\s+prompt)", "System Prompt Leak Attempt"),
        (r"what\s+(is|are)\s+your\s+(exact\s+)?(system\s+prompt|hidden\s+instructions|system\s+instructions)", "System Prompt Inspection"),
        
        # Jailbreak personas
        (r"\byou\s+are\s+now\s+(in\s+)?dan(\s+mode)?\b", "DAN (Do Anything Now) Jailbreak"),
        (r"\bjailbreak(\s+mode)?\b", "Explicit Jailbreak Mention"),
        (r"\bdeveloper\s+mode\s+(enabled|on|activate)\b", "Developer Mode Jailbreak"),
        (r"act\s+as\s+(an?\s+)?(unfiltered|unrestricted|evil|malicious|hacker)\s+(ai|assistant|model)", "Unrestricted Persona Hijack"),
        (r"\bsudo\s+mode\b", "Sudo Mode Override"),
        
        # Delimiter & token manipulation
        (r"(<\|im_start\|>|<\|im_end\|>|<\|system\|>)", "ChatML Delimiter Injection"),
        (r"(^|\n)\s*system:\s*", "Raw System Role Injection"),
        (r"\[system\s*prompt\]", "System Delimiter Injection"),
    ]

    @classmethod
    def scan(cls, text: str) -> Tuple[bool, float, List[Dict[str, str]]]:
        """
        Scans input text for prompt injection patterns.
        Returns: (is_injection: bool, risk_score: float, matched_rules: List[Dict])
        """
        matches = []
        lowered = text.lower()

        for pattern, rule_name in cls.INJECTION_PATTERNS:
            if re.search(pattern, lowered, re.IGNORECASE):
                matches.append({
                    "rule": rule_name,
                    "pattern": pattern,
                })

        if not matches:
            return False, 0.0, []

        # Risk score calculation: 1 match -> 0.85, 2+ matches -> 1.0
        risk_score = min(1.0, 0.7 + (len(matches) * 0.15))
        return True, risk_score, matches


class PIIDetector:
    """Detects and redacts Personally Identifiable Information and sensitive secrets."""

    PII_RULES = [
        # Credit Card Numbers (Visa, MasterCard, Amex, Discover: 13 to 19 digits formatted or raw)
        (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11}|(?:[0-9]{4}[-\s]?){3}[0-9]{4})\b", "[REDACTED_CREDIT_CARD]", "Credit Card Number"),
        
        # Social Security Numbers (US SSN)
        (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", "Social Security Number"),
        
        # API Keys & Bearer Tokens (OpenAI sk- keys, GitHub tokens, JWTs)
        (r"\bsk-[a-zA-Z0-9_-]{20,}\b", "[REDACTED_API_KEY]", "OpenAI Secret Key"),
        (r"\bgh[pousr]-[a-zA-Z0-9]{36}\b", "[REDACTED_TOKEN]", "GitHub Personal Access Token"),
        (r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b", "[REDACTED_JWT]", "JWT Token"),
        
        # Common passwords in queries e.g. "password: xyz123"
        (r"(?i)\bpassword\s*[:=]\s*['\"]?([^\s'\"]{6,})['\"]?", "[REDACTED_PASSWORD]", "Password Credential"),
    ]

    @classmethod
    def scan_and_redact(cls, text: str) -> Tuple[bool, str, List[Dict[str, str]]]:
        """
        Detects PII / secrets and produces a sanitized version of the text.
        Returns: (pii_found: bool, sanitized_text: str, detections: List[Dict])
        """
        sanitized = text
        detections = []

        for pattern, replacement, label in cls.PII_RULES:
            found = re.findall(pattern, sanitized)
            if found:
                detections.append({
                    "type": label,
                    "count": len(found),
                    "placeholder": replacement,
                })
                sanitized = re.sub(pattern, replacement, sanitized)

        return len(detections) > 0, sanitized, detections


class TopicScopeClassifier:
    """Classifies queries to ensure they align with the DevOps Shack ecommerce and technical domain."""

    IN_SCOPE_KEYWORDS = [
        "product", "products", "keyboard", "headset", "desk mat", "mat", "yubikey", "security key",
        "monitor", "display", "notebook", "paper", "switches", "gateron", "anc", "price", "pricing",
        "quote", "cost", "discount", "promo", "coupon", "code", "devops10", "cloud20", "welcome5",
        "shackfree", "shipping", "return", "warranty", "refund", "policy", "cart", "order", "checkout",
        "inventory", "stock", "architecture", "microservice", "microservices", "java", "go", "node",
        "python", "c#", "ruby", "php", "catalog", "auth", "payment", "notification", "analytics",
        "rag", "chroma", "vector", "database", "postgres", "specs", "specifications", "features"
    ]

    OUT_OF_SCOPE_DOMAINS = [
        (r"\b(politics|presidential\s+election|political\s+party|vote\s+for|senator|congress)\b", "Politics"),
        (r"\b(medical|doctor|medicine|diagnose|symptoms?|disease|chest pain|health condition|headache|fever)\b", "Medical Diagnosis"),
        (r"\b(how\s+to\s+bake|cake\s+recipe|chocolate\s+chip\s+cookies?|pasta\s+recipe)\b", "Culinary / Recipes"),
        (r"\b(write\s+malware|ransomware|ddos\s+attack|dos\s+attack|exploit\s+vulnerability|hack\s+wifi|sql\s+injection|keylogger)\b", "Malicious Cyber Exploit"),
        (r"\b(stock\s+market\s+tips|crypto\s+investment|bitcoin\s+prediction|forex\s+trading)\b", "Financial Investment Advice"),
    ]

    @classmethod
    def check_scope(cls, text: str) -> Tuple[bool, str, Optional[str]]:
        """
        Determines if user input is within domain scope.
        Returns: (is_in_scope: bool, classification: str, refusal_reason: Optional[str])
        """
        lowered = text.lower()

        # 1. Explicit out-of-scope check
        for pattern, domain in cls.OUT_OF_SCOPE_DOMAINS:
            if re.search(pattern, lowered):
                return False, f"Out of Scope ({domain})", f"I am the DevOps Shack Store Assistant. I can only assist with our developer hardware products, pricing quotes, orders, and platform architecture. I cannot provide assistance with {domain}."

        # 2. In-scope keyword presence check
        has_in_scope = any(k in lowered for k in cls.IN_SCOPE_KEYWORDS)
        
        # Very short greetings or generic conversation are allowed
        greetings = ["hi", "hello", "hey", "help", "who are you", "what can you do", "good morning", "good evening", "thanks", "thank you"]
        is_greeting = any(lowered.strip().startswith(g) for g in greetings) or len(lowered.split()) <= 3

        if has_in_scope or is_greeting:
            return True, "in_scope", None

        # If completely unrecognized, allow with neutral classification or guide user
        return True, "neutral_scope", None


class SecretLeakDetector:
    """Verifies that LLM outputs do not leak system secrets or private keys."""

    SECRET_PATTERNS = [
        r"sk-[a-zA-Z0-9_-]{20,}",
        r"postgres://[^\s]+:[^\s]+@",
        r"postgrespassword",
        r"microapp123",
        r"BEGIN PRIVATE KEY",
        r"OPENAI_API_KEY\s*=\s*[^\s]+",
    ]

    @classmethod
    def scan_output(cls, output_text: str) -> Tuple[bool, str]:
        """
        Checks output text for leaked secrets.
        Returns: (has_leak: bool, sanitized_output: str)
        """
        sanitized = output_text
        has_leak = False

        for pat in cls.SECRET_PATTERNS:
            if re.search(pat, sanitized):
                has_leak = True
                sanitized = re.sub(pat, "[INTERNAL_SECRET_REDACTED]", sanitized)

        return has_leak, sanitized
