#!/usr/bin/env python3
"""
State Manager for control-plane-what-next v2

Handles:
- Loading state from disk
- v1 to v2 schema migration
- Saving state with validation
- State recovery on restart
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy
from typing import Any, Optional

# Default state file location
STATE_FILE = Path.home() / ".openclaw" / "workspace" / ".control-plane-what-next-state.json"

# Default pool configuration
DEFAULT_POOLS = {
    "coder": {
        "models": ["qwen3-coder-next:cloud"],
        "maxConcurrent": 2,
        "taskTypes": ["infrastructure", "coding"],
        "maxTokensPerJob": 500000,
        "allowDestructive": False,
        "allowProductionImpact": False,
    },
    "review": {
        "models": ["qwen3.5:397b-cloud"],
        "maxConcurrent": 1,
        "taskTypes": ["review"],
        "maxTokensPerJob": 300000,
        "allowDestructive": False,
        "allowProductionImpact": True,
    },
    "docs": {
        "models": ["llama3.1:8b", "qwen3:14b"],
        "maxConcurrent": 2,
        "taskTypes": ["docs"],
        "maxTokensPerJob": 100000,
        "allowDestructive": False,
        "allowProductionImpact": False,
    },
    "security": {
        "models": ["Codex"],
        "maxConcurrent": 1,
        "taskTypes": ["security"],
        "maxTokensPerJob": 200000,
        "allowDestructive": False,
        "allowProductionImpact": True,
    },
}

DEFAULT_POLICY = {
    "allowDestructive": False,
    "allowProdChanges": False,
    "maxTokensPerJob": 500000,
    "maxTokensPerWindow": 2000000,
    "autoRetryTransientFailures": True,
    "maxAutomaticRetries": 1,
    "maxParallelDispatches": 4,
}


def now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def create_default_state() -> dict:
    """Create a fresh v2 state with defaults."""
    now = now_utc().isoformat()
    return {
        "version": 2,
        "approvalWindow": {
            "mode": "none",
            "startedAt": None,
            "followNewJobs": False,
            "windowCompletedJobs": [],
            "windowTokenUsage": 0,
            "status": "idle",
        },
        "tokenGovernance": {
            "maxTokensPerJob": DEFAULT_POLICY["maxTokensPerJob"],
            "maxTokensPerWindow": DEFAULT_POLICY["maxTokensPerWindow"],
            "windowTokensUsed": 0,
            "perPoolTokensUsed": {},
        },
        "history": {
            "windowCompletedJobs": [],
            "sessionCompletedJobs": [],
            "quarantinedJobs": [],
            "failedJobs": [],
        },
        "dispatch": {
            "activeJobs": [],
            "lastDispatchedJobId": None,
            "lastDispatchAt": None,
        },
        "locks": {
            "activeLocks": [],
        },
        "pools": deepcopy(DEFAULT_POOLS),
        "policy": deepcopy(DEFAULT_POLICY),
    }


def migrate_v1_to_v2(v1_state: dict) -> dict:
    """
    Migrate v1 state schema to v2.
    
    Key changes:
    - activeWindow -> approvalWindow
    - current.inFlightJobId -> dispatch.activeJobs[0]
    - session.completedJobs -> history.sessionCompletedJobs
    - session.failedJobs -> history.failedJobs
    - session.quarantinedJobs -> history.quarantinedJobs
    - Add locks, pools, tokenGovernance
    """
    v2 = create_default_state()
    
    # Migrate approval window
    if "activeWindow" in v1_state:
        aw = v1_state["activeWindow"]
        v2["approvalWindow"] = {
            "mode": aw.get("mode", "none"),
            "startedAt": aw.get("startedAt"),
            "expiresAt": aw.get("expiresAt"),
            "maxJobs": aw.get("maxJobs"),
            "jobsRemaining": aw.get("jobsRemaining"),
            "followNewJobs": aw.get("followNewJobs", False),
            "approvedSnapshotJobIds": aw.get("approvedSnapshotJobIds", []),
            "windowCompletedJobs": aw.get("windowCompletedJobs", []),
            "windowTokenUsage": aw.get("windowTokenUsage", 0),
            "status": aw.get("status", "idle"),
        }
    
    # Migrate session -> history
    if "session" in v1_state:
        session = v1_state["session"]
        v2["history"]["sessionCompletedJobs"] = session.get("completedJobs", [])
        v2["history"]["failedJobs"] = session.get("failedJobs", [])
        v2["history"]["quarantinedJobs"] = session.get("quarantinedJobs", [])
        
        # Token usage from session
        if "tokenUsage" in session:
            v2["tokenGovernance"]["windowTokensUsed"] = session["tokenUsage"]
        if "byModel" in session:
            v2["tokenGovernance"]["perPoolTokensUsed"] = session["byModel"]
    
    # Migrate in-flight job
    if "current" in v1_state:
        current = v1_state["current"]
        in_flight = current.get("inFlightJobId")
        if in_flight:
            # Create an active job entry for the in-flight job
            v2["dispatch"]["activeJobs"] = [{
                "jobId": in_flight,
                "pool": "coder",  # Default pool
                "model": "unknown",
                "taskType": "unknown",
                "status": "running",
                "startedAt": current.get("lastEvaluatedAt") or now_utc().isoformat(),
                "approvalSlotConsumed": True,
                "estimatedTokens": 0,
                "retryCount": 0,
                "locksHeld": [],
            }]
        v2["dispatch"]["lastDispatchedJobId"] = current.get("lastDispatchedJobId")
        v2["dispatch"]["lastDispatchAt"] = current.get("lastEvaluatedAt")
    
    # Migrate policy
    if "policy" in v1_state:
        policy = v1_state["policy"]
        v2["policy"]["allowDestructive"] = policy.get("allowDestructive", False)
        v2["policy"]["allowProdChanges"] = policy.get("allowProdChanges", False)
        v2["policy"]["maxTokensPerJob"] = policy.get("maxTokensPerJob", 500000)
        v2["policy"]["maxTokensPerWindow"] = policy.get("maxTokensPerWindow", 2000000)
        v2["policy"]["autoRetryTransientFailures"] = policy.get("autoRetryTransientFailures", True)
        v2["policy"]["maxAutomaticRetries"] = policy.get("maxAutomaticRetries", 1)
        
        # Token governance
        v2["tokenGovernance"]["maxTokensPerJob"] = policy.get("maxTokensPerJob", 500000)
        v2["tokenGovernance"]["maxTokensPerWindow"] = policy.get("maxTokensPerWindow", 2000000)
    
    # Lifetime is not migrated - it's cumulative across sessions
    
    return v2


def validate_state_v2(state: dict) -> list[str]:
    """
    Validate v2 state structure.
    Returns list of validation errors (empty if valid).
    """
    errors = []
    
    # Required top-level fields
    required_fields = [
        "version", "approvalWindow", "tokenGovernance", "history",
        "dispatch", "locks", "pools", "policy"
    ]
    for field in required_fields:
        if field not in state:
            errors.append(f"Missing required field: {field}")
    
    if state.get("version") != 2:
        errors.append(f"Invalid version: expected 2, got {state.get('version')}")
    
    # Validate approvalWindow
    aw = state.get("approvalWindow", {})
    if aw.get("mode") not in ["time", "jobs", "until-empty", "none"]:
        errors.append(f"Invalid approvalWindow mode: {aw.get('mode')}")
    if aw.get("status") not in ["active", "expired", "exhausted", "revoked", "idle"]:
        errors.append(f"Invalid approvalWindow status: {aw.get('status')}")
    
    # Validate dispatch.activeJobs
    for job in state.get("dispatch", {}).get("activeJobs", []):
        if not job.get("jobId"):
            errors.append("Active job missing jobId")
        if job.get("status") not in ["queued_for_dispatch", "running", "succeeded", "failed", "quarantined", "cancelled"]:
            errors.append(f"Invalid active job status: {job.get('status')}")
    
    # Validate locks
    for lock in state.get("locks", {}).get("activeLocks", []):
        if not lock.get("lockId"):
            errors.append("Lock missing lockId")
        if not lock.get("jobId"):
            errors.append("Lock missing jobId")
        if lock.get("type") not in ["file", "service", "environment", "deployment"]:
            errors.append(f"Invalid lock type: {lock.get('type')}")
    
    return errors


def load_state(state_file: Path = STATE_FILE) -> dict:
    """
    Load state from disk.
    
    - If no file exists, create default v2 state
    - If v1 state, migrate to v2
    - If v2 state, validate and return
    """
    if not state_file.exists():
        return create_default_state()
    
    try:
        raw = state_file.read_text()
        state = json.loads(raw)
    except (json.JSONDecodeError, IOError) as e:
        # Return default state on read error
        return create_default_state()
    
    # Detect version and migrate if needed
    version = state.get("version", 1)
    
    if version == 1:
        # Migrate v1 to v2
        return migrate_v1_to_v2(state)
    elif version == 2:
        # Validate v2
        errors = validate_state_v2(state)
        if errors:
            # Return default state on validation error
            return create_default_state()
        return state
    else:
        # Unknown version, return default
        return create_default_state()


def save_state(state: dict, state_file: Path = STATE_FILE) -> bool:
    """
    Save state to disk.
    
    Returns True on success, False on failure.
    """
    # Ensure state is v2
    if state.get("version") != 2:
        return False
    
    # Validate before saving
    errors = validate_state_v2(state)
    if errors:
        return False
    
    # Ensure parent directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Atomic write: write to temp file, then rename
        temp_file = state_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(state, indent=2, sort_keys=True))
        temp_file.replace(state_file)
        return True
    except IOError:
        return False


def get_active_jobs(state: dict) -> list[dict]:
    """Get list of currently active jobs."""
    return state.get("dispatch", {}).get("activeJobs", [])


def get_active_jobs_by_pool(state: dict) -> dict[str, list[dict]]:
    """Get active jobs grouped by pool."""
    result = {}
    for job in get_active_jobs(state):
        pool = job.get("pool", "unknown")
        if pool not in result:
            result[pool] = []
        result[pool].append(job)
    return result


def get_pool_capacity(state: dict, pool_name: str) -> dict:
    """
    Get pool capacity information.
    
    Returns:
        {
            "pool": str,
            "maxConcurrent": int,
            "currentActive": int,
            "available": int,
            "utilizationPercent": float
        }
    """
    pool_config = state.get("pools", {}).get(pool_name, {})
    max_concurrent = pool_config.get("maxConcurrent", 1)
    
    active_by_pool = get_active_jobs_by_pool(state)
    current_active = len(active_by_pool.get(pool_name, []))
    available = max(0, max_concurrent - current_active)
    utilization = (current_active / max_concurrent * 100) if max_concurrent > 0 else 0
    
    return {
        "pool": pool_name,
        "maxConcurrent": max_concurrent,
        "currentActive": current_active,
        "available": available,
        "utilizationPercent": round(utilization, 1),
    }


def get_all_pool_capacities(state: dict) -> dict[str, dict]:
    """Get capacity info for all pools."""
    result = {}
    for pool_name in state.get("pools", {}).keys():
        result[pool_name] = get_pool_capacity(state, pool_name)
    return result


def get_active_locks(state: dict) -> list[dict]:
    """Get list of currently active locks."""
    return state.get("locks", {}).get("activeLocks", [])


def get_locks_by_job(state: dict, job_id: str) -> list[dict]:
    """Get locks held by a specific job."""
    return [lock for lock in get_active_locks(state) if lock.get("jobId") == job_id]


def add_active_job(state: dict, job: dict) -> dict:
    """Add a job to active dispatches."""
    state = deepcopy(state)
    if "dispatch" not in state:
        state["dispatch"] = {"activeJobs": [], "lastDispatchedJobId": None, "lastDispatchAt": None}
    if "activeJobs" not in state["dispatch"]:
        state["dispatch"]["activeJobs"] = []
    
    state["dispatch"]["activeJobs"].append(job)
    state["dispatch"]["lastDispatchedJobId"] = job.get("jobId")
    state["dispatch"]["lastDispatchAt"] = job.get("startedAt", now_utc().isoformat())
    
    return state


def remove_active_job(state: dict, job_id: str) -> dict:
    """Remove a job from active dispatches."""
    state = deepcopy(state)
    if "dispatch" not in state:
        return state
    
    state["dispatch"]["activeJobs"] = [
        job for job in state["dispatch"].get("activeJobs", [])
        if job.get("jobId") != job_id
    ]
    
    return state


def add_lock(state: dict, lock: dict) -> dict:
    """Add a lock to active locks."""
    state = deepcopy(state)
    if "locks" not in state:
        state["locks"] = {"activeLocks": []}
    if "activeLocks" not in state["locks"]:
        state["locks"]["activeLocks"] = []
    
    # Ensure lock has required fields
    lock.setdefault("acquiredAt", now_utc().isoformat())
    lock.setdefault("mode", "exclusive")
    
    state["locks"]["activeLocks"].append(lock)
    return state


def remove_locks_for_job(state: dict, job_id: str) -> dict:
    """Remove all locks held by a job."""
    state = deepcopy(state)
    if "locks" not in state:
        return state
    
    state["locks"]["activeLocks"] = [
        lock for lock in state["locks"].get("activeLocks", [])
        if lock.get("jobId") != job_id
    ]
    
    return state


def update_window_tokens(state: dict, pool_name: str, tokens_used: int) -> dict:
    """Update token usage for a pool."""
    state = deepcopy(state)
    
    # Update window tokens
    state["tokenGovernance"]["windowTokensUsed"] = (
        state["tokenGovernance"].get("windowTokensUsed", 0) + tokens_used
    )
    
    # Update pool-specific tokens
    per_pool = state["tokenGovernance"].get("perPoolTokensUsed", {})
    per_pool[pool_name] = per_pool.get(pool_name, 0) + tokens_used
    state["tokenGovernance"]["perPoolTokensUsed"] = per_pool
    
    return state


def decrement_jobs_remaining(state: dict) -> dict:
    """Decrement jobs remaining in jobs-mode window."""
    state = deepcopy(state)
    
    if state["approvalWindow"].get("mode") == "jobs":
        remaining = state["approvalWindow"].get("jobsRemaining", 0)
        if remaining > 0:
            state["approvalWindow"]["jobsRemaining"] = remaining - 1
    
    return state


def add_completed_job(state: dict, job_id: str) -> dict:
    """Add a job to completed history."""
    state = deepcopy(state)
    
    if job_id not in state.get("history", {}).get("windowCompletedJobs", []):
        if "history" not in state:
            state["history"] = {"windowCompletedJobs": [], "sessionCompletedJobs": [], "quarantinedJobs": [], "failedJobs": []}
        state["history"]["windowCompletedJobs"].append(job_id)
    
    if job_id not in state.get("history", {}).get("sessionCompletedJobs", []):
        state["history"]["sessionCompletedJobs"].append(job_id)
    
    return state


def add_failed_job(state: dict, job_id: str) -> dict:
    """Add a job to failed history."""
    state = deepcopy(state)
    
    if "history" not in state:
        state["history"] = {"windowCompletedJobs": [], "sessionCompletedJobs": [], "quarantinedJobs": [], "failedJobs": []}
    
    if job_id not in state["history"].get("failedJobs", []):
        state["history"]["failedJobs"].append(job_id)
    
    return state


def add_quarantined_job(state: dict, job_id: str) -> dict:
    """Add a job to quarantine."""
    state = deepcopy(state)
    
    if "history" not in state:
        state["history"] = {"windowCompletedJobs": [], "sessionCompletedJobs": [], "quarantinedJobs": [], "failedJobs": []}
    
    if job_id not in state["history"].get("quarantinedJobs", []):
        state["history"]["quarantinedJobs"].append(job_id)
    
    return state


def is_quarantined(state: dict, job_id: str) -> bool:
    """Check if a job is quarantined."""
    return job_id in state.get("history", {}).get("quarantinedJobs", [])


def is_failed(state: dict, job_id: str) -> bool:
    """Check if a job has failed."""
    return job_id in state.get("history", {}).get("failedJobs", [])


def get_window_status(state: dict) -> tuple[str, str]:
    """
    Check approval window status.
    
    Returns (status, reason) tuple.
    - status: 'active', 'expired', 'exhausted', 'revoked', 'idle'
    - reason: Human-readable explanation
    """
    aw = state.get("approvalWindow", {})
    mode = aw.get("mode", "none")
    
    if mode == "none":
        return "idle", "no approval window"
    
    status = aw.get("status", "idle")
    
    if status in ["expired", "exhausted", "revoked"]:
        return status, f"window {status}"
    
    if mode == "time":
        expires = aw.get("expiresAt")
        if expires:
            try:
                expires_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                if now_utc() > expires_dt:
                    return "expired", "time window expired"
            except (ValueError, TypeError):
                pass
        return "active", "time window active"
    
    if mode == "jobs":
        remaining = aw.get("jobsRemaining", 0)
        if remaining <= 0:
            return "exhausted", "jobs window exhausted"
        return "active", f"jobs window active ({remaining} remaining)"
    
    if mode == "until-empty":
        return "active", "until-empty window active"
    
    return status, f"window status: {status}"


def check_token_budget(state: dict, estimated_tokens: int) -> tuple[bool, str]:
    """
    Check if estimated tokens fit within budget.
    
    Returns (ok, reason) tuple.
    """
    tg = state.get("tokenGovernance", {})
    
    # Check window budget
    window_used = tg.get("windowTokensUsed", 0)
    window_max = tg.get("maxTokensPerWindow", 2000000)
    if window_used + estimated_tokens > window_max:
        return False, f"window token budget exceeded ({window_used + estimated_tokens} > {window_max})"
    
    # Check per-job budget
    job_max = tg.get("maxTokensPerJob", 500000)
    if estimated_tokens > job_max:
        return False, f"per-job token limit exceeded ({estimated_tokens} > {job_max})"
    
    return True, "within budget"


def reconcile_state(state: dict, actual_running_jobs: list[str] | None = None) -> dict:
    """
    Reconcile state on restart.
    
    - Remove active jobs that are no longer running
    - Re-acquire locks for still-running jobs
    - Update status appropriately
    """
    state = deepcopy(state)
    
    if actual_running_jobs is None:
        actual_running_jobs = []
    
    # Find orphaned jobs (in state but not actually running)
    active_jobs = get_active_jobs(state)
    orphaned_job_ids = [
        job["jobId"] for job in active_jobs
        if job.get("jobId") not in actual_running_jobs
    ]
    
    # Remove orphaned jobs from active
    state["dispatch"]["activeJobs"] = [
        job for job in active_jobs
        if job.get("jobId") in actual_running_jobs
    ]
    
    # Remove locks for orphaned jobs
    state["locks"]["activeLocks"] = [
        lock for lock in state.get("locks", {}).get("activeLocks", [])
        if lock.get("jobId") not in orphaned_job_ids
    ]
    
    # Add orphaned jobs to failed list
    for job_id in orphaned_job_ids:
        state = add_failed_job(state, job_id)
    
    return state


if __name__ == "__main__":
    # Quick test
    print("Testing state_manager...")
    
    # Create default state
    state = create_default_state()
    print(f"Created default v2 state with version: {state['version']}")
    
    # Test migration
    v1_state = {
        "version": 1,
        "activeWindow": {
            "mode": "jobs",
            "startedAt": "2026-03-25T10:00:00Z",
            "maxJobs": 5,
            "jobsRemaining": 3,
            "followNewJobs": True,
            "windowCompletedJobs": ["CP-100"],
            "windowTokenUsage": 50000,
            "status": "active",
        },
        "session": {
            "startedAt": "2026-03-25T10:00:00Z",
            "completedJobs": ["CP-100"],
            "failedJobs": [],
            "quarantinedJobs": [],
            "tokenUsage": 50000,
        },
        "current": {
            "lastEvaluatedAt": "2026-03-25T10:05:00Z",
            "lastDispatchedJobId": "CP-101",
            "inFlightJobId": "CP-101",
        },
        "policy": {
            "allowDestructive": False,
            "allowProdChanges": False,
            "maxTokensPerJob": 500000,
            "maxTokensPerWindow": 2000000,
        },
    }
    
    v2_state = migrate_v1_to_v2(v1_state)
    print(f"Migrated v1 state to v2: {v2_state['version']}")
    print(f"Active jobs after migration: {len(v2_state['dispatch']['activeJobs'])}")
    
    # Test pool capacity
    capacity = get_pool_capacity(state, "coder")
    print(f"Coder pool capacity: {capacity}")
    
    # Test save/load
    saved = save_state(state, Path("/tmp/test-state.json"))
    print(f"Save state: {saved}")
    
    loaded = load_state(Path("/tmp/test-state.json"))
    print(f"Load state version: {loaded['version']}")
    
    print("\nstate_manager tests passed!")