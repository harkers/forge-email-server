# Forge Pipeline Architecture

## Runtime components

### 1. Web UI

Location:
- `app/public/`

Purpose:
- human-facing project board
- inline editing of projects and tasks
- search/filter interface
- visual summary of open/done work

### 2. API layer

Location:
- `api/server.py`

Purpose:
- shared data access layer
- CRUD for projects and tasks
- summary endpoint
- filtering/search support
- automation and MCP integration surface

### 3. Storage layer

Location:
- `api/storage/forge-pipeline.json`

Purpose:
- persistent project/task state
- simple portable JSON store for early-stage development

## Data flow

### Human flow

1. user opens the web UI
2. web UI calls the API
3. API reads/writes the JSON store
4. UI refreshes from shared state

### Automation flow

1. external tool or MCP pipeline calls API
2. API updates project/task records
3. web UI reflects new state on next refresh or reload

## Design principles

- keep the source of truth shared
- keep the storage simple at first
- optimize for clarity over cleverness
- make it easy for other systems to push status updates
- support both human and machine updates without diverging models

## Current limitations

- no auth yet
- JSON file store is simple but not concurrency-heavy
- no formal event log yet
- no websocket/live update layer yet

## Expected next architectural step

If usage grows, the likely next progression is:

- add auth
- add activity/event logging
- add API endpoints for upsert/event-style writes
- eventually move from flat JSON file to SQLite or PostgreSQL if needed
