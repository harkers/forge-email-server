# Forge Pipeline

Forge Pipeline is the workspace's central project and task hub.

It is designed to answer:

- what is in flight?
- what is blocked?
- what should happen next?
- what has already been completed?

It combines:
- a polished browser UI for human use
- a shared API for automation and MCP integration
- SQLite-backed persistent storage for projects, tasks, and events

## Goals

- Track actions by project
- Maintain rich notes alongside tasks
- Provide a polished browser-based interface
- Expose a proper shared data layer for MCP pipeline integration
- Become the central operational board across multiple projects
- Support straightforward Docker deployment
- Support API-key-protected write access for automations
- Support MCP-friendly upsert/event endpoints
- Surface recent activity directly in the UI

## Structure

- `app/` — browser UI
- `api/` — HTTP API and SQLite-backed storage
- `deploy/` — deployment configs such as Nginx
- `docs/` — overview, architecture, API, usage, integration, and Docker docs
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
- view recent audit/activity events in the sidebar

### API
- health endpoint
- summary endpoint
- project CRUD
- task CRUD
- search/filter support
- bulk import endpoint
- optional API-key-protected write access
- MCP-friendly project/task upsert endpoints
- MCP event/update endpoints
- lightweight event log endpoint

### Storage
- SQLite backend
- migration from legacy JSON files on startup

### Deployment
- Docker API image
- Docker web image
- docker-compose setup
- Nginx reverse proxy config for `/api`
- `.env.example` for API key config

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

Then open:
- Web UI: `http://localhost:4173`
- API health via web proxy: `http://localhost:4173/api/health`

## Run locally without Docker

### API

```bash
cd api
FORGE_PIPELINE_API_KEY=change-me python3 server.py
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
- `docs/docker.md`
