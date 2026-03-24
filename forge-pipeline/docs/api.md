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

## Validation rules

The API performs tighter request validation.

### Project payloads
- `name`: required on create, string, max 200 chars
- `description`: string, max 5000 chars
- `notes`: string, max 5000 chars
- `status`: one of:
  - `on-track`
  - `at-risk`
  - `off-track`
  - `not-started`
  - `in-progress`
  - `blocked`
  - `completed`
  - `overdue`
  - `cancelled`
- `tags`: list of strings, max 50 items, max 64 chars each

### Task payloads
- `title`: required on create, string, max 200 chars
- `status`: one of `todo`, `in-progress`, `blocked`, `done`
- `priority`: one of `low`, `medium`, `high`
- `dueDate`: blank or `YYYY-MM-DD`
- `tags`: list of strings, max 50 items, max 64 chars each
- `notes`: string, max 5000 chars

### Validation errors

Invalid writes return:

```json
{
  "error": "validation_error",
  "message": "...",
  "field": "..."
}
```

with HTTP status `400`.

## Source tagging

MCP and webhook-oriented write flows support a `source` field.

When provided, the API automatically applies a matching source tag:
- `source:your-source`

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

### Export
- `GET /api/export`

### Webhook
- `POST /api/webhook`

## MCP-friendly event/update endpoints

### Project upsert
- `POST /api/mcp/project-upsert`

### Task upsert
- `POST /api/mcp/task-upsert`

### Project update event
- `POST /api/mcp/project-update`

### Generic MCP event
- `POST /api/mcp/event`
