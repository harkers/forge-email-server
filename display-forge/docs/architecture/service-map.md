# Display Forge — Service Map

## Runtime Services

### db

Purpose:
- persistent PostgreSQL database

Stores:
- campaigns
- feeds
- schedules
- playlist snapshots
- audit logs
- screen/device state

### api

Purpose:
- primary backend API

Responsibilities:
- campaign CRUD
- media metadata handling
- feed configuration
- schedule/rule evaluation
- playlist generation endpoints
- health and event endpoints

### worker

Purpose:
- background processing

Responsibilities:
- RSS polling
- content normalization
- expiry/archive jobs
- cache preparation
- maintenance routines

### admin-ui

Purpose:
- administrator-facing web UI

Responsibilities:
- dashboard
- campaign editor
- content library
- feed manager
- playlist preview
- health/status panels

### player-ui

Purpose:
- signage playback frontend

Responsibilities:
- render active playlist
- preload/cycle assets
- handle offline-safe playback behaviour
- report playback status and heartbeat

## Data / Control Flow

1. Admin users create or edit campaigns in `admin-ui`.
2. `admin-ui` talks to `api`.
3. `worker` polls feeds and writes normalized content through shared database state.
4. `api` evaluates schedules and builds the current active playlist.
5. `player-ui` requests playlist data from `api` and renders the output.
6. `player-ui` reports heartbeat/status back to `api`.
7. `db` stores persistent application state for all services.

## Mounted Storage

- `./storage/postgres` — PostgreSQL data
- `./storage/media` — uploaded and cached media assets
- `./storage/cache` — generated/cache files
- `./storage/logs` — service logs and operational output
- `./storage/backups` — backups/export bundles

## Environment Variables

Core variables are defined in `.env.example` and should be copied into `.env` before first run.

Key variables:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `API_PORT`
- `ADMIN_UI_PORT`
- `PLAYER_UI_PORT`
- `MEDIA_ROOT`
- `CACHE_ROOT`
- `RSS_POLL_INTERVAL_SECONDS`
- `PLAYER_HEARTBEAT_SECRET`
