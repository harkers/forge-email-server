# Forge Pipeline Deployment Framework

Forge Pipeline now includes a more deployment-oriented Docker framework.

## Included

- root `docker-compose.yml` for local/dev usage
- `deploy/compose/docker-compose.prod.yml` for production-style image deployment
- reverse proxy examples:
  - `deploy/examples/Caddyfile`
  - `deploy/examples/nginx.conf`

## Deployment shape

### API container
- serves the Forge Pipeline API
- stores SQLite data under mounted `api/storage`

### Web container
- serves the UI via Nginx
- proxies `/api/` to the API container internally

## Typical deploy flow

### 1. Build images

```bash
docker build -f Dockerfile.api -t forge-pipeline-api:latest .
docker build -f Dockerfile.web -t forge-pipeline-web:latest .
```

### 2. Set environment

```bash
cp .env.example .env
```

### 3. Start stack

```bash
docker compose -f deploy/compose/docker-compose.prod.yml up -d
```

## Persistence

Ensure persistent storage exists for:
- `api/storage/`
- backup/export files if retained locally

## Reverse proxy

You can place the stack behind:
- Caddy
- Nginx
- Nginx Proxy Manager
- Traefik

Use the included examples as a starting point.

## Recommended deployment checklist

- set `FORGE_PIPELINE_API_KEY`
- keep `api/storage/` on persistent disk
- verify healthchecks pass
- test backup rotation after deployment
- confirm webhook/MCP integrations can reach the deployed API

## Related docs

- `docs/image-publishing.md`
