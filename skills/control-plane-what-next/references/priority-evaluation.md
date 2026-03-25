# Priority Evaluation Rules

## Priority Levels

### P0 — Critical (Do Now)
- Production is down
- Security vulnerability
- Data loss risk
- Blocks multiple other P0/P1 items
- Customer-facing outage

### P1 — High (Do Today/Tomorrow)
- Feature blocked waiting on this
- Performance degradation
- Important deadline approaching
- Dependencies at risk
- Multiple stakeholders affected

### P2 — Medium (Do This Week)
- Planned work
- Technical debt
- Quality improvements
- Documentation
- Minor dependencies

### P3 — Low (Do When Possible)
- Nice-to-haves
- Polish
- Exploration
- Backlog grooming

## Dependency Resolution

### Blocked By
If task A is blocked by task B:
- Task B gets priority boost
- Task A waits in queue
- Show dependency chain in evaluation

### Blocking
If task A blocks multiple tasks:
- Count blocked tasks
- Priority boost = number of blocked tasks * priority_weight
- Show "blocking X tasks" in justification

## Project Health Scoring

### Red (Unhealthy)
- Critical bugs
- No recent activity
- Missing documentation
- Failing tests

### Yellow (Needs Attention)
- Some open issues
- Minor bugs
- Documentation gaps
- Stale dependencies

### Green (Healthy)
- Active development
- Tests passing
- Documented
- Dependencies current

## Resource Considerations

### Model Availability
- Check model is loaded/available
- Prefer local models for non-critical work
- Reserve cloud models for P0/P1

### Token Budget
- Track session token usage
- Reserve budget for critical work
- Defer heavy tasks if budget low

### Time Estimates
- P0: Assume 2-4 hours
- P1: Assume 1-2 hours
- P2: Assume 30min-1hour
- P3: Assume ad-hoc

## Escalation

When multiple P0 items exist:
1. Compare impact (customer-facing > internal)
2. Compare blocked count (more blocked = higher priority)
3. Compare time estimate (shorter = quicker win)
4. Ask user if still unclear