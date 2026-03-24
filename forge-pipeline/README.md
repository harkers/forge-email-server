# Forge Pipeline

Project workspace for a project-based todo system with a fancy web display, extensive notes, and the usual scaffolding.

## Goals

- Track actions by project
- Maintain rich notes alongside tasks
- Provide a polished browser-based interface
- Keep data simple and portable during early development
- Become the central board for "where am I at and what do I do next?"
- Expose a proper data/API layer for MCP pipeline integration

## Structure

- `app/` — web app source
- `app/data/` — original starter seed data
- `api/` — file-backed Forge Pipeline API
- `docs/` — API documentation and support docs
- `notes/` — product notes, planning, and decisions
- `scripts/` — helper scripts

## Current Features

### Web app
- Project list with inline editing
- Add/delete projects
- Per-project task list
- Add/delete tasks
- Edit task title, status, priority, due date, tags, and notes
- Rich project notes
- Search across projects/tasks/tags
- Filter tasks by status
- API-backed shared data model

### API
- File-backed JSON data store
- Project CRUD endpoints
- Task CRUD endpoints
- Summary endpoint
- Search/filter support
- Bulk import endpoint for automation workflows
- Intended for MCP / pipeline integration

## Running It

### Start the API

```bash
cd api
python3 server.py
```

### Start the web app

```bash
./scripts/serve.sh
```

Then open the app in a browser.

Default endpoints:
- Web UI: `http://localhost:4173`
- API: `http://localhost:4181`

## API Docs

See:
- `docs/api.md`
