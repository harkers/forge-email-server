# Forge Pipeline

Forge Pipeline is the workspace's central project and task hub.

It is designed to answer:

- what is in flight?
- what is blocked?
- what should happen next?
- what has already been completed?

It combines:
- a polished browser UI for human use
- a shared file-backed API for automation and MCP integration
- a simple portable JSON storage model for early development

## Goals

- Track actions by project
- Maintain rich notes alongside tasks
- Provide a polished browser-based interface
- Expose a proper shared data layer for MCP pipeline integration
- Become the central operational board across multiple projects

## Structure

- `app/` — browser UI
- `api/` — file-backed HTTP API and storage
- `docs/` — overview, architecture, API, usage, and integration notes
- `notes/` — product notes, planning, and decisions
- `scripts/` — helper scripts

## Current Capabilities

### Web UI
- create/edit/delete projects
- create/edit/delete tasks
- edit task status, priority, due date, tags, and notes
- edit project notes and descriptions inline
- search across projects/tasks/tags
- filter by task status

### API
- health endpoint
- summary endpoint
- project CRUD
- task CRUD
- search/filter support
- bulk import endpoint
- intended MCP-friendly shared data layer

## Run locally

### API

```bash
cd api
python3 server.py
```

### Web UI

```bash
./scripts/serve.sh
```

### Default local URLs

- Web UI: `http://localhost:4173`
- API: `http://localhost:4181`

## Documentation

- `docs/overview.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/usage.md`
- `docs/mcp-integration.md`
- `docs/data-model.md`
