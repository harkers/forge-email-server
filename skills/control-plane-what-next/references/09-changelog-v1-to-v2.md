# Changelog: State Schema v1 to v2

This document describes the evolution from state schema v1 (single-job dispatch) to v2 (bounded parallel dispatch).

## Version Comparison

| Feature | v1 (Single-Job) | v2 (Parallel) |
|---------|------------------|---------------|
| Concurrent dispatches | 1 | Multiple (configurable) |
| Lock tracking | No | Yes |
| Pool management | Global policy | Per-pool config |
| Active job tracking | `inFlightJobId` | `dispatch.activeJobs[]` |
| Token governance | Global limits | Per-pool tracking |
| Dependency graph | Basic | Extended with `blocks`, `sharedResources` |
| Operator output | Single job | Summary with multiple dispatches |

## Schema Changes

### New Top-Level Fields (v2)

#### `dispatch` (replaces `current.inFlightJobId`)

The `dispatch` object tracks all active dispatches:

```json
{
  "dispatch": {
    "activeJobs": [
      {
        "jobId": "CP-101",
        "pool": "coder",
        "model": "qwen3-coder-next:cloud",
        "taskType": "coding",
        "status": "running",
        "startedAt": "2026-03-25T10:00:00Z",
        "approvalSlotConsumed": true,
        "estimatedTokens": 40000,
        "actualTokens": null,
        "retryCount": 0,
        "locksHeld": ["lock-001"]
      }
    ],
    "lastDispatchedJobId": "CP-101",
    "lastDispatchAt": "2026-03-25T10:00:00Z"
  }
}
```

**Migration from v1:**
- v1's `current.inFlightJobId` → v2's `dispatch.activeJobs[0].jobId` (if present)
- v1's `current.lastDispatchedJobId` → v2's `dispatch.lastDispatchedJobId`

#### `locks`

Tracks resource locks for conflict detection:

```json
{
  "locks": {
    "activeLocks": [
      {
        "lockId": "lock-001",
        "jobId": "CP-101",
        "type": "file",
        "value": "src/auth/middleware.ts",
        "acquiredAt": "2026-03-25T10:00:00Z"
      }
    ]
  }
}
```

**Lock types:**
- `file` - File or directory path
- `service` - Service or API endpoint
- `environment` - Environment variable or configuration
- `deployment` - Deployment target or infrastructure

#### `pools`

Per-pool configuration for parallel dispatch:

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

#### `tokenGovernance`

Extended token tracking with per-pool usage:

```json
{
  "tokenGovernance": {
    "maxTokensPerJob": 500000,
    "maxTokensPerWindow": 2000000,
    "windowTokensUsed": 150000,
    "perPoolTokensUsed": {
      "coder": 100000,
      "review": 50000
    }
  }
}
```

**Migration from v1:**
- v1's `policy.maxTokensPerJob` → v2's `tokenGovernance.maxTokensPerJob`
- v1's `policy.maxTokensPerWindow` → v2's `tokenGovernance.maxTokensPerWindow`

#### `history`

Reorganized history tracking:

```json
{
  "history": {
    "windowCompletedJobs": ["CP-100"],
    "sessionCompletedJobs": ["CP-100", "CP-099"],
    "quarantinedJobs": ["CP-050"],
    "failedJobs": ["CP-040"]
  }
}
```

**Migration from v1:**
- v1's `session.completedJobs` → v2's `history.sessionCompletedJobs`
- v1's `session.failedJobs` → v2's `history.failedJobs`
- v1's `session.quarantinedJobs` → v2's `history.quarantinedJobs`

### Renamed Fields

| v1 Field | v2 Field | Notes |
|----------|----------|-------|
| `activeWindow` | `approvalWindow` | Renamed for clarity |
| `current` | `dispatch` | Restructured for parallel tracking |

### Preserved Fields

The following fields are preserved with minimal changes:

- `approvalWindow.mode` - unchanged
- `approvalWindow.startedAt` - unchanged
- `approvalWindow.expiresAt` - unchanged
- `approvalWindow.maxJobs` - unchanged
- `approvalWindow.jobsRemaining` - unchanged
- `approvalWindow.status` - unchanged
- `policy.allowDestructive` - unchanged
- `policy.allowProdChanges` - unchanged

