# TOOLS.md - Local Notes

# Tool and Service Registry

This file is the operational registry for all locally deployed tools, services, integrations, automations, and managed runtimes used by this OpenClaw workspace.

**For the full tool registry, see `TITAN-TOOLS-REGISTRY.md`** which contains:
- All 212 MCP tools via proxy
- All 148 installed skills
- All 34 workspace skills
- Model providers (Ollama, llama.cpp lanes)
- Docker container status
- Network ports

Quick reference:
```bash
# List MCP tools
curl -s http://127.0.0.1:18100/tools | jq '.tools | map(.mcp_name) | sort'

# List installed skills
ls ~/.openclaw/skills/

# List workspace skills
ls ~/.openclaw/workspace/skills/

# List Ollama models
curl -s http://127.0.0.1:11434/api/tags | jq '.models[].name'
```

## Registry rule
Any OpenClaw-delivered capability that changes runtime behaviour or operator workflow must be added here before the task is considered complete.

## Required fields for each entry
Each entry must include:
- Name
- Project code
- Status
- Purpose
- Host / environment
- Workspace / owner
- Type
- Runtime location
- Access method
- Ports / sockets / bindings
- Authentication
- Storage / state paths
- Dependencies
- Start / stop / restart commands
- Validation commands
- Rollback steps
- Security notes
- Change impact / related services

## Entry template

### <Name>
- Project code:
- Status:
- Purpose:
- Host / environment:
- Workspace / owner:
- Type:
- Runtime location:
- Access method:
- Ports / sockets / bindings:
- Authentication:
- Storage / state paths:
- Dependencies:
- Start command:
- Stop command:
- Restart command:
- Validation:
- Rollback:
- Security notes:
- Change impact / related services:

## Titan-specific rule
Document all new:
- Docker services
- compose projects
- systemd units
- ports
- localhost bindings
- Unix sockets
- bind mounts
- persistent storage paths
- health checks
- operational commands
- rollback steps

If a change affects nginx, lighttpd, WordPress, Redis, MariaDB, Ollama, or existing published ports, note the interaction explicitly.

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

### Forge-Syslog-Collector
- Project code: OC-LOG-001
- Status: deployed (collector live; receiving Docker containers + pfSense via UDP and TLS)
- Purpose: Centralized syslog collector for Docker containers and network devices (pfSense)
- Host / environment: titan / Debian 12
- Workspace / owner: `/home/stu/.openclaw/workspace/forge-syslog-collector`
- Type: Docker Compose service (rsyslog + stunnel for TLS)
- Runtime location: `docker-compose.yml` in project workspace
- Access method: UDP/TCP syslog on port 5514, TLS on port 6514
- Ports / sockets / bindings:
  - `127.0.0.1:5514/tcp` - Docker containers (local)
  - `192.168.10.80:5514/tcp` - Plain TCP senders
  - `192.168.10.80:5514/udp` - pfSense native syslog (UDP)
  - `192.168.10.80:6514/tcp` - TLS syslog (syslog-ng from pfSense)
- Authentication: none for UDP/TCP; TLS uses self-signed CA
- Storage / state paths: `/data/appdata/forge-syslog-collector/logs`
  - `/data/appdata/forge-syslog-collector/logs/pfSense.harker.systems/` - pfSense logs by program
  - `/data/appdata/forge-syslog-collector/logs/<container-ip>/` - Docker container logs
- Dependencies: Docker, Docker Compose, `rsyslog/rsyslog:latest`, `dweomer/stunnel:latest`, logrotate (host)
- TLS certificates:
  - CA: `./tls/ca.crt` (distribute to pfSense)
  - Server cert: `./tls/server.crt`
  - Server key: `./tls/server.key`
  - Combined PEM: `./tls/stunnel.pem`
- Start command: `cd /home/stu/.openclaw/workspace/forge-syslog-collector && docker compose up -d`
- Stop command: `cd /home/stu/.openclaw/workspace/forge-syslog-collector && docker compose down`
- Restart command: `cd /home/stu/.openclaw/workspace/forge-syslog-collector && docker compose restart`
- Validation:
  - `docker compose ps`
  - `ss -tlnup | grep -E "(5514|6514)"` (should show UDP 5514, TCP 5514, TCP 6514)
  - `ls -la /data/appdata/forge-syslog-collector/logs/pfSense.harker.systems/`
  - `openssl s_client -connect 192.168.10.80:6514` (verify TLS cert)
- Log rotation:
  - Config: `/etc/logrotate.d/forge-syslog-collector`
  - Install: `sudo cp config/logrotate.conf /etc/logrotate.d/forge-syslog-collector`
  - Test: `sudo logrotate -d /etc/logrotate.d/forge-syslog-collector`
  - Force: `sudo logrotate -f /etc/logrotate.d/forge-syslog-collector`
  - Rotation: daily, 14-day retention, compressed
