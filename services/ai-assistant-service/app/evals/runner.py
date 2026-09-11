import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.evals.dataset import GOLDEN_EVAL_DATASET
from app.evals.metrics import (
    score_faithfulness,
    score_relevance,
    score_pricing_accuracy,
    score_guardrail_defense,
)
from app.guardrails.manager import guardrail_manager
from app.assistant import assistant

logger = logging.getLogger(__name__)

class EvalRunner:
    """Executes benchmark evaluation test cases, calculates LLM metrics, and profiles latency."""

    def __init__(self):
        self._latest_run: Optional[Dict[str, Any]] = None

    async def run_suite(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes all benchmark test cases against Guardrails and AI Assistant.
        """
        cases = GOLDEN_EVAL_DATASET[:limit] if limit else GOLDEN_EVAL_DATASET
        results = []
        start_suite = time.perf_counter()

        category_scores: Dict[str, List[float]] = {
            "rag_faithfulness": [],
            "pricing_accuracy": [],
            "guardrail_defense": [],
            "product_catalog": [],
        }

        for case in cases:
            case_id = case["id"]
            category = case["category"]
            query = case["query"]
            expected_action = case.get("expected_action", "ALLOW")
            expected_violation = case.get("expected_violation")
            ground_truth = case.get("ground_truth_concepts", [])
            expected_numbers = case.get("expected_numbers", [])

            t0 = time.perf_counter()

            # 1. Pre-flight Guardrail Check
            guard_res = guardrail_manager.check_input(query)
            
            # 2. Call Assistant if allowed, or use Guardrail refusal if blocked
            if not guard_res.allowed:
                reply = guard_res.refusal_reply or "Blocked by safety policy."
                tools_called = []
                mode = "guardrail_block"
            else:
                chat_res = await assistant.chat(message=guard_res.sanitized_text)
                reply = chat_res.get("reply", "")
                tools_called = chat_res.get("tools_called", [])
                mode = chat_res.get("mode", "assistant")

            latency_ms = round((time.perf_counter() - t0) * 1000, 1)

            # 3. Compute Metrics
            guard_score = score_guardrail_defense(guard_res, expected_action, expected_violation)
            faith_score = score_faithfulness(reply, ground_truth) if ground_truth else 1.0
            relev_score = score_relevance(reply, query)
            price_score = score_pricing_accuracy(reply, expected_numbers) if expected_numbers else 1.0

            # Overall case score
            if category == "guardrail_defense":
                case_score = guard_score
            elif category == "pricing_accuracy":
                case_score = round((price_score * 0.7) + (faith_score * 0.3), 2)
            elif category == "rag_faithfulness":
                case_score = round((faith_score * 0.7) + (relev_score * 0.3), 2)
            else:
                case_score = round((faith_score * 0.5) + (relev_score * 0.5), 2)

            is_passed = case_score >= 0.70
            category_scores[category].append(case_score)

            results.append({
                "id": case_id,
                "name": case["name"],
                "category": category,
                "query": query,
                "expected_action": expected_action,
                "actual_action": "BLOCK" if not guard_res.allowed else ("SANITIZE" if guard_res.flagged else "ALLOW"),
                "passed": is_passed,
                "score": case_score,
                "faithfulness": faith_score,
                "relevance": relev_score,
                "pricing_accuracy": price_score,
                "guardrail_defense": guard_score,
                "latency_ms": latency_ms,
                "tools_called": [t.get("tool") for t in tools_called if isinstance(t, dict)],
                "reply_snippet": (reply[:180] + "...") if len(reply) > 180 else reply,
                "mode": mode,
            })

        total_duration_sec = round(time.perf_counter() - start_suite, 2)
        total_cases = len(results)
        passed_count = sum(1 for r in results if r["passed"])
        pass_rate = round((passed_count / total_cases * 100) if total_cases else 0.0, 1)

        def avg_category(cat: str) -> float:
            scores = category_scores.get(cat, [])
            return round((sum(scores) / len(scores) * 100) if scores else 0.0, 1)

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": total_duration_sec,
            "total_test_cases": total_cases,
            "passed_test_cases": passed_count,
            "failed_test_cases": total_cases - passed_count,
            "pass_rate_percent": pass_rate,
            "overall_health": "EXCELLENT" if pass_rate >= 90 else ("GOOD" if pass_rate >= 75 else "NEEDS_IMPROVEMENT"),
            "metrics": {
                "rag_faithfulness_percent": avg_category("rag_faithfulness"),
                "pricing_accuracy_percent": avg_category("pricing_accuracy"),
                "guardrail_defense_percent": avg_category("guardrail_defense"),
                "product_catalog_percent": avg_category("product_catalog"),
            },
            "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / total_cases if total_cases else 0.0, 1),
            "results": results,
        }

        self._latest_run = summary
        logger.info(f"Evals suite completed: {passed_count}/{total_cases} passed ({pass_rate}%) in {total_duration_sec}s")
        return summary

    @property
    def latest_results(self) -> Optional[Dict[str, Any]]:
        return self._latest_run

eval_runner = EvalRunner()
