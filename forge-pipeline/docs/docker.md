# Forge Pipeline Docker Deployment

Forge Pipeline can now be run as a small two-container setup:

- `api` — Python API service on port `4181`
- `web` — Nginx serving the UI and proxying `/api/` to the API on port `4173`

## Why this shape

This keeps deployment simple:

- one container for shared data/API logic
- one container for static UI + reverse proxy
- persisted JSON storage mounted from the host

It also removes the earlier hardcoded localhost API assumption by serving the UI and API under the same web origin.

## Files

- `Dockerfile.api`
- `Dockerfile.web`
- `docker-compose.yml`
- `deploy/nginx/default.conf`

## Run

```bash
docker compose up --build
```

## Default ports

- UI: `http://localhost:4173`
- API direct: `http://localhost:4181`
- UI-routed API: `http://localhost:4173/api/health`

## Persistence

The API uses:

- `./api/storage` mounted into the API container

That means the shared JSON data survives container restarts.

## Deployment notes

For Proxmox or a VPS, the most likely next step is to put this behind:

- Nginx Proxy Manager
- Caddy
- Traefik
- or your existing reverse proxy

## Recommended next improvements before public exposure

- auth / API key support
- audit/event log
- request validation hardening
- possible move from JSON file to SQLite if write volume grows
