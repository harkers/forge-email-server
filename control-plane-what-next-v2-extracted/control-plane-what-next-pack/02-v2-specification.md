# `control-plane-what-next` v2 Specification

## 1. Purpose

`control-plane-what-next` is a control-plane skill that continuously determines the highest-ranked eligible item in Forge Pipeline, validates it against policy and operator approval rules, selects an execution model, and either dispatches or requests renewed operator approval.

Its job is not merely to list pending work. Its job is to make the next-action decision safely, predictably, and transparently.

## 2. Core responsibilities

The skill must:

1. query Forge Pipeline for pending items
2. normalize task metadata
3. calculate a deterministic priority score
4. apply tie-break rules when scores are equal
5. validate the chosen task against safety gates
6. validate the current approval window
7. select an execution model and token budget
8. dispatch the task if allowed
9. record the outcome and update state
10. report the decision in a standard operator-facing format

## 3. Trigger conditions

The skill may be invoked:

- after a task completes
- when the operator asks “what’s next?”
- when a new approval window is granted
- after a blocked or quarantined item is resolved
- on demand as part of a control-plane status check

## 4. Inputs

Required inputs:

- pipeline task list
- current auto-approve state
- task metadata
- model-routing policy
- token budget policy
- safety policy flags

Recommended task metadata fields:

- taskId
- title
- description
- category
- dueAt
- dependencies
- blockedBy
- impactsProduction
- touchesSecrets
- destructive
- estimatedComplexity
- estimatedTokens
- createdAt
- updatedAt
- owner
- tags
- confidence
- executionReadiness

## 5. Selection flow

The control-plane selection flow must operate in this order:

### Step 1: Fetch pipeline
Read all pending items from Forge Pipeline.

### Step 2: Filter ineligible items
Exclude items that are:

- already complete
- cancelled
- missing required metadata
- blocked by unresolved dependencies
- explicitly quarantined
- already in progress elsewhere

### Step 3: Score each eligible item
Compute the weighted priority score described in `04-priority-scoring-model.md`.

### Step 4: Apply tie-break rules
Where multiple items have the same priority band or same numeric score, apply tie-break rules in the defined order.

### Step 5: Select highest-ranked eligible item
Choose the top-ranked item after scoring and tie-breaks.

### Step 6: Apply safety gates
Check whether the item is safe for auto-dispatch under current policy.

### Step 7: Validate approval window
Check whether the current approval window still authorizes dispatch.

### Step 8: Select model and execution budget
Assign a model and token ceiling using routing rules.

### Step 9: Dispatch or hold
- If approved and safe: dispatch
- If not approved: request renewed operator approval
- If unsafe: hold and explain why

### Step 10: Persist state and report decision
Update persisted state and emit a standard decision summary.

## 6. Priority bands

The skill must classify tasks into four operator-friendly bands:

- P0 — critical blockers or severe risk
- P1 — high importance with real urgency or dependency impact
- P2 — standard planned work
- P3 — low-impact improvements or exploratory work

The visible band must be derived from the underlying weighted score rather than manually guessed.

## 7. Approval window modes

Supported modes:

### Time mode
Valid until a fixed timestamp.
Examples:
- 6 hours
- 12 hours
- 24 hours
- 72 hours

### Jobs mode
Valid for the next N executions.
Examples:
- 1 job
- 3 jobs
- 5 jobs
- 10 jobs

### Until-empty mode
Valid until the approved queue snapshot is empty.

By default, newly created jobs after window creation are not included unless `followNewJobs = true`.

## 8. State persistence

State must be stored in a durable JSON file and updated after every decision boundary.

The persisted state must cleanly separate:

- session-level history
- active approval-window history
- lifetime statistics
- current dispatch state

## 9. Model routing

Routing must use a policy-driven system, not only a fixed table.

### Default routing table

- Infrastructure → `qwen3-coder-next:cloud`
- Coding → `qwen3-coder-next:cloud`
- Review → `qwen3.5:397b-cloud`
- Security → `Codex`
- Docs (simple) → `llama3.1:8b`
- Docs (complex / policy / architecture) → `qwen3.5:397b-cloud`
- Planning → `qwen3.5:397b-cloud`

### Escalation rules
Escalate to a stronger model when:

- complexity is high
- confidence is low
- safety sensitivity is high
- required context is broad
- task affects multiple downstream items

## 10. Token management

The skill must track:

- estimated tokens before dispatch
- actual tokens after completion
- variance between estimate and actual
- total tokens used in current approval window
- total tokens used in current session
- totals by model

The skill must refuse auto-dispatch if the task breaches configured token ceilings.

## 11. Failure handling

Failures must be classified as either:

- transient
- permanent
- policy-related
- dependency-related

### Required behaviors

- transient failures may be retried once automatically
- repeated failures move the task to quarantine
- dependency failures prevent downstream auto-dispatch when relevant
- malformed tasks are held for operator review
- pipeline fetch failures stop auto-dispatch for that cycle

## 12. Standard operator output

Every invocation must return a concise structured summary including:

- selected job ID
- priority band and score
- reason for selection
- model and token estimate
- approval status
- safety status
- dispatch outcome
- remaining approval window capacity

## 13. Non-goals

The skill does not:

- replace pipeline governance
- make destructive production changes by default
- silently ignore unsafe work
- continue indefinitely without state accounting

## 14. Success criteria

The skill is successful when it:

- consistently chooses the correct next eligible item
- explains why that item was chosen
- respects approval limits
- avoids unsafe auto-dispatch
- records enough state for audit and troubleshooting
