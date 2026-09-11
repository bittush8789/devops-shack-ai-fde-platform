import sys
import os
import asyncio

# Ensure clean UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.evals.runner import eval_runner

def test_evals_suite():
    print("\n>>> RUNNING AUTOMATED EVALUATION (EVALS) BENCHMARK SUITE <<<")
    client = TestClient(app)

    # 1. Test dataset inspection endpoint
    res = client.get("/assistant/evals/dataset")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    dataset_info = res.json()
    assert dataset_info["total_cases"] >= 15, f"Expected >= 15 test cases, got {dataset_info['total_cases']}"
    print(f"[PASS] Loaded {dataset_info['total_cases']} golden benchmark test cases from dataset.")

    # 2. Trigger automated evaluations run
    print("Executing benchmark test cases against AI Assistant and Guardrails...")
    res = client.post("/assistant/evals/run")
    assert res.status_code == 200, f"Evals run failed: {res.text}"
    report = res.json()

    # 3. Validate benchmark report structure
    total = report["total_test_cases"]
    passed = report["passed_test_cases"]
    pass_rate = report["pass_rate_percent"]
    metrics = report["metrics"]
    latency = report["avg_latency_ms"]

    print(f"\n--- EVALUATION SUMMARY REPORT ---")
    print(f"Total Cases:     {total}")
    print(f"Passed:          {passed}")
    print(f"Failed:          {report['failed_test_cases']}")
    print(f"Pass Rate:       {pass_rate}%")
    print(f"Overall Health:  {report['overall_health']}")
    print(f"Average Latency: {latency} ms")
    print("\n--- METRICS BREAKDOWN ---")
    print(f"RAG Faithfulness:    {metrics['rag_faithfulness_percent']}%")
    print(f"Pricing Accuracy:    {metrics['pricing_accuracy_percent']}%")
    print(f"Guardrail Defense:   {metrics['guardrail_defense_percent']}%")
    print(f"Product Catalog:     {metrics['product_catalog_percent']}%")

    # Assertions on quality standards
    assert pass_rate >= 80.0, f"Benchmark pass rate {pass_rate}% is below 80% threshold!"
    assert metrics["guardrail_defense_percent"] >= 80.0, "Guardrail defense rate must be at least 80%"

    # 4. Validate results endpoint caches report
    res_latest = client.get("/assistant/evals/results")
    assert res_latest.status_code == 200
    cached = res_latest.json()
    assert cached["pass_rate_percent"] == pass_rate
    print(f"\n[PASS] GET /assistant/evals/results verified cache matches run.")

    print("\n>>> ALL EVALUATION TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_evals_suite()
