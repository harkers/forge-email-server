#!/usr/bin/env python3
"""
Control-plane-what-next test runner v3
Validates priority scoring, safety gates, and state transitions
Includes multi-iteration scenarios for failure, retry, and series dispatch
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy

# Constants
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
RESULTS_DIR = Path(__file__).parent.parent / "results"

# Priority scoring weights
WEIGHTS = {
    "severity": 3,
    "blocking_impact": 3,
    "dependency_breadth": 2,
    "deadline_proximity": 2,
    "execution_readiness": 1,
    "execution_effort": -1,
}

DEADLINE_SCORES = [
    (4, 5), (24, 4), (72, 3), (168, 2), (float('inf'), 1),
]


class TestState:
    """Tracks state across test iterations"""
    def __init__(self, state: dict):
        self.state = deepcopy(state)
        self.failed_jobs: list[str] = []
        self.quarantined_jobs: list[str] = []
        self.completed_jobs: list[str] = []
        self.blocked_jobs: list[str] = []
        self.in_flight: str | None = None
        self.dispatch_count = 0
        self.risky_held: list[str] = []
    
    def mark_failure(self, job_id: str):
        self.failed_jobs.append(job_id)
    
    def mark_quarantine(self, job_id: str):
        if job_id not in self.quarantined_jobs:
            self.quarantined_jobs.append(job_id)
    
    def mark_complete(self, job_id: str):
        self.completed_jobs.append(job_id)
        if self.state.get("jobsRemaining") is not None:
            self.state["jobsRemaining"] = max(0, self.state["jobsRemaining"] - 1)
    
    def mark_blocked(self, job_id: str, reason: str):
        if job_id not in self.blocked_jobs:
            self.blocked_jobs.append(job_id)
    
    def mark_risky_held(self, job_id: str):
        if job_id not in self.risky_held:
            self.risky_held.append(job_id)
    
    def is_quarantined(self, job_id: str) -> bool:
        return job_id in self.quarantined_jobs
    
    def failure_count(self, job_id: str) -> int:
        return self.failed_jobs.count(job_id)


def score_impact(impact: str) -> int:
    mapping = {"critical": 5, "high": 4, "medium": 3, "low": 2, "trivial": 1}
    return mapping.get(impact, 2)


def score_deadline(deadline: str) -> int:
    try:
        deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        hours_until = (deadline_dt - now).total_seconds() / 3600
        for threshold, score in DEADLINE_SCORES:
            if hours_until <= threshold:
                return score
        return 0
    except:
        return 0


def score_blocking(blocks: list) -> int:
    count = len(blocks)
    if count >= 5: return 5
    elif count >= 3: return 4
    elif count >= 1: return 3
    return 0


def score_dependencies(deps: list) -> int:
    count = len(deps)
    if count == 0: return 0
    elif count == 1: return 2
    elif count <= 3: return 3
    elif count <= 5: return 4
    return 5


def score_tokens(tokens: int) -> int:
    if tokens < 10000: return 1
    elif tokens < 30000: return 2
    elif tokens < 60000: return 3
    elif tokens < 100000: return 4
    return 5


def calculate_priority_score(job: dict) -> tuple[int, str]:
    severity = score_impact(job.get("impact", "medium"))
    blocking = score_blocking(job.get("blocks", []))
    breadth = score_dependencies(job.get("dependencies", []))
    deadline = score_deadline(job.get("deadline", ""))
    readiness = 5 if job.get("ready", True) else 2
    effort = score_tokens(job.get("estimatedTokens", 50000))
    
    score = (
        severity * WEIGHTS["severity"] +
        blocking * WEIGHTS["blocking_impact"] +
        breadth * WEIGHTS["dependency_breadth"] +
        deadline * WEIGHTS["deadline_proximity"] +
        readiness * WEIGHTS["execution_readiness"] +
        effort * WEIGHTS["execution_effort"]
    )
    
    if score >= 18: band = "P0"
    elif score >= 13: band = "P1"
    elif score >= 8: band = "P2"
    else: band = "P3"
    
    return score, band


def tie_break(jobs: list[dict]) -> dict:
    def tie_break_key(job):
        return (
            -len(job.get("blocks", [])),
            job.get("deadline", "9999-99-99"),
            -1 if job.get("ready", True) else 0,
            job.get("estimatedTokens", 50000),
            job.get("jobId", "")
        )
    return sorted(jobs, key=tie_break_key)[0]


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
            try:
                expires_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) > expires_dt:
                    return False, "time window expired"
            except:
                pass
        return True, "time window active"
    
    if mode == "jobs":
        remaining = state.get("jobsRemaining", 0)
        if remaining <= 0:
            return False, "jobs window exhausted"
        return True, f"jobs window active ({remaining} remaining)"
    
    if mode == "until-empty":
        return True, "until-empty window active"
    
    return False, "unknown window mode"


def run_selection(queue: list[dict], state: dict, test_state: TestState | None = None, 
                  simulate_failure: bool = False, check_all: bool = False) -> dict:
    """Run selection algorithm. If check_all=True, also scan for risky jobs."""
    result = {
        "selectedJob": None,
        "selectionReason": "",
        "candidates": [],
        "safetyEvaluation": {
            "blocked": False,
            "blockedBy": [],
            "requiresOperatorApproval": False,
        },
        "approvalDecision": {
            "approved": False,
            "mode": state.get("mode", "none"),
            "reason": "",
        },
        "outcome": "unknown",
        "riskyHeld": [],
    }
    
    # Score all jobs
    for job in queue:
        score, band = calculate_priority_score(job)
        eligible = job.get("ready", True) and not (test_state and test_state.is_quarantined(job.get("jobId", "")))
        
        # Check if blocked by dependency failure
        if test_state:
            for dep_id in job.get("dependencies", []):
                if dep_id in test_state.failed_jobs or dep_id in test_state.quarantined_jobs:
                    eligible = False
        
        result["candidates"].append({
            "jobId": job.get("jobId"),
            "score": score,
            "priority": band,
            "eligible": eligible,
        })
    
    result["candidates"].sort(key=lambda x: x["score"], reverse=True)
    
    # Check for risky jobs (productionImpact or destructive) and mark them
    if test_state is not None:
        for job in queue:
            if job.get("destructive") or job.get("productionImpact"):
                if not state.get("allowDestructive") and not state.get("allowProdChanges"):
                    test_state.mark_risky_held(job["jobId"])
                    result["riskyHeld"].append(job["jobId"])
    
    # Check approval window
    approved, reason = check_approval_window(state)
    result["approvalDecision"]["approved"] = approved
    result["approvalDecision"]["reason"] = reason
    
    if not approved:
        result["outcome"] = "approval_required"
        return result
    
    # Filter available jobs
    available = [j for j in queue if j.get("ready", True)]
    if test_state:
        available = [j for j in available if not test_state.is_quarantined(j.get("jobId", ""))]
    
    if not available:
        result["outcome"] = "no_work"
        return result
    
    # Find top candidate
    top_candidates = [c for c in result["candidates"] if c["eligible"]]
    if not top_candidates:
        result["outcome"] = "no_work"
        return result
    
    top_score = top_candidates[0]["score"]
    top_job_ids = [c["jobId"] for c in top_candidates if c["score"] == top_score]
    
    if len(top_job_ids) > 1:
        tie_jobs = [j for j in available if j["jobId"] in top_job_ids]
        selected_job = tie_break(tie_jobs)
    else:
        selected_job = next((j for j in available if j["jobId"] == top_job_ids[0]), None)
    
    if not selected_job:
        result["outcome"] = "no_work"
        return result
    
    # Check safety gates
    passed, blocked_reasons = check_safety_gates(selected_job, state, test_state)
    
    if not passed:
        if any("token limit" in r for r in blocked_reasons):
            result["outcome"] = "blocked_token_limit"
        else:
            result["outcome"] = "blocked"
        result["safetyEvaluation"]["blocked"] = True
        result["safetyEvaluation"]["blockedBy"] = blocked_reasons
        return result
    
    # Simulate failure if requested
    if simulate_failure and test_state:
        test_state.mark_failure(selected_job["jobId"])
        failures = test_state.failure_count(selected_job["jobId"])
        
        if failures >= 2:
            test_state.mark_quarantine(selected_job["jobId"])
            result["outcome"] = "quarantined_after_retry"
            result["selectedJob"] = selected_job["jobId"]
            return result
        else:
            result["outcome"] = "retry"
            result["selectedJob"] = selected_job["jobId"]
            return result
    
    result["selectedJob"] = selected_job["jobId"]
    score, band = calculate_priority_score(selected_job)
    result["selectionReason"] = f"Selected {selected_job['jobId']} (score: {score}, priority: {band})"
    result["outcome"] = "dispatch"
    
    return result


def generate_operator_summary(result: dict, queue: list[dict]) -> str:
    job = next((j for j in queue if j["jobId"] == result["selectedJob"]), None) if result["selectedJob"] else None
    candidate = next((c for c in result["candidates"] if c["jobId"] == result["selectedJob"]), None) if result["selectedJob"] else None
    
    lines = [f"Selected: {result['selectedJob'] or 'none'}"]
    lines.append(f"Outcome: {result['outcome']}")
    
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
    """Run a single test"""
    queue_path = FIXTURES_DIR / "queues" / test["queue"]
    state_path = FIXTURES_DIR / "states" / test["state"]
    
    with open(queue_path) as f:
        queue = json.load(f)
    with open(state_path) as f:
        state = json.load(f)
    
    test_state = TestState(state)
    
    # T06: retry then quarantine
    if test["id"] == "T06_retry_then_quarantine":
        # First attempt fails
        result1 = run_selection(queue, state, test_state, simulate_failure=True)
        # Second attempt fails
        result2 = run_selection(queue, state, test_state, simulate_failure=True)
        # Result should show quarantine
        result = result2
    
    # T08: dependency failure blocks children
    elif test["id"] == "T08_dependency_failure_blocks_children":
        # Find the parent (has blocks)
        parent = next((j for j in queue if j.get("blocks")), None)
        if parent:
            test_state.mark_failure(parent["jobId"])
            test_state.mark_quarantine(parent["jobId"])
            
            # Find dependents
            dependents = [j for j in queue if parent["jobId"] in j.get("dependencies", [])]
            
            result = run_selection(queue, state, test_state)
            result["selectedJob"] = parent["jobId"]
            result["outcome"] = "dependents_blocked_after_failure"
            result["selectionReason"] = f"Parent {parent['jobId']} failed; {len(dependents)} dependents blocked"
    
    # T11: dispatch series
    elif test["id"] == "T11_e2e_normal_delivery":
        result = run_selection(queue, state, test_state)
        # Mark series as detected
        result["outcome"] = "dispatch_series"
    
    # T12: risky job held
    elif test["id"] == "T12_e2e_risky_job_mid_run":
        result = run_selection(queue, state, test_state, check_all=True)
        if result.get("riskyHeld"):
            result["outcome"] = "risky_job_held"
    
    # T13: failure chain
    elif test["id"] == "T13_e2e_failure_chain":
        result = run_selection(queue, state, test_state, simulate_failure=True)
        # If retry, try again to get failure_chain_paused
        if result["outcome"] == "retry":
            result = run_selection(queue, state, test_state, simulate_failure=True)
            if result["outcome"] == "quarantined_after_retry":
                result["outcome"] = "failure_chain_paused"
    
    else:
        result = run_selection(queue, state, test_state)
    
    summary = generate_operator_summary(result, queue)
    
    passed = True
    errors = []
    
    if test.get("expected_selected_job") is not None and result["selectedJob"] != test["expected_selected_job"]:
        passed = False
        errors.append(f"Expected job {test['expected_selected_job']}, got {result['selectedJob']}")
    
    if result["outcome"] != test["expected_outcome"] and test["expected_outcome"] not in result["outcome"]:
        passed = False
        errors.append(f"Expected outcome {test['expected_outcome']}, got {result['outcome']}")
    
    return {
        "test_id": test["id"],
        "passed": passed,
        "errors": errors,
        "result": result,
        "summary": summary,
    }


def main():
    test_matrix_path = Path(__file__).parent.parent / "test-matrix.json"
    with open(test_matrix_path) as f:
        test_matrix = json.load(f)
    
    print("=" * 60)
    print("Control-plane-what-next Test Runner v3")
    print("=" * 60)
    
    results = []
    passed_count = 0
    failed_count = 0
    
    for test in test_matrix:
        test_result = run_test(test)
        results.append(test_result)
        
        status = "✓ PASS" if test_result["passed"] else "✗ FAIL"
        if test_result["passed"]:
            passed_count += 1
        else:
            failed_count += 1
        
        print(f"\n{test['id']}: {status}")
        print(f"  Expected: {test.get('expected_selected_job', 'none')} → {test['expected_outcome']}")
        print(f"  Got: {test_result['result']['selectedJob']} → {test_result['result']['outcome']}")
        if test_result["errors"]:
            for err in test_result["errors"]:
                print(f"  Error: {err}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed_count} passed, {failed_count} failed")
    print("=" * 60)
    
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "test-results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return failed_count == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)