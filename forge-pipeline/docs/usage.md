# Forge Pipeline Usage Guide

## Run locally

### Start the API

```bash
cd api
python3 server.py
```

### Start the web UI

```bash
./scripts/serve.sh
```

### Open locally

- Web UI: `http://localhost:4173`
- API: `http://localhost:4181`

## Project status model

Forge Pipeline now supports these project-level statuses:

- `on-track` — On Track / Green
- `at-risk` — At Risk / Yellow
- `off-track` — Off Track / Red
- `not-started` — Not Started / Pending
- `in-progress` — In Progress / Active
- `blocked` — Blocked / On Hold
- `completed` — Completed / Done
- `overdue` — Overdue
- `cancelled` — Cancelled

These are distinct from task statuses.

## Human workflow

Use the web UI to:

- create projects
- set project status
- update project descriptions and notes
- add tasks to projects
- update task status, priority, due date, tags, and notes
- search for tasks/projects
- filter by task status
- inspect recent API/MCP activity in the sidebar audit log
- use dashboard sections for:
  - **Next up** — likely priority work to tackle next
  - **Blocked** — currently stuck work
  - **Recently changed** — freshest task movement

The UI also polls the API automatically and shows a live refresh status indicator.

## Automation workflow

Use the API to:

- create or update projects from other systems
- set project status using the project status model above
- add tasks as milestones or next actions
- mark items blocked/done/in-progress
- query open or blocked work
- generate rollups via summary endpoint
- emit MCP update events
- push webhook updates from external systems

## Suggested conventions

### Project level

Use one project per initiative, product, or stream of work.

Examples:
- `Display Forge`
- `Privacy / DSAR`
- `MCP Pipeline`
- `Ops / Infra`

### Task level

Keep tasks actionable and specific.

Good:
- `Add API auth`
- `Define MCP sync contract`
- `Investigate feed error handling`

Less good:
- `Work on project`

### Tags

Use tags for:
- source system
- area/domain
- urgency
- technical grouping

Examples:
- `mcp`
- `privacy`
- `api`
- `blocked`
- `ops`
