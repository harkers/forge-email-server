# Control-Plane-What-Next Test Results

## Comprehensive Analysis Report

**Date:** 2026-03-25  
**Scope:** Full analysis of `control-plane-what-next` test suite results  
**Status:** 13/13 PASS

---

## Executive Summary

This report presents a comprehensive analysis of the `control-plane-what-next` test suite. The suite validates:

- priority scoring
- deterministic tie-breaking
- safety gates
- approval-window behavior
- failure handling
- dependency protection
- state persistence and recovery
- end-to-end orchestration behavior

### Final Result

**13 of 13 tests passed (100%)**

This means the current implementation correctly handles both normal dispatch behavior and the key failure/risk scenarios expected from a control-plane next-action selector.

---

## Core Decision Model

### Priority Scoring Formula

The implementation uses the following weighted score:

```text
score = (severity × 3)
      + (blocking × 3)
      + (breadth × 2)
      + (deadline × 2)
      + readiness
      - effort
```

### Score Dimensions

| Dimension | Weight | Range | Meaning |
|---|---:|---:|---|
| Severity | 3 | 0–5 | Impact if not handled |
| Blocking Impact | 3 | 0–5 | How much other work is blocked |
| Dependency Breadth | 2 | 0–5 | Number/breadth of downstream items affected |
| Deadline Proximity | 2 | 0–5 | Urgency by time |
| Execution Readiness | 1 | 0–5 | How ready and clear the task is |
| Execution Effort | -1 | 0–5 | Cost/effort penalty |

### Priority Bands

| Band | Score Range | Meaning |
|---|---:|---|
| P0 | 18+ | Critical blocker / severe urgency |
| P1 | 13–17 | High importance with real urgency |
| P2 | 8–12 | Standard planned work |
| P3 | 0–7 | Lower-impact work |

---

## Safety Model

The skill blocks auto-dispatch when a task is unsafe under current policy.

### Safety Gates Covered

- destructive operations
- production-impacting work
- token ceiling breaches
- failed or quarantined dependencies
- repeated failure leading to quarantine
- approval-window expiry

### Approval Window Modes Covered

| Mode | Meaning | Condition |
|---|---|---|
| `jobs` | Allow next N jobs | `jobsRemaining > 0` |
| `time` | Allow until timestamp | `now < expiresAt` |
| `until-empty` | Allow until approved queue empties | queue still eligible |
| `none` | No automatic approval | always require approval |

---

## Detailed Test Analysis

## T01 — Priority P0 Beats All

**Purpose:** Validate that an obvious P0 blocker outranks all lower-priority work.

**Expected:** `CP-106` selected  
**Actual:** `CP-106` selected  
**Result:** PASS

### Why it passed

`CP-106` combined:
- high impact
- multiple blocked downstream items
- meaningful urgency

That produced the highest weighted score, so the selector chose it correctly.

### What this proves

The scoring model properly favors unblockers and urgent high-impact work over routine medium/low-impact tasks.

---

## T02 — Tie-Break by Deadline

**Purpose:** Validate deterministic selection when base scores are effectively equal.

**Expected:** `CP-202`  
**Actual:** `CP-202`  
**Result:** PASS

### Why it passed

The tie-break logic preferred the earlier deadline when candidate scores were otherwise equal.

### What this proves

The selector is not just priority-driven — it is deterministic under ambiguity.
That matters for auditability and reproducibility.

---

## T03 — Jobs Window Decrements

**Purpose:** Validate that a jobs-based approval window decrements correctly.

**Expected:** dispatch + decrement  
**Actual:** correct dispatch and decrement  
**Result:** PASS

### Why it passed

When the job entered execution, `jobsRemaining` reduced by one as intended.

### What this proves

Approval slots are consumed at the correct decision boundary.
This is important because retries should not silently mint extra approval.

---

## T04 — Time Window Expires

**Purpose:** Validate that an expired time window prevents new dispatch.

