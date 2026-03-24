# Forge Pipeline Docker Deployment

Forge Pipeline runs as a small two-container setup:

- `api` — Python API service on port `4181`
- `web` — Nginx serving the UI and proxying `/api/` to the API on port `4173`

## Why this shape

This keeps deployment simple:

- one container for shared data/API logic
- one container for static UI + reverse proxy
- persisted SQLite storage mounted from the host
- same-origin browser/API setup

## Files

- `Dockerfile.api`
- `Dockerfile.web`
- `docker-compose.yml`
- `deploy/nginx/default.conf`
- `.env.example`

## Quick start

```bash
cp .env.example .env
docker compose up --build -d
```

## Default ports

- UI: `http://localhost:4173`
- API direct: `http://localhost:4181`
- UI-routed API: `http://localhost:4173/api/health`

## Healthchecks

The compose file now includes healthchecks for:
- `api`
- `web`

That helps with:
- startup ordering
- restart visibility
- reverse-proxy confidence

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

This directory should live on persistent storage.

## Production-ish notes

For a cleaner deployment:

- keep `api/storage/` on persistent disk
- place the stack behind your existing reverse proxy if exposing beyond localhost
- do not expose direct API port publicly unless you mean to
- keep the API key in `.env`, not hardcoded into scripts
- monitor container health via `docker ps` or your host tooling

## Suggested reverse-proxy pattern

Expose only the web container externally and let Nginx inside it proxy `/api/` internally.

That gives you:
- one origin
- simpler browser behavior
- less CORS nonsense

## Useful commands

### Start

```bash
docker compose up --build -d
```

### Logs

```bash
docker compose logs -f
```

### Restart

```bash
docker compose restart
```

### Stop

```bash
docker compose down
```

## Recommended next improvements before wider exposure

- webhook endpoint for external systems
- stronger auth model if internet-exposed
- optional TLS/reverse-proxy examples
- live UI refresh/polling if multiple writers are expected
