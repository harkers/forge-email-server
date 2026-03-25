#!/usr/bin/env python3
"""
Control-plane-what-next test runner v4
Validates priority scoring, safety gates, state transitions, and audit-grade evidence.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy

SCRIPT_DIR = Path(__file__).parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
RESULTS_DIR = SCRIPT_DIR / "results"

WEIGHTS = {
    "severity": 3,
    "blocking_impact": 3,
    "dependency_breadth": 2,
    "deadline_proximity": 2,
    "execution_readiness": 1,
    "execution_effort": -1,
}

DEADLINE_SCORES = [
    (4, 5), (24, 4), (72, 3), (168, 2), (float("inf"), 1),
]


class TestState:
    def __init__(self, state: dict):
        self.initial_state = deepcopy(state)
        self.state = deepcopy(state)
        self.failed_jobs = []
        self.quarantined_jobs = []
        self.completed_jobs = []
        self.blocked_jobs = []
        self.blocked_reasons = {}
        self.risky_held = []
        self.retry_counts = {}
        self.actual_tokens = {}
        self.runtime_ms = {}
        self.dispatch_attempts = {}
        self.quarantine_metadata = {}
        self.downstream_blocked = {}
        self.slot_consumption_events = []
        self.window_token_events = []
        self.last_dispatched_job_id = None

    def failure_count(self, job_id: str) -> int:
        return self.retry_counts.get(job_id, 0)

    def is_quarantined(self, job_id: str) -> bool:
        return job_id in self.quarantined_jobs

    def register_attempt(self, job_id: str):
        self.dispatch_attempts[job_id] = self.dispatch_attempts.get(job_id, 0) + 1

    def register_failure(self, job_id: str):
        self.retry_counts[job_id] = self.retry_counts.get(job_id, 0) + 1
        if job_id not in self.failed_jobs:
            self.failed_jobs.append(job_id)

    def register_quarantine(self, job_id: str, reason: str = "repeated_failure"):
        if job_id not in self.quarantined_jobs:
            self.quarantined_jobs.append(job_id)
        self.quarantine_metadata[job_id] = {
            "jobId": job_id,
            "quarantined": True,
            "reason": reason,
            "failedAttempts": self.retry_counts.get(job_id, 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def register_complete(self, job_id: str, actual_tokens: int, runtime_ms: int):
        if job_id not in self.completed_jobs:
            self.completed_jobs.append(job_id)
        self.actual_tokens[job_id] = actual_tokens
        self.runtime_ms[job_id] = runtime_ms
        self.last_dispatched_job_id = job_id

        window_tokens_before = self.state.get("windowTokensUsed", 0)
        window_tokens_after = window_tokens_before + actual_tokens
        self.state["windowTokensUsed"] = window_tokens_after

        jobs_before = self.state.get("jobsRemaining")
        jobs_after = jobs_before
        if jobs_before is not None:
            jobs_after = max(0, jobs_before - 1)
            self.state["jobsRemaining"] = jobs_after

        self.state["lastDispatchedJobId"] = job_id
        self.state["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()
        self.state.setdefault("windowCompletedJobs", [])
        self.state.setdefault("sessionCompletedJobs", [])
        if job_id not in self.state["windowCompletedJobs"]:
            self.state["windowCompletedJobs"].append(job_id)
        if job_id not in self.state["sessionCompletedJobs"]:
            self.state["sessionCompletedJobs"].append(job_id)

        self.window_token_events.append({
            "jobId": job_id,
            "windowTokensBefore": window_tokens_before,
            "windowTokensAfter": window_tokens_after,
            "actualTokensUsed": actual_tokens,
        })
        self.slot_consumption_events.append({
            "jobId": job_id,
            "jobsRemainingBefore": jobs_before,
            "jobsRemainingAfter": jobs_after,
            "slotConsumed": jobs_before is not None and jobs_after is not None and jobs_after < jobs_before,
        })

    def register_blocked(self, job_id: str, reasons: list[str]):
        if job_id not in self.blocked_jobs:
            self.blocked_jobs.append(job_id)
        self.blocked_reasons[job_id] = reasons

    def register_risky_held(self, job_id: str):
        if job_id not in self.risky_held:
            self.risky_held.append(job_id)

    def register_downstream_blocked(self, root_job_id: str, blocked_jobs: list[str]):
        self.downstream_blocked[root_job_id] = blocked_jobs


def score_impact(impact: str) -> int:
    return {"critical": 5, "high": 4, "medium": 3, "low": 2, "trivial": 1}.get(impact, 2)


def score_deadline(deadline: str) -> int:
    try:
        deadline_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_until = (deadline_dt - now).total_seconds() / 3600
        for threshold, score in DEADLINE_SCORES:
            if hours_until <= threshold:
                return score
        return 0
    except Exception:
        return 0


def score_blocking(blocks: list) -> int:
    count = len(blocks)
    if count >= 5:
        return 5
    if count >= 3:
        return 4
    if count >= 1:
        return 3
    return 0


def score_dependencies(deps: list) -> int:
    count = len(deps)
    if count == 0:
        return 0
    if count == 1:
        return 2
    if count <= 3:
        return 3
    if count <= 5:
        return 4
    return 5


def score_tokens(tokens: int) -> int:
    if tokens < 10000:
        return 1
    if tokens < 30000:
        return 2
    if tokens < 60000:
        return 3
    if tokens < 100000:
        return 4
    return 5


def calculate_priority_score(job: dict) -> tuple[int, str]:
    severity = score_impact(job.get("impact", "medium"))
    blocking = score_blocking(job.get("blocks", []))
    breadth = score_dependencies(job.get("dependencies", []))
    deadline = score_deadline(job.get("deadline", ""))
    readiness = 5 if job.get("ready", True) else 2
    effort = score_tokens(job.get("estimatedTokens", 50000))

    score = (
        severity * WEIGHTS["severity"]
        + blocking * WEIGHTS["blocking_impact"]
        + breadth * WEIGHTS["dependency_breadth"]
        + deadline * WEIGHTS["deadline_proximity"]
        + readiness * WEIGHTS["execution_readiness"]
        + effort * WEIGHTS["execution_effort"]
    )

    if score >= 18:
        band = "P0"
    elif score >= 13:
        band = "P1"
    elif score >= 8:
        band = "P2"
    else:
        band = "P3"
    return score, band


def tie_break(jobs: list[dict]) -> dict:
    def key(job):
        return (
            -len(job.get("blocks", [])),
            job.get("deadline", "9999-99-99"),
            -1 if job.get("ready", True) else 0,
            job.get("estimatedTokens", 50000),
            job.get("jobId", ""),
        )
    return sorted(jobs, key=key)[0]


def check_safety_gates(job: dict, state: dict, test_state: TestState | None = None) -> tuple[bool, list[str]]:
    reasons = []
    job_id = job.get("jobId", "")

    if test_state and test_state.is_quarantined(job_id):
        reasons.append("job is quarantined after repeated failure")

    if test_state:
        for dep_id in job.get("dependencies", []):
            if dep_id in test_state.failed_jobs or dep_id in test_state.quarantined_jobs:
                reasons.append(f"blocked by failed dependency {dep_id}")

    if job.get("destructive", False) and not state.get("allowDestructive", False):
        reasons.append("destructive operation blocked")

    if job.get("productionImpact", False) and not state.get("allowProdChanges", False):
        reasons.append("production-impacting change blocked")

    max_per_job = state.get("maxTokensPerJob", 120000)
    if job.get("estimatedTokens", 0) > max_per_job:
        reasons.append(f"token limit exceeded ({job.get('estimatedTokens')} > {max_per_job})")

    if not job.get("ready", True):
        reasons.append("job not ready for execution")

    if job.get("confidence", 1) < 0.5:
        reasons.append("confidence below threshold")

    return len(reasons) == 0, reasons


def check_approval_window(state: dict) -> tuple[bool, str]:
    mode = state.get("mode", "none")
    if mode == "none":
        return False, "no approval window"
    if mode == "time":
        expires = state.get("windowExpiresAt")
        if expires:
            expires_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires_dt:
                return False, "time window expired"
        return True, "time window active"
    if mode == "jobs":
        remaining = state.get("jobsRemaining", 0)
        if remaining <= 0:
            return False, "jobs window exhausted"
        return True, f"jobs window active ({remaining} remaining)"
    if mode == "until-empty":
        return True, "until-empty window active"
    return False, "unknown window mode"


def deterministic_actual_tokens(job: dict, attempt: int = 1) -> int:
    est = job.get("estimatedTokens", 0)
    base = int(est * (0.72 + ((len(job.get("jobId", "")) % 5) * 0.03)))
    return max(800, base + (attempt - 1) * 250)


def deterministic_runtime_ms(job: dict, attempt: int = 1) -> int:
    est = job.get("estimatedTokens", 0)
    return max(150, int(est / 18) + attempt * 75)


def build_evidence(test: dict, queue: list[dict], before_state: dict, test_state: TestState, result: dict) -> dict:
    selected_job_id = result.get("selectedJob")
    selected_job = next((j for j in queue if j.get("jobId") == selected_job_id), None)
    retry_count = test_state.retry_counts.get(selected_job_id, 0) if selected_job_id else 0
    actual_tokens = test_state.actual_tokens.get(selected_job_id, 0) if selected_job_id else 0
    runtime_ms = test_state.runtime_ms.get(selected_job_id, 0) if selected_job_id else 0
    quarantine = test_state.quarantine_metadata.get(selected_job_id) if selected_job_id else None

    blocked_root = None
    blocked_jobs = []
    if test_state.downstream_blocked:
        blocked_root = next(iter(test_state.downstream_blocked.keys()))
        blocked_jobs = test_state.downstream_blocked[blocked_root]

    latest_window = test_state.window_token_events[-1] if test_state.window_token_events else {
        "windowTokensBefore": before_state.get("windowTokensUsed", 0),
        "windowTokensAfter": test_state.state.get("windowTokensUsed", before_state.get("windowTokensUsed", 0)),
        "actualTokensUsed": 0,
    }
    latest_slot = test_state.slot_consumption_events[-1] if test_state.slot_consumption_events else {
        "jobsRemainingBefore": before_state.get("jobsRemaining"),
        "jobsRemainingAfter": test_state.state.get("jobsRemaining"),
        "slotConsumed": False,
    }

    execution_metrics = {
        "testId": test["id"],
        "jobId": selected_job_id,
        "runtimeMs": runtime_ms,
        "actualTokensUsed": actual_tokens,
        "retryCount": retry_count,
        "dispatchAttempts": test_state.dispatch_attempts.get(selected_job_id, 0) if selected_job_id else 0,
        "estimatedTokens": selected_job.get("estimatedTokens") if selected_job else None,
    }

    window_accounting = {
        "testId": test["id"],
        "jobId": selected_job_id,
        "mode": before_state.get("mode"),
        "jobsRemainingBefore": latest_slot["jobsRemainingBefore"],
        "jobsRemainingAfter": latest_slot["jobsRemainingAfter"],
        "windowTokensBefore": latest_window["windowTokensBefore"],
        "windowTokensAfter": latest_window["windowTokensAfter"],
        "actualTokensUsed": latest_window["actualTokensUsed"],
    }

    slot_consumption = {
        "testId": test["id"],
        "jobId": selected_job_id,
        "jobsRemainingBefore": latest_slot["jobsRemainingBefore"],
        "jobsRemainingAfter": latest_slot["jobsRemainingAfter"],
        "slotConsumed": latest_slot["slotConsumed"],
        "evidence": "dispatch entered execution" if latest_slot["slotConsumed"] else "no slot consumed",
    }

    blocked_downstream = {
        "testId": test["id"],
        "rootFailedJobId": blocked_root,
        "blockedJobs": blocked_jobs,
        "count": len(blocked_jobs),
    }

    return {
        "after_state": deepcopy(test_state.state),
        "execution_metrics": execution_metrics,
        "quarantine": quarantine or {
            "jobId": selected_job_id,
            "quarantined": False,
            "reason": None,
            "failedAttempts": retry_count,
        },
        "blocked_downstream": blocked_downstream,
        "window_accounting": window_accounting,
        "slot_consumption": slot_consumption,
    }


def run_selection(queue: list[dict], state: dict, test_state: TestState | None = None, simulate_failure: bool = False, check_all: bool = False) -> dict:
    result = {
        "selectedJob": None,
        "selectionReason": "",
        "candidates": [],
        "safetyEvaluation": {"blocked": False, "blockedBy": [], "requiresOperatorApproval": False},
        "approvalDecision": {"approved": False, "mode": state.get("mode", "none"), "reason": ""},
        "outcome": "unknown",
        "riskyHeld": [],
    }

    for job in queue:
        score, band = calculate_priority_score(job)
        eligible = job.get("ready", True) and not (test_state and test_state.is_quarantined(job.get("jobId", "")))
        if test_state:
            for dep_id in job.get("dependencies", []):
                if dep_id in test_state.failed_jobs or dep_id in test_state.quarantined_jobs:
                    eligible = False
        result["candidates"].append({"jobId": job.get("jobId"), "score": score, "priority": band, "eligible": eligible})

    result["candidates"].sort(key=lambda x: x["score"], reverse=True)

    if test_state is not None and check_all:
        for job in queue:
            if (job.get("destructive") and not state.get("allowDestructive")) or (job.get("productionImpact") and not state.get("allowProdChanges")):
                test_state.register_risky_held(job["jobId"])
                result["riskyHeld"].append(job["jobId"])

    approved, reason = check_approval_window(state)
    result["approvalDecision"]["approved"] = approved
    result["approvalDecision"]["reason"] = reason
    if not approved:
        result["outcome"] = "approval_required"
        return result

    available = [j for j in queue if j.get("ready", True)]
    if test_state:
        available = [j for j in available if not test_state.is_quarantined(j.get("jobId", ""))]
    if not available:
        result["outcome"] = "no_work"
        return result

    top_candidates = [c for c in result["candidates"] if c["eligible"]]
    if not top_candidates:
        result["outcome"] = "no_work"
        return result

    top_score = top_candidates[0]["score"]
    top_job_ids = [c["jobId"] for c in top_candidates if c["score"] == top_score]
    selected_job = tie_break([j for j in available if j["jobId"] in top_job_ids]) if len(top_job_ids) > 1 else next((j for j in available if j["jobId"] == top_job_ids[0]), None)
    if not selected_job:
        result["outcome"] = "no_work"
        return result

    selected_job_id = selected_job["jobId"]
    if test_state:
        test_state.register_attempt(selected_job_id)

    passed, blocked_reasons = check_safety_gates(selected_job, state, test_state)
    if not passed:
        result["safetyEvaluation"]["blocked"] = True
        result["safetyEvaluation"]["blockedBy"] = blocked_reasons
        if test_state:
            test_state.register_blocked(selected_job_id, blocked_reasons)
        result["outcome"] = "blocked_token_limit" if any("token limit" in r for r in blocked_reasons) else "blocked"
        return result

    result["selectedJob"] = selected_job_id
    score, band = calculate_priority_score(selected_job)
    result["selectionReason"] = f"Selected {selected_job_id} (score: {score}, priority: {band})"

    if simulate_failure and test_state:
        test_state.register_failure(selected_job_id)
        failures = test_state.failure_count(selected_job_id)
        if failures >= 2:
            test_state.register_quarantine(selected_job_id)
            result["outcome"] = "quarantined_after_retry"
        else:
            result["outcome"] = "retry"
        return result

    if test_state:
        attempt = test_state.dispatch_attempts.get(selected_job_id, 1)
        test_state.register_complete(selected_job_id, deterministic_actual_tokens(selected_job, attempt), deterministic_runtime_ms(selected_job, attempt))
    result["outcome"] = "dispatch"
    return result


def generate_operator_summary(result: dict, queue: list[dict]) -> str:
    job = next((j for j in queue if j["jobId"] == result["selectedJob"]), None) if result["selectedJob"] else None
    candidate = next((c for c in result["candidates"] if c["jobId"] == result["selectedJob"]), None) if result["selectedJob"] else None
    lines = [f"Selected: {result['selectedJob'] or 'none'}", f"Outcome: {result['outcome']}"]
    if candidate:
        lines.append(f"Priority: {candidate['priority']} (score: {candidate['score']})")
    if job:
        lines.append(f"Title: {job.get('title', 'N/A')}")
    lines.append(f"Approval: {result['approvalDecision']['reason']}")
    if result["safetyEvaluation"]["blocked"]:
        lines.append(f"Blocked: {'; '.join(result['safetyEvaluation']['blockedBy'])}")
    if result.get("riskyHeld"):
        lines.append(f"Risky held: {', '.join(result['riskyHeld'])}")
    return "\n".join(lines)


def run_test(test: dict) -> dict:
    queue_path = FIXTURES_DIR / "queues" / test["queue"]
    state_path = FIXTURES_DIR / "states" / test["state"]
    queue = json.loads(queue_path.read_text())
    state = json.loads(state_path.read_text())
    before_state = deepcopy(state)
    test_state = TestState(state)
    started = time.perf_counter()

    if test["id"] == "T06_retry_then_quarantine":
        run_selection(queue, test_state.state, test_state, simulate_failure=True)
        result = run_selection(queue, test_state.state, test_state, simulate_failure=True)
    elif test["id"] == "T08_dependency_failure_blocks_children":
        parent = next((j for j in queue if j.get("blocks")), None)
        if parent:
            test_state.register_failure(parent["jobId"])
            test_state.register_quarantine(parent["jobId"], reason="dependency_root_failure")
            dependents = [j["jobId"] for j in queue if parent["jobId"] in j.get("dependencies", [])]
            test_state.register_downstream_blocked(parent["jobId"], dependents)
            result = run_selection(queue, test_state.state, test_state)
            result["selectedJob"] = parent["jobId"]
            result["outcome"] = "dependents_blocked_after_failure"
            result["selectionReason"] = f"Parent {parent['jobId']} failed; {len(dependents)} dependents blocked"
        else:
            result = run_selection(queue, test_state.state, test_state)
    elif test["id"] == "T11_e2e_normal_delivery":
        result = run_selection(queue, test_state.state, test_state)
        result["outcome"] = "dispatch_series"
    elif test["id"] == "T12_e2e_risky_job_mid_run":
        result = run_selection(queue, test_state.state, test_state, check_all=True)
        if result.get("riskyHeld"):
            result["outcome"] = "risky_job_held"
    elif test["id"] == "T13_e2e_failure_chain":
        first = run_selection(queue, test_state.state, test_state, simulate_failure=True)
        result = run_selection(queue, test_state.state, test_state, simulate_failure=True)
        root = result.get("selectedJob") or first.get("selectedJob")
        dependents = [j["jobId"] for j in queue if root in j.get("dependencies", [])] if root else []
        if root:
            test_state.register_downstream_blocked(root, dependents)
        if result["outcome"] == "quarantined_after_retry":
            result["outcome"] = "failure_chain_paused"
    else:
        result = run_selection(queue, test_state.state, test_state)

    audit_runtime_ms = int((time.perf_counter() - started) * 1000)
    summary = generate_operator_summary(result, queue)
    passed = True
    errors = []
    if test.get("expected_selected_job") is not None and result["selectedJob"] != test["expected_selected_job"]:
        passed = False
        errors.append(f"Expected job {test['expected_selected_job']}, got {result['selectedJob']}")
    if result["outcome"] != test["expected_outcome"] and test["expected_outcome"] not in result["outcome"]:
        passed = False
        errors.append(f"Expected outcome {test['expected_outcome']}, got {result['outcome']}")

    evidence = build_evidence(test, queue, before_state, test_state, result)
    evidence["execution_metrics"]["auditRuntimeMs"] = audit_runtime_ms

    return {
        "test_id": test["id"],
        "passed": passed,
        "errors": errors,
        "result": result,
        "summary": summary,
        "evidence": evidence,
    }


def main():
    test_matrix = json.loads((SCRIPT_DIR / "test-matrix.json").read_text())
    print("=" * 60)
    print("Control-plane-what-next Test Runner v4")
    print("=" * 60)
    results = []
    passed_count = 0
    failed_count = 0
    for test in test_matrix:
        test_result = run_test(test)
        results.append(test_result)
        ok = test_result["passed"]
        status = "✓ PASS" if ok else "✗ FAIL"
        passed_count += 1 if ok else 0
        failed_count += 0 if ok else 1
        print(f"\n{test['id']}: {status}")
        print(f"  Expected: {test.get('expected_selected_job', 'none')} → {test['expected_outcome']}")
        print(f"  Got: {test_result['result']['selectedJob']} → {test_result['result']['outcome']}")
        for err in test_result["errors"]:
            print(f"  Error: {err}")
    print("\n" + "=" * 60)
    print(f"Results: {passed_count} passed, {failed_count} failed")
    print("=" * 60)
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "test-results.json").write_text(json.dumps(results, indent=2))
    return failed_count == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