- Rollback:
  - `cd /home/stu/.openclaw/workspace/forge-syslog-collector && docker compose down`
  - `sudo rm /etc/logrotate.d/forge-syslog-collector`
  - revert docker-compose.yml to UDP-only
  - retain collected logs unless explicit purge is requested
- Security notes:
  - LAN binding (192.168.10.80) accepts syslog from trusted network only
  - pfSense IP (192.168.10.1) expected as source
  - TLS uses self-signed CA (distribute ca.crt to clients)
  - no reverse proxy involvement
  - no daemon-wide Docker log-driver change
- Change impact / related services:
  - no impact to nginx, lighttpd, WordPress, MariaDB, Redis, Ollama, or published ports
  - current logged sources: Docker containers (syslog driver), pfSense (UDP), pfSense (TLS)
- pfSense configuration (UDP):
  - Status → System Logs → Settings → Remote Logging
  - Enable: checked
  - Remote Log Servers: `192.168.10.80:5514`
  - Protocol: UDP (default)
- pfSense configuration (TLS/syslog-ng):
  - Install syslog-ng package (System → Package Manager → Available Packages)
  - Configure TLS source with ca.crt from this collector
  - Destination: `192.168.10.80:6514` with TLS

### OpenClaw Usage Dashboard
- Project code: OC-DASH-001
- Status: deployed (phase 1 local project)
- Purpose: Internal-only OpenClaw usage dashboard aggregating sessions, tokens, and cost by day/week/month while marking incomplete usage as unknown
- Host / environment: titan / Debian 12
- Workspace / owner: `/home/stu/.openclaw/workspace/projects/openclaw-usage-dashboard`
- Type: local Python HTTP service
- Runtime location: `/home/stu/.openclaw/workspace/projects/openclaw-usage-dashboard/openclaw_usage_dashboard.py`
- Access method: local browser to `http://127.0.0.1:8899`
- Ports / sockets / bindings: `127.0.0.1:8899/tcp` by default
- Authentication: none in phase 1; localhost-only binding
- Storage / state paths: reads `/home/stu/.openclaw/agents/main/sessions/sessions.json` and transcript `*.jsonl`; no separate database
- Dependencies: Python 3, OpenClaw session files on disk
- Start command: `cd /home/stu/.openclaw/workspace/projects/openclaw-usage-dashboard && python3 openclaw_usage_dashboard.py`
- Stop command: stop the foreground Python process or terminate its service wrapper if one is added later
- Restart command: rerun the start command
- Validation:
  - `curl -s http://127.0.0.1:8899/api/health | jq`
  - `curl -s http://127.0.0.1:8899/api/dashboard | jq '.stats, .summary.day[0], .recentSessions[0]'`
  - verify rows with missing provider usage display `unknown`
  - verify rows with real tokens but unreliable zero-cost persistence display `usageState: "reported"` and `costState: "unknown"`
- Rollback:
  - stop the dashboard process
  - remove any future launcher/proxy/service wrapper
  - optionally remove `projects/openclaw-usage-dashboard`
  - verify no listener remains on port 8899
- Security notes:
  - internal-only bind in phase 1
  - no gateway config changes
  - no reverse proxy exposure by default
  - treats incomplete local/OpenAI-compatible usage persistence as unknown rather than fake precision
- Change impact / related services:
  - reads existing OpenClaw session telemetry only
  - does not modify nginx, lighttpd, WordPress, MariaDB, Redis, Ollama, or published ports

### Titan Dashboard (Homepage)
- Project code: OC-DASH-002
- Status: planning
- Purpose: Internal launcher dashboard for Titan services using Homepage with Docker label discovery
- Host / environment: titan / Debian 12
- Workspace / owner: `/home/stu/.openclaw/workspace/projects/titan-dashboard`
- Type: Docker Compose service (Homepage + docker-socket-proxy)
- Runtime location: `deploy/docker-compose.yml` in project workspace
- Access method: Nginx reverse proxy at `dash.titan.local`
- Ports / sockets / bindings:
  - `127.0.0.1:3000/tcp` — Homepage HTTP
  - `127.0.0.1:2375/tcp` — Docker socket proxy (internal only)
- Authentication: none in Homepage; Nginx + Authentik handle access control
- Storage / state paths: `./config/` for settings, services, widgets, custom CSS/JS
- Dependencies: Docker, Docker Compose, Nginx (existing), `ghcr.io/gethomepage/homepage:latest`, `ghcr.io/tecnativa/docker-socket-proxy:latest`
- Start command: `cd /opt/homepage && docker compose up -d`
- Stop command: `cd /opt/homepage && docker compose down`
- Restart command: `cd /opt/homepage && docker compose restart`
- Validation:
  - `docker compose ps`
  - `curl -s http://127.0.0.1:3000 | head -20`
  - `curl -s https://dash.titan.local | head -20`
- Rollback:
  - `docker compose down`
  - remove `/opt/homepage` if needed
  - remove Nginx vhost config
- Security notes:
  - Homepage has no built-in auth; relies on Nginx/Authentik
  - Docker socket accessed via restricted proxy, not direct mount
  - HOMEPAGE_ALLOWED_HOSTS limits access
