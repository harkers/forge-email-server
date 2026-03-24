# Forge Pipeline MCP Deployer Skill

## Purpose

Deploy Forge Pipeline (ddh) via the MCP deployer tool with cross-machine network access. Uses host network mode for direct binding to titan's interfaces.

## Configuration

Add to `TOOLS.md`:

```markdown
### MCP Deployer Settings

- **Registry**: `localhost:5000` (on titan)
- **Host**: titan (192.168.10.80 LAN, 100.117.50.105 Tailscale)
- **Images**:
  - `localhost:5000/ddh-web:latest` (port 4173)
  - `localhost:5000/ddh-api:latest` (port 4181)
- **Network**: host mode (direct interface binding)
- **Access**:
  - LAN: `http://192.168.10.80:4173` / `http://192.168.10.80:4181`
  - Tailscale: `http://100.117.50.105:4173` / `http://100.117.50.105:4181`
  - Local: `http://localhost:4173` / `http://localhost:4181`
```

## Deployment Workflow

### Step 1 — Push Images to Local Registry (on titan)

**Current images** (as of 2026-03-24):
```
localhost:5000/forge-pipeline-web   latest
localhost:5000/forge-pipeline-api   latest
```

**Tag for MCP deployer** (ddh-* names):
```bash
# Web container
DOCKER_API_VERSION=1.41 docker tag localhost:5000/forge-pipeline-web:latest localhost:5000/ddh-web:latest
DOCKER_API_VERSION=1.41 docker push localhost:5000/ddh-web:latest

# API container
DOCKER_API_VERSION=1.41 docker tag localhost:5000/forge-pipeline-api:latest localhost:5000/ddh-api:latest
DOCKER_API_VERSION=1.41 docker push localhost:5000/ddh-api:latest
```

**Note**: The MCP deployer expects `ddh-web` and `ddh-api` image names. Tag accordingly.

### Step 2 — Deploy via MCP Deployer Tool

#### Web Container (port 4173)

```json
{
  "label": "ddh-web",
  "image": "localhost:5000/ddh-web:latest",
  "listen_port": 4173,
  "pull": false,
  "auto_approve": false,
  "env": {
    "VITE_API_URL": "http://192.168.10.80:4181"
  }
}
```

#### API Container (port 4181)

```json
{
  "label": "ddh-api",
  "image": "localhost:5000/ddh-api:latest",
  "listen_port": 4181,
  "pull": false,
  "auto_approve": false,
  "env": {
    "NODE_ENV": "production",
    "PORT": "4181"
  }
}
```

**Critical Settings:**
- `auto_approve: false` — These apps are NOT MCP tool servers (no `/health`, `/tools`, `/call` endpoints). Don't let gateway try to register them as MCP tools.
- `pull: false` — Using local registry, no need to pull from remote.
- `listen_port` — Matches container's internal port (host network mode).

### Step 3 — Access from Other Machines

**Host network mode** means containers bind directly to titan's network interfaces — no port mapping needed.

| Interface | Web | API |
|-----------|-----|-----|
| LAN | `http://192.168.10.80:4173` | `http://192.168.10.80:4181` |
| Tailscale | `http://100.117.50.105:4173` | `http://100.117.50.105:4181` |
| Local (titan) | `http://localhost:4173` | `http://localhost:4181` |

## Vite Build Caveat

**Important**: If the web app has a hardcoded API URL baked into the Vite build (e.g., `VITE_API_URL=http://localhost:4181`), it won't resolve from other machines.

**Solution**: Rebuild with correct URL:
```bash
# For LAN access
VITE_API_URL=http://192.168.10.80:4181 npm run build

# For Tailscale access
VITE_API_URL=http://100.117.50.105:4181 npm run build

# Or use environment variable at runtime
```

## Tool Commands

### Check Current Images
```bash
docker images | grep -E "forge-pipeline|ddh"
```

