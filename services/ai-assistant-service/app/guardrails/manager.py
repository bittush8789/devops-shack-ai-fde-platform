import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from app.guardrails.detector import (
    PromptInjectionDetector,
    PIIDetector,
    TopicScopeClassifier,
    SecretLeakDetector,
)

logger = logging.getLogger(__name__)

class GuardrailResult(BaseModel):
    allowed: bool = Field(..., description="Whether the request is allowed to proceed to LLM")
    flagged: bool = Field(default=False, description="Whether any policy violation or PII was detected")
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    violations: List[str] = Field(default_factory=list)
    sanitized_text: str = Field(..., description="Sanitized/redacted text")
    refusal_reply: Optional[str] = Field(default=None, description="Pre-crafted refusal if blocked")
    checks: List[Dict[str, Any]] = Field(default_factory=list)


class GuardrailManager:
    """Orchestrates pre-flight input and post-flight output guardrail verifications."""

    def __init__(self):
        self.injection_detector = PromptInjectionDetector
        self.pii_detector = PIIDetector
        self.scope_classifier = TopicScopeClassifier
        self.secret_detector = SecretLeakDetector

    def check_input(self, text: str) -> GuardrailResult:
        """
        Runs comprehensive pre-flight guardrail checks on incoming user query.
        """
        violations = []
        checks = []
        refusal_reply = None
        current_text = text
        max_risk = 0.0
        blocked = False

        # 1. Prompt Injection & Jailbreak Check
        is_injection, injection_risk, injection_matches = self.injection_detector.scan(current_text)
        checks.append({
            "name": "prompt_injection_detector",
            "status": "FAIL" if is_injection else "PASS",
            "risk_score": injection_risk,
            "details": injection_matches,
        })
        if is_injection:
            max_risk = max(max_risk, injection_risk)
            rule_names = [m["rule"] for m in injection_matches]
            violations.append(f"Prompt Injection Detected: {', '.join(rule_names)}")
            blocked = True
            refusal_reply = (
                "🛡️ **Security Guardrail Triggered**\n\n"
                "Your request contains instructions attempting to override system behavior, reveal hidden prompts, or bypass platform safety policies. "
                "For security reasons, this query cannot be processed. Please ask about products, pricing, or system architecture."
            )

        # 2. PII & Secret Redaction Check
        has_pii, redacted_text, pii_matches = self.pii_detector.scan_and_redact(current_text)
        current_text = redacted_text
        checks.append({
            "name": "pii_data_masker",
            "status": "FLAGGED" if has_pii else "PASS",
            "risk_score": 0.5 if has_pii else 0.0,
            "details": pii_matches,
        })
        if has_pii:
            max_risk = max(max_risk, 0.5)
            pii_types = [f"{p['count']}x {p['type']}" for p in pii_matches]
            violations.append(f"PII Detected and Redacted: {', '.join(pii_types)}")

        # 3. Topic & Scope Verification Check
        if not blocked:
            is_in_scope, scope_type, scope_refusal = self.scope_classifier.check_scope(current_text)
            checks.append({
                "name": "topic_scope_classifier",
                "status": "PASS" if is_in_scope else "FAIL",
                "classification": scope_type,
            })
            if not is_in_scope:
                blocked = True
                max_risk = max(max_risk, 0.6)
                violations.append(f"Topic Out of Scope: {scope_type}")
                refusal_reply = f"🛡️ **Domain Scope Notice**\n\n{scope_refusal}"

        return GuardrailResult(
            allowed=not blocked,
            flagged=len(violations) > 0,
            risk_score=max_risk,
            violations=violations,
            sanitized_text=current_text,
            refusal_reply=refusal_reply,
            checks=checks,
        )

    def check_output(self, reply: str) -> Tuple[bool, str, List[str]]:
        """
        Inspects generated assistant reply before sending to user.
        Redacts any leaked credentials or secrets.
        Returns: (has_violation: bool, sanitized_reply: str, violations: List[str])
        """
        has_leak, clean_reply = self.secret_detector.scan_output(reply)
        violations = []
        if has_leak:
            violations.append("Internal secret/credential leak prevented in output.")
            logger.warning("Guardrail caught and sanitized secret leak in output reply.")

        return has_leak, clean_reply, violations

    @property
    def policies(self) -> Dict[str, Any]:
        """Summary of active guardrail rules for API and dashboard inspection."""
        modules = [
            {
                "name": "Prompt Injection Defense",
                "type": "SECURITY",
                "description": "Intercepts instruction overrides, DAN personas, and system prompt extraction attacks.",
                "action": "BLOCK",
                "severity": "CRITICAL",
            },
            {
                "name": "PII & Secret Redaction",
                "type": "PRIVACY",
                "description": "Automatically masks credit cards, SSNs, API tokens, and credentials with safe placeholder tokens.",
                "action": "SANITIZE & ALLOW",
                "severity": "HIGH",
            },
            {
                "name": "Domain Scope Classifier",
                "type": "COMPLIANCE",
                "description": "Restricts interactions to ecommerce products, hardware specs, pricing, and microservices architecture.",
                "action": "BLOCK & REDIRECT",
                "severity": "MEDIUM",
            },
            {
                "name": "Output Secret Leak Prevention",
                "type": "SECURITY",
                "description": "Guarantees no internal environment secrets or API keys are returned to users.",
                "action": "SANITIZE",
                "severity": "CRITICAL",
            },
        ]
        return {
            "guardrails_active": True,
            "modules": modules,
            "policies": modules,
            "total_rules": len(modules),
        }

guardrail_manager = GuardrailManager()
