# Data Model

## Core principle

Do not model workflow history as a mutable note field. Model it as events.

## Tables

### cases
Primary intake record.

### case_metadata
Flexible structured attributes stored in `jsonb`.

### tasks
Workflow units created from a case.

### task_events
Append-only event stream recording what happened, when, and why.

### artefacts
References to generated documents, exports, or uploaded files.

### access_audit
Application-level access audit for viewing and admin actions.

## Event strategy

Every meaningful action creates a `task_events` row.

Examples:
- `case_created`
- `validation_passed`
- `task_created`
- `task_dispatched`
- `worker_started`
- `commentary_added`
- `status_changed`
- `skill_handoff_requested`
- `skill_handoff_recorded`
- `artefact_created`
- `task_completed`
- `task_failed`

## Commentary design

Each event includes:
- `summary` for concise timeline display
- `commentary` for full human-readable detail
- `payload_jsonb` for machine-readable context
- `event_at` for exact audit timestamp

This supports:
- human review
- operational debugging
- audit export
- future analytics

## Time policy

- Store timestamps as `timestamptz`
- Use UTC in the database
- Present localised timestamps in the UI if desired