- Change impact / related services:
  - Nginx gains new vhost for `dash.titan.local`
  - No impact to existing services


### MCP Control Plane RAG Stack
- Project code: MCP-RAG-001
- Status: available (profile not started)
- Purpose: Document ingestion and semantic search for OpenClaw
- Host / environment: titan / Debian 12
- Workspace / owner: `/data/appdata/mcp-control-plane`
- Type: Docker Compose profile (`--profile rag`)
- Runtime location: `infra/docker-compose.yml` in MCP Control Plane
- Access method: MCP gateway tools `ingest_document`, `search_documents`
- Ports / sockets / bindings:
  - `embedding-worker` internal port 8080
  - Qdrant internal (profile-dependent)
- Authentication: MCP gateway authentication
- Storage / state paths: `/data/appdata/mcp-control-plane/data/`
- Dependencies: Docker, Docker Compose, OpenClaw MCP gateway
- Start command: `cd /data/appdata/mcp-control-plane && DOCKER_API_VERSION=1.41 docker compose -f infra/docker-compose.yml --profile rag up -d`
- Stop command: `cd /data/appdata/mcp-control-plane && DOCKER_API_VERSION=1.41 docker compose -f infra/docker-compose.yml --profile rag down`
- Validation:
  - `docker compose -f infra/docker-compose.yml --profile rag ps`
  - MCP gateway `ingest_document` and `search_documents` tools should be available
- Rollback:
  - `docker compose -f infra/docker-compose.yml --profile rag down`
  - No data loss if Qdrant storage preserved
- Security notes:
  - Internal-only embedding worker
  - Qdrant not exposed externally
  - Access only via MCP gateway
- Change impact / related services:
  - No impact to existing services
  - Provides RAG capability to OpenClaw through MCP tools

---

## Automation Gotchas

### GitHub Project CLI Field Updates

**Issue**: The `gh project item-edit` command cannot update single-select fields (like Workflow Stage) by name alone. It requires the specific option's internal ID.

**Current behavior**:
- Attempting to update a single-select field with `--text "In Progress"` fails with:
  ```
  GraphQL: Did not receive a single select option Id to update a field of type single_select
  ```
- The CLI doesn't expose single-select option IDs through standard commands
- `gh project field-list` returns field IDs only, not option IDs

**Workaround options**:
1. Use the GitHub GraphQL API directly to query field options and option IDs
2. Manually update via the GitHub web UI
3. Wait for `gh` CLI improvement

**Current DPM workflow impact**:
- The DPM hourly intake check runs successfully
- Project items can be updated with text fields (Assessment Notes, Attachments, Completion Summary)
- Workflow Stage updates currently require manual web UI action or GraphQL API call
- This creates a partial automation gap in the DPM workflow

**Resolution tracking**:
- Self-improvement entry: `LRN-20260330-001`, `ERR-20260330-001`, `LRN-20260331-001`, `LRN-20260331-003`
- Updated memory: `/home/stu/.openclaw/workspace/memory/2026-03-31.md`
- Status: documented limitation, workaround identified, waiting for CLI improvement

**Persistence across sessions (2026-03-31)**:
- First identified: 2026-03-30 09:56
- Second occurrence: 2026-03-31 00:36 (DraftIssue items)
- Third occurrence: 2026-03-31 04:45 (DraftIssue items)
- Fourth occurrence: 2026-03-31 05:49 (DraftIssue items)
- Fifth occurrence: 2026-03-31 07:01 (DraftIssue items)
- **Impact**: 6 DraftIssue items remain untriaged for ~24 hours, blocked from automated triage

**Validation**:
- Check automation gap is documented in this file
- Verify self-improvement entries exist in `.learnings/LEARNINGS.md`
- Confirm memory entry is current in `memory/YYYY-MM-DD.md`

### GitHub Project DraftIssue Items

**Issue**: New GitHub Project items appear as "DraftIssue" state, not in workflow stages. They need manual workflow stage assignment to move from "New" to "In Progress".

**Current behavior**:
- Items created as new issues appear with `contentType: "DraftIssue"` instead of workflow stage
- No `status` field (Workflow Stage) is assigned initially
- Items show up in project but outside the expected workflow stages

**Root cause**:
- DraftIssue items were likely added to the project without being first configured with a workflow stage
- The `gh project item-list` command shows these items but doesn't include workflow stage information
- The DPM runbook's "New" stage items are actually in DraftIssue state
- The `gh project item-edit` command cannot update single-select fields by name alone; requires internal option ID not exposed through standard CLI commands

**Workaround options**:
1. Use the GitHub web UI to manually update Workflow Stage for DraftIssue items
2. Use GraphQL API directly to query field options and option IDs, then update the field
3. Create items through the project's "New" workflow stage directly (if possible)