**Expected:** approval required  
**Actual:** approval required  
**Result:** PASS

### Why it passed

The dispatcher checked time eligibility at dispatch time and correctly refused to continue under an expired window.

### What this proves

Time-based approval is enforced at the correct boundary and is not being ignored or loosely interpreted.

---

## T05 — Destructive Job Blocked

**Purpose:** Validate that destructive production-impacting work is not auto-dispatched under safe defaults.

**Expected:** blocked  
**Actual:** blocked  
**Result:** PASS

### Why it passed

The highest-ranked candidate was blocked because:
- it was destructive
- it had production impact
- policy defaults did not allow either

### What this proves

The safety system correctly overrides ranking. High score alone cannot force unsafe execution.

---

## T06 — Retry Then Quarantine

**Purpose:** Validate transient retry behavior and quarantine after repeated failure.

**Expected:** `quarantined_after_retry`  
**Actual:** `quarantined_after_retry`  
**Result:** PASS

### Execution path

1. first dispatch attempt failed
2. retry allowed once
3. second failure caused quarantine

### What this proves

The system distinguishes between:
- retryable failure
- repeated failure
- quarantined work

That is a strong sign of operational maturity. It avoids both silent looping and premature abandonment.

---

## T07 — Token Limit Enforced

**Purpose:** Validate that per-job token ceilings block excessive work.

**Expected:** `blocked_token_limit`  
**Actual:** `blocked_token_limit`  
**Result:** PASS

### Why it passed

The candidate exceeded `maxTokensPerJob`, so dispatch was blocked.

### What this proves

The implementation enforces cost and context-budget boundaries rather than treating them as advisory.

---

## T08 — Dependency Failure Blocks Children

**Purpose:** Validate that failed foundational work prevents downstream auto-dispatch.

**Expected:** `dependents_blocked_after_failure`  
**Actual:** `dependents_blocked_after_failure`  
**Result:** PASS

### Why it passed

After the parent task failed and was quarantined, dependent tasks remained blocked.

### What this proves

The control plane respects dependency chains and avoids cascading invalid work.
This is exactly the right behavior for a safe orchestration layer.

---

## T09 — Pipeline Empty Stops Cleanly

**Purpose:** Validate that an empty queue produces a clean no-work outcome.

**Expected:** `no_work`  
**Actual:** `no_work`  
**Result:** PASS

### Why it passed

The system detected the empty queue and exited cleanly without corrupting state or attempting fallback behavior.

### What this proves

No-work conditions are treated as a valid operational state, not an error.

---

## T10 — Session Restart State Recovery

**Purpose:** Validate that persisted state survives restart and resumes safely.

**Expected:** `CP-1004`  
**Actual:** `CP-1004`  
**Result:** PASS

### Why it passed

The selector resumed from persisted history/state and chose the correct next eligible task.

### What this proves

The state model is durable enough for restart recovery and not dependent on fragile in-memory assumptions.

---

## T11 — E2E Normal Delivery

**Purpose:** Validate a normal end-to-end dispatch series over a safe mixed queue.

**Expected:** `dispatch_series` starting with `CP-1101`  
**Actual:** `dispatch_series` starting with `CP-1101`  
**Result:** PASS

### Why it passed

The system correctly:
- chose the highest-value root task first
- recognized its dependency importance
- modeled the queue as a sequence rather than a single isolated pick

### What this proves

The skill behaves like a real orchestration decision engine, not just a one-shot ranker.

---

## T12 — Risky Job Mid-Run

**Purpose:** Validate that risky work appearing during otherwise safe flow is held.

**Expected:** `risky_job_held` with first safe dispatch `CP-1201`  
**Actual:** `risky_job_held` with first safe dispatch `CP-1201`  
**Result:** PASS

### Why it passed

The system allowed safe work to proceed while separately identifying and holding the risky production-impacting task.

### What this proves

The selector can differentiate between:
- safe continuation
- work that needs explicit approval

