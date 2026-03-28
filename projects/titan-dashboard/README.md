# Titan Dashboard (Homepage)

Internal launcher dashboard for Titan services using Homepage with Docker label discovery.

## Architecture

- **Homepage** — launcher UI with Docker label discovery
- **Nginx** — reverse proxy front door (existing)
- **Docker labels** — registration mechanism for services
- **docker-socket-proxy** — secure read-only Docker API access

## Status

- **Phase**: planning
- **Next**: deploy Homepage container, configure Nginx route

## Quick Start

```bash
cd /opt/homepage
docker compose up -d
```

## Configuration

- `docker-compose.yml` — container definitions
- `config/settings.yaml` — global settings (title, theme, target: _blank)
- `config/docker.yaml` — Docker integration via socket proxy
- `config/custom.css` — 125×125 launcher tile styling
- `config/services.yaml` — manual overrides for non-Docker services
- `config/widgets.yaml` — system widgets (datetime, resources)

## Label Standard

Every Dockerized service adds Homepage labels:

```yaml
labels:
  - homepage.group=Core
  - homepage.name=OpenClaw
  - homepage.icon=mdi-robot-outline
  - homepage.href=https://openclaw.titan.local
  - homepage.description=Agent orchestration
  - homepage.weight=5
```

Homepage auto-discovers labeled containers through the Docker proxy.

## Groups

| Group | Services |
|-------|----------|
| Core | OpenClaw, Homepage, Nginx, Authentik, Trilium |
| Infra | Proxmox, Portainer, Grafana, Uptime Kuma |
| Forge | Forge Pipeline, ForgeHome, ForgeGarden |
| Labs | Ollama, Stable Diffusion, test apps |

## Security Notes

- Homepage has no built-in auth; Nginx + Authentik handle access control
- Docker socket accessed via restricted proxy, not direct mount
- HOMEPAGE_ALLOWED_HOSTS limits which hosts can access