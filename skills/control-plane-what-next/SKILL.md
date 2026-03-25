---
name: control-plane-what-next
description: "Determine the next priority work item after control-plane completes a task. Query Forge Pipeline for pending items, apply deterministic priority scoring, validate against safety gates and approval windows, and dispatch or hold accordingly. Use when control-plane finishes work, when user asks 'what's next', or when setting auto-approve windows."
---

# Control Plane: What Next (v3)

Continuously determine the highest-ranked eligible item in Forge Pipeline, validate against policy and approval rules, select an execution model, and either dispatch or request renewed operator approval.

## Core Responsibilities

1. Query Forge Pipeline for pending items
2. Normalize task metadata
3. Calculate deterministic priority score
4. Apply tie-break rules when scores are equal
5. Validate chosen task against safety gates
6. Validate current approval window
7. Select execution model and token budget
8. Dispatch task if allowed
9. Record outcome and update state
10. Report decision in standard operator format

## Trigger Conditions

- After a task completes
- When operator asks "what's next?"
- When a new approval window is granted
- After a blocked or quarantined item is resolved
- On demand as part of control-plane status check

## Priority Scoring Model

Each eligible task receives a calibrated weighted score:

```
priorityScore =
  (severity * 3) +
  (blockingBreadth * 3) +
  (deadlineProximity * 2) +
  (businessImpact * 2) +
  (executionReadiness * 1) -
  (executionEffort * 1)
```

### Scoring Dimensions

| Dimension | Range | Description |
|-----------|-------|-------------|
| Severity | 0-5 | Seriousness if not handled |
| Blocking Breadth | 0-5 | Breadth of downstream work blocked |
| Deadline Proximity | 0-5 | Time urgency |
| Business Impact | 0-5 | Operational/business significance |
| Execution Readiness | 0-5 | Well-specified and ready |
| Execution Effort | 0-5 | Cost (subtractive) |

### Priority Bands

- **P0** (score 24+): rare, genuine urgency only
- **P1** (score 16-23): normal important work
- **P2** (score 8-15): planned work
- **P3** (score 0-7): polish / low-impact work

### Mandatory P0 Cap Rule

A task must **not** be assigned **P0** unless at least one of these is true:
- `severity >= 4`
- `blockingBreadth >= 3`
- `deadlineProximity >= 4`

If score is in the P0 range but none of those conditions hold, assigned priority is capped at **P1**.

### Tie-Break Rules

When scores are equal, apply tie-breaks in this exact order:
1. Higher blocking breadth
2. Earlier deadline
3. Higher business impact
4. Lower estimated token cost
5. Older queue insertion time
6. Lexical taskId as final tie-break

## Selection Flow

1. **Fetch pipeline** — Read all pending items from Forge Pipeline
2. **Filter ineligible** — Exclude complete, cancelled, blocked, quarantined
3. **Score each item** — Compute weighted priority score
4. **Apply tie-breaks** — Order items with same score
5. **Select highest-ranked** — Choose top item after scoring
6. **Apply safety gates** — Check if safe for auto-dispatch
7. **Validate approval window** — Check if window authorizes dispatch
8. **Select model and budget** — Assign model and token ceiling
9. **Dispatch or hold** — Execute or request approval
10. **Persist and report** — Update state, emit decision summary

## Safety Gates (Auto-Dispatch Must Stop When...)

1. **Destructive** — deletion, irreversible changes (unless `allowDestructive: true`)
2. **Production impact** — live infra, auth, routing (unless `allowProdChanges: true`)
3. **Secrets/privileges** — credential handling, key access
4. **Missing metadata** — no category, no dependency state, no token estimate
5. **Invalid approval window** — expired, exhausted, revoked
6. **Token ceiling exceeded** — exceeds `maxTokensPerJob` or `maxTokensPerWindow`
7. **Failed/quarantined dependency** — prerequisite chain broken
8. **Low confidence** — execution readiness below threshold
9. **Conflicting concurrency** — related task already in flight

## Approval Window Modes

| Mode | Description | Check |
|------|-------------|-------|
| `time` | Valid until timestamp | `currentTime < expiresAt` |
| `jobs` | Valid for N executions | `jobsRemaining > 0` |
| `until-empty` | Valid until queue empty | pipeline has pending tasks |
| `none` | No auto-approve | always ask |

### Jobs Mode Semantics
- Slot consumed when job enters execution
- Retries don't consume new slot unless re-queued
- Skipped/rejected tasks don't consume slot
- In-flight work may finish after window expires

### Time Mode Semantics
- Time checked at dispatch time
- In-flight jobs may complete after expiry
- No new dispatch after expiry

## State Persistence

State stored in `~/.openclaw/workspace/.control-plane-what-next-state.json`:

```json
{
  "version": 1,
  "activeWindow": {
    "mode": "jobs" | "time" | "until-empty" | "none",
    "startedAt": "ISO-8601",
    "expiresAt": "ISO-8601 | null",
    "maxJobs": number | null,
    "jobsRemaining": number | null,
    "followNewJobs": boolean,
    "approvedSnapshotJobIds": ["id1", "id2"],
    "windowCompletedJobs": ["CP-001"],
    "windowTokenUsage": 150000,
    "status": "active" | "expired" | "exhausted" | "revoked" | "idle"
  },
  "session": {
    "startedAt": "ISO-8601",
    "completedJobs": ["CP-001", "CP-002"],
    "failedJobs": ["CP-003"],
    "quarantinedJobs": ["CP-004"],
    "tokenUsage": 500000,
    "byModel": { "qwen3:14b": 200000, "gpt-oss:20b": 300000 }
  },
  "lifetime": {
    "completedCount": 42,
    "failedCount": 3,
    "quarantinedCount": 2,
    "tokenUsage": 5000000
  },
  "current": {
    "lastEvaluatedAt": "ISO-8601",
    "lastDispatchedJobId": "CP-002",
    "lastDecision": "dispatched" | "held-awaiting-approval" | "held-by-safety-gate" | ...,
    "inFlightJobId": "CP-006"
  },
  "policy": {
    "allowDestructive": false,
    "allowProdChanges": false,
    "maxTokensPerJob": 500000,
    "maxTokensPerWindow": 2000000,
    "autoRetryTransientFailures": true,
    "maxAutomaticRetries": 1
  }
}
```

## Model Routing

| Task Category | Default Model | Escalate To |
|---------------|---------------|-------------|
| Infrastructure | `qwen3-coder-next:cloud` | Codex |
| Coding | `qwen3-coder-next:cloud` | Codex |
| Review | `qwen3.5:397b-cloud` | Codex |
| Security | `Codex` | — |
| Docs (simple) | `llama3.1:8b` | `qwen3:14b` |
| Docs (complex) | `qwen3.5:397b-cloud` | Codex |
| Planning | `qwen3.5:397b-cloud` | Codex |
| Investigation | `qwen3:14b` | `qwen3.5:397b-cloud` |

### Escalation Rules
Escalate to stronger model when:
- Complexity is high
- Confidence is low
- Safety sensitivity is high
- Task affects multiple downstream items

## Failure Handling

| Failure Type | Action |
|--------------|--------|
| Transient | Retry once if policy allows, then quarantine |
| Permanent | Hold for operator review |
| Policy | Explain policy block, don't retry |
| Dependency | Hold, prevent downstream auto-dispatch |
| Metadata | Hold, request task definition repair |

## Operator Output Format

Every invocation returns:

```
Next job selected: {id}
Priority: P{0-3} (score: {number})
Reason: {one-line justification}
Scope: {low|medium|high}
Model: {model}
Estimated tokens: {number}k
Approval window: {mode}, {remaining} remaining
Safety status: passed | failed (reason)
Action: dispatched | holding for {reason}
```

### Example Outputs

**Auto-dispatch allowed:**
```
Next job selected: CP-006
Priority: P1 (score: 15)
Reason: blocks 3 queued items, due within 24h
Model: qwen3-coder-next:cloud
Estimated tokens: 42k
Approval window: jobs mode, 4 remaining after dispatch
Safety status: passed
Action: dispatching now
```

**Approval expired:**
```
Next eligible job: CP-007
Priority: P1 (score: 14)
Reason: important dependency item with high readiness
Model: qwen3.5:397b-cloud
Estimated tokens: 31k
Approval window: expired
Safety status: passed
Action: holding for renewed approval
```

**Blocked by safety gate:**
```
Next ranked job: CP-008
Priority: P0 (score: 22)
Reason: production-impacting networking task
Model: qwen3-coder-next:cloud
Estimated tokens: 55k
Approval window: active
Safety status: failed (production-impacting not allowed)
Action: holding for explicit approval
```

## Test Suite

The skill includes two validated suites:

### Regression suite

| Test ID | Purpose | Status |
|---------|---------|--------|
| T01 | P0 beats all — highest score selected | ✓ |
| T02 | Tie-break by deadline | ✓ |
| T03 | Jobs window decrements | ✓ |
| T04 | Time window expires | ✓ |
| T05 | Destructive job blocked | ✓ |
| T06 | Retry then quarantine | ✓ |
| T07 | Token limit enforced | ✓ |
| T08 | Dependency failure blocks children | ✓ |
| T09 | Pipeline empty stops cleanly | ✓ |
| T10 | Session restart state recovery | ✓ |
| T11 | E2E normal delivery series | ✓ |
| T12 | Risky job held | ✓ |
| T13 | Failure chain paused | ✓ |

### Calibration suite

| Test ID | Purpose | Status |
|---------|---------|--------|
| C01 | True P0 production blocker / genuine urgency | ✓ |
| C02 | True P1 important deadline | ✓ |
| C03 | True P2 planned work | ✓ |
| C04 | True P3 polish task | ✓ |
| C05 | High score but capped to P1 | ✓ |
| C06 | Tie-break by blocking breadth | ✓ |
| C07 | Tie-break by deadline | ✓ |
| C08 | Tie-break by business impact | ✓ |
| C09 | Tie-break by estimated tokens | ✓ |
| C10 | Mixed queue distribution | ✓ |

Run tests:
```bash
python3 skills/control-plane-what-next/references/run_tests.py
python3 skills/control-plane-what-next/references/run_calibration.py
```

## v2 Parallel Dispatch (Phase 2)

The control-plane supports bounded parallel dispatch, allowing multiple jobs to run concurrently across different model pools while respecting dependencies, lock conflicts, and pool capacity limits.

### Parallel Dispatch Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Forge Pipeline                           │
│                  (Pending Items)                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              compute_eligible_set()                         │
│  ┌─────────────────┬─────────────────┬───────────────────┐ │
│  │  Filter Complete│  Filter Blocked │  Filter Ineligible │ │
│  │  /Quarantined   │  Dependencies   │  (Safety Gates)    │ │
│  └─────────────────┴─────────────────┴───────────────────┘ │
│                      │                                      │
│                      ▼                                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │            Priority Scoring + Tie-breaks              │ │
│  └───────────────────────────────────────────────────────┘ │
│                      │                                      │
│                      ▼                                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │            Eligible Set (sorted by priority)          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         select_jobs_for_parallel_dispatch()                 │
│  ┌─────────────────┬─────────────────┬───────────────────┐ │
│  │  Pool Capacity   │  Lock Conflicts  │  Approval Window  │ │
│  │  Per Pool        │  Detection       │  Slot Limits      │ │
│  └─────────────────┴─────────────────┴───────────────────┘ │
│                      │                                      │
│                      ▼                                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         Selected Jobs (up to maxParallelDispatches)   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    dispatch_parallel()                      │
│  ┌─────────────────┬─────────────────┬───────────────────┐ │
│  │  dispatch_job() │  dispatch_job() │  dispatch_job()   │ │
│  │   Pool: coder   │   Pool: review  │   Pool: docs     │ │
│  │   Lock: file.ts │   (no locks)    │   Lock: README   │ │
│  └─────────────────┴─────────────────┴───────────────────┘ │
│                      │                                      │
│                      ▼                                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         State Updated: activeJobs[], locks[], tokens  │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. `state_manager.py` — State File Management

Handles v1/v2 state loading, migration, and persistence:

```python
from state_manager import (
    load_state,           # Load v1 or v2 state (auto-migrate)
    save_state,           # Persist state to disk
    create_default_state, # Create fresh v2 state
    migrate_v1_to_v2,     # Convert v1 state to v2 format
    reconcile_state,      # Recover from restart
    get_active_jobs,      # Get all active dispatches
    get_pool_capacity,    # Check pool capacity
    get_active_locks,     # Get held locks
    add_active_job,       # Add dispatch to state
    remove_active_job,    # Remove completed dispatch
    add_lock,             # Acquire resource lock
    remove_locks_for_job, # Release job's locks
)
```

#### 2. `dispatch_engine.py` — Core Dispatch Logic

Handles eligible-set scheduling and parallel dispatch:

```python
from dispatch_engine import (
    compute_eligible_set,     # Find all ready jobs
    check_dependencies_satisfied,  # Verify deps complete
    check_lock_conflicts,     # Detect resource conflicts
    check_pool_capacity,      # Check pool has room
    check_safety_gates,       # Validate safety constraints
    dispatch_job,             # Single job dispatch
    dispatch_parallel,        # Multi-job parallel dispatch
    complete_job,             # Mark job complete, release locks
    generate_operator_summary, # Human-readable output
    generate_decision_trace,  # Audit logging
)
```

#### 3. `forge_pipeline_client.py` — Pipeline Integration

Fetches pending items and updates status:

```python
from forge_pipeline_client import (
    fetch_pending_items,   # Query Forge Pipeline
    update_task_status,    # Mark dispatched/running/completed
    get_pipeline_item,    # Get specific task by ID
    get_dependencies,      # Get prerequisite tasks
    get_blocked_tasks,     # Get tasks blocked by this one
)
```

### Parallel Dispatch Flow

1. **Compute Eligible Set**
   - Query Forge Pipeline for pending items
   - Filter out completed, quarantined, failed tasks
   - Check dependencies satisfied
   - Check lock conflicts
   - Check pool capacity
   - Apply safety gates
   - Score remaining jobs by priority

2. **Select Jobs for Dispatch**
   - Take top N eligible jobs (up to `maxParallelDispatches`)
   - Respect per-pool `maxConcurrent` limits
   - Each dispatch consumes one approval slot (jobs mode)
   - Skip jobs with lock conflicts

3. **Dispatch Parallel**
   - Acquire locks for each job's `sharedResources`
   - Create active dispatch record
   - Update pool tracking
   - Decrement approval window slots
   - Log decision trace

4. **Job Completion**
   - Release all locks held by job
   - Remove from active dispatches
   - Update token usage
   - Add to history (completed/failed/quarantined)
   - Record execution metrics

### Lock Semantics

| Lock Type | Description | Exclusive Mode | Shared Mode |
|-----------|-------------|----------------|-------------|
| `file` | File path | Blocks all access | Allows concurrent readers |
| `service` | Service/API endpoint | Blocks all access | Allows concurrent readers |
| `environment` | Environment variable/config | Blocks all access | N/A |
| `deployment` | Deployment target | Blocks all access | N/A |

Lock acquisition:
- Exclusive lock: blocks all other jobs for same resource
- Shared lock: allows multiple concurrent shared locks, blocks exclusive
- Locks released automatically on job completion

### Pool Configuration

Pools defined in state file under `pools`:

```json
{
  "pools": {
    "coder": {
      "models": ["qwen3-coder-next:cloud"],
      "maxConcurrent": 2,
      "taskTypes": ["infrastructure", "coding"],
      "maxTokensPerJob": 500000,
      "allowDestructive": false,
      "allowProductionImpact": false
    },
    "review": {
      "models": ["qwen3.5:397b-cloud"],
      "maxConcurrent": 1,
      "taskTypes": ["review"],
      "maxTokensPerJob": 300000,
      "allowDestructive": false,
      "allowProductionImpact": true
    }
  }
}
```

### Restart Recovery

On startup, the system:
1. Loads state from `.control-plane-what-next-state.json`
2. Reconciles `dispatch.activeJobs` with actual running jobs
3. Removes orphaned jobs (in state but not running)
4. Releases locks for orphaned jobs
5. Marks orphaned jobs as failed
6. Resumes dispatch cycle

### Usage Example

```python
from state_manager import load_state, save_state
from dispatch_engine import compute_eligible_set, dispatch_parallel, generate_operator_summary
from forge_pipeline_client import fetch_pending_items

# Load state
state = load_state()

# Fetch pending work
pending = fetch_pending_items()

# Compute eligible set
eligible, blocked = compute_eligible_set(pending, state)

# Dispatch up to max parallel dispatches
state, dispatch_records, blocked_jobs = dispatch_parallel(pending, state)

# Save updated state
save_state(state)

# Generate operator summary
summary = generate_operator_summary(state, eligible[:len(dispatch_records)], blocked, dispatch_records)
print(summary["message"])
```

### Parallel Dispatch Tests (S01-S10)

| Test ID | Purpose | Status |
|---------|---------|--------|
| S01 | State schema v2 roundtrip serialization | ✓ |
| S02 | Parallel active jobs recorded correctly | ✓ |
| S03 | Lock conflict blocks second job | ✓ |
| S04 | Dependency blocks parallel dispatch | ✓ |
| S05 | Pool capacity enforced | ✓ |
| S06 | Slot consumption per parallel dispatch | ✓ |
| S07 | Time expiry blocks new dispatch | ✓ |
| S08 | Restart recovers active jobs | ✓ |
| S09 | Execution metrics recorded | ✓ |
| S10 | Operator summary matches state | ✓ |

Run parallel tests:
```bash
python3 skills/control-plane-what-next/references/parallel_tests.py
```

## References
- `references/priority-scoring-model.md`: scoring formula
- `references/auto-approve-config.md`: window configuration
- `references/model-assignments.md`: routing table
- `references/operational-guardrails.md`: safety gates
- `references/03-state-schema.json`: state schema v1 (single-job dispatch)
- `references/03-state-schema-v2.json`: state schema v2 (parallel dispatch)
- `references/model-pool-schema.json`: model pool configuration
- `references/job-schema.json`: extended job metadata
- `references/active-dispatch-schema.json`: active dispatch tracking
- `references/lock-schema.json`: resource lock schema
- `references/execution-metrics-schema.json`: post-dispatch metrics
- `references/safety-report-schema.json`: pre-dispatch safety evaluation
- `references/decision-trace-schema.json`: per-cycle decision logging
- `references/operator-summary-schema.json`: operator-facing summary
- `references/09-changelog-v1-to-v2.md`: v1 to v2 migration guide
- `state_manager.py`: state file management
- `dispatch_engine.py`: parallel dispatch engine
- `forge_pipeline_client.py`: pipeline integration
- `references/run_tests.py`: test runner
- `references/test-matrix.json`: regression test definitions
- `references/parallel-schema-tests.json`: parallel dispatch test suite
- `references/parallel_tests.py`: parallel test runner
- `references/fixtures/`: test fixtures