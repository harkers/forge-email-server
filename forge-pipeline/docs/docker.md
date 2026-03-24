# Forge Pipeline Docker Deployment

Forge Pipeline runs as a small two-container setup:

- `api` — Python API service on port `4181`
- `web` — Nginx serving the UI and proxying `/api/` to the API on port `4173`

## Why this shape

This keeps deployment simple:

- one container for shared data/API logic
- one container for static UI + reverse proxy
- persisted SQLite storage mounted from the host

It also serves the UI and API under the same web origin.

## Files

- `Dockerfile.api`
- `Dockerfile.web`
- `docker-compose.yml`
- `deploy/nginx/default.conf`
- `.env.example`

## Run

```bash
cp .env.example .env
docker compose up --build
```

## Default ports

- UI: `http://localhost:4173`
- API direct: `http://localhost:4181`
- UI-routed API: `http://localhost:4173/api/health`

## Auth

Write protection is controlled by:

- `FORGE_PIPELINE_API_KEY`

If set:
- reads stay open
- writes require `X-API-Key`

## Persistence

The API uses:

- `./api/storage` mounted into the API container

Primary database file:
- `forge-pipeline.db`

## Migration note

If legacy JSON files are present in `api/storage/`, the API migrates them into SQLite on startup.

## Recommended next improvements before public exposure

- stronger auth model if internet-exposed
- richer audit/event views
- request validation hardening
