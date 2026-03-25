# Packet Schemas

Use JSON packets when the workflow needs deterministic machine-readable handoff.

## Task packet fields

Recommended minimum:
- `task_id`
- `parent_task_id` if derived from another task
- `assigned_agent`
- `created_at`
- `priority`
- `objective`
- `inputs`
- `constraints`
- `expected_output`
- `status`

Suggested status values:
- `queued`
- `claimed`
- `processing`
- `completed`
- `failed`
- `rejected`

## Result packet fields

Recommended minimum:
- `task_id`
- `agent`
- `status`
- `completed_at`
- `summary`
- `outputs`
- `review_required`
- `confidence`
- `issues`

Suggested confidence values:
- `low`
- `medium`
- `high`

## Why packets help
- deterministic handoff
- easier audit and replay
- easier queue inspection
- easier future upgrade to a metadata store or dashboard

## Recommended queue layout

```text
queue/
  inbox/
  claimed/
  done/
  failed/
artifacts/
  <task-id>/
state/
  tasks/
  reviews/
```

## Review rule

Route completed worker output back through the manager/control-plane role before:
- external sends
- publication
- authoritative record writes
- downstream triggering with side effects
