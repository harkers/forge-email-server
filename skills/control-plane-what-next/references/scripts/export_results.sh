#!/bin/bash
# Export test results to zip

cd "$(dirname "$0")/.."

# Create results directory if needed
mkdir -p results

# Run tests and capture output
python3 run_tests.py 2>&1 | tee results/test-run-output.txt

# Create individual result folders
for test_id in T01_priority_p0_beats_all T02_tiebreak_deadline T03_jobs_window_decrements T04_time_window_expires T05_destructive_job_blocked T06_retry_then_quarantine T07_token_limit_enforced T08_dependency_failure_blocks_children T09_pipeline_empty_stops_cleanly T10_session_restart_state_recovery T11_e2e_normal_delivery T12_e2e_risky_job_mid_run T13_e2e_failure_chain; do
    mkdir -p "results/$test_id"
    cp fixtures/queues/$(echo $test_id | cut -d_ -f1 | tr '[:upper:]' '[:lower]')_queue.json "results/$test_id/queue-input.json" 2>/dev/null || true
done

# Create zip
zip -r control-plane-what-next-test-results.zip results/ fixtures/ test-matrix.json run_tests.py

echo "Created: control-plane-what-next-test-results.zip"