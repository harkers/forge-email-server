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
- recent activity/audit display

### 2. API layer

Location:
- `api/server.py`

Purpose:
- shared data access layer
- CRUD for projects and tasks
- summary endpoint
- filtering/search support
- automation and MCP integration surface
- event/upsert endpoints for external tools

### 3. Storage layer

Location:
- `api/storage/forge-pipeline.db`

Purpose:
- persistent shared state
- SQLite-backed storage for projects, tasks, and events
- safer evolution path than a flat JSON file

## Data flow

### Human flow

1. user opens the web UI
2. web UI calls the API
3. API reads/writes SQLite
4. UI refreshes from shared state

### Automation flow

1. external tool or MCP pipeline calls API
2. API updates SQLite-backed state
3. event records are written for recent activity visibility
4. web UI reflects new state on next refresh or reload

## Design principles

- keep the source of truth shared
- keep the interface simple for both humans and tools
- make it easy for other systems to push status updates
- support both CRUD and higher-level event/upsert workflows
- use a storage layer that can handle modest concurrent access better than raw JSON

## Current limitations

- still lightweight and single-process
- no formal user model yet
- no websocket/live update layer yet
- not intended as a high-volume event bus

## Expected next architectural step

Likely next progression:

- stronger auth if internet-exposed
- richer audit/event views
- request validation tightening
- possibly move to a fuller app framework if complexity keeps growing