**Current DPM workflow impact**:
- The DPM hourly intake check runs successfully
- Project items can be reviewed and assessed
- Moving items to "In Progress" or "Human Review" requires manual UI update or GraphQL API call
- This creates a partial automation gap in the DPM workflow for initial item triage

**Persistence across sessions (2026-03-31)**:
- First identified: 2026-03-30 09:56
- Second occurrence: 2026-03-31 00:36 (DraftIssue items)
- Third occurrence: 2026-03-31 04:45 (DraftIssue items)
- Fourth occurrence: 2026-03-31 05:49 (DraftIssue items)
- Fifth occurrence: 2026-03-31 07:01 (DraftIssue items)
- **Impact**: 6 DraftIssue items remain untriaged for ~24 hours, blocked from automated triage

**Resolution tracking**:
- Self-improvement entry: `LRN-20260331-001`, `LRN-20260331-003`, `LRN-20260331-006`
- Updated memory: `/home/stu/.openclaw/workspace/memory/2026-03-31.md`
- Status: documented limitation, workaround identified, waiting for CLI/project improvement
- **Next review**: 2026-04-01 or when GitHub CLI gains better project field support

**Validation**:
- Check automation gap is documented in this file
- Verify self-improvement entry exists in `.learnings/LEARNINGS.md`
- Confirm memory entry is current in `memory/YYYY-MM-DD.md`

**DPM Status (2026-03-31 07:01)**:
- DraftIssue items need manual workflow stage assignment via web UI or GraphQL API
- Until then, DPM can review and assess items, but cannot move them through workflow stages automatically
- Consider adding manual step in DPM workflow for workflow stage updates until CLI support improves
- **Session observation**: All 7 Human Review items completed triage and are ready for human sign-off; project state stable across consecutive hourly checks

---

## Infrastructure Learnings (2026-03-24)

### Titan (Host)

**LAN**: `192.168.10.80`  
**Tailscale**: `100.117.50.105`  
**Tailscale HTTPS**: `https://titan.tail1a2109.ts.net/`

**Images**:
- `localhost:5000/ddh-web:latest` (port 4173)
- `localhost:5000/ddh-api:latest` (port 4181)

**Nginx Config (Host Network Mode)**:
```nginx
location /api/ {
    proxy_pass http://192.168.10.80:4181/api/;  # Use explicit IP, not 'api' hostname
}
```

**Why**: Host network mode bypasses Docker DNS. Container uses host's DNS, not Docker's internal DNS. Using `api` hostname causes public DNS lookup → Cloudflare IPs → timeout.

**MCP Deployer Payload**:
```json
{
  "label": "ddh-web",
  "image": "localhost:5000/ddh-web:latest",
  "listen_port": 4173,
  "pull": false,
  "auto_approve": false,
  "env": { "VITE_API_URL": "http://192.168.10.80:4181" }
}
```

### Trilium ETAPI

**Host**: `http://192.168.10.5:8080`
**Auth**: Plain `Authorization: <token>` header (NOT Bearer)
**Token**: `x2aVxHZNg6HO_2GItibwJswEbIqRJDPerRW3LIk1MTquibcjXpVgvdHQ=`

**Calendar Structure**:
```
Calendar → 2026 → 03 - March → 24 - Tuesday → Daily Summary
```

### GitHub CLI (gh) Authentication

**Token Location**: `~/.config/gh/hosts.yml`
**Active Account**: `harkers`
**Scopes**: `gist`, `project`, `read:org`, `repo`

**Export for curl/GitHub API calls**:
```bash
export GH_TOKEN=$(gh auth token)
```

**Skill Integration**:
The `gh-issues` skill uses curl + GitHub REST API, not the `gh` CLI directly. It expects `GH_TOKEN` in environment. The token from `gh auth token` works for both API calls and git operations.

**Validation**:
```bash
gh auth status
curl -s -H "Authorization: Bearer $(gh auth token)" https://api.github.com/user | jq -r '.login'
```

### Quarto CLI

**Location**: `~/.local/bin/quarto`
**Real binary**: `~/.local/quarto/bin/quarto`
**Version**: 1.4.557
**Bundled Deno**: `~/.local/quarto/bin/tools/x86_64/deno` (v2.3.1)

**Important**: Must use bundled Deno, not system Deno. System Deno (v2.7.7) incompatible with quarto.js.

**Launcher note (2026-03-28)**:
- `~/.local/bin/quarto` had been a copied wrapper script and failed on `--version` because it resolved the wrong root and looked for `~/.local/share/version`
- fixed by replacing it with a symlink to `~/.local/quarto/bin/quarto`
- `~/.local/bin/quarto --version` now works correctly again

### Vite API URL

**Rule**: Set `VITE_API_URL` at build time based on deployment target:
```bash
VITE_API_URL=http://192.168.10.80:4181 npm run build
```

Hardcoded URL bakes into static assets. `localhost` only works on titan.

### ZFS Storage Pool (data)

**Pool**: `data` - 3× 4TB HDD RAIDZ1 (7.14TB usable, single-disk parity)

