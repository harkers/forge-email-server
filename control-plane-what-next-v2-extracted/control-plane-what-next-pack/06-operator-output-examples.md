# Operator Output Examples

## Example 1 — auto-dispatch allowed

```text
Next job selected: CP-006
Priority: P1 (score: 15)
Reason: blocks 3 queued items and is due within 24h
Scope: medium
Model: qwen3-coder-next:cloud
Estimated tokens: 42k
Approval window: jobs mode, 4 remaining after dispatch
Safety status: passed
Action: dispatching now
```

## Example 2 — approval expired

```text
Next eligible job: CP-007
Priority: P1 (score: 14)
Reason: important dependency item with high readiness
Model: qwen3.5:397b-cloud
Estimated tokens: 31k
Approval window: expired
Safety status: passed
Action: holding for renewed approval
Suggested approval phrases:
- auto approve for 6 hours
- auto approve for 5 jobs
- auto approve until pipeline empty
```

## Example 3 — blocked by safety gate

```text
Next ranked job: CP-008
Priority: P0 (score: 22)
Reason: production-impacting networking task blocking multiple downstream items
Model: qwen3-coder-next:cloud
Estimated tokens: 55k
Approval window: active
Safety status: failed (production-impacting change not allowed under current policy)
Action: holding for explicit operator approval
```

## Example 4 — no eligible work

```text
Pipeline status: no eligible work
Reason: all remaining items are blocked, quarantined, or awaiting metadata repair
Approval window: active
Action: no dispatch performed
```

## Example 5 — token ceiling exceeded

```text
Next ranked job: CP-011
Priority: P1 (score: 13)
Reason: architecture review due within 24h
Model: qwen3.5:397b-cloud
Estimated tokens: 145k
Approval window: active
Safety status: failed (estimated tokens exceed maxTokensPerJob=120k)
Action: holding for manual review or revised token budget
```
