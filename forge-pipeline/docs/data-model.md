# Forge Pipeline Data Model

## Project object

```json
{
  "id": "display-forge",
  "name": "Display Forge",
  "description": "Build the signage platform and playback stack.",
  "notes": "Focus on API, scheduling, playback resilience, and admin flow.",
  "status": "active",
  "tags": ["signage", "platform"],
  "updatedAt": "2026-03-24T10:00:00+00:00",
  "tasks": []
}
```

### Fields

- `id`: stable project identifier
- `name`: display name
- `description`: short summary
- `notes`: richer context
- `status`: current project state
- `tags[]`: labels for grouping/filtering
- `updatedAt`: ISO timestamp
- `tasks[]`: task collection

## Task object

```json
{
  "id": "task-123",
  "title": "Add API auth",
  "status": "todo",
  "priority": "high",
  "dueDate": "2026-03-30",
  "tags": ["api", "security"],
  "notes": "Protect the shared board before wider exposure.",
  "updatedAt": "2026-03-24T10:00:00+00:00"
}
```

### Fields

- `id`: stable task identifier
- `title`: concise actionable task title
- `status`: task state (`todo`, `in-progress`, `blocked`, `done`)
- `priority`: priority level (`low`, `medium`, `high`)
- `dueDate`: optional date string
- `tags[]`: labels for grouping/filtering
- `notes`: detailed task context
- `updatedAt`: ISO timestamp