### Tag and Push
```bash
# Adjust source image name based on what was built
DOCKER_API_VERSION=1.41 docker tag <source-image>:latest localhost:5000/ddh-web:latest
DOCKER_API_VERSION=1.41 docker push localhost:5000/ddh-web:latest

DOCKER_API_VERSION=1.41 docker tag <source-image>:latest localhost:5000/ddh-api:latest
DOCKER_API_VERSION=1.41 docker push localhost:5000/ddh-api:latest
```

### Deploy via MCP
```bash
# Use sessions_spawn or direct MCP tool call
# Depends on your MCP gateway setup
```

### Verify Deployment
```bash
# Health checks
curl http://192.168.10.80:4181/api/health
curl http://192.168.10.80:4173/

# Check running containers
docker ps | grep ddh

# View logs
docker logs ddh-web
docker logs ddh-api
```

### Stop/Remove
```bash
# Via MCP deployer tool (preferred)
# Or direct docker commands:
docker stop ddh-web ddh-api
docker rm ddh-web ddh-api
```

## Environment Variables

### Web Container
| Var | Value | Purpose |
|-----|-------|---------|
| `VITE_API_URL` | `http://192.168.10.80:4181` | API endpoint for frontend fetches |

### API Container
| Var | Value | Purpose |
|-----|-------|---------|
| `NODE_ENV` | `production` | Node runtime mode |
| `PORT` | `4181` | Internal port (matches listen_port) |
| `FORGE_PIPELINE_API_KEY` | `<your-key>` | Write protection (optional) |

## Network Architecture

```
┌─────────────────────────────────────────────────────────┐
│ titan (192.168.10.80 / 100.117.50.105)                  │
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │ ddh-web:4173    │    │ ddh-api:4181    │            │
│  │ (host network)  │    │ (host network)  │            │
│  └─────────────────┘    └─────────────────┘            │
│           │                    │                        │
│           └────────┬───────────┘                        │
│                    │                                    │
│         Direct bind to titan interfaces                 │
└────────────────────│────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    LAN:80     Tailscale:105   Local:4173/4181
    .10.80       .50.105        (titan only)
```

**No port mapping** — containers use host network stack directly.

## MCP Deployer Tool Shape

The MCP deployer expects this payload shape:

```json
{
  "label": "<container-name>",
  "image": "<registry>:<port>/<image>:<tag>",
  "listen_port": <number>,
  "pull": <boolean>,
  "auto_approve": <boolean>,
  "env": {
    "<KEY>": "<VALUE>"
  }
}
```

**Key fields:**
- `label`: Container name (used in docker ps, logs)
- `image`: Full image reference (registry must be reachable)
- `listen_port`: Port container binds to (host mode = direct)
- `pull`: Skip pull if using local registry
- `auto_approve`: Only true for actual MCP tool servers
- `env`: Runtime environment variables

## Troubleshooting

### Container Won't Start
- Check image exists: `docker images | grep ddh`
- Verify registry reachable: `curl -v http://localhost:5000/v2/_catalog`
- Check port conflict: `netstat -tlnp | grep 4173`

### Can't Access from Other Machines
- Verify host network mode (not bridge)
- Check firewall: `ufw status`
- Test from titan first: `curl http://localhost:4173`

### Web App API Calls Fail
- Rebuild with correct `VITE_API_URL`
- Check browser dev tools for CORS errors
- Verify API is responding: `curl http://192.168.10.80:4181/api/health`

### MCP Gateway Issues
- Gateway status: `openclaw gateway status`
- Deployer tool available: check MCP tool list
- Review gateway logs for deployment errors

## Version Notes

Tested with:
- Docker API version: 1.41
- Local registry: port 5000 on titan
- Network mode: host (cross-machine access)
- MCP deployer: OpenClaw gateway integration

## Security Notes

- `auto_approve: false` prevents MCP tool registration attempts
- API key auth for writes (if enabled via `FORGE_PIPELINE_API_KEY`)
- Host network mode exposes containers directly — ensure firewall rules appropriate
- Local registry (localhost:5000) only accessible from titan

## Related Skills

- `trilium-etapi` — Log deployment to Trilium daily summary
- `coding-agent` — Build images via background agent if needed
