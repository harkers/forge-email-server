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

## Human workflow

Use the web UI to:

- create projects
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

The recent activity feed is rendered in a human-friendly format rather than as raw event JSON.

## Automation workflow

Use the API to:

- create or update projects from other systems
- add tasks as milestones or next actions
- mark items blocked/done/in-progress
- query open or blocked work
- generate rollups via summary endpoint
- emit MCP update events

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
