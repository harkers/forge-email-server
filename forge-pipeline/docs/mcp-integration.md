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

## Suggested automation pattern

For each external project or automation:

1. call project upsert
2. call task upserts for major tasks/milestones
3. call project update when status or summary changes
4. optionally emit generic events for major syncs or failures

## Event visibility

Recent events can be inspected via:
- `GET /api/events`

This gives a lightweight operational trail even before a full audit system exists.

## Caveat

These endpoints are still file-backed and lightweight.
They are suitable for modest automation and MCP usage, but not yet a high-concurrency event bus.
