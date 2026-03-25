# Forge Pipeline — Implementation Spec

## Product intent
Forge Pipeline is the operational workspace for tracking projects, actions, notes, momentum, blockers, and change across Forge modules.

It should answer:
- What needs attention now?
- What is blocked?
- What changed recently?
- What is becoming risky?
- What should happen next?

## MVP outcome
The first usable version should let a user:
- view active work across sources
- see a prioritised Next up queue
- see blockers clearly
- see recent activity with timestamps
- understand top-level counts
- trust source freshness
- spot overdue or stale work quickly

## Canonical state model

### Task status
- todo
- in_progress
- blocked
- done
- archived

### Priority
- low
- medium
- high
- critical

### Risk state
- none
- watch
- at_risk
- critical

### Time state
- on_track
- due_soon
- overdue
- stale

### Source state
- healthy
- delayed
- error
- paused

## Rules engine
- Due soon: task due within 7 days and not done
- Overdue: due date passed and not done
- Stale: no meaningful update in 5 working days
- At risk: high priority due soon, blocked >48h, overdue, or stale high-priority work
