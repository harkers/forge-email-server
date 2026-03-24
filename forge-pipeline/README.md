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
- Support straightforward Docker deployment

## Structure

- `app/` — browser UI
- `api/` — file-backed HTTP API and storage
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

### API
- health endpoint
- summary endpoint
- project CRUD
- task CRUD
- search/filter support
- bulk import endpoint
- intended MCP-friendly shared data layer

### Deployment
- Docker API image
- Docker web image
- docker-compose setup
- Nginx reverse proxy config for `/api`

## Run locally without Docker

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

## Run with Docker

```bash
docker compose up --build
```

Then open:
- Web UI: `http://localhost:4173`
- API health via web proxy: `http://localhost:4173/api/health`

## Documentation

- `docs/overview.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/usage.md`
- `docs/mcp-integration.md`
- `docs/data-model.md`
- `docs/docker.md`
