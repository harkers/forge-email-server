#!/usr/bin/env python3
"""Export test results to structured zip with audit-grade evidence."""

import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from run_tests import run_test

SCRIPT_DIR = Path(__file__).parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
RESULTS_DIR = SCRIPT_DIR / "results"
TEST_MATRIX_PATH = SCRIPT_DIR / "test-matrix.json"


def main():
    test_matrix = json.loads(TEST_MATRIX_PATH.read_text())
    RESULTS_DIR.mkdir(exist_ok=True)
    all_results = []

    for test in test_matrix:
        queue = json.loads((FIXTURES_DIR / "queues" / test["queue"]).read_text())
        state = json.loads((FIXTURES_DIR / "states" / test["state"]).read_text())
        test_result = run_test(test)
        test_dir = RESULTS_DIR / test["id"]
        test_dir.mkdir(exist_ok=True)

        (test_dir / "queue-input.json").write_text(json.dumps(queue, indent=2))
        (test_dir / "before-state.json").write_text(json.dumps(state, indent=2))
        (test_dir / "result.json").write_text(json.dumps(test_result, indent=2))
        (test_dir / "summary.txt").write_text(test_result["summary"])

        decision_trace = {
            "testId": test["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expected": {
                "selectedJob": test.get("expected_selected_job"),
                "outcome": test["expected_outcome"],
            },
            "actual": {
                "selectedJob": test_result["result"]["selectedJob"],
                "outcome": test_result["result"]["outcome"],
            },
            "passed": test_result["passed"],
            "candidates": test_result["result"]["candidates"],
            "safetyEvaluation": test_result["result"]["safetyEvaluation"],
            "approvalDecision": test_result["result"]["approvalDecision"],
        }
        (test_dir / "decision-trace.json").write_text(json.dumps(decision_trace, indent=2))

        evidence = test_result["evidence"]
        (test_dir / "after-state.json").write_text(json.dumps(evidence["after_state"], indent=2))
        (test_dir / "execution-metrics.json").write_text(json.dumps(evidence["execution_metrics"], indent=2))
        (test_dir / "quarantine.json").write_text(json.dumps(evidence["quarantine"], indent=2))
        (test_dir / "blocked-downstream.json").write_text(json.dumps(evidence["blocked_downstream"], indent=2))
        (test_dir / "window-accounting.json").write_text(json.dumps(evidence["window_accounting"], indent=2))
        (test_dir / "slot-consumption.json").write_text(json.dumps(evidence["slot_consumption"], indent=2))

        all_results.append(test_result)

    (RESULTS_DIR / "test-results.json").write_text(json.dumps(all_results, indent=2))

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    zip_path = SCRIPT_DIR / f"control-plane-what-next-test-results-{timestamp}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for test_result in all_results:
            test_id = test_result["test_id"]
            test_dir = RESULTS_DIR / test_id
            for filename in [
                "queue-input.json",
                "before-state.json",
                "after-state.json",
                "result.json",
                "summary.txt",
                "decision-trace.json",
                "execution-metrics.json",
                "quarantine.json",
                "blocked-downstream.json",
                "window-accounting.json",
                "slot-consumption.json",
            ]:
                filepath = test_dir / filename
                if filepath.exists():
                    zf.write(filepath, f"results/{test_id}/{filename}")
        zf.write(RESULTS_DIR / "test-results.json", "results/test-results.json")
        for fixture_file in (FIXTURES_DIR / "queues").glob("*.json"):
            zf.write(fixture_file, f"fixtures/queues/{fixture_file.name}")
        for fixture_file in (FIXTURES_DIR / "states").glob("*.json"):
            zf.write(fixture_file, f"fixtures/states/{fixture_file.name}")
        zf.write(TEST_MATRIX_PATH, "test-matrix.json")

    print(f"\nCreated: {zip_path}")
    passed = sum(1 for r in all_results if r["passed"])
    failed = len(all_results) - passed
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