**Datasets** (all with compression=lz4, atime=off):
| Dataset | Mount Point | Purpose |
|---------|-------------|---------|
| `data/workspaces` | `/data/workspaces` | Active projects |
| `data/home` | `/data/home` | Personal (go, DevForge, data) |
| `data/appdata` | `/data/appdata` | Container persistent data |
| `data/clients` | `/data/clients` | Client work |
| `data/backups` | `/data/backups` | Backup storage |
| `data/docker-volumes` | `/data/docker-volumes` | Docker named volumes |

**Auto-Snapshots** (zfs-auto-snapshot):
- Frequent (15min): 4 snapshots on `data/appdata` only
- Hourly: 48 snapshots
- Daily: 14 snapshots
- Weekly: 8 snapshots
- Monthly: 12 snapshots

**Key Symlinks** (backward compatibility):
- `~/go` → `/data/home/go`
- `~/mcp-control-plane` → `/data/appdata/mcp-control-plane`
- `~/docker/trilium` → `/data/appdata/trilium`
- `~/.openclaw/workspace/forge-pipeline` → `/data/appdata/forge-pipeline`
- `~/.openclaw/workspace/privacy-intake-pack` → `/data/appdata/privacy-intake`

**Useful Commands**:
```bash
zpool status              # Pool health
zfs list                   # All datasets
zfs list -t snapshot       # View snapshots
zfs snapshot -r data@manual-$(date +%Y%m%d-%H%M)  # Manual snapshot
zfs rollback data/appdata@zfs-auto-snap_frequent-2026-03-27-1435  # Restore
```

**Not on ZFS**: `/var/lib/docker`, `/var/lib/containerd`, `~/.ollama`, `~/ollama`

### llama-cpp-turboquant (CUDA)

**Location**: `/opt/llama-cpp-turboquant`
**Branch**: `feature/turboquant-kv-cache`
**Build**: `/opt/llama-cpp-turboquant/build`

**Key Binaries**:
- `build/bin/llama-cli` - Main inference CLI
- `build/bin/llama-server` - HTTP server
- `build/bin/llama-bench` - Benchmarking
- `build/bin/llama-quantize` - Model quantization

**CUDA Config**:
- CUDA 11.8.89
- Architecture: 89-real (RTX 4080 SUPER Ada Lovelace)
- ggml version: 0.9.8

**Models Directory**: `/data/models/`

**Available Models**:
| Model | Path | Size | Use Case |
|-------|------|------|----------|
| Phi-4-mini Q4_K_M | `/data/models/phi4-mini/Phi-4-mini-instruct-Q4_K_M.gguf` | 2.4 GB | Fast drafting |
| Qwen2.5-Coder-7B Q4_K_M | `/data/models/qwen25-coder-7b/qwen2.5-coder-7b-instruct-q4_k_m.gguf` | 4.4 GB | Code tasks |
| Qwen2.5-1.5B Q4_K_M | `/data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf` | 1.1 GB | Lightweight |
| Qwen3-8B Q4_K_M | `/data/models/Qwen3-8B-Q4_K_M.gguf` | 5 GB | General |

**Performance** (Qwen2.5-1.5B Q4_K_M):
- Prompt: ~3588 t/s
- Generation: ~367 t/s

**Usage**:
```bash
# One-shot prompt
/opt/llama-cpp-turboquant/build/bin/llama-cli -m /data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf -p "Your prompt" -n 100

# Interactive chat
/opt/llama-cpp-turboquant/build/bin/llama-cli -m /data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf -cnv

# HTTP server (Phi-4-mini)
/opt/llama-cpp-turboquant/build/bin/llama-server \
  -m /data/models/phi4-mini/Phi-4-mini-instruct-Q4_K_M.gguf \
  --port 8091 --host 127.0.0.1 --n-gpu-layers 99 --threads 8 --ctx-size 8192

# HTTP server (Coder-7B)
/opt/llama-cpp-turboquant/build/bin/llama-server \
  -m /data/models/qwen25-coder-7b/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  --port 8092 --host 127.0.0.1 --n-gpu-layers 99 --threads 8 --ctx-size 8192
```

**VRAM Coexistence** (RTX 4080 SUPER 16GB):
- SD XL alone: 7.1 GB
- SD + Phi-4-mini: 11.2 GB ✅ (4.5 GB headroom)
- SD + both llama lanes: 15.3 GB ❌ OOM
- Recommendation: Run SD with one llama lane at a time

### Stable Diffusion XL

**Location**: `/opt/stable-diffusion-webui/`
**Type**: Automatic1111 WebUI (native, not Docker)
**Port**: 7860 (configurable)
**GPU**: CUDA with xformers optimization

**Systemd Service**: `stable-diffusion.service`
**Idle Timer**: `sd-idle-stop.timer` (stops after 5 min idle)

**Start**: `sudo systemctl start stable-diffusion.service`
**Stop**: `sudo systemctl stop stable-diffusion.service`
**Disable auto-stop**: `sudo systemctl stop sd-idle-stop.timer`
**Re-enable auto-stop**: `sudo systemctl start sd-idle-stop.timer`

