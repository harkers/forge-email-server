# Forge Pipeline Deployment Guide

## Quick Deploy

```bash
cd /home/stu/.openclaw/workspace/forge-pipeline
docker-compose up -d --build
```

## Current Status

**Built:** v1.0.1 (2026-03-24)
- ForgeOrchestra design system integrated
- Version control and timestamp display added
- Obsidian Intelligence colour palette
- Luminous Platinum Blue accent (#7AA6FF)
- Port conflict resolved: now running on 4174

## Default Ports

- **UI:** `http://localhost:4174`
- **API (direct):** `http://localhost:4181`
- **API (via UI proxy):** `http://localhost:4174/api/health`

### Port 4173 / 4174 Note

Port 4173 is occupied by `openclaw-dynamic-ddh-web`, which runs in Docker host network mode and serves the DDH frontend. Forge Pipeline correctly runs on port 4174. Both services share the same API backend (port 4181). This is working as designed.

## Architecture

- **API container** (`forge-pipeline-api`): Python HTTP server on port 4181 (internal only)
- **Web container** (`forge-pipeline-web`): Nginx serving static UI + proxying `/api/` to API
- **Storage**: SQLite database mounted from `./api/storage/`

## Health Checks

Both containers have healthchecks:
- API: HTTP GET `/api/health`
- Web: HTTP GET `/`

Check status:
```bash
docker-compose ps
curl http://localhost:4174/api/health
```

## Environment Variables

Set in `.env` file:
```bash
FORGE_PIPELINE_API_KEY=your-secret-key-here
```

If `FORGE_PIPELINE_API_KEY` is set:
- Read operations (GET) remain open
- Write operations (POST/PUT/PATCH/DELETE) require `X-API-Key` header

## URLs

- **UI**: `http://localhost:4174`
- **API (direct)**: `http://localhost:4181`
- **API (via UI proxy)**: `http://localhost:4174/api/health`

## Logs

```bash
docker-compose logs -f
docker-compose logs -f api
docker-compose logs -f web
```

## Rebuild & Redeploy

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Production Considerations

### Before exposing beyond localhost:

1. **Set API key** in `.env`
2. **Place behind TLS-terminating reverse proxy** (your existing nginx, Caddy, Traefik)
3. **Persist `./api/storage/`** on durable disk
4. **Monitor container health** via your host tooling
5. **Consider rate limiting** if internet-exposed
6. **Review webhook auth** if accepting external events

### Recommended deployment pattern:

- Expose only the **web container** externally
- Let internal nginx proxy `/api/` to API container
- Keep API container on internal network only
- Single origin avoids CORS complexity

## Redis Cache Integration (TODO)

Future enhancement: add Redis for:
- Summary endpoint caching (project/task counts)
- Event log read caching
- Rate limiting if internet-exposed

```yaml
services:
  redis:
    image: redis:alpine
    container_name: forge-pipeline-redis
    restart: unless-stopped
    expose:
      - "6379"
```

API would need modification to use Redis for hot paths.

---

**ForgeOrchestra Design System:** See `/forgeorchestra/DESIGN_GUIDE.md`
