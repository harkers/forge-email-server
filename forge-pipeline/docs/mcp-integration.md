# Forge Pipeline MCP Integration Notes

Forge Pipeline is intended to be a shared board that other projects can update programmatically.

## Best integration path now

Use the MCP-specific endpoints rather than raw CRUD whenever possible.

Why:
- fewer round-trips
- less duplicate matching logic in external tools
- easier idempotent-ish updates
- better activity visibility via recorded events

## Recommended endpoint usage

### 1. `POST /api/mcp/project-upsert`
Use when:
- a project may or may not already exist
- you want to ensure it exists with current metadata

### 2. `POST /api/mcp/task-upsert`
Use when:
- you want to create/update a task under a project
- you want matching by task title or task id

### 3. `POST /api/mcp/project-update`
Use when:
- an external project wants to push a fresh summary
- you want to append a note
- you want to adjust project-level tags/status

### 4. `POST /api/mcp/event`
Use when:
- you want a lightweight audit-style event record
- there is no direct project/task mutation
- you want visibility into pipeline activity

## Source-aware tagging convention

Forge Pipeline now supports source-aware filtering in the UI.

Recommended convention:
- add source tags like `source:display-forge`
- add source tags like `source:mcp-pipeline`
- attach them to projects and/or tasks

This lets the board filter by origin and makes the dashboard, task views, and event feed much more usable.

## Suggested automation pattern

For each external project or automation:

1. call project upsert
2. include a stable source tag such as `source:display-forge`
3. call task upserts for major tasks/milestones
4. include the same source tag on tasks where useful
5. call project update when status or summary changes
6. optionally emit generic events for major syncs or failures

## Event visibility

Recent events can be inspected via:
- `GET /api/events`

This gives a lightweight operational trail even before a full audit system exists.

## Caveat

These endpoints are still lightweight and not a high-volume event bus.
They are meant for practical coordination, not infinite firehose theatre.
