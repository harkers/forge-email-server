# Operational Guardrails

## Purpose

These guardrails define when `control-plane-what-next` must refuse auto-dispatch, even if a task ranks highest.

## Auto-dispatch must stop when

### 1. The task is destructive
Examples:

- deletion operations
- destructive migrations
- data removal
- force resets
- irreversible changes

Unless `allowDestructive = true`, the task must be held.

### 2. The task impacts production
Examples:

- live infrastructure changes
- auth changes
- storage changes
- routing/network changes
- billing-sensitive operations

Unless `allowProdChanges = true`, the task must be held.

### 3. The task touches secrets or privileged material without explicit policy coverage
Examples:

- credential rotation
- secrets retrieval
- key handling
- privileged environment inspection

### 4. Required metadata is missing
Examples:

- no task category
- no dependency state
- no token estimate or no complexity estimate
- no clear objective or execution scope

### 5. Approval window is invalid
Examples:

- expired time window
- zero jobs remaining
- until-empty snapshot exhausted
- revoked window

### 6. Token ceilings would be exceeded
Examples:

- estimated tokens exceed `maxTokensPerJob`
- cumulative window usage would exceed `maxTokensPerWindow`

### 7. The task depends on a failed or quarantined prerequisite
The control plane must not blunder forward into a broken dependency chain.

### 8. Confidence is too low
If execution readiness or confidence falls below the configured threshold, the system must hold for review.

### 9. Conflicting concurrency exists
Do not auto-dispatch when:

- a related task is already in flight
- the same asset is being modified elsewhere
- a serial dependency chain is unresolved

## Approval-window semantics

### Jobs mode
- a slot is consumed when a job enters execution
- retries do not consume a new slot unless the job is explicitly re-queued as new work
- skipped or rejected tasks do not consume a slot
- in-flight work may finish even if the window expires during execution

### Time mode
- time is checked at dispatch time, not continuously during execution
- jobs already in flight may complete after expiry
- no new dispatch may occur after expiry

### Until-empty mode
- default behavior applies only to the approved queue snapshot
- newly added jobs are not included unless `followNewJobs = true`

## Failure policy

### Transient failure
- retry once automatically if policy allows
- on second failure, move to quarantine

### Permanent failure
- do not retry automatically
- hold for operator review

### Policy failure
- do not retry
- explain the policy block

### Metadata failure
- hold and request repair of task definition

## Logging requirements

Every hold or dispatch decision should record:

- job ID
- score and visible priority band
- reasons for ranking
- approval basis
- safety-gate result
- model selection
- token estimate
- final outcome

## Principle

The control plane should be biased toward safe continuation, not blind continuation.
