# TOOLS.md - Local Notes

# Tool and Service Registry

This file is the operational registry for all locally deployed tools, services, integrations, automations, and managed runtimes used by this OpenClaw workspace.

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


Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

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

### Quarto CLI

**Location**: `~/.local/bin/quarto`
**Version**: 1.4.557
**Bundled Deno**: `~/.local/quarto/bin/tools/x86_64/deno` (v2.3.1)

**Important**: Must use bundled Deno, not system Deno. System Deno (v2.7.7) incompatible with quarto.js.

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

**Test Model**: `qwen2.5-1.5b-instruct-q4_k_m.gguf` (~1.1GB)

**Performance** (Qwen2.5-1.5B Q4_K_M):
- Prompt: ~3588 t/s
- Generation: ~367 t/s

**Usage**:
```bash
# One-shot prompt
/opt/llama-cpp-turboquant/build/bin/llama-cli -m /data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf -p "Your prompt" -n 100

# Interactive chat
/opt/llama-cpp-turboquant/build/bin/llama-cli -m /data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf -cnv

# HTTP server
/opt/llama-cpp-turboquant/build/bin/llama-server -m /data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 8080
```

### Titan Model Lanes (2026-03-27)

**Deployed**: Two specialist local LLM lanes alongside Ollama

**Architecture:**
| Service | Port | Model | Use Case | Speed |
|---------|------|-------|----------|-------|
| **Ollama** | 11434 | Various (glm-5:cloud default) | Tools, orchestration, safe default | Cloud |
| **Phi-4-mini** | 8091 | Phi-4-mini Q4_K_M | Fast summaries, triage, drafting | 221 t/s |
| **Coder-7B** | 8092 | Qwen2.5-Coder-7B Q4_K_M | Code review, configs, debugging | 137 t/s |

**VRAM Usage:** ~10GB / 16GB (62%) - comfortable headroom

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
- ⚠️ HTTP routing returns 404 (use direct HTTP for now)
- ✅ Ollama routing unchanged and working

**Performance Benchmarks:**
| Model | Prompt (8K) | Gen (128) | Size |
|-------|-------------|-----------|------|
| Phi-4-mini | 14,382 t/s | 221 t/s | 2.4GB |
| Qwen2.5-Coder-7B | ~8,100 t/s | 137 t/s | 4.4GB |
| Qwen3.5-27B | 2,050 t/s | 48 t/s | 11GB (not deployed - VRAM constraint) |
