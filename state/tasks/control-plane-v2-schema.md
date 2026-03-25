# Work Packet: control-plane-v2-schema

## Identity
- **WORK ID:** control-plane-v2-schema
- **TASK TYPE:** build
- **CREATED:** 2026-03-25T14:12:00+00:00
- **STATUS:** queued
- **PREREQUISITE FOR:** control-plane-parallel-dispatch

## Goal
Define and implement the state schema, model-pool schema, active-dispatch schema, lock schema, and operator output schema required for bounded parallel dispatch in control-plane-what-next.

## Context
The current control-plane-what-next skill (v3) supports single-job dispatch. To enable parallel dispatch across multiple model pools, we need to evolve the state schema from v1 to v2, adding:

- `dispatch.activeJobs[]` - track multiple concurrent jobs
- `locks.activeLocks[]` - conflict detection
- `pools` - per-pool configuration and capacity
- Extended job metadata with `dependsOn`, `blocks`, `sharedResources`
- Operator summary with active dispatches, blocked jobs, pool utilisation

**Workspace:** `/home/stu/.openclaw/workspace/skills/control-plane-what-next/`

**Current state schema:** `references/03-state-schema.json` (v1)

## Allowed Scope
- `skills/control-plane-what-next/references/03-state-schema.json` - evolve to v2
- `skills/control-plane-what-next/references/` - add new schema files
- `skills/control-plane-what-next/SKILL.md` - update to reflect schema changes
- New files for: model-pool config, job schema extensions, lock schema, execution-metrics schema, safety-report schema, decision-trace schema, operator-summary schema
- New test file: `references/parallel-schema-tests.json` or similar

## Forbidden Scope
- Modifying anything outside `skills/control-plane-what-next/`
- Breaking existing v1 state file compatibility (must support migration or coexistence)
- Weakening existing safety gates, approval windows, or protections

## Required Outputs

### 1. Control-plane state schema v2
File: `references/03-state-schema-v2.json`

Must include:
- `version: 2`
- `approvalWindow` (preserve existing, add followNewJobs semantics)
- `tokenGovernance` with `maxTokensPerJob`, `maxTokensPerWindow`, `windowTokensUsed`, `perPoolTokensUsed`
- `history` with `windowCompletedJobs`, `sessionCompletedJobs`, `quarantinedJobs`, `failedJobs`
- `dispatch` with `activeJobs[]`, `lastDispatchedJobId`, `lastDispatchAt`
- `locks` with `activeLocks[]`
- `pools` configuration per pool name

### 2. Model-pool config schema
File: `references/model-pool-schema.json`

Must include for each pool:
- `models[]` - array of model identifiers
- `maxConcurrent` - parallel capacity
- `taskTypes[]` - allowed task categories
- `maxTokensPerJob` - per-job token ceiling
- `allowDestructive` - safety gate
- `allowProductionImpact` - safety gate

Initial pools: `coder`, `review`, `docs`, `security`

### 3. Job schema extensions
File: `references/job-schema.json`

Must include:
- `jobId`, `title`, `taskType`
- `dependsOn[]` - prerequisite job IDs
- `blocks[]` - jobs this blocks
- `sharedResources[]` - lockable resources with `{type, value}`
- `estimatedTokens`
- `deadline`, `queueInsertedAt`
- `destructive`, `productionImpact`
- `executionReadiness`

### 4. Active-dispatch schema
File: `references/active-dispatch-schema.json`

Must include per active job:
- `jobId`, `pool`, `model`, `taskType`, `status`
- `startedAt`, `approvalSlotConsumed`
- `estimatedTokens`, `actualTokens`
- `retryCount`, `locksHeld[]`

Allowed status values: `queued_for_dispatch`, `running`, `succeeded`, `failed`, `quarantined`, `cancelled`

### 5. Lock schema
File: `references/lock-schema.json`

Must include:
- `lockId`, `jobId`, `type`, `value`, `acquiredAt`
- Supported lock types: `file`, `service`, `environment`, `deployment`

### 6. Execution-metrics schema
File: `references/execution-metrics-schema.json`

Must include per completed job:
- `jobId`, `pool`, `model`, `estimatedTokens`, `actualTokens`
- `runtimeMs`, `retryCount`, `approvalSlotConsumed`, `result`

### 7. Safety-report schema
File: `references/safety-report-schema.json`

Must include per evaluated job:
- `jobId`, `eligible`, `blockedBy[]`, `requiresOperatorApproval`
- `conflictingLocks[]`, `unmetDependencies[]`, `action`

### 8. Decision-trace schema
File: `references/decision-trace-schema.json`

Must include per scheduling cycle:
- `jobId`, `priorityScore`, `assignedPriority`, `pool`, `model`
- All scoring dimensions
- `dependenciesSatisfied`, `lockConflict`, `poolCapacityAvailable`
- `selected`, `selectedReason`, `tieBreakReason`

### 9. Operator summary schema
File: `references/operator-summary-schema.json`

Must include:
- `cycleId`, `approvalWindow` summary
- `activeDispatches[]`, `blockedJobs[]` with reasons
- `poolUtilisation` per pool
- `activeLocks[]`

## Required Test Suite
File: `references/parallel-schema-tests.json`

Tests:
- S01: state schema roundtrip
- S02: parallel active jobs recorded correctly
- S03: lock conflict blocks second job
- S04: dependency blocks parallel dispatch
- S05: pool capacity enforced
- S06: slot consumption per parallel dispatch
- S07: time expiry blocks new dispatch only
- S08: restart recovers active jobs and clears orphans
- S09: execution metrics recorded correctly
- S10: operator summary matches state

## Required Validation Evidence
- All schema files pass JSON Schema validation
- New schemas are compatible with existing test fixtures where applicable
- Test runner can load new schemas without error
- SKILL.md updated to reference new schemas
- Chelog documenting v1/v2 evolution

## Stop Conditions
- If schema changes would break existing state file loading → stop and ask
- If model pool definitions conflict with existing routing → stop and ask
- If lock semantics need clarification beyond spec → document and proceed

## Completion Format
Return a handoff packet with:
- Summary of schemas created/modified
- Files created with paths
- Test results (pass/fail for schema validation)
- Open questions or follow-up needs
- Recommended next action (hand to parallel dispatch implementer)

## Routing
- **First owner:** coding-worker-agent
- **Expected handoff:** schema validation pass → manager acceptance → dispatch to parallel-dispatch implementer