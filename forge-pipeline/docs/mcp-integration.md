# Forge Pipeline MCP Integration Notes

Forge Pipeline is intended to be a shared board that other projects can update programmatically.

## Best integration path now

Use the MCP-specific endpoints rather than raw CRUD whenever possible.

Why:
- fewer round-trips
- less duplicate matching logic in external tools
- easier idempotent-ish updates
- better activity visibility via recorded events
- automatic source tagging now works when `source` is provided

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

## Automatic source tagging

Forge Pipeline now auto-applies source tags in MCP flows.

If you send:

```json
{
  "source": "display-forge"
}
```

then the API will add:

- `source:display-forge`

onto project/task tags where relevant.

That means you do not need to manually duplicate both:
- `source`
- and `tags: ["source:..."]`

though you still can if you want.

## Suggested automation pattern

For each external project or automation:

1. call project upsert with `source`
2. call task upserts with the same `source`
3. call project update when status or summary changes
4. optionally emit generic events for major syncs or failures

Example:

```json
{
  "projectName": "Display Forge",
  "title": "Stabilise playback route",
  "status": "in-progress",
  "priority": "high",
  "source": "display-forge"
}
```

This will automatically result in source-aware tagging for filtering in the UI.

## Event visibility

Recent events can be inspected via:
- `GET /api/events`

This gives a lightweight operational trail even before a full audit system exists.

## Caveat

These endpoints are still lightweight and not a high-volume event bus.
They are meant for practical coordination, not infinite firehose theatre.