**Models Available** (`/opt/stable-diffusion-webui/models/Stable-diffusion/`):
| Model | Size | Notes |
|-------|------|-------|
| `proteusV04.safetensors` | 6.9 GB | Currently selected |
| `realvisxl_v4.safetensors` | 6.9 GB | |
| `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors` | 7.1 GB | |
| `sd_xl_base_1.0.safetensors` | 6.1 GB | SDXL base |
| `sd_xl_refiner_1.0.safetensors` | 6 GB | SDXL refiner |
| `dreamshaperXL10.safetensors` | 2 GB | |
| `cyberrealistic_v40.safetensors` | 2 GB | |

**Additional Model Directories**:
- `VAE/` - VAE models
- `Lora/` - LoRA adapters
- `ControlNet/` - ControlNet models
- `ESRGAN/` - Upscalers

**Configuration**: `/opt/stable-diffusion-webui/webui-user.sh`
```bash
COMMANDLINE_ARGS="--xformers --opt-sdp-attention --listen --port 7860 --no-half-vae --upcast-sampling"
```

**MCP Integration**:
- `openclaw-sd-mcp` container (port 8082 internal)
- `openclaw-sd-gateway` container
- SD_URL: `http://host.docker.internal:7860`
- MCP tools registered but require SD running

**VRAM Usage**: ~7.1 GB with xformers + SDP attention

**API Endpoints** (when running):
- WebUI: `http://127.0.0.1:7860`
- API docs: `http://127.0.0.1:7860/docs`
- Models: `GET /sdapi/v1/sd-models`
- Text-to-image: `POST /sdapi/v1/txt2img`

**Rollback**:
- Stop service: `sudo systemctl stop stable-diffusion.service`
- Models stored in `/opt/stable-diffusion-webui/models/`
- Config in `/opt/stable-diffusion-webui/config.json`

#### GCP Workload Identity Federation
- Project code: GCP-WIF-001
- Status: deployed
- Purpose: Secure, keyless authentication from Titan to Google Cloud using Authentik OIDC as identity provider
- Host / environment: titan / Debian 12
- Workspace / owner: `/home/stu/.openclaw/workspace/`
- Type: OIDC token exchange pipeline
- Runtime location: Authentik (auth.titan.lan) + GCP Workload Identity Pool
- Access method: `~/.local/bin/gcp-auth` script
- GCP Project: `cloudflare-access-379915`
- GCP Project Number: `434360693306`
- Workload Identity Pool: `rker`
- Workload Identity Provider: `authentik-titan`
- Authentik OAuth2 Provider: `name-gcp-workload-identity-app`
- Authentik Client ID: `ML9f52R43wKpYgNBvyy7RX3E2FmDia7O5Wfk3n1f`
- Service Account: `titan-workload@cloudflare-access-379915.iam.gserviceaccount.com`
- Authentication: Client credentials flow via Authentik OIDC → STS token exchange → Service account impersonation
- Storage / state paths:
  - `~/.config/gcp-workload-identity-config.json` — Configuration
  - `~/.config/gcp-oidc-token` — Authentik ID token (cached)
  - `~/.config/gcp-sa-access-token` — GCP access token (cached)
  - `~/.config/gcp-credentials-generated.json` — ADC credential file
  - `~/.openclaw/workspace/gcp-workload-identity-jwks.json` — JWKS file for Authentik provider
- Dependencies: Authentik OAuth2 provider, GCP Workload Identity Pool, Service Account with `roles/iam.serviceAccountTokenCreator` binding
- Start command: `export GCP_WORKLOAD_CLIENT_SECRET='...' && ~/.local/bin/gcp-auth`
- Validation:
  - `curl -s -H "Authorization: Bearer $(cat ~/.config/gcp-sa-access-token)" https://cloudresourcemanager.googleapis.com/v1/projects`
  - `gcloud projects list` (after setting `GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp-credentials-generated.json`)
- Rollback:
  - Delete Authentik OAuth2 provider: `authentik-titan`
  - Delete GCP Workload Identity Pool: `rker`
  - Delete GCP Service Account: `titan-workload`
  - Remove IAM binding: `roles/iam.serviceAccountTokenCreator`
  - Delete local files: `rm ~/.config/gcp-* ~/.openclaw/workspace/gcp-workload-identity-jwks.json`
- Security notes:
  - Client secret should be stored in environment variable, not hardcoded
  - Service Account has `roles/owner` on GCP project — restrict in production
  - Token lifetime is ~300 seconds (5 minutes) for Authentik ID token
  - Workload Identity Pool allows all subjects (`principalSet://.../*`) — restrict to specific user IDs for production
- Change impact / related services:
  - No impact on existing Authentik providers or applications
  - GCP access requires token refresh before expiry

## Titan Model Lanes (2026-03-29)

**Deployed**: Two specialist local LLM lanes alongside Ollama

