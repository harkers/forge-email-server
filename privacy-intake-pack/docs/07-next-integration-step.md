# Next Integration Step: Privacy Skill Handoff

The worker in this pack is a placeholder designed to prove the event model and audit trail.

## Replace the placeholder with one of these patterns

### Pattern A: local webhook
The worker calls a local endpoint exposed by your orchestration layer.

### Pattern B: queue table
The worker inserts into a downstream work queue table and updates status as the privacy skill picks up work.

### Pattern C: file drop
The worker writes structured JSON jobs into a watched directory.

## Recommended first production move

Use a queue-table or webhook model so that:
- case creation stays fast
- downstream skill processing is decoupled
- retry logic can be tracked cleanly
- every handoff can be recorded as a `task_event`

## Recommended extra event types for live integration

- `handoff_requested`
- `handoff_acknowledged`
- `prompt_prepared`
- `model_selected`
- `model_run_started`
- `model_run_completed`
- `review_requested`
- `review_completed`
- `artefact_published`
