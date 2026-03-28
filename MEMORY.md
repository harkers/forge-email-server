# MEMORY.md

Curated long-term memory for the main OpenClaw workspace.

This file should hold stable facts, durable decisions, recurring rules, and important context worth keeping beyond daily notes.

## Workspace operating truths

- This workspace relies on **daily memory files** under `memory/YYYY-MM-DD.md` for raw logs and short-term continuity.
- `MEMORY.md` is the **curated long-term layer** and should stay distilled rather than becoming another daily log.
- When important facts, repeated lessons, durable preferences, or major decisions emerge, they should be promoted here.
- The workspace default is to **write things down**, not rely on transient session memory.

## Core workspace defaults

When creating new Forge-style workspaces or derived project workspaces, include these defaults unless explicitly overridden:
- **Forge Pipeline sync** for meaningful project-state changes
- **self-improvement** for failures, corrections, missing capabilities, and better recurring approaches
- **self-reflection** after meaningful multi-step work, rework, or feedback
- **Quarto / `.qmd`** as a default option for reports, specs, architecture docs, review packs, and other structured long-form outputs when useful

## Documentation and delivery policy

- A task is not complete until implementation, validation, documentation, and rollback guidance are all handled.
- If a runtime, service, port, dependency, authentication method, storage path, or operational command changes, `TOOLS.md` should be updated.
- If a new repeatable practice or project-wide rule is established, `AGENTS.md` should be updated.
- Prefer minimal, surgical changes on titan rather than sprawling rework.

## Titan infrastructure memory

### Host and storage
- Hostname: `titan`
- Main ZFS pool: `data` (3× 4TB HDD RAIDZ1, ~7.14TB usable)
- Key datasets:
  - `/data/workspaces`
  - `/data/home`
  - `/data/appdata`
  - `/data/clients`
  - `/data/backups`
  - `/data/docker-volumes`
- Important note: Docker engine and Ollama data are **not** on ZFS.

### Key symlink-backed paths
- `~/mcp-control-plane` → `/data/appdata/mcp-control-plane`
- `~/.openclaw/workspace/forge-pipeline` → `/data/appdata/forge-pipeline`
- `~/.openclaw/workspace/privacy-intake-pack` → `/data/appdata/privacy-intake`
- `~/docker/trilium` → `/data/appdata/trilium`
- `~/go` → `/data/home/go`

### Local service lanes and tooling
- Forge Pipeline API is local on `http://127.0.0.1:4181/api`
- OpenClaw Usage Dashboard is local on `http://127.0.0.1:8899`
- Local specialist model lanes:
  - Phi-4-mini on `127.0.0.1:8091`
  - Qwen2.5-Coder-7B on `127.0.0.1:8092`

## Memory search configuration lesson

- `all-minilm:latest` was too small-context for larger workspace memory files.
- Recommended default embedding model for memory indexing on this machine is `nomic-embed-text:latest` because it handles much larger context windows.

## Quarto memory

- Working CLI path: `~/.local/bin/quarto`
- Real binary path: `~/.local/quarto/bin/quarto`
- Verified version: `1.4.557`
- Bundled Deno path: `~/.local/quarto/bin/tools/x86_64/deno`
- Important: use Quarto’s bundled Deno, not system Deno, when Quarto execution depends on it.
- A broken copied wrapper at `~/.local/bin/quarto` was fixed on 2026-03-28 by replacing it with a symlink to the real binary.

## Stable project memory

### DevForge: Project Foundry
- Planning workspace exists at `/home/stu/.openclaw/workspace/workspaces/devforge-project-foundry`
- This is the master OpenClaw planning workspace and future GitHub template repository for governed project delivery.
- Future repo name: `devforge-project-foundry`
- Internal execution domains use the `forge-*` naming convention.
- ForgeComms, ForgeTraining, and ForgeRisk are first-class domains in the model.
- Privacy is a dedicated specialist function.
- The project is currently **planning only**; repository bootstrap should not start until approval gates are satisfied.

### Forge Pipeline project record
- The Forge Pipeline record for **DevForge: Project Foundry** was cleaned and is now the canonical project entry for this effort.
- It reflects the planning workspace rather than the older `dev-forge-foundry-configuration` framing.

### Forge Syslog Collector
- Forge-Syslog-Collector is deployed and live on titan.
- It receives Docker container logs and pfSense syslog (UDP and TLS).
- Stable MCP log sources currently include:
  - `openclaw-github-mcp`
  - `openclaw-powerpoint-mcp`
  - `openclaw-vault-mcp`
  - `openclaw-nextcloud-mcp`
  - `openclaw-wordpress-mcp`
- `openclaw-glances-mcp` was removed from the stable set because it generated mostly health-check noise.

### OpenClaw Usage Dashboard
- Project code: `OC-DASH-001`
- Internal-only phase 1 dashboard exists at `projects/openclaw-usage-dashboard`
- Local access: `http://127.0.0.1:8899`
- It treats incomplete usage persistence as `unknown` rather than fake-zero precision.

## Known operational issue to revisit

- There is a stale paired Mac device (`clientId: openclaw-control-ui`, platform `MacIntel`) causing repeated websocket auth noise with `token_mismatch` in OpenClaw logs.
- User explicitly does **not** want to use the Mac node.
- Likely next cleanup is revoking or removing the stale paired device entry.

## Long-term principle

Keep this file curated.

If something is merely recent, it belongs in a daily log.
If it is durable, repeatedly useful, or likely to matter across future sessions, it belongs here.
