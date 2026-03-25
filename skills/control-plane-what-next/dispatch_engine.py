#!/usr/bin/env python3
"""
Dispatch Engine for control-plane-what-next v2

Handles:
- Eligible-set scheduling
- Dependency-aware dispatch
- Lock conflict detection
- Pool capacity enforcement
- Parallel approval semantics
- Restart recovery
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy
from typing import Any, Optional
from uuid import uuid4

from state_manager import (
    STATE_FILE,
    now_utc,
    create_default_state,
    load_state,
    save_state,
    get_active_jobs,
    get_active_jobs_by_pool,
    get_pool_capacity,
    get_all_pool_capacities,
    get_active_locks,
    get_locks_by_job,
    add_active_job,
    remove_active_job,
    add_lock,
    remove_locks_for_job,
    update_window_tokens,
    decrement_jobs_remaining,
    add_completed_job,
    add_failed_job,
    add_quarantined_job,
    is_quarantined,
    is_failed,
    get_window_status,
    check_token_budget,
    reconcile_state,
    DEFAULT_POOLS,
    DEFAULT_POLICY,
)


# Import priority scoring from run_tests.py
SCRIPT_DIR = Path(__file__).parent


def normalize_deadline(deadline: str) -> datetime:
    """Parse ISO deadline to datetime."""
    return datetime.fromisoformat(deadline.replace("Z", "+00:00"))


def score_severity(job: dict) -> int:
    """Score job severity (0-5)."""
    impact = job.get("impact", "medium")
    mapping = {"critical": 5, "high": 4, "medium": 3, "low": 1, "trivial": 0}
    score = mapping.get(impact, 2)
    if job.get("productionImpact"):
        score = max(score, 4)
    return min(score, 5)


def score_blocking_breadth(job: dict) -> int:
    """Score blocking breadth (0-5)."""
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
    """Score deadline urgency (0-5)."""
    try:
        hours_until = (normalize_deadline(job.get("deadline", "9999-12-31T23:59:59Z")) - now_utc()).total_seconds() / 3600
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
    """Score business impact (0-5)."""
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
    """Score execution readiness (0-5)."""
    confidence = job.get("confidence", job.get("executionReadiness", 0.8))
    if isinstance(confidence, float):
        if confidence >= 0.95:
            return 5
        if confidence >= 0.85:
            return 4
        if confidence >= 0.7:
            return 3
        if confidence >= 0.5:
            return 2
        return 1
    return 3


def score_execution_effort(job: dict) -> int:
    """Score execution effort (0-5, subtractive)."""
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
    """Compute all priority factors for a job."""
    return {
        "severity": score_severity(job),
        "blockingBreadth": score_blocking_breadth(job),
        "deadlineProximity": score_deadline_proximity(job),
        "businessImpact": score_business_impact(job),
        "executionReadiness": score_execution_readiness(job),
        "executionEffort": score_execution_effort(job),
    }


def priority_score_from_factors(f: dict) -> int:
    """Compute weighted priority score from factors."""
    return (
        (f["severity"] * 3)
        + (f["blockingBreadth"] * 3)
        + (f["deadlineProximity"] * 2)
        + (f["businessImpact"] * 2)
        + (f["executionReadiness"] * 1)
        - (f["executionEffort"] * 1)
    )


def assigned_priority_from_score(score: int, f: dict) -> str:
    """Assign priority band from score, applying P0 cap."""
    if score >= 24:
        # P0 cap: must have severity>=4, blockingBreadth>=3, or deadlineProximity>=4
        if f["severity"] >= 4 or f["blockingBreadth"] >= 3 or f["deadlineProximity"] >= 4:
            return "P0"
        return "P1"
    if score >= 16:
        return "P1"
    if score >= 8:
        return "P2"
    return "P3"


def sort_key(scored_job: dict):
    """Sort key for priority ranking."""
    job = scored_job["job"]
    return (
        -scored_job["priorityScore"],
        -scored_job["factors"]["blockingBreadth"],
        job.get("deadline", "9999-12-31T23:59:59Z"),
        -scored_job["factors"]["businessImpact"],
        job.get("estimatedTokens", 0),
        job.get("queueInsertedAt", "9999-12-31T23:59:59Z"),
        job.get("jobId", ""),
    )


def tie_break_reason(a: dict, b: dict) -> Optional[str]:
    """Determine tie-break reason between two jobs."""
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


def get_pool_for_task_type(job: dict, state: dict) -> str:
    """Determine which pool a job should use based on task type."""
    task_type = job.get("taskType", "coding")
    pools = state.get("pools", DEFAULT_POOLS)
    
    for pool_name, pool_config in pools.items():
        if task_type in pool_config.get("taskTypes", []):
            return pool_name
    
    # Default to first pool or 'coder'
    return "coder"


def get_model_for_job(job: dict, state: dict) -> str:
    """Get the model to use for a job based on its pool."""
    pool_name = job.get("pool", get_pool_for_task_type(job, state))
    pools = state.get("pools", DEFAULT_POOLS)
    pool_config = pools.get(pool_name, {})
    models = pool_config.get("models", ["qwen3-coder-next:cloud"])
    return models[0] if models else "qwen3-coder-next:cloud"


def check_dependencies_satisfied(job: dict, state: dict, pipeline_items: list[dict]) -> tuple[bool, list[dict]]:
    """
    Check if all dependencies are satisfied.
    
    Returns (satisfied, unmet_dependencies).
    """
    depends_on = job.get("dependsOn", [])
    if not depends_on:
        return True, []
    
    unmet = []
    completed = state.get("history", {}).get("sessionCompletedJobs", [])
    quarantined = state.get("history", {}).get("quarantinedJobs", [])
    failed = state.get("history", {}).get("failedJobs", [])
    active_jobs = {j["jobId"] for j in get_active_jobs(state)}
    
    for dep_id in depends_on:
        # Check if completed
        if dep_id in completed:
            continue
        
        # Check if failed/quarantined
        if dep_id in quarantined:
            unmet.append({"jobId": dep_id, "status": "quarantined", "blocking": True})
            continue
        if dep_id in failed:
            unmet.append({"jobId": dep_id, "status": "failed", "blocking": True})
            continue
        
        # Check if running
        if dep_id in active_jobs:
            unmet.append({"jobId": dep_id, "status": "running", "blocking": True})
            continue
        
        # Check pipeline status
        dep_job = next((j for j in pipeline_items if j.get("jobId") == dep_id), None)
        if dep_job:
            status = dep_job.get("status", "pending")
            if status not in ["completed", "succeeded"]:
                unmet.append({"jobId": dep_id, "status": status, "blocking": True})
        else:
            # Dependency not found - assume pending
            unmet.append({"jobId": dep_id, "status": "pending", "blocking": True})
    
    return len(unmet) == 0, unmet


def check_lock_conflicts(job: dict, state: dict) -> tuple[bool, list[dict]]:
    """
    Check if job has lock conflicts with active jobs.
    
    Returns (no_conflicts, conflicting_locks).
    """
    shared_resources = job.get("sharedResources", [])
    if not shared_resources:
        return True, []
    
    active_locks = get_active_locks(state)
    conflicts = []
    
    for resource in shared_resources:
        resource_type = resource.get("type", "file")
        resource_value = resource.get("value", "")
        resource_mode = resource.get("mode", "exclusive")
        
        for lock in active_locks:
            if lock.get("type") == resource_type and lock.get("value") == resource_value:
                # Found a potential conflict
                lock_mode = lock.get("mode", "exclusive")
                
                # Shared mode allows multiple readers
                if resource_mode == "shared" and lock_mode == "shared":
                    continue
                
                conflicts.append({
                    "lockId": lock.get("lockId"),
                    "type": resource_type,
                    "value": resource_value,
                    "heldByJobId": lock.get("jobId"),
                    "mode": lock_mode,
                    "requestedMode": resource_mode,
                })
    
    return len(conflicts) == 0, conflicts


def check_pool_capacity(pool_name: str, state: dict) -> tuple[bool, dict]:
    """
    Check if pool has capacity for a new dispatch.
    
    Returns (has_capacity, capacity_info).
    """
    capacity = get_pool_capacity(state, pool_name)
    has_capacity = capacity["available"] > 0
    return has_capacity, capacity


def check_safety_gates(job: dict, state: dict, pipeline_items: list[dict] = None) -> tuple[bool, list[str], dict]:
    """
    Check all safety gates for a job.
    
    Returns (passed, blocking_reasons, safety_report).
    """
    reasons = []
    report = {
        "destructive": True,
        "productionImpact": True,
        "tokenBudget": True,
        "metadata": True,
        "confidence": True,
        "dependencies": True,
        "locks": True,
        "quarantine": True,
    }
    
    # Check quarantine
    if is_quarantined(state, job.get("jobId", "")):
        reasons.append("job is quarantined after repeated failure")
        report["quarantine"] = False
    
    # Check failed status
    if is_failed(state, job.get("jobId", "")):
        reasons.append("job has previously failed")
        report["quarantine"] = False
    
    # Check destructive
    if job.get("destructive") and not state.get("policy", {}).get("allowDestructive", False):
        reasons.append("destructive operation blocked")
        report["destructive"] = False
    
    # Check production impact
    if job.get("productionImpact") and not state.get("policy", {}).get("allowProdChanges", False):
        reasons.append("production-impacting change blocked")
        report["productionImpact"] = False
    
    # Check token budget
    estimated_tokens = job.get("estimatedTokens", 0)
    token_ok, token_reason = check_token_budget(state, estimated_tokens)
    if not token_ok:
        reasons.append(token_reason)
        report["tokenBudget"] = False
    
    # Check metadata
    if not job.get("taskType"):
        reasons.append("missing task category")
        report["metadata"] = False
    if job.get("estimatedTokens", 0) <= 0:
        reasons.append("missing token estimate")
        report["metadata"] = False
    
    # Check confidence
    confidence = job.get("confidence", job.get("executionReadiness", 0.8))
    if isinstance(confidence, float) and confidence < 0.5:
        reasons.append("confidence below threshold")
        report["confidence"] = False
    
    # Check dependencies
    if pipeline_items:
        deps_ok, unmet = check_dependencies_satisfied(job, state, pipeline_items)
        if not deps_ok:
            for dep in unmet:
                reasons.append(f"dependency {dep['jobId']} not satisfied ({dep['status']})")
            report["dependencies"] = False
    
    # Check locks
    locks_ok, conflicts = check_lock_conflicts(job, state)
    if not locks_ok:
        for conflict in conflicts:
            reasons.append(f"lock conflict on {conflict['type']} {conflict['value']} (held by {conflict['heldByJobId']})")
        report["locks"] = False
    
    return len(reasons) == 0, reasons, report


def compute_eligible_set(
    pipeline_items: list[dict],
    state: dict,
    check_capacity: bool = True,
) -> tuple[list[dict], list[dict]]:
    """
    Compute eligible set: jobs ready for dispatch.
    
    Returns (eligible_jobs, blocked_jobs_with_reasons).
    """
    eligible = []
    blocked = []
    
    # Get completed/failed/quarantined jobs
    completed = set(state.get("history", {}).get("sessionCompletedJobs", []))
    quarantined = set(state.get("history", {}).get("quarantinedJobs", []))
    failed = set(state.get("history", {}).get("failedJobs", []))
    active_job_ids = {j["jobId"] for j in get_active_jobs(state)}
    
    for job in pipeline_items:
        job_id = job.get("jobId", "")
        
        # Skip if already processed
        if job_id in completed:
            continue
        if job_id in quarantined:
            blocked.append({
                "job": job,
                "reasons": ["job is quarantined"],
                "eligible": False,
            })
            continue
        if job_id in active_job_ids:
            continue  # Already running
        
        # Score the job
        factors = compute_priority_factors(job)
        score = priority_score_from_factors(factors)
        priority = assigned_priority_from_score(score, factors)
        
        # Check dependencies
        deps_ok, unmet = check_dependencies_satisfied(job, state, pipeline_items)
        
        # Check locks
        locks_ok, conflicts = check_lock_conflicts(job, state)
        
        # Check pool capacity
        pool_name = get_pool_for_task_type(job, state)
        pool_has_capacity, pool_info = check_pool_capacity(pool_name, state) if check_capacity else (True, {})
        
        # Check safety gates
        safe, reasons, _ = check_safety_gates(job, state, pipeline_items)
        
        # Check approval window
        window_status, _ = get_window_status(state)
        window_ok = window_status == "active"
        
        # Collect blocking reasons
        blocking_reasons = []
        if not deps_ok:
            for dep in unmet:
                blocking_reasons.append(f"Dependency {dep['jobId']} not satisfied ({dep['status']})")
        if not locks_ok:
            for conflict in conflicts:
                blocking_reasons.append(f"Lock conflict on {conflict['type']} {conflict['value']}")
        if not pool_has_capacity:
            blocking_reasons.append(f"Pool '{pool_name}' at capacity ({pool_info['currentActive']}/{pool_info['maxConcurrent']} active)")
        if not safe:
            blocking_reasons.extend(reasons)
        if not window_ok:
            blocking_reasons.append(f"Approval window {window_status}")
        
        # Determine eligibility
        is_eligible = len(blocking_reasons) == 0
        
        scored_job = {
            "job": job,
            "factors": factors,
            "priorityScore": score,
            "assignedPriority": priority,
            "pool": pool_name,
            "model": get_model_for_job({**job, "pool": pool_name}, state),
            "eligible": is_eligible,
            "blockingReasons": blocking_reasons,
            "dependencyInfo": unmet,
            "lockConflicts": conflicts,
            "poolCapacity": pool_info if pool_info else {},
        }
        
        if is_eligible:
            eligible.append(scored_job)
        else:
            blocked.append(scored_job)
    
    # Sort eligible by priority
    eligible.sort(key=sort_key)
    
    return eligible, blocked


def select_jobs_for_parallel_dispatch(
    eligible: list[dict],
    state: dict,
    max_dispatches: Optional[int] = None,
) -> list[dict]:
    """
    Select jobs for parallel dispatch respecting pool capacity and approval limits.
    
    Returns list of selected jobs.
    """
    if not eligible:
        return []
    
    # Get global limit
    if max_dispatches is None:
        max_dispatches = state.get("policy", {}).get("maxParallelDispatches", 4)
    
    # Get approval window jobs remaining
    aw = state.get("approvalWindow", {})
    if aw.get("mode") == "jobs":
        jobs_remaining = aw.get("jobsRemaining", 0)
        if jobs_remaining <= 0:
            return []
        max_dispatches = min(max_dispatches, jobs_remaining)
    
    # Track pool capacity
    pool_usage = {}
    for pool_name in state.get("pools", DEFAULT_POOLS).keys():
        capacity = get_pool_capacity(state, pool_name)
        pool_usage[pool_name] = {
            "maxConcurrent": capacity["maxConcurrent"],
            "currentActive": capacity["currentActive"],
            "available": capacity["available"],
        }
    
    # Select jobs respecting capacity
    selected = []
    for scored_job in eligible:
        if len(selected) >= max_dispatches:
            break
        
        pool_name = scored_job.get("pool", "coder")
        
        # Check pool capacity
        pool_info = pool_usage.get(pool_name, {"available": 0})
        if pool_info["available"] <= 0:
            scored_job["skipReason"] = f"Pool {pool_name} at capacity"
            continue
        
        # Select this job
        selected.append(scored_job)
        
        # Update pool tracking
        pool_info["currentActive"] += 1
        pool_info["available"] -= 1
    
    return selected


def acquire_locks(job: dict, state: dict) -> tuple[dict, list[dict]]:
    """
    Acquire locks for a job's shared resources.
    
    Returns (updated_state, acquired_locks).
    """
    shared_resources = job.get("sharedResources", [])
    if not shared_resources:
        return state, []
    
    acquired = []
    job_id = job.get("jobId", "unknown")
    
    for resource in shared_resources:
        lock_id = f"lock-{uuid4().hex[:8]}"
        lock = {
            "lockId": lock_id,
            "jobId": job_id,
            "type": resource.get("type", "file"),
            "value": resource.get("value", ""),
            "mode": resource.get("mode", "exclusive"),
            "acquiredAt": now_utc().isoformat(),
        }
        state = add_lock(state, lock)
        acquired.append(lock)
    
    return state, acquired


def release_locks(job_id: str, state: dict) -> dict:
    """Release all locks held by a job."""
    return remove_locks_for_job(state, job_id)


def dispatch_job(job: dict, state: dict, approval_slot_consumed: bool = True) -> tuple[dict, dict]:
    """
    Dispatch a single job.
    
    Returns (updated_state, dispatch_record).
    """
    job_id = job.get("jobId", "unknown")
    pool_name = get_pool_for_task_type(job, state)
    model = get_model_for_job({**job, "pool": pool_name}, state)
    
    # Create active job record
    active_job = {
        "jobId": job_id,
        "pool": pool_name,
        "model": model,
        "taskType": job.get("taskType", "coding"),
        "status": "running",
        "startedAt": now_utc().isoformat(),
        "approvalSlotConsumed": approval_slot_consumed,
        "estimatedTokens": job.get("estimatedTokens", 0),
        "actualTokens": None,
        "retryCount": 0,
        "locksHeld": [],
    }
    
    # Acquire locks
    state, acquired_locks = acquire_locks(job, state)
    active_job["locksHeld"] = [lock["lockId"] for lock in acquired_locks]
    
    # Add to active jobs
    state = add_active_job(state, active_job)
    
    # Decrement jobs remaining if jobs-mode window
    if approval_slot_consumed and state.get("approvalWindow", {}).get("mode") == "jobs":
        state = decrement_jobs_remaining(state)
    
    # Create dispatch record for logging
    dispatch_record = {
        "jobId": job_id,
        "pool": pool_name,
        "model": model,
        "status": "dispatched",
        "startedAt": active_job["startedAt"],
        "locksAcquired": acquired_locks,
        "approvalSlotConsumed": approval_slot_consumed,
    }
    
    return state, dispatch_record


def dispatch_parallel(
    jobs: list[dict],
    state: dict,
    max_dispatches: Optional[int] = None,
) -> tuple[dict, list[dict], list[dict]]:
    """
    Dispatch multiple jobs in parallel.
    
    Returns (updated_state, dispatch_records, blocked_jobs).
    """
    if not jobs:
        return state, [], []
    
    dispatch_records = []
    blocked = []
    
    # Compute eligible set
    eligible, blocked_from_eligible = compute_eligible_set(jobs, state)
    blocked.extend(blocked_from_eligible)
    
    # Select jobs for dispatch
    selected = select_jobs_for_parallel_dispatch(eligible, state, max_dispatches)
    
    if not selected:
        return state, [], blocked
    
    # Dispatch each selected job
    for scored_job in selected:
        job = scored_job["job"]
        
        # Check capacity again (may have changed)
        pool_name = scored_job.get("pool", "coder")
        has_capacity, _ = check_pool_capacity(pool_name, state)
        
        if not has_capacity:
            scored_job["skipReason"] = f"Pool {pool_name} at capacity"
            blocked.append(scored_job)
            continue
        
        # Check locks again
        locks_ok, conflicts = check_lock_conflicts(job, state)
        if not locks_ok:
            scored_job["skipReason"] = "Lock conflict"
            blocked.append(scored_job)
            continue
        
        # Dispatch the job
        state, record = dispatch_job(job, state)
        dispatch_records.append(record)
    
    return state, dispatch_records, blocked


def complete_job(
    job_id: str,
    state: dict,
    result: str = "success",
    actual_tokens: int = None,
    runtime_ms: int = None,
) -> tuple[dict, dict]:
    """
    Mark a job as completed and release resources.
    
    Returns (updated_state, completion_record).
    """
    # Find the active job
    active_jobs = get_active_jobs(state)
    job = next((j for j in active_jobs if j.get("jobId") == job_id), None)
    
    if not job:
        # Job not in active dispatches
        return state, {"jobId": job_id, "status": "not_found"}
    
    # Release locks
    state = release_locks(job_id, state)
    
    # Remove from active jobs
    state = remove_active_job(state, job_id)
    
    # Update token usage
    pool = job.get("pool", "coder")
    tokens = actual_tokens or job.get("estimatedTokens", 0)
    state = update_window_tokens(state, pool, tokens)
    
    # Add to appropriate history
    if result == "success":
        state = add_completed_job(state, job_id)
    elif result == "failure":
        state = add_failed_job(state, job_id)
    elif result == "quarantined":
        state = add_quarantined_job(state, job_id)
    
    # Create completion record
    completion_record = {
        "jobId": job_id,
        "pool": pool,
        "model": job.get("model"),
        "result": result,
        "actualTokens": tokens,
        "runtimeMs": runtime_ms,
        "startedAt": job.get("startedAt"),
        "completedAt": now_utc().isoformat(),
        "approvalSlotConsumed": job.get("approvalSlotConsumed", True),
        "retryCount": job.get("retryCount", 0),
    }
    
    # Calculate efficiency
    estimated = job.get("estimatedTokens", 0)
    if estimated > 0 and tokens > 0:
        completion_record["efficiency"] = round(tokens / estimated, 2)
    
    return state, completion_record


def generate_decision_trace(
    cycle_id: str,
    scored_jobs: list[dict],
    selected_jobs: list[dict],
    blocked_jobs: list[dict],
    state: dict,
) -> dict:
    """
    Generate decision trace for logging.
    
    Returns decision trace in schema format.
    """
    traces = []
    timestamp = now_utc().isoformat()
    
    for rank, scored_job in enumerate(scored_jobs, 1):
        job = scored_job["job"]
        is_selected = any(s["job"]["jobId"] == job["jobId"] for s in selected_jobs)
        
        trace = {
            "cycleId": cycle_id,
            "jobId": job.get("jobId"),
            "priorityScore": scored_job.get("priorityScore"),
            "assignedPriority": scored_job.get("assignedPriority"),
            "pool": scored_job.get("pool"),
            "model": scored_job.get("model"),
            "taskType": job.get("taskType"),
            "scoringDimensions": scored_job.get("factors"),
            "dependenciesSatisfied": len(scored_job.get("dependencyInfo", [])) == 0,
            "lockConflict": len(scored_job.get("lockConflicts", [])) > 0,
            "lockConflicts": scored_job.get("lockConflicts"),
            "poolCapacityAvailable": scored_job.get("poolCapacity", {}).get("available", 0) > 0,
            "poolCapacity": scored_job.get("poolCapacity"),
            "selected": is_selected,
            "selectedReason": None if is_selected else scored_job.get("skipReason", "Not selected"),
            "rank": rank,
            "eligibleForDispatch": scored_job.get("eligible", False),
            "timestamp": timestamp,
        }
        
        if is_selected:
            trace["selectedReason"] = "Highest priority eligible job"
        
        traces.append(trace)
    
    return {
        "cycleId": cycle_id,
        "timestamp": timestamp,
        "traces": traces,
        "summary": {
            "totalJobs": len(scored_jobs),
            "selectedCount": len(selected_jobs),
            "blockedCount": len(blocked_jobs),
        }
    }


def generate_operator_summary(
    state: dict,
    selected_jobs: list[dict],
    blocked_jobs: list[dict],
    dispatch_records: list[dict],
) -> dict:
    """
    Generate operator-facing summary.
    
    Returns summary in operator-summary-schema format.
    """
    cycle_id = f"cycle-{now_utc().isoformat()}"
    aw = state.get("approvalWindow", {})
    
    # Get pool utilizations
    pool_util = get_all_pool_capacities(state)
    
    # Get active dispatches
    active_dispatches = []
    for job in get_active_jobs(state):
        active_dispatches.append({
            "jobId": job.get("jobId"),
            "pool": job.get("pool"),
            "model": job.get("model"),
            "status": job.get("status"),
            "startedAt": job.get("startedAt"),
            "estimatedTokens": job.get("estimatedTokens"),
        })
    
    # Get active locks
    active_locks = []
    for lock in get_active_locks(state):
        active_locks.append({
            "lockId": lock.get("lockId"),
            "type": lock.get("type"),
            "value": lock.get("value"),
            "heldByJobId": lock.get("jobId"),
            "heldByPool": next(
                (j.get("pool") for j in get_active_jobs(state) if j.get("jobId") == lock.get("jobId")),
                "unknown"
            ),
            "acquiredAt": lock.get("acquiredAt"),
        })
    
    # Format selected job
    selected_job = None
    if selected_jobs:
        sj = selected_jobs[0]
        selected_job = {
            "jobId": sj["job"].get("jobId"),
            "title": sj["job"].get("title"),
            "priority": sj.get("assignedPriority"),
            "priorityScore": sj.get("priorityScore"),
            "model": sj.get("model"),
            "pool": sj.get("pool"),
            "estimatedTokens": sj["job"].get("estimatedTokens"),
            "reason": "Highest priority score" if sj.get("eligible") else "Not eligible",
        }
    
    # Format blocked jobs
    blocked = []
    for bj in blocked_jobs[:10]:  # Limit to 10 for readability
        blocked.append({
            "jobId": bj["job"].get("jobId"),
            "priority": bj.get("assignedPriority"),
            "priorityScore": bj.get("priorityScore"),
            "reasons": bj.get("blockingReasons", []),
            "waitingOn": [d["jobId"] for d in bj.get("dependencyInfo", [])],
        })
    
    # Determine action
    if dispatch_records:
        action = "dispatching"
        message = f"Dispatching {len(dispatch_records)} job(s): {', '.join(r['jobId'] for r in dispatch_records)}"
    elif blocked_jobs and not selected_jobs:
        action = "holding_for_capacity" if any("capacity" in str(b.get("skipReason", "")) for b in blocked_jobs) else "holding_for_approval"
        if blocked:
            message = f"Jobs blocked: {', '.join(b['jobId'] for b in blocked[:3])}"
        else:
            message = "No eligible jobs"
    else:
        action = "no_work"
        message = "No eligible work available"
    
    return {
        "cycleId": cycle_id,
        "timestamp": now_utc().isoformat(),
        "approvalWindow": {
            "mode": aw.get("mode"),
            "status": aw.get("status"),
            "remaining": aw.get("jobsRemaining"),
            "tokensUsed": state.get("tokenGovernance", {}).get("windowTokensUsed", 0),
            "tokensRemaining": state.get("tokenGovernance", {}).get("maxTokensPerWindow", 2000000) - state.get("tokenGovernance", {}).get("windowTokensUsed", 0),
        },
        "selectedJob": selected_job,
        "activeDispatches": active_dispatches,
        "blockedJobs": blocked,
        "poolUtilisation": pool_util,
        "activeLocks": active_locks,
        "action": action,
        "message": message,
    }


if __name__ == "__main__":
    # Quick test
    print("Testing dispatch_engine...")
    
    state = create_default_state()
    state["approvalWindow"] = {
        "mode": "jobs",
        "startedAt": now_utc().isoformat(),
        "followNewJobs": True,
        "windowCompletedJobs": [],
        "windowTokenUsage": 0,
        "status": "active",
        "maxJobs": 5,
        "jobsRemaining": 5,
    }
    
    # Test pipeline items
    pipeline = [
        {
            "jobId": "CP-100",
            "title": "Test job 1",
            "taskType": "coding",
            "dependsOn": [],
            "blocks": ["CP-101"],
            "sharedResources": [],
            "estimatedTokens": 30000,
            "deadline": "2026-03-26T00:00:00Z",
            "productionImpact": False,
            "destructive": False,
            "confidence": 0.9,
            "impact": "high",
        },
        {
            "jobId": "CP-101",
            "title": "Test job 2 (depends on CP-100)",
            "taskType": "coding",
            "dependsOn": ["CP-100"],
            "blocks": [],
            "sharedResources": [],
            "estimatedTokens": 20000,
            "deadline": "2026-03-27T00:00:00Z",
            "productionImpact": False,
            "destructive": False,
            "confidence": 0.85,
            "impact": "medium",
        },
    ]
    
    # Compute eligible set
    eligible, blocked = compute_eligible_set(pipeline, state)
    print(f"Eligible jobs: {[e['job']['jobId'] for e in eligible]}")
    print(f"Blocked jobs: {[b['job']['jobId'] for b in blocked]}")
    
    # Test dispatch
    state, records, blocked_after = dispatch_parallel(pipeline, state)
    print(f"Dispatched: {[r['jobId'] for r in records]}")
    
    # Check active jobs
    active = get_active_jobs(state)
    print(f"Active jobs: {[j['jobId'] for j in active]}")
    
    # Test pool capacity
    capacity = get_pool_capacity(state, "coder")
    print(f"Coder pool capacity: {capacity}")
    
    print("\ndispatch_engine tests passed!")