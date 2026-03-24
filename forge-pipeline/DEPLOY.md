# Forge Pipeline Deployment Guide

## Quick Deploy

```bash
cd /home/stu/.openclaw/workspace/forge-pipeline
docker-compose up -d --build
```

## Current Status

**Built:** v1.0.0 (2026-03-24)
- ForgeOrchestra design system integrated
- Version control and timestamp display added
- Obsidian Intelligence colour palette
- Luminous Platinum Blue accent (#7AA6FF)

## Port Conflict Resolution

If you see `bind: address already in use` for port 4173:

### Option 1: Stop host nginx (if you control the host)
```bash
sudo systemctl stop nginx
docker-compose up -d
```

### Option 2: Use alternate port
Edit `docker-compose.yml`:
```yaml
ports:
  - "4174:80"  # Change from 4173 to 4174
```
Then access at `http://localhost:4174`

### Option 3: Configure host nginx as reverse proxy
Add upstream in host nginx config:
```nginx
upstream forge_pipeline {
    server 127.0.0.1:4173;
}

server {
    listen 4173;
    location / {
        proxy_pass http://forge_pipeline;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

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
curl http://localhost:4173/api/health
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

- **UI**: `http://localhost:4173`
- **API (direct)**: `http://localhost:4181`
- **API (via UI proxy)**: `http://localhost:4173/api/health`

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
