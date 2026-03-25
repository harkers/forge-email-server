# Implementation Outline

## 1. Suggested module boundaries

### pipeline-client
Responsibilities:
- fetch pending tasks
- normalize task metadata
- expose dependency state

### scorer
Responsibilities:
- calculate weighted score
- assign P0-P3 band
- expose tie-break metadata

### policy-engine
Responsibilities:
- validate approval window
- evaluate safety gates
- enforce token limits

### model-router
Responsibilities:
- choose model
- set token ceilings
- apply escalation rules

### dispatcher
Responsibilities:
- dispatch task
- record in-flight state
- classify result

### state-store
Responsibilities:
- read/write JSON state
- preserve session and window history
- update counters consistently

### reporter
Responsibilities:
- generate standard operator-facing status message
- emit machine-readable decision event if needed

## 2. Pseudo-flow

```text
load state
fetch pipeline
normalize tasks
filter ineligible items
if none eligible:
    report no eligible work
    persist state
    stop

score eligible items
sort by score and tie-break rules
candidate = highest-ranked item

run safety checks on candidate
if safety check fails:
    report hold reason
    persist state
    stop

validate approval window
if approval invalid:
    report approval required
    persist state
    stop

route candidate to model
check token ceilings
if token ceiling fails:
    report token hold
    persist state
    stop

dispatch candidate
update window/session/lifetime state
report outcome
persist state
```

## 3. Recommended event names

- `pipeline.evaluated`
- `task.scored`
- `task.selected`
- `task.held`
- `task.dispatched`
- `task.retrying`
- `task.quarantined`
- `window.expired`
- `window.exhausted`

## 4. Implementation notes

- keep scoring pure and deterministic
- keep policy checks explicit and independently testable
- do not bury safety logic inside dispatch code
- write state atomically to avoid corruption on crash
- separate visible operator history from internal execution detail
