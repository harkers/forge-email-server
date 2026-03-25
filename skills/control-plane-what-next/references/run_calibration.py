#!/usr/bin/env python3
"""Run calibrated priority suite and emit class distribution report."""

import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from run_tests import run_test, score_queue, legacy_assigned_priority, now_utc

SCRIPT_DIR = Path(__file__).parent
FIXTURES_DIR = SCRIPT_DIR / "calibration_fixtures"
RESULTS_DIR = SCRIPT_DIR / "calibration_results"
MATRIX_PATH = SCRIPT_DIR / "calibration_test_matrix.json"
CHANGELOG_PATH = SCRIPT_DIR / "calibration_changelog.md"


def pct(n, total):
    return round((n / total) * 100, 2) if total else 0.0


def main():
    matrix = json.loads(MATRIX_PATH.read_text())
    RESULTS_DIR.mkdir(exist_ok=True)
    all_results = []
    total_candidates = 0
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    legacy_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    mixed_has_p2 = False
    mixed_has_p3 = False
    tie_break_visible = False

    for test in matrix:
        queue = json.loads((FIXTURES_DIR / "queues" / test["queue"]).read_text())
        state = json.loads((FIXTURES_DIR / "states" / test["state"]).read_text())
        test_result = run_test(test, fixtures_dir=FIXTURES_DIR)
        test_dir = RESULTS_DIR / test["id"]
        test_dir.mkdir(exist_ok=True)

        scored = score_queue(queue)
        for item in scored:
            counts[item["assignedPriority"]] += 1
            legacy_counts[legacy_assigned_priority(item["job"])] += 1
            total_candidates += 1
        if test["id"] == "C10_mixed_queue_distribution":
            mixed_priorities = {item["assignedPriority"] for item in scored}
            mixed_has_p2 = "P2" in mixed_priorities
            mixed_has_p3 = "P3" in mixed_priorities
        if any("tieBreakReason" in c for c in test_result["result"]["candidates"]):
            tie_break_visible = True

        decision_trace = {
            "testId": test["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expected": {
                "selectedJob": test.get("expected_selected_job"),
                "priority": test.get("expected_priority"),
                "outcome": test.get("expected_outcome"),
            },
            "actual": {
                "selectedJob": test_result["result"].get("selectedJob"),
                "priority": test_result["result"].get("selectedPriority"),
                "outcome": test_result["result"].get("outcome"),
            },
            "passed": test_result["passed"],
            "candidates": test_result["result"]["candidates"],
            "tieBreakReason": test_result["result"].get("tieBreakReason"),
        }

        files = {
            "queue-input.json": queue,
            "before-state.json": state,
            "after-state.json": test_result["evidence"]["after_state"],
            "decision-trace.json": decision_trace,
            "execution-metrics.json": test_result["evidence"]["execution_metrics"],
            "safety-report.json": test_result["evidence"]["safety_report"],
            "validator-output.json": test_result["evidence"]["validator_output"],
        }
        for filename, payload in files.items():
            (test_dir / filename).write_text(json.dumps(payload, indent=2))
        (test_dir / "summary.txt").write_text(test_result["summary"])
        all_results.append(test_result)

    distribution = {
        "totalCandidatesEvaluated": total_candidates,
        "p0Count": counts["P0"],
        "p1Count": counts["P1"],
        "p2Count": counts["P2"],
        "p3Count": counts["P3"],
        "p0Percent": pct(counts["P0"], total_candidates),
        "p1Percent": pct(counts["P1"], total_candidates),
        "p2Percent": pct(counts["P2"], total_candidates),
        "p3Percent": pct(counts["P3"], total_candidates),
        "legacyP0Count": legacy_counts["P0"],
        "legacyP1Count": legacy_counts["P1"],
        "legacyP2Count": legacy_counts["P2"],
        "legacyP3Count": legacy_counts["P3"],
        "mixedQueueHasP2": mixed_has_p2,
        "mixedQueueHasP3": mixed_has_p3,
        "tieBreakVisible": tie_break_visible,
    }
    (RESULTS_DIR / "class-distribution-summary.json").write_text(json.dumps(distribution, indent=2))

    changelog = f"""# Calibration changelog

## Priority behavior comparison

- Old threshold bands: P0 >= 18, P1 13..17, P2 8..12, P3 0..7
- New threshold bands: P0 >= 24, P1 16..23, P2 8..15, P3 0..7
- Added mandatory P0 cap rule requiring severity >= 4 or blockingBreadth >= 3 or deadlineProximity >= 4
- Tie-break order is now: higher blockingBreadth, earlier deadline, higher businessImpact, lower estimatedTokens, older queue insertion time
- Decision traces now log calibrated factor scores and tie-break reasons

## Distribution comparison on calibration pack

- Legacy P0 count: {legacy_counts['P0']} of {total_candidates} ({pct(legacy_counts['P0'], total_candidates)}%)
- New P0 count: {counts['P0']} of {total_candidates} ({pct(counts['P0'], total_candidates)}%)
- New P1 count: {counts['P1']} of {total_candidates} ({pct(counts['P1'], total_candidates)}%)
- New P2 count: {counts['P2']} of {total_candidates} ({pct(counts['P2'], total_candidates)}%)
- New P3 count: {counts['P3']} of {total_candidates} ({pct(counts['P3'], total_candidates)}%)

## Acceptance observations

- P0 materially reduced vs legacy model: {counts['P0'] < legacy_counts['P0']}
- Mixed queue includes P2: {mixed_has_p2}
- Mixed queue includes P3: {mixed_has_p3}
- Tie-break usage visible: {tie_break_visible}
"""
    CHANGELOG_PATH.write_text(changelog)

    summary = {
        "passed": sum(1 for r in all_results if r["passed"]),
        "failed": sum(1 for r in all_results if not r["passed"]),
        "distribution": distribution,
    }
    (RESULTS_DIR / "calibration-summary.json").write_text(json.dumps(summary, indent=2))

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    zip_path = SCRIPT_DIR / f"control-plane-what-next-calibration-pack-{timestamp}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for test in matrix:
            test_dir = RESULTS_DIR / test["id"]
            for path in test_dir.iterdir():
                zf.write(path, f"calibration_results/{test['id']}/{path.name}")
        zf.write(RESULTS_DIR / "class-distribution-summary.json", "calibration_results/class-distribution-summary.json")
        zf.write(RESULTS_DIR / "calibration-summary.json", "calibration_results/calibration-summary.json")
        zf.write(MATRIX_PATH, "calibration_test_matrix.json")
        zf.write(CHANGELOG_PATH, "calibration_changelog.md")
        for fixture in (FIXTURES_DIR / "queues").glob("*.json"):
            zf.write(fixture, f"calibration_fixtures/queues/{fixture.name}")
        for fixture in (FIXTURES_DIR / "states").glob("*.json"):
            zf.write(fixture, f"calibration_fixtures/states/{fixture.name}")

    print(f"Created calibration pack: {zip_path}")
    print(json.dumps(distribution, indent=2))
    return summary["failed"] == 0 and mixed_has_p2 and mixed_has_p3 and counts["P0"] < legacy_counts["P0"] and tie_break_visible


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
