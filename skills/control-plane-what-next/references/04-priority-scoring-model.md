# Priority Scoring Model

## Goal

The original design used descriptive categories. This v2 model makes task ranking deterministic and auditable.

## Score dimensions

Each eligible task receives a score on the following dimensions.

### 1. Severity (0-5)
Measures the seriousness of the issue if not handled.

- 5 — production outage, security event, major operational failure
- 4 — severe user or workflow degradation
- 3 — meaningful issue with contained impact
- 2 — moderate inconvenience or quality problem
- 1 — minor issue
- 0 — no immediate consequence

### 2. Blocking impact (0-5)
Measures whether the task blocks other work.

- 5 — blocks many queued items or a shared dependency
- 4 — blocks multiple important items
- 3 — blocks one important downstream item
- 2 — creates friction for later work
- 1 — weak dependency effect
- 0 — no dependency effect

### 3. Dependency breadth (0-5)
Measures how many downstream items rely on the outcome.

- 5 — platform/foundation work affecting broad areas
- 4 — multiple linked workstreams
- 3 — one workstream with several related tasks
- 2 — limited dependency graph
- 1 — narrow impact
- 0 — isolated task

### 4. Deadline proximity (0-5)
Measures urgency in time.

- 5 — overdue or due within 4 hours
- 4 — due within 24 hours
- 3 — due within 72 hours
- 2 — due within 7 days
- 1 — due later but scheduled
- 0 — no time pressure

### 5. Execution readiness (0-5)
Measures whether the task is well specified and ready.

- 5 — fully specified, safe, clear dependencies
- 4 — small metadata gaps but still dispatchable
- 3 — moderately defined
- 2 — material ambiguity
- 1 — poorly defined
- 0 — not dispatchable

### 6. Execution effort (0-5)
Measures the expected effort cost. This is subtractive because very expensive work is less attractive as a “next step” when two tasks are otherwise comparable.

- 5 — very high effort
- 4 — high effort
- 3 — medium effort
- 2 — modest effort
- 1 — low effort
- 0 — trivial effort

## Weighted formula

Use:

```text
priorityScore =
  (severity * 3) +
  (blockingImpact * 3) +
  (dependencyBreadth * 2) +
  (deadlineProximity * 2) +
  (executionReadiness * 1) -
  (executionEffort * 1)
```

## Score bands

Map numeric scores to visible priority bands:

- 18 and above → P0
- 13 to 17 → P1
- 8 to 12 → P2
- 0 to 7 → P3

## Tie-break rules

When two tasks have the same band or numeric score, apply tie-breakers in this order:

1. higher blocking impact
2. earlier due date
3. higher execution readiness
4. lower estimated token cost
5. older queue age
6. lexical taskId as final deterministic tie-break

## Notes

This model intentionally favors unblockers and urgent items, while still rewarding tasks that are ready to execute. It prevents the control plane from over-preferring large, poorly defined work merely because it sounds important.
