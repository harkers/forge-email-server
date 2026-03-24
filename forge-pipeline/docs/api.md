# Forge Pipeline API

Base URL:

- local default direct API: `http://localhost:4181`
- via Docker web proxy: `http://localhost:4173/api`

This API is intended to become the shared data layer for Forge Pipeline so other tools, automations, or MCP pipeline components can update project state.

## Authentication

Forge Pipeline supports a simple API key for write operations.

Environment variable:
- `FORGE_PIPELINE_API_KEY`

Header:
- `X-API-Key: <your-key>`

Behaviour:
- `GET` endpoints remain open by default so the UI can read shared state
- `POST`, `PUT`, `PATCH`, and `DELETE` require a valid API key **if** `FORGE_PIPELINE_API_KEY` is set
- if no key is configured, the API behaves as open/writeable as before

## Core endpoints

### Health
- `GET /api/health`

### Summary
- `GET /api/summary`

### Projects
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{projectId}`
- `PUT /api/projects/{projectId}`
- `PATCH /api/projects/{projectId}`
- `DELETE /api/projects/{projectId}`

### Tasks
- `GET /api/tasks`
- `GET /api/projects/{projectId}/tasks`
- `POST /api/projects/{projectId}/tasks`
- `PUT /api/projects/{projectId}/tasks/{taskId}`
- `PATCH /api/projects/{projectId}/tasks/{taskId}`
- `DELETE /api/projects/{projectId}/tasks/{taskId}`

### Bulk import
- `POST /api/bulk/import`

### Events
- `GET /api/events?limit=50`

Returns the latest recorded API/MCP activity entries.

## MCP-friendly event/update endpoints

These are intended to reduce friction for automation workflows.

### Project upsert
- `POST /api/mcp/project-upsert`

Purpose:
- create a project if it does not exist
- update it if it already exists by `id` or `name`

Example:

```bash
curl -X POST http://localhost:4181/api/mcp/project-upsert \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: change-me' \
  -d '{
    "name": "MCP Pipeline",
    "description": "Shared automation control plane",
    "notes": "Feeds status into Forge Pipeline.",
    "status": "active",
    "tags": ["mcp", "automation"]
  }'
```

### Task upsert
- `POST /api/mcp/task-upsert`

Purpose:
- create/update a task under a project using `projectId` or `projectName`
- match existing task by `id` or `title`

Example:

```bash
curl -X POST http://localhost:4181/api/mcp/task-upsert \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: change-me' \
  -d '{
    "projectName": "MCP Pipeline",
    "title": "Define sync contract",
    "status": "in-progress",
    "priority": "high",
    "tags": ["mcp", "api"],
    "notes": "Need stable write/update semantics."
  }'
```

### Project update event
- `POST /api/mcp/project-update`

Purpose:
- append/update project-level state without replacing the whole object
- useful for status snapshots from another system

Supported fields:
- `projectId`
- `summary`
- `note`
- `status`
- `tags[]`

### Generic MCP event
- `POST /api/mcp/event`

Purpose:
- record a general event even when it is not directly mapped to a project/task mutation

Body example:

```json
{
  "source": "display-forge",
  "kind": "sync",
  "payload": {
    "message": "nightly sync complete",
    "itemsUpdated": 12
  }
}
```

## MCP / automation fit

Good patterns for external tools:
- create one project per tracked initiative
- use `project-upsert` to avoid duplicate project creation
- use `task-upsert` for milestone/task sync
- use `project-update` for higher-level status snapshots
- use `GET /api/summary` for dashboard rollups
- use `GET /api/tasks?status=blocked` to identify blockers quickly
- use `GET /api/events` to inspect recent automation activity
