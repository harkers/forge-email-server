# OpenClaw Workspace Registry

Last updated: 2026-03-28
Maintained by: OpenClaw agent (auto-generated draft)

## Purpose
Canonical inventory of top-level workspaces and projects under `/home/stu/.openclaw/workspace` with status classification and one-line purpose.

## Status Legend
- **planning** — Design/spec phase, no deployment
- **active** — Implementation in progress
- **live** — Deployed and running in production
- **dormant** — On hold, inactive, or complete

---

## Core Infrastructure

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `forge-pipeline` | **live** | Central portfolio/project visibility layer (symlink to /data/appdata/forge-pipeline) |
| `forge-syslog-collector` | **live** | Docker syslog collector for containers and network devices |
| `benchmark` | **live** | Local LLM benchmark suite for titan model lanes |

## Forge Ecosystem

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `forge-wordpress` | **active** | ForgeWordPress plugin monorepo (SEO Forge, Image Forge, Form Forge, Cache Forge) |
| `devforge-mcp-control-plane` | **active** | MCP control plane coordination system with specialist agents |
| `devforge-openclaw-skills` | **active** | Curated OpenClaw skills collection for DevForge projects |
| `github-forge-pipeline` | **planning** | GitHub Projects V2 bidirectional sync with Forge Pipeline |
| `dev-forge-foundry-configuration` | **planning** | DevForge Project Foundry design — OS for project delivery |
| `forgedeck` | **planning** | Presentation/deck system planning and templates |
| `forgediscord` | **active** | ForgeDiscord integration and bot workspace |

## Ambiguous / Duplicate Directories

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `forge-orchestra` | **dormant** | ForgeOrchestra design docs (appears superseded by forgeorchestrate) |
| `forgeorchestra` | **dormant** | Duplicate/variant — unclear relation to forge-orchestra |
| `forgeorchestrate` | **planning** | ForgeOrchestrate — master environment layer (appears current) |

## Privacy & Security

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `privacy-intake-pack` | **active** | Privacy intake workflow (symlink to /data/appdata/privacy-intake) |
| `privacy-dsar-processing` | **dormant** | DSAR case handling workspace |
| `privacy-agents` | **dormant** | Reusable privacy agent specs (publisher, incident reporter, vendor assessor) |
| `authentik` | **active** | Authentik SSO deployment configuration |
| `sso-home-lab` | **active** | Home lab SSO design and deployment (Trilium + Authentik) |

## Services & Tools

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `trilium` | **active** | Trilium note-taking instance configuration |
| `display-forge` | **dormant** | Digital signage platform scaffold for Proxmox |

## Personal & Household

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `orderedhome` | **dormant** | Household organization and management workspace |

## Support & Utilities

| Workspace | Status | Purpose |
|-----------|--------|---------|
| `memory-stack` | **dormant** | Portable memory stack giveaway kit for new OpenClaw workspaces |
| `skills/` | **live** | Agent skills collection (architecture-reviewer, coding-worker, control-plane, etc.) |
| `projects/` | **active** | Sub-projects (knowledge-layer, openclaw-usage-dashboard, devforge-project-foundry) |

---

## Symlinks

| Path | Target | Notes |
|------|--------|-------|
| `forge-pipeline` | `/data/appdata/forge-pipeline` | Forge Pipeline state |
| `privacy-intake-pack` | `/data/appdata/privacy-intake` | Privacy intake data |

---

## Ambiguity Flags

1. **ForgeOrchestra naming collision**: Three directories (`forge-orchestra`, `forgeorchestra`, `forgeorchestrate`) with overlapping purpose. Clarify which is canonical.

2. **`trilium` directory**: Appears nearly empty. Confirm status vs. `sso-home-lab/trilium/`.

3. **`projects/` substructure**: Contains sub-projects that may warrant explicit top-level entries or separate treatment.

4. **`control-plane-what-next-v2-extracted`**: Appears to be an extracted archive — cleanup candidate.

---

## Metadata

- Generated: 2026-03-28T01:36Z
- Workspace root: `/home/stu/.openclaw/workspace`
- Status distribution: 3 live, 8 active, 5 planning, 9 dormant, remaining unclassified