### New Policy Fields

```json
{
  "policy": {
    "maxParallelDispatches": 4
  }
}
```

## New Schemas

### `model-pool-schema.json`

Defines pool configuration:

- Pool names: `coder`, `review`, `docs`, `security`
- Per-pool: `models[]`, `maxConcurrent`, `taskTypes[]`, `maxTokensPerJob`
- `allowDestructive`, `allowProductionImpact` flags

### `job-schema.json`

Extended job metadata:

- `dependsOn[]` - prerequisite job IDs
- `blocks[]` - jobs blocked by this one
- `sharedResources[]` - resources requiring locks
- `executionReadiness` - confidence score

### `active-dispatch-schema.json`

Tracks individual dispatches:

- Status values: `queued_for_dispatch`, `running`, `succeeded`, `failed`, `quarantined`, `cancelled`
- `approvalSlotConsumed` - whether dispatch counted against window
- `locksHeld[]` - locks acquired by this dispatch

### `lock-schema.json`

Resource lock tracking:

- Lock types: `file`, `service`, `environment`, `deployment`
- `mode`: `exclusive` or `shared`

### `execution-metrics-schema.json`

Post-dispatch metrics:

- `estimatedTokens` vs `actualTokens`
- `runtimeMs`, `retryCount`
- `efficiency` = `actualTokens / estimatedTokens`

### `safety-report-schema.json`

Pre-dispatch safety evaluation:

- `eligible` - passes all gates
- `blockedBy[]` - gate failures
- `conflictingLocks[]` - active lock conflicts
- `unmetDependencies[]` - pending dependencies

### `decision-trace-schema.json`

Per-cycle decision logging:

- All scoring dimensions
- `dependenciesSatisfied`, `lockConflict`, `poolCapacityAvailable`
- `selected`, `selectedReason`, `tieBreakReason`

### `operator-summary-schema.json`

Operator-facing output:

- `activeDispatches[]` - currently running
- `blockedJobs[]` - waiting with reasons
- `poolUtilisation` - per-pool capacity
- `activeLocks[]` - currently held

## Migration Considerations

### Backward Compatibility

v1 state files can be loaded and automatically upgraded:

```json
{
  "version": 1,
  "activeWindow": { ... },
  "current": { "inFlightJobId": "CP-100", ... },
  ...
}
```

**Automatic v2 conversion:**

```json
{
  "version": 2,
  "approvalWindow": { ... },
  "dispatch": {
    "activeJobs": [
      { "jobId": "CP-100", "status": "running", ... }
    ],
    "lastDispatchedJobId": "CP-100"
  },
  "locks": { "activeLocks": [] },
  ...
}
```

### Breaking Changes

1. **`inFlightJobId` removed** - Use `dispatch.activeJobs[0].jobId` instead
2. **`current` removed** - Replaced by `dispatch`
3. **`activeWindow` renamed** - Now `approvalWindow`
4. **Token tracking moved** - From `policy` to `tokenGovernance`

### State File Location

Unchanged: `~/.openclaw/workspace/.control-plane-what-next-state.json`

### Test Suite Compatibility

Existing v1 tests (T01-T13) continue to pass with v2 schema. New parallel tests (S01-S10) validate v2-specific features.

## Semantic Changes

### Approval Window Slots

In v2, each parallel dispatch consumes one approval slot:

- `jobsRemaining` decrements for each `activeJobs[].approvalSlotConsumed = true`
- Retries don't consume new slots unless re-queued
- Time windows allow concurrent dispatches until expiry

### Lock Semantics

Locks enable conflict detection:

- **Exclusive locks** - Block all other jobs for same resource
- **Shared locks** - Allow multiple readers, block writers
- Locks are released when job completes (success, fail, or quarantine)

### Pool Capacity

Pools enforce `maxConcurrent` limits:

- `coder` pool may allow 2 concurrent jobs
- `review` pool may allow 1 concurrent job
- New dispatch blocked if pool at capacity
- Capacity released when job completes

### Token Budget

Per-pool token tracking:

- Each pool has its own token budget
- Global `maxTokensPerWindow` still enforced
- `perPoolTokensUsed` tracks consumption per pool
- Budget resets with new approval window