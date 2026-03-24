# Forge Pipeline MCP Integration Notes

Forge Pipeline is intended to be a shared board that other projects can update programmatically.

## Good API usage patterns for MCP pipelines

### Create a project once

When a new initiative begins, create a project and keep reusing its ID.

### Add tasks for milestones or next steps

Examples:
- implementation milestone
- blocker discovered
- follow-up action required
- deployment step
- documentation gap

### Use PATCH for lightweight status changes

Examples:
- mark task `in-progress`
- mark task `blocked`
- mark task `done`
- update notes with fresh context

### Query for dashboards and triage

Useful calls:
- `GET /api/summary`
- `GET /api/tasks?status=blocked`
- `GET /api/tasks?status=todo`
- `GET /api/projects?q=display`

## Recommended integration model

For each external project or automation:

1. resolve/create the relevant project in Forge Pipeline
2. write important milestones as tasks
3. update status as work moves
4. append notes when context changes
5. use tags to identify source and domain

## Practical convention suggestion

Use tags to identify source pipelines.

Examples:
- `source:display-forge`
- `source:privacy-dsar`
- `source:mcp-pipeline`

Even though tags are currently free-form strings, using a pseudo-namespaced convention now will make later filtering cleaner.

## Important current caveat

This is currently a lightweight file-backed API.
That is good for speed and portability, but not yet designed for high-concurrency write storms or hostile network exposure.

Before exposing it broadly, add:
- auth
- request validation tightening
- audit/event logging
