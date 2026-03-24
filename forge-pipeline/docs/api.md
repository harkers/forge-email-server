# Forge Pipeline API

Base URL:

- local default: `http://localhost:4181`

This API is intended to become the shared data layer for Forge Pipeline so other tools, automations, or MCP pipeline components can update project state.

## Endpoints

### Health

- `GET /api/health`

### Summary

- `GET /api/summary`

Returns high-level counts:
- projects
- tasks
- open tasks
- done tasks
- blocked tasks

### Projects

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{projectId}`
- `PUT /api/projects/{projectId}`
- `PATCH /api/projects/{projectId}`
- `DELETE /api/projects/{projectId}`

Query params for list:
- `q` — search text
- `status` — filter by project status

Project object fields:
- `id`
- `name`
- `description`
- `notes`
- `status`
- `tags[]`
- `updatedAt`
- `tasks[]`

### Tasks

- `GET /api/tasks`
- `GET /api/projects/{projectId}/tasks`
- `POST /api/projects/{projectId}/tasks`
- `PUT /api/projects/{projectId}/tasks/{taskId}`
- `PATCH /api/projects/{projectId}/tasks/{taskId}`
- `DELETE /api/projects/{projectId}/tasks/{taskId}`

Query params for task list endpoints:
- `q` — search text
- `status` — filter by task status

Task object fields:
- `id`
- `title`
- `status`
- `priority`
- `dueDate`
- `tags[]`
- `notes`
- `updatedAt`

### Bulk import / replace

- `POST /api/bulk/import`

Body format:

```json
{
  "projects": [ ... ]
}
```

Use this carefully: it replaces the entire stored project list.

## Example requests

### Create project

```bash
curl -X POST http://localhost:4181/api/projects \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Forge Pipeline",
    "description": "Central project board",
    "notes": "Used to answer what is next.",
    "status": "active",
    "tags": ["hub", "planning"]
  }'
```

### Add task to project

```bash
curl -X POST http://localhost:4181/api/projects/<projectId>/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Define MCP sync contract",
    "status": "todo",
    "priority": "high",
    "dueDate": "2026-03-30",
    "tags": ["api", "mcp"],
    "notes": "Other projects should be able to push status updates here."
  }'
```

### Patch task status

```bash
curl -X PATCH http://localhost:4181/api/projects/<projectId>/tasks/<taskId> \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "done"
  }'
```

## MCP / automation fit

Good patterns for external tools:
- create one project per tracked initiative
- append/update tasks as milestones move
- use tags for source system labels (`display-forge`, `privacy`, `mcp`, `ops`)
- use `PATCH` for lightweight status changes
- use `GET /api/summary` for dashboard rollups
- use `GET /api/tasks?status=blocked` to identify blockers quickly
