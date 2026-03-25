#!/usr/bin/env python3
"""
Export test results to structured zip
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime
from run_tests import run_test, generate_operator_summary

# Paths
SCRIPT_DIR = Path(__file__).parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
RESULTS_DIR = SCRIPT_DIR / "results"
TEST_MATRIX_PATH = SCRIPT_DIR / "test-matrix.json"

def main():
    # Load test matrix
    with open(TEST_MATRIX_PATH) as f:
        test_matrix = json.load(f)
    
    # Create results directory
    RESULTS_DIR.mkdir(exist_ok=True)
    
    # Run all tests and collect results
    all_results = []
    
    for test in test_matrix:
        # Load fixtures
        queue_path = FIXTURES_DIR / "queues" / test["queue"]
        state_path = FIXTURES_DIR / "states" / test["state"]
        
        with open(queue_path) as f:
            queue = json.load(f)
        with open(state_path) as f:
            state = json.load(f)
        
        # Run test
        test_result = run_test(test)
        
        # Create result folder
        test_dir = RESULTS_DIR / test["id"]
        test_dir.mkdir(exist_ok=True)
        
        # Write result files
        with open(test_dir / "queue-input.json", "w") as f:
            json.dump(queue, f, indent=2)
        
        with open(test_dir / "before-state.json", "w") as f:
            json.dump(state, f, indent=2)
        
        with open(test_dir / "result.json", "w") as f:
            json.dump(test_result, f, indent=2)
        
        with open(test_dir / "summary.txt", "w") as f:
            f.write(test_result["summary"])
        
        # Create decision trace
        decision_trace = {
            "testId": test["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expected": {
                "selectedJob": test.get("expected_selected_job"),
                "outcome": test["expected_outcome"]
            },
            "actual": {
                "selectedJob": test_result["result"]["selectedJob"],
                "outcome": test_result["result"]["outcome"]
            },
            "passed": test_result["passed"],
            "candidates": test_result["result"]["candidates"],
            "safetyEvaluation": test_result["result"]["safetyEvaluation"],
            "approvalDecision": test_result["result"]["approvalDecision"]
        }
        
        with open(test_dir / "decision-trace.json", "w") as f:
            json.dump(decision_trace, f, indent=2)
        
        all_results.append(test_result)
    
    # Write summary
    with open(RESULTS_DIR / "test-results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Create zip
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    zip_path = SCRIPT_DIR / f"control-plane-what-next-test-results-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add results
        for test_result in all_results:
            test_id = test_result["test_id"]
            test_dir = RESULTS_DIR / test_id
            
            for filename in ["queue-input.json", "before-state.json", "result.json", "summary.txt", "decision-trace.json"]:
                filepath = test_dir / filename
                if filepath.exists():
                    zf.write(filepath, f"results/{test_id}/{filename}")
        
        # Add summary
        zf.write(RESULTS_DIR / "test-results.json", "results/test-results.json")
        
        # Add fixtures
        for fixture_file in (FIXTURES_DIR / "queues").glob("*.json"):
            zf.write(fixture_file, f"fixtures/queues/{fixture_file.name}")
        
        for fixture_file in (FIXTURES_DIR / "states").glob("*.json"):
            zf.write(fixture_file, f"fixtures/states/{fixture_file.name}")
        
        # Add test matrix
        zf.write(TEST_MATRIX_PATH, "test-matrix.json")
    
    print(f"\nCreated: {zip_path}")
    
    # Print summary
    passed = sum(1 for r in all_results if r["passed"])
    failed = len(all_results) - passed
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    from datetime import timezone
    sys.exit(0 if main() else 1)