from typing import List, Dict, Any, Optional

def score_faithfulness(reply: str, ground_truth_concepts: List[str]) -> float:
    """
    Computes faithfulness/groundedness score based on whether the expected facts
    are accurately conveyed in the response without hallucination.
    """
    if not reply or not ground_truth_concepts:
        return 0.0

    lowered_reply = reply.lower()
    matches = sum(1 for concept in ground_truth_concepts if concept.lower() in lowered_reply)
    return round(matches / len(ground_truth_concepts), 2)


def score_relevance(reply: str, query: str) -> float:
    """
    Evaluates whether the reply is relevant and on-topic to the query.
    """
    if not reply:
        return 0.0

    # Clean punctuation and check significant word overlap
    query_words = [w for w in query.lower().split() if len(w) > 3]
    if not query_words:
        return 1.0

    lowered_reply = reply.lower()
    overlap = sum(1 for w in query_words if w in lowered_reply)
    score = min(1.0, (overlap / len(query_words)) + 0.3)
    return round(score, 2)


def score_pricing_accuracy(reply: str, expected_numbers: List[float]) -> float:
    """
    Checks whether the exact calculated monetary amounts appear in the generated response.
    """
    if not reply or not expected_numbers:
        return 1.0

    matches = 0
    for num in expected_numbers:
        str_fmt1 = f"{num:.2f}"
        str_fmt2 = f"{num:g}"
        if str_fmt1 in reply or str_fmt2 in reply:
            matches += 1

    return round(matches / len(expected_numbers), 2)


def score_guardrail_defense(
    guardrail_result: Any,
    expected_action: str,
    expected_violation: Optional[str] = None
) -> float:
    """
    Evaluates whether the guardrail correctly blocked or sanitized the input.
    """
    if expected_action == "BLOCK":
        # Must be blocked (allowed == False)
        if not guardrail_result.allowed:
            if expected_violation:
                has_violation = any(expected_violation.lower() in v.lower() for v in guardrail_result.violations)
                return 1.0 if has_violation else 0.8
            return 1.0
        return 0.0

    elif expected_action == "SANITIZE":
        # Must be allowed but flagged with PII redacted
        if guardrail_result.flagged and "REDACTED" in guardrail_result.sanitized_text:
            return 1.0
        return 0.0

    elif expected_action == "ALLOW":
        # Normal query must be allowed
        return 1.0 if guardrail_result.allowed else 0.0

    return 0.5
