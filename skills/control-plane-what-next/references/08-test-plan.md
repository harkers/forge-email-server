# Test Plan

## Objective

Validate that the skill makes safe, deterministic next-step decisions across normal, edge, and failure scenarios.

## Functional tests

### 1. Picks highest-ranked eligible item
- create several pending tasks with distinct scores
- confirm highest score is selected

### 2. Applies tie-breaks deterministically
- create two equal-score tasks
- confirm tie-break order is followed exactly

### 3. Skips blocked items
- mark task as blocked by unresolved dependency
- confirm it is not selected

### 4. Stops when approval window expires
- simulate expired time window
- confirm no auto-dispatch occurs

### 5. Consumes jobs window correctly
- set jobsRemaining = 2
- dispatch two tasks
- confirm third task is held

### 6. Uses until-empty snapshot correctly
- approve snapshot of three jobs
- add a fourth after approval
- confirm fourth is excluded unless `followNewJobs = true`

## Safety tests

### 7. Holds destructive task by default
- mark highest-ranked task as destructive
- confirm safety hold occurs

### 8. Holds production-impacting task by default
- mark task as production affecting
- confirm safety hold occurs

### 9. Holds task with missing metadata
- remove category or token estimate
- confirm metadata hold occurs

### 10. Holds task that would exceed token ceiling
- set estimate over allowed threshold
- confirm token hold occurs

## Failure tests

### 11. Retries transient failure once
- simulate transient dispatch failure
- confirm one retry occurs

### 12. Quarantines after repeated transient failure
- simulate second transient failure
- confirm task is quarantined

### 13. Stops chain on dependency failure
- fail a foundational task
- confirm dependent tasks are not auto-dispatched

### 14. Stops when pipeline fetch fails
- simulate pipeline client failure
- confirm no selection occurs

## State tests

### 15. Writes state consistently after dispatch
- confirm session, lifetime, and window state update correctly

### 16. Separates session and window histories
- confirm completed jobs appear in the right structures

### 17. Recovers from restart
- persist state mid-session
- restart process
- confirm state resumes cleanly

## Output tests

### 18. Emits standard operator message
- confirm all expected fields are present
- confirm hold reasons are explicit