That separation is crucial for a practical control plane.

---

## T13 — Failure Chain Paused

**Purpose:** Validate that downstream work pauses when a root blocker repeatedly fails.

**Expected:** `failure_chain_paused` with root `CP-1301`  
**Actual:** `failure_chain_paused` with root `CP-1301`  
**Result:** PASS

### Why it passed

The system recognized the failed root, quarantined it, and paused downstream continuation.

### What this proves

The failure model is not local-only; it propagates correctly through dependency structure.

---

## Coverage Summary

## Functional Coverage

| Area | Covered By | Status |
|---|---|---|
| Priority scoring | T01, T02 | PASS |
| Jobs approval window | T03 | PASS |
| Time approval window | T04 | PASS |
| Safety gate blocking | T05, T07 | PASS |
| Retry and quarantine | T06 | PASS |
| Dependency protection | T08, T13 | PASS |
| Empty queue handling | T09 | PASS |
| Restart recovery | T10 | PASS |
| End-to-end sequencing | T11, T12 | PASS |

## Safety Coverage

| Safety Control | Covered | Status |
|---|---|---|
| Destructive task block | Yes | PASS |
| Production-impact block | Yes | PASS |
| Token ceiling block | Yes | PASS |
| Failed dependency hold | Yes | PASS |
| Repeated failure quarantine | Yes | PASS |

## Edge-Case Coverage

| Edge Case | Status |
|---|---|
| Empty pipeline | PASS |
| Expired approval window | PASS |
| Tie-score resolution | PASS |
| Restart recovery | PASS |
| Mid-run risky task | PASS |
| Failure chain pause | PASS |

---

## Quality Assessment

## What is strong

### 1. Determinism
The test suite shows the selector behaves predictably under both normal and ambiguous conditions.

### 2. Safety Override
Unsafe work is blocked even when it ranks highly.
That is the right design for a control plane.

### 3. Failure Discipline
The implementation does not either:
- blindly retry forever, or
- panic-stop after one transient failure

It follows a disciplined retry/quarantine path.

### 4. Dependency Awareness
The system understands that some jobs are structurally unsafe after prerequisite failure.
That is a major strength.

### 5. State Recovery
Restart persistence works, which makes the design much more realistic for operational use.

---

## Remaining Gaps / Next Improvements

The current suite is strong, but there are still useful next steps.

### Recommended improvements

1. **Track cumulative token usage per approval window**  
   The tests cover per-job token ceilings, but fuller window-budget accounting would be useful.

2. **Add concurrency/conflict checks**  
   Prevent simultaneous dispatch of jobs touching the same asset or scope.

3. **Add metadata-gap tests**  
   Explicitly validate behavior when required metadata is missing or malformed.

4. **Add follow-up completion accounting**  
   Track not just dispatch decision quality, but whether downstream completion closes the loop cleanly.

5. **Add larger mixed-queue stress tests**  
   Useful for seeing whether ranking still feels correct under wider distributions of task quality and urgency.

---

## Final Conclusion

The `control-plane-what-next` implementation is in good shape.

The suite demonstrates that it can:
- pick the right next task
- explain the choice deterministically
- respect approval constraints
- enforce safety boundaries
- quarantine repeated failures
- protect dependency chains
- survive restart safely

### Bottom line

**The current implementation passes all designed validation scenarios and is credible as a safe, auditable next-action control-plane skill.**

---

## File References

- Analysis report (this file): `control-plane-what-next-test-analysis.md`
- HTML report: `control-plane-what-next-test-analysis.html`
- Quarto source: `control-plane-what-next-test-analysis.qmd`
- Full zipped results: `control-plane-what-next-test-results-20260325-0955.zip`
- Test runner: `skills/control-plane-what-next/references/run_tests.py`
- Test matrix: `skills/control-plane-what-next/references/test-matrix.json`

---

*Generated from the validated test suite results for control-plane-what-next on 2026-03-25.*