**Architecture:**
| Service | Port | Model | Use Case | Speed |
|---------|------|-------|----------|-------|
| **Ollama** | 11434 | Various (glm-5:cloud default) | Tools, orchestration, safe default | Cloud |
| **Phi-4-mini** | 8091 | Phi-4-mini Q4_K_M | Fast summaries, triage, drafting | 221 t/s |
| **Coder-7B** | 8092 | Qwen2.5-Coder-7B Q4_K_M | Code review, configs, debugging | 137 t/s |

**VRAM Usage:** ~10GB / 16GB (62%) - comfortable headroom

**Model Paths:**
- Phi-4-mini: `/data/models/phi4-mini/Phi-4-mini-instruct-Q4_K_M.gguf`
- Coder-7B: `/data/models/qwen25-coder-7b/qwen2.5-coder-7b-instruct-q4_k_m.gguf`

**Startup Commands:**
```bash
# Phi-4-mini (port 8091)
/opt/llama-cpp-turboquant/build/bin/llama-server \
  -m /data/models/phi4-mini/Phi-4-mini-instruct-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8091 -c 8192 -np 2 &

# Coder-7B (port 8092)
/opt/llama-cpp-turboquant/build/bin/llama-server \
  -m /data/models/qwen25-coder-7b/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  --host 127.0.0.1 --port 8092 -c 8192 -np 2 &
```

**Direct HTTP Usage:**
```bash
# Phi-4-mini - Fast text tasks
curl http://127.0.0.1:8091/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "Phi-4-mini-instruct-Q4_K_M.gguf", "messages": [{"role": "user", "content": "Summarize this"}]}'

# Coder-7B - Code tasks
curl http://127.0.0.1:8092/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5-coder-7b-instruct-q4_k_m.gguf", "messages": [{"role": "user", "content": "Review this code"}]}'
```

**OpenClaw Status:**
- ✅ Models registered and authenticated
- ✅ Canonical local lane model references:
  - `titan-phi4mini/Phi-4-mini-instruct-Q4_K_M.gguf`
  - `titan-coder/qwen2.5-coder-7b-instruct-q4_k_m.gguf`
- ✅ Local lane providers use the `openai-responses` adapter
- ✅ Ollama routing working

**Performance Benchmarks:**
| Model | Prompt (8K) | Gen (128) | Size |
|-------|-------------|-----------|------|
| Phi-4-mini | 14,382 t/s | 221 t/s | 2.4GB |
| Qwen2.5-Coder-7B | ~8,100 t/s | 137 t/s | 4.4GB |
| Qwen3.5-27B | 2,050 t/s | 48 t/s | 11GB (not deployed - VRAM constraint) |

### Cloudflare Access Configuration

**Account ID**: `eac1644dd8754f262096546933957d79`
**Tunnel ID**: `18a78b3b-7b30-465f-b09f-4e6912daee1f`

**API Token** (previous limited token):
- Token: `cfut_BijhXmWOFaphntYUMXsqx8m7qjrC2EWrDLgpjny6357abe65`
- Permissions: Zone DNS: Edit, Zone Zone: Read
- Expires: 2027-03-06
- **Limitation**: did not reliably cover all needed Account-level Access + new-zone operations

**Global API token (current)**:
- Token: `cfk_ErZIzRxeSfZ4My5MtK0B39OBNj1kzrpl1foL2tLqee710f44`
- Purpose: preferred credential for Cloudflare Access / dashboard / new-zone work unless replaced

**Tunnel Routes (updated 2026-03-31)**:
| Hostname | Service | Notes |
|----------|---------|-------|
| `auth.harker.systems` | `http://localhost:9000` | Authentik (primary) |
| `auth.orderededge.co.uk` | `http://localhost:9000` | Authentik (added 2026-03-31) |
| `notes.harker.systems` | `http://localhost:8082` | Trilium |
| `privacy.rker.dev` | `http://192.168.10.80:3010` | Privacy Dashboard |
| `dashboard.rker.dev` | `http://192.168.10.80:3010` | Privacy Dashboard |
| `privacy-dashboard.orderededge.co.uk` | `http://192.168.10.80:3010` | Privacy Dashboard |

**Access Apps**:
| App | ID | Domain |
|-----|-----|--------|
| Privacy-Ops Dashboard | `ca2b698e-3eb7-4d5c-b3a8-2f4f422d09c0` | `*.rker.dev` |
| Mermaid Analyzer | `e05c087e-1c31-477d-ab6d-d679c4d67723` | `merm.rker.dev` |
| App Launcher | `44db7370-a3a5-4bcc-bb1c-8c8173a9c654` | `forgeshield.cloudflareaccess.com` |

**Service Token** (from memory, may be rotated):
- Client ID: `a68339ac5e98cdf615d267a8d2512448.access`
- Client Secret: `610a189924ea3332328f14e82a81ee7decf11cdeecdb5eef2b1ff165476664ab`

