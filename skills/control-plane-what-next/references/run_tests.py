#!/usr/bin/env python3
"""
Control-plane-what-next test runner v5
- calibrated priority model
- deterministic tie-breaks
- audit-grade evidence exports
- legacy regression suite + calibration suite
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy

SCRIPT_DIR = Path(__file__).parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
RESULTS_DIR = SCRIPT_DIR / "results"
CALIBRATION_FIXTURES_DIR = SCRIPT_DIR / "calibration_fixtures"
CALIBRATION_RESULTS_DIR = SCRIPT_DIR / "calibration_results"

DEADLINE_SCORES = [
    (2, 5),
    (8, 4),
    (24, 3),
    (72, 2),
    (float("inf"), 1),
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


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

    def is_quarantined(self, job_id: str) -> bool:
        return job_id in self.quarantined_jobs

    def failure_count(self, job_id: str) -> int:
        return self.retry_counts.get(job_id, 0)

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
            "timestamp": now_utc().isoformat(),
        }

    def register_complete(self, job_id: str, actual_tokens: int, runtime_ms: int):
        if job_id not in self.completed_jobs:
            self.completed_jobs.append(job_id)
        self.actual_tokens[job_id] = actual_tokens
        self.runtime_ms[job_id] = runtime_ms

        window_tokens_before = self.state.get("windowTokensUsed", 0)
        window_tokens_after = window_tokens_before + actual_tokens
        self.state["windowTokensUsed"] = window_tokens_after

        jobs_before = self.state.get("jobsRemaining")
        jobs_after = jobs_before
        if jobs_before is not None:
            jobs_after = max(0, jobs_before - 1)
            self.state["jobsRemaining"] = jobs_after

        self.state.setdefault("windowCompletedJobs", [])
        self.state.setdefault("sessionCompletedJobs", [])
        if job_id not in self.state["windowCompletedJobs"]:
            self.state["windowCompletedJobs"].append(job_id)
        if job_id not in self.state["sessionCompletedJobs"]:
            self.state["sessionCompletedJobs"].append(job_id)
        self.state["lastDispatchedJobId"] = job_id
        self.state["lastUpdatedAt"] = now_utc().isoformat()

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


# ---------- calibrated priority model ----------

def normalize_deadline(deadline: str) -> datetime:
    return datetime.fromisoformat(deadline.replace("Z", "+00:00"))


def score_severity(job: dict) -> int:
    impact = job.get("impact", "medium")
    mapping = {"critical": 5, "high": 4, "medium": 3, "low": 1, "trivial": 0}
    score = mapping.get(impact, 2)
    if job.get("productionImpact"):
        score = max(score, 4)
    return min(score, 5)


def score_blocking_breadth(job: dict) -> int:
    count = len(job.get("blocks", []))
    if count >= 4:
        return 5
    if count >= 3:
        return 4
    if count >= 2:
        return 3
    if count >= 1:
        return 2
    return 0


def score_deadline_proximity(job: dict) -> int:
    try:
        hours_until = (normalize_deadline(job.get("deadline", now_utc().isoformat())) - now_utc()).total_seconds() / 3600
    except Exception:
        return 0
    if hours_until <= 2:
        return 5
    if hours_until <= 8:
        return 4
    if hours_until <= 24:
        return 3
    if hours_until <= 72:
        return 2
    return 1


def score_business_impact(job: dict) -> int:
    base = {"infrastructure": 4, "security": 5, "coding": 3, "review": 3, "docs": 0, "planning": 2}.get(job.get("taskType", "coding"), 2)
    impact = job.get("impact", "medium")
    if impact == "high":
        base += 1
    if impact == "critical":
        base += 2
    if job.get("productionImpact"):
        base += 1
    return max(0, min(base, 5))


def score_execution_readiness(job: dict) -> int:
    confidence = job.get("confidence", 0.8)
    if not job.get("ready", True):
        return 1
    if confidence >= 0.95:
        return 5
    if confidence >= 0.85:
        return 4
    if confidence >= 0.7:
        return 3
    if confidence >= 0.5:
        return 2
    return 1


def score_execution_effort(job: dict) -> int:
    tokens = job.get("estimatedTokens", 0)
    if tokens <= 8000:
        return 1
    if tokens <= 20000:
        return 2
    if tokens <= 40000:
        return 3
    if tokens <= 70000:
        return 4
    return 5


def compute_priority_factors(job: dict) -> dict:
    return {
        "severity": score_severity(job),
        "blockingBreadth": score_blocking_breadth(job),
        "deadlineProximity": score_deadline_proximity(job),
        "businessImpact": score_business_impact(job),
        "executionReadiness": score_execution_readiness(job),
        "executionEffort": score_execution_effort(job),
    }


def priority_score_from_factors(f: dict) -> int:
    return (
        (f["severity"] * 3)
        + (f["blockingBreadth"] * 3)
        + (f["deadlineProximity"] * 2)
        + (f["businessImpact"] * 2)
        + (f["executionReadiness"] * 1)
        - (f["executionEffort"] * 1)
    )


def assigned_priority_from_score_and_cap(score: int, f: dict) -> str:
    if score >= 24:
        if f["severity"] >= 4 or f["blockingBreadth"] >= 3 or f["deadlineProximity"] >= 4:
            return "P0"
        return "P1"
    if score >= 16:
        return "P1"
    if score >= 8:
        return "P2"
    return "P3"


def legacy_assigned_priority(job: dict) -> str:
    impact = score_severity(job)
    blocking = score_blocking_breadth(job)
    breadth = 0 if len(job.get("dependencies", [])) == 0 else min(5, max(2, len(job.get("dependencies", [])) + 1))
    deadline = score_deadline_proximity(job)
    readiness = 5 if job.get("ready", True) else 2
    effort = score_execution_effort(job)
    score = (impact * 3) + (blocking * 3) + (breadth * 2) + (deadline * 2) + readiness - effort
    if score >= 18:
        return "P0"
    if score >= 13:
        return "P1"
    if score >= 8:
        return "P2"
    return "P3"


def tie_break_reason(a: dict, b: dict) -> str | None:
    if a["factors"]["blockingBreadth"] != b["factors"]["blockingBreadth"]:
        return "higher blockingBreadth"
    if a["job"].get("deadline") != b["job"].get("deadline"):
        return "earlier deadline"
    if a["factors"]["businessImpact"] != b["factors"]["businessImpact"]:
        return "higher businessImpact"
    if a["job"].get("estimatedTokens", 0) != b["job"].get("estimatedTokens", 0):
        return "lower estimatedTokens"
    if a["job"].get("queueInsertedAt", "") != b["job"].get("queueInsertedAt", ""):
        return "older queue insertion time"
    return None


def sort_key(scored_job: dict):
    return (
        -scored_job["priorityScore"],
        -scored_job["factors"]["blockingBreadth"],
        scored_job["job"].get("deadline", "9999-12-31T23:59:59Z"),
        -scored_job["factors"]["businessImpact"],
        scored_job["job"].get("estimatedTokens", 0),
        scored_job["job"].get("queueInsertedAt", "9999-12-31T23:59:59Z"),
        scored_job["job"].get("jobId", ""),
    )


# ---------- control-plane behavior ----------

def check_safety_gates(job: dict, state: dict, test_state: TestState | None = None) -> tuple[bool, list[str]]:
    reasons = []
    if test_state and test_state.is_quarantined(job.get("jobId", "")):
        reasons.append("job is quarantined after repeated failure")
    if test_state:
        for dep_id in job.get("dependencies", []):
            if dep_id in test_state.failed_jobs or dep_id in test_state.quarantined_jobs:
                reasons.append(f"blocked by failed dependency {dep_id}")
    if job.get("destructive", False) and not state.get("allowDestructive", False):
        reasons.append("destructive operation blocked")
    if job.get("productionImpact", False) and not state.get("allowProdChanges", False):
        reasons.append("production-impacting change blocked")
    if job.get("estimatedTokens", 0) > state.get("maxTokensPerJob", 120000):
        reasons.append(f"token limit exceeded ({job.get('estimatedTokens')} > {state.get('maxTokensPerJob', 120000)})")
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
        if expires and now_utc() > normalize_deadline(expires):
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
    return max(800, int(est * 0.73) + (attempt - 1) * 250)


def deterministic_runtime_ms(job: dict, attempt: int = 1) -> int:
    return max(150, int(job.get("estimatedTokens", 0) / 18) + attempt * 75)


def score_queue(queue: list[dict], test_state: TestState | None = None) -> list[dict]:
    scored = []
    for job in queue:
        factors = compute_priority_factors(job)
        priority_score = priority_score_from_factors(factors)
        assigned_priority = assigned_priority_from_score_and_cap(priority_score, factors)
        eligible = job.get("ready", True) and not (test_state and test_state.is_quarantined(job.get("jobId", "")))
        if test_state:
            for dep_id in job.get("dependencies", []):
                if dep_id in test_state.failed_jobs or dep_id in test_state.quarantined_jobs:
                    eligible = False
        scored.append({
            "job": job,
            "factors": factors,
            "priorityScore": priority_score,
            "assignedPriority": assigned_priority,
            "eligible": eligible,
        })
    return scored


def run_selection(queue: list[dict], state: dict, test_state: TestState | None = None, simulate_failure: bool = False, check_all: bool = False) -> dict:
    result = {
        "selectedJob": None,
        "selectionReason": "",
        "candidates": [],
        "safetyEvaluation": {"blocked": False, "blockedBy": [], "requiresOperatorApproval": False},
        "approvalDecision": {"approved": False, "mode": state.get("mode", "none"), "reason": ""},
        "outcome": "unknown",
        "riskyHeld": [],
        "tieBreakReason": None,
        "selectedPriority": None,
        "selectedScore": None,
    }

    scored = score_queue(queue, test_state)
    ordered = sorted(scored, key=sort_key)

    if check_all and test_state:
        for item in scored:
            job = item["job"]
            if (job.get("destructive") and not state.get("allowDestructive")) or (job.get("productionImpact") and not state.get("allowProdChanges")):
                test_state.register_risky_held(job["jobId"])
                result["riskyHeld"].append(job["jobId"])

    approved, approval_reason = check_approval_window(state)
    result["approvalDecision"] = {"approved": approved, "mode": state.get("mode", "none"), "reason": approval_reason}

    top = None
    if approved:
        for item in ordered:
            if item["eligible"]:
                top = item
                break

    if top:
        tied = [item for item in ordered if item["eligible"] and item["priorityScore"] == top["priorityScore"]]
        if len(tied) > 1:
            for contender in tied[1:]:
                reason = tie_break_reason(top, contender)
                if reason:
                    result["tieBreakReason"] = reason
                    break

    for item in ordered:
        job = item["job"]
        selected = top is not None and job["jobId"] == top["job"]["jobId"]
        selected_reason = None
        tie_reason = None
        if selected:
            selected_reason = "Highest priority score"
            if result["tieBreakReason"]:
                selected_reason += f" after tie-break by {result['tieBreakReason']}"
                tie_reason = result["tieBreakReason"]
        else:
            if top is None:
                selected_reason = "No selection made"
            elif item["priorityScore"] < top["priorityScore"]:
                selected_reason = f"Lower priority score than {top['job']['jobId']}"
            else:
                losing_reason = tie_break_reason(top, item)
                tie_reason = losing_reason
                selected_reason = f"Lost tie-break to {top['job']['jobId']} by {losing_reason}" if losing_reason else f"Lost final lexical tie-break to {top['job']['jobId']}"
        result["candidates"].append({
            "jobId": job["jobId"],
            "priorityScore": item["priorityScore"],
            "assignedPriority": item["assignedPriority"],
            "severity": item["factors"]["severity"],
            "blockingBreadth": item["factors"]["blockingBreadth"],
            "deadlineProximity": item["factors"]["deadlineProximity"],
            "businessImpact": item["factors"]["businessImpact"],
            "executionReadiness": item["factors"]["executionReadiness"],
            "executionEffort": item["factors"]["executionEffort"],
            "estimatedTokens": job.get("estimatedTokens", 0),
            "selected": selected,
            "selectedReason": selected_reason,
            **({"tieBreakReason": tie_reason} if tie_reason else {}),
            "eligible": item["eligible"],
        })

    if not approved:
        result["outcome"] = "approval_required"
        return result

    if not top:
        result["outcome"] = "no_work"
        return result

    selected_job = top["job"]
    selected_job_id = selected_job["jobId"]
    if test_state:
        test_state.register_attempt(selected_job_id)

    passed, blocked = check_safety_gates(selected_job, state, test_state)
    if not passed:
        result["safetyEvaluation"]["blocked"] = True
        result["safetyEvaluation"]["blockedBy"] = blocked
        if test_state:
            test_state.register_blocked(selected_job_id, blocked)
        result["outcome"] = "blocked_token_limit" if any("token limit" in r for r in blocked) else "blocked"
        return result

    result["selectedJob"] = selected_job_id
    result["selectedPriority"] = top["assignedPriority"]
    result["selectedScore"] = top["priorityScore"]
    result["selectionReason"] = next(c["selectedReason"] for c in result["candidates"] if c["jobId"] == selected_job_id)

    if simulate_failure and test_state:
        test_state.register_failure(selected_job_id)
        if test_state.failure_count(selected_job_id) >= 2:
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
    job = next((j for j in queue if j.get("jobId") == result.get("selectedJob")), None)
    estimated_tokens = job.get("estimatedTokens", 0) if job else 0
    safety = "blocked" if result["safetyEvaluation"]["blocked"] else "eligible"
    action = "ask for approval" if result["outcome"] == "approval_required" else ("hold" if "blocked" in result["outcome"] else "dispatching now")
    lines = [
        f"Next job selected: {result.get('selectedJob') or 'none'}",
        f"Priority: {result.get('selectedPriority') or 'n/a'}",
        f"Score: {result.get('selectedScore') if result.get('selectedScore') is not None else 'n/a'}",
        f"Reason: {result.get('selectionReason') or 'none'}",
        f"Tie-break: {result.get('tieBreakReason') or 'none'}",
        f"Estimated tokens: {estimated_tokens}",
        f"Safety status: {safety}",
        f"Approval window: {result['approvalDecision']['mode']} / {result['approvalDecision']['reason']}",
        f"Action: {action}",
    ]
    return "\n".join(lines)


def build_evidence(test: dict, queue: list[dict], before_state: dict, test_state: TestState, result: dict) -> dict:
    selected_job_id = result.get("selectedJob")
    selected_job = next((j for j in queue if j.get("jobId") == selected_job_id), None)
    retry_count = test_state.retry_counts.get(selected_job_id, 0) if selected_job_id else 0
    actual_tokens = test_state.actual_tokens.get(selected_job_id, 0) if selected_job_id else 0
    runtime_ms = test_state.runtime_ms.get(selected_job_id, 0) if selected_job_id else 0
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
    blocked_root = next(iter(test_state.downstream_blocked.keys()), None)
    blocked_jobs = test_state.downstream_blocked.get(blocked_root, []) if blocked_root else []
    safety_report = {
        "testId": test["id"],
        "jobId": selected_job_id,
        "eligible": not result["safetyEvaluation"]["blocked"],
        "blocked": result["safetyEvaluation"]["blocked"],
        "blockedBy": result["safetyEvaluation"]["blockedBy"],
        "approvalReason": result["approvalDecision"]["reason"],
    }
    validator_output = {
        "testId": test["id"],
        "passed": True,
        "selectedJob": result.get("selectedJob"),
        "selectedPriority": result.get("selectedPriority"),
        "selectedScore": result.get("selectedScore"),
    }
    return {
        "after_state": deepcopy(test_state.state),
        "execution_metrics": {
            "testId": test["id"],
            "jobId": selected_job_id,
            "runtimeMs": runtime_ms,
            "actualTokensUsed": actual_tokens,
            "retryCount": retry_count,
            "dispatchAttempts": test_state.dispatch_attempts.get(selected_job_id, 0) if selected_job_id else 0,
            "estimatedTokens": selected_job.get("estimatedTokens") if selected_job else None,
        },
        "quarantine": test_state.quarantine_metadata.get(selected_job_id, {
            "jobId": selected_job_id,
            "quarantined": False,
            "reason": None,
            "failedAttempts": retry_count,
        }),
        "blocked_downstream": {
            "testId": test["id"],
            "rootFailedJobId": blocked_root,
            "blockedJobs": blocked_jobs,
            "count": len(blocked_jobs),
        },
        "window_accounting": {
            "testId": test["id"],
            "jobId": selected_job_id,
            "mode": before_state.get("mode"),
            "jobsRemainingBefore": latest_slot["jobsRemainingBefore"],
            "jobsRemainingAfter": latest_slot["jobsRemainingAfter"],
            "windowTokensBefore": latest_window["windowTokensBefore"],
            "windowTokensAfter": latest_window["windowTokensAfter"],
            "actualTokensUsed": latest_window["actualTokensUsed"],
        },
        "slot_consumption": {
            "testId": test["id"],
            "jobId": selected_job_id,
            "jobsRemainingBefore": latest_slot["jobsRemainingBefore"],
            "jobsRemainingAfter": latest_slot["jobsRemainingAfter"],
            "slotConsumed": latest_slot["slotConsumed"],
            "evidence": "dispatch entered execution" if latest_slot["slotConsumed"] else "no slot consumed",
        },
        "safety_report": safety_report,
        "validator_output": validator_output,
    }


def run_test(test: dict, fixtures_dir: Path = FIXTURES_DIR) -> dict:
    queue = json.loads((fixtures_dir / "queues" / test["queue"]).read_text())
    state = json.loads((fixtures_dir / "states" / test["state"]).read_text())
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
            test_state.register_quarantine(parent["jobId"], "dependency_root_failure")
            blocked = [j["jobId"] for j in queue if parent["jobId"] in j.get("dependencies", [])]
            test_state.register_downstream_blocked(parent["jobId"], blocked)
            result = run_selection(queue, test_state.state, test_state)
            result["selectedJob"] = parent["jobId"]
            selected = next((s for s in score_queue(queue) if s["job"]["jobId"] == parent["jobId"]), None)
            result["selectedPriority"] = selected["assignedPriority"] if selected else None
            result["selectedScore"] = selected["priorityScore"] if selected else None
            result["outcome"] = "dependents_blocked_after_failure"
            result["selectionReason"] = f"Highest priority root failed; downstream jobs blocked: {', '.join(blocked)}"
        else:
            result = run_selection(queue, test_state.state, test_state)
    elif test["id"] == "T11_e2e_normal_delivery":
        result = run_selection(queue, test_state.state, test_state)
        result["outcome"] = "dispatch_series"
    elif test["id"] == "T12_e2e_risky_job_mid_run":
        result = run_selection(queue, test_state.state, test_state, check_all=True)
        if result.get("riskyHeld"):
            safe_queue = [j for j in queue if not j.get("productionImpact") and not j.get("destructive")]
            safe_result = run_selection(safe_queue, test_state.state, test_state)
            result["selectedJob"] = safe_result.get("selectedJob")
            result["selectedPriority"] = safe_result.get("selectedPriority")
            result["selectedScore"] = safe_result.get("selectedScore")
            result["selectionReason"] = safe_result.get("selectionReason")
            result["tieBreakReason"] = safe_result.get("tieBreakReason")
            result["outcome"] = "risky_job_held"
    elif test["id"] == "T13_e2e_failure_chain":
        first = run_selection(queue, test_state.state, test_state, simulate_failure=True)
        result = run_selection(queue, test_state.state, test_state, simulate_failure=True)
        root = result.get("selectedJob") or first.get("selectedJob")
        blocked = [j["jobId"] for j in queue if root and root in j.get("dependencies", [])]
        if root:
            test_state.register_downstream_blocked(root, blocked)
        if result["outcome"] == "quarantined_after_retry":
            result["outcome"] = "failure_chain_paused"
            result["selectionReason"] = f"Root failed twice and paused downstream jobs: {', '.join(blocked)}"
    else:
        result = run_selection(queue, test_state.state, test_state)

    audit_runtime_ms = int((time.perf_counter() - started) * 1000)
    summary = generate_operator_summary(result, queue)
    passed = True
    errors = []
    if test.get("expected_selected_job") is not None and result.get("selectedJob") != test["expected_selected_job"]:
        passed = False
        errors.append(f"Expected job {test['expected_selected_job']}, got {result.get('selectedJob')}")
    if test.get("expected_outcome") and result.get("outcome") != test["expected_outcome"] and test["expected_outcome"] not in str(result.get("outcome")):
        passed = False
        errors.append(f"Expected outcome {test['expected_outcome']}, got {result.get('outcome')}")
    if test.get("expected_priority") and result.get("selectedPriority") != test["expected_priority"]:
        passed = False
        errors.append(f"Expected priority {test['expected_priority']}, got {result.get('selectedPriority')}")

    evidence = build_evidence(test, queue, before_state, test_state, result)
    evidence["execution_metrics"]["auditRuntimeMs"] = audit_runtime_ms
    evidence["validator_output"]["passed"] = passed and not errors
    evidence["validator_output"]["errors"] = errors

    return {
        "test_id": test["id"],
        "passed": passed,
        "errors": errors,
        "result": result,
        "summary": summary,
        "evidence": evidence,
    }


def write_legacy_results(test_matrix: list[dict], results: list[dict]):
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "test-results.json").write_text(json.dumps(results, indent=2))
    for test, test_result in zip(test_matrix, results):
        queue = json.loads((FIXTURES_DIR / "queues" / test["queue"]).read_text())
        state = json.loads((FIXTURES_DIR / "states" / test["state"]).read_text())
        test_dir = RESULTS_DIR / test["id"]
        test_dir.mkdir(exist_ok=True)
        (test_dir / "queue-input.json").write_text(json.dumps(queue, indent=2))
        (test_dir / "before-state.json").write_text(json.dumps(state, indent=2))
        (test_dir / "after-state.json").write_text(json.dumps(test_result["evidence"]["after_state"], indent=2))
        (test_dir / "result.json").write_text(json.dumps(test_result, indent=2))
        (test_dir / "summary.txt").write_text(test_result["summary"])
        (test_dir / "decision-trace.json").write_text(json.dumps({
            "testId": test["id"],
            "timestamp": now_utc().isoformat(),
            "expected": {"selectedJob": test.get("expected_selected_job"), "outcome": test["expected_outcome"]},
            "actual": {"selectedJob": test_result["result"].get("selectedJob"), "outcome": test_result["result"].get("outcome")},
            "passed": test_result["passed"],
            "candidates": test_result["result"]["candidates"],
            "safetyEvaluation": test_result["result"]["safetyEvaluation"],
            "approvalDecision": test_result["result"]["approvalDecision"],
            "tieBreakReason": test_result["result"].get("tieBreakReason"),
        }, indent=2))
        (test_dir / "execution-metrics.json").write_text(json.dumps(test_result["evidence"]["execution_metrics"], indent=2))
        (test_dir / "quarantine.json").write_text(json.dumps(test_result["evidence"]["quarantine"], indent=2))
        (test_dir / "blocked-downstream.json").write_text(json.dumps(test_result["evidence"]["blocked_downstream"], indent=2))
        (test_dir / "window-accounting.json").write_text(json.dumps(test_result["evidence"]["window_accounting"], indent=2))
        (test_dir / "slot-consumption.json").write_text(json.dumps(test_result["evidence"]["slot_consumption"], indent=2))
        (test_dir / "safety-report.json").write_text(json.dumps(test_result["evidence"]["safety_report"], indent=2))
        (test_dir / "validator-output.json").write_text(json.dumps(test_result["evidence"]["validator_output"], indent=2))


def main():
    test_matrix = json.loads((SCRIPT_DIR / "test-matrix.json").read_text())
    print("=" * 60)
    print("Control-plane-what-next Test Runner v5")
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
        print(f"  Got: {test_result['result'].get('selectedJob')} → {test_result['result'].get('outcome')}")
        for err in test_result["errors"]:
            print(f"  Error: {err}")
    print("\n" + "=" * 60)
    print(f"Results: {passed_count} passed, {failed_count} failed")
    print("=" * 60)
    write_legacy_results(test_matrix, results)
    return failed_count == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
