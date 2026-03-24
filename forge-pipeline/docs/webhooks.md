# Forge Pipeline Webhook Endpoint

Forge Pipeline now supports a generic webhook endpoint for external systems.

## Endpoint

- `POST /api/webhook`

Authentication:
- same API key model as other write endpoints
- send `X-API-Key` when write protection is enabled

## Purpose

This endpoint gives external tools a single write entrypoint without needing to know the full MCP-specific route layout.

## Supported actions

### 1. `project_upsert`

Create or update a project.

Example:

```json
{
  "action": "project_upsert",
  "source": "display-forge",
  "name": "Display Forge",
  "description": "Signage platform work",
  "status": "active",
  "tags": ["platform"]
}
```

### 2. `task_upsert`

Create or update a task under a project.

Example:

```json
{
  "action": "task_upsert",
  "source": "display-forge",
  "projectName": "Display Forge",
  "title": "Stabilise playback route",
  "status": "in-progress",
  "priority": "high",
  "tags": ["frontend", "player"]
}
```

### 3. `project_update`

Apply a project-level update.

Example:

```json
{
  "action": "project_update",
  "source": "display-forge",
  "projectId": "display-forge",
  "summary": "Playback shell stable, API still evolving",
  "note": "Need to test reconnect behaviour next.",
  "status": "active"
}
```

### 4. `event`

Record a generic webhook event.

Example:

```json
{
  "action": "event",
  "source": "mcp-pipeline",
  "kind": "sync",
  "payload": {
    "message": "nightly sync complete",
    "itemsUpdated": 14
  }
}
```

## Automatic source tagging

If `source` is present, Forge Pipeline automatically applies:
- `source:<value>`

to relevant project/task records where appropriate.

## Response shape

Successful responses return:

```json
{
  "ok": true,
  ...
}
```

Validation failures return:

```json
{
  "error": "validation_error",
  "message": "...",
  "field": "..."
}
```