**Working Access**:
- Primary public URL: `https://privacy-dashboard.orderededge.co.uk/` (API key auth, no Cloudflare Access)
- Legacy public URL: `https://dashboard.rker.dev/` (service token auth, separate app)
- LAN: `http://192.168.10.80:3010/`
- API key: `X-Api-Key: podash_agent_bacd98bf35a6e52c233c52a91e9b215c`

**Cloudflare Access app for orderededge DELETED (2026-03-29)**:
- Root cause: Access app for `privacy-dashboard.orderededge.co.uk` had email-only policy; service token headers from nginx were not recognized.
- Fixed by deleting the Access app entirely. Tunnel routes directly to backend with `X-Api-Key` auth handling security.
- `dashboard.rker.dev` still has its own Access app with service token `d44bc0d1-f6a5-4e59-8319-354f8f05af21`.

**Cloudflare API token (active)**:
- `cfut_P06ecgVYACRl3t7Dve2ZhJjXQ3TxGxO1Gx5gCAoI21569f1c` — Permissions: Account.Access: Apps, Account.Access: Keys, Zone.DNS, Argo Tunnel. Expires ~2027.

**Cloudflare Access Application (created 2026-03-29):**
- App Name: Privacy-Ops Dashboard
- App ID: `48e6d26b-3921-42ac-9f7c-22771fbcf8d7`
- Domain: `privacy-dashboard.orderededge.co.uk`
- Policy ID: `f8440afa-d58b-4942-a45b-066fe29cc4d5`
- Policy Name: "Allow stuharker@gmail.com only"
- Session Duration: 12 hours
- Current Auth Method: Email-based (direct email proof)
- **Pending:** Google Workspace SSO integration via OAuth 2.0

**Google Cloud Platform OAuth for Cloudflare Access (2026-03-29):**
- GCP Project ID: `cloudflare-access-379915`
- OAuth Client Type: Web application
- Authorized Redirect URI: `https://forgeshield.cloudflareaccess.com/cdn-cgi/access/callback`
- Status: OAuth credentials created in GCP Console; pending Cloudflare Zero Trust IdP configuration
- Next Step: Add Google Workspace as Identity Provider in Cloudflare Zero Trust Dashboard using OAuth Client ID + Secret

---

### OrderedEdge Sentinel (Planning Project)

- Project code: OC-SEC-001
- Status: planning (workspace scaffolded, planning phase active)
- Purpose: Centralized security visibility across infrastructure, endpoints, network telemetry, and key platforms
- Host / environment: titan / Debian 12
- Workspace / owner: `/home/stu/.openclaw/workspace/projects/orderededge-sentinel`
- Type: Project workspace (future SIEM deployment)
- Runtime location: `projects/orderededge-sentinel/`
- Access method: Local workspace files
- Ports / sockets / bindings: N/A (planning phase)
- Authentication: N/A (planning phase)
- Storage / state paths: `projects/orderededge-sentinel/`
- Dependencies: None (planning phase)
- Start command: N/A
- Stop command: N/A
- Restart command: N/A
- Validation:
  - Check planning artifacts exist: `ls projects/orderededge-sentinel/planning/`
  - Verify workspace structure: `ls -la projects/orderededge-sentinel/`
- Rollback: `rm -rf projects/orderededge-sentinel`
- Security notes:
  - Planning phase: no runtime exposure
  - Future deployment: will require security hardening per phase
- Change impact / related services:
  - N/A during planning phase
  - Future: will require firewall, network, and security infrastructure configuration

---

### Privacy-Ops Model Routing (2026-03-29)

**Routing document:** `privacy-ops-model-routing.md`

**Key routing for subagent workflows:**
| Agent Role | Primary Model | Notes |
|------------|--------------|-------|
| Orchestrator | `minimax-m2.7:cloud` | Workflow coordination |
| Intake/Classifier | `glm-5:cloud` | Schema extraction, categorization |
| Timeline | `glm-5:cloud` | Chronology construction |
| Risk Analyst | `glm-5:cloud` | Severity and harm assessment |
| Challenger | `deepseek-v3.2:cloud` | Independent challenge review |
| Report Writer | `glm-5:cloud` | Final incident reports |
| Comms Draft | `titan-phi4mini` (8091) | Fast drafts |
| Code/Automation | `titan-coder` (8092) | GitHub workflows |

**Critical lesson (Smoke Test 001):**
- Local models `gemma3:12b` and `mistral-nemo` do NOT support tool calls in Ollama
- For Privacy-Ops subagent workflows that require file I/O, use cloud models
- Direct execution without tools works but loses subagent isolation

**Smoke Test 001 Result:** ✅ PASS
- Intake correctly distinguished confirmed facts from unknowns (16 facts, 10 unknowns)
- Timeline correctly identified gaps with confidence levels
- Risk assessment correctly avoided automatic regulator notification
- Containment status correctly marked INCOMPLETE
- Controller notification correctly assessed as URGENT
- Challenger successfully identified gaps (auto-preview, intent verification)
