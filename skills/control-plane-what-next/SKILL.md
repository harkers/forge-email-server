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

## References
- `references/priority-scoring-model.md`: scoring formula
- `references/auto-approve-config.md`: window configuration
- `references/model-assignments.md`: routing table
- `references/operational-guardrails.md`: safety gates
- `references/state-schema.json`: state schema
- `references/run_tests.py`: test runner
- `references/test-matrix.json`: test definitions
- `references/fixtures/`: test fixtures