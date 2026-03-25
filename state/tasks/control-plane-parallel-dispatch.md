# Work Packet: control-plane-parallel-dispatch

## Identity
- **WORK ID:** control-plane-parallel-dispatch
- **TASK TYPE:** build
- **CREATED:** 2026-03-25T14:12:00+00:00
- **STATUS:** blocked
- **BLOCKED BY:** control-plane-v2-schema (must complete first)

## Goal
Enable the control plane to dispatch multiple independent jobs in parallel across different model types to improve throughput, while preserving safety, determinism, approval-window behaviour, and state correctness.

## Context
After schema v2 is implemented, the control-plane-what-next skill needs to evolve from single-job dispatch to parallel scheduling:

- Query pipeline, score all jobs, filter to eligible set
- Dispatch multiple jobs up to configured concurrency limits
- Respect dependency chains, lock conflicts, and pool capacity
- Preserve all existing safety gates, approval semantics, and audit trails

**Workspace:** `/home/stu/.openclaw/workspace/skills/control-plane-what-next/`

**Dependencies:**
- Schema v2 files from `control-plane-v2-schema` task
- Existing test infrastructure in `references/run_tests.py`

## Allowed Scope
- `skills/control-plane-what-next/references/` - implementation files
- `skills/control-plane-what-next/SKILL.md` - update documentation
- New scheduling logic files
- New test fixtures for parallel dispatch scenarios

## Forbidden Scope
- Modifying anything outside `skills/control-plane-what-next/`
- Weakening existing safety gates, approval windows, or protections
- Removing existing single-job dispatch behaviour (must coexist with parallel mode)
- Changing regression tests T01-T13 without explicit approval

## Required Outputs

### 1. Eligible-set scheduling
Replace single-job dispatch with:
- Query pipeline for all pending items
- Score and filter to eligible jobs
- Exclude blocked jobs (dependency, lock conflict, safety gate)
- Select multiple jobs up to concurrency limits
- Dispatch eligible set atomically or in sequence

### 2. Dependency-aware scheduling
Each job supports:
- `dependsOn[]` - prerequisite job IDs (must complete before this job)
- `blocks[]` - jobs this job blocks
- `sharedResources[]` - lockable resources

Scheduling rules:
- Do not dispatch jobs with unmet `dependsOn`
- Do not dispatch jobs whose `sharedResources` conflict with active locks
- Unblock downstream jobs only after successful completion of dependencies

### 3. Model pool dispatch
Pool-based dispatch with per-pool configuration:

| Pool | Model | MaxConcurrent | TaskTypes |
|------|-------|---------------|-----------|
| coder | qwen3-coder-next:cloud | 2 | coding, infrastructure |
| review | qwen3.5:397b-cloud | 1 | review, planning |
| docs | llama3.1:8b | 2 | docs |
| security | Codex | 1 | security |

### 4. Conflict locking
Implement lock acquisition for:
- `file` - path-based file locks
- `service` - service instance locks
- `environment` - deployment environment locks
- `deployment` - deployment target locks

Rules:
- Only one active job may hold a conflicting lock
- Locks acquired before dispatch committed
- Locks released on success, failure, quarantine, or cancellation
- Orphaned locks cleaned up on restart recovery

### 5. Parallel approval semantics
- Each dispatched job consumes one approval slot at dispatch time
- Time window checked per dispatch (not per batch)
- Time expiry stops new dispatches only
- In-flight jobs allowed to complete
- Failed pre-dispatch validation does NOT consume a slot

### 6. Operator output expansion
Add active-dispatch summary:
- `activeDispatches[]` - jobId, model, taskType, status
- `blockedJobs[]` with reason per blocked job
- `remaining approval slots`
- `activeLocks[]`
- `poolUtilisation{}` per pool

### 7. State tracking for active jobs
Track per-job:
- jobId, pool, model, taskType, status, startedAt
- approvalSlotConsumed, estimatedTokens, actualTokens
- retryCount, locksHeld[]

### 8. Restart recovery
On startup/recovery:
- Reconcile `activeJobs[]` against actual running work
- Clear orphaned locks
- Preserve valid running jobs
- Do not duplicate approval slot consumption
- Do not double-count tokens

## Required Tests
File: `references/parallel-dispatch-tests.json`

Tests:
- P01: Independent jobs dispatch in parallel
- P02: Conflicting jobs serialize (lock conflict)
- P03: Dependency-blocked jobs wait
- P04: Different model pools run concurrently
- P05: Slot consumption works with parallel dispatch
- P06: Time expiry stops new dispatches but not active jobs
- P07: Failure in one active job does not corrupt unrelated active jobs
- P08: Downstream unblock after successful dependency completion
- P09: Pool capacity enforced (maxConcurrent)
- P10: Mixed pool utilisation across coder/docs/review/security

## Preserved Behaviours
Do not change or weaken:
- Approval-window logic
- Slot consumption rules
- Token ceilings
- Destructive-task blocks
- Production-impact safety gates
- Retry and quarantine behaviour
- Dependency-blocking semantics
- Before-state / after-state logging

## Required Validation Evidence
- All existing regression tests T01-T13 still pass
- All new parallel-dispatch tests P01-P10 pass
- Schema validation passes for all new schema files
- Manual test: dispatch 2 independent coder jobs → both run
- Manual test: dispatch conflicting jobs → second waits
- Manual test: dispatch with dependency → downstream waits
- Operator summary shows active dispatches, blocked jobs, pool utilisation

## Stop Conditions
- If schema v2 files are not present → stop and wait
- If existing regression tests fail → stop and fix
- If parallel dispatch breaks single-job mode → stop and investigate
- If approval semantics diverge from spec → stop and ask

## Completion Format
Return a handoff packet with:
- Summary of implementation changes
- Files modified with paths
- Test results (all tests pass)
- Manual validation results
- Open risks or follow-up needs
- Recommended next action

## Routing
- **First owner:** coding-worker-agent (blocked until schema v2 complete)
- **Expected handoff:** all tests pass → reviewer-agent → manager acceptance