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
| `forge-orchestra` | **dormant** | ForgeOrchestra design system/brand docs (no AGENTS.md, just design tokens) |
| `forgeorchestra` | **dormant** | ForgeOrchestra workspace skeleton (has AGENTS.md but minimal content) |
| `forgeorchestrate` | **planning** | ForgeOrchestrate — master environment layer (active planning workspace) |

**Resolution:** `forgeorchestrate` is the canonical active workspace. `forge-orchestra` and `forgeorchestra` appear to be earlier iterations or design docs. Consider consolidating or archiving.

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
| `trilium` | **dormant** | Trilium note-taking placeholder (empty, config in sso-home-lab) |
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
| `projects/` | **active** | Sub-projects container (devforge-project-foundry, knowledge-layer, openclaw-usage-dashboard, titan-dashboard) |

### Projects Subdirectory

| Project | Status | Purpose |
|---------|--------|---------|
| `projects/devforge-project-foundry` | **planning** | Master template for governed project delivery |
| `projects/knowledge-layer` | **active** | Knowledge layer development |
| `projects/openclaw-usage-dashboard` | **live** | Internal usage dashboard for session/token visibility |
| `projects/titan-dashboard` | **planning** | Homepage-based launcher dashboard for Titan services |

---

## Symlinks

| Path | Target | Notes |
|------|--------|-------|
| `forge-pipeline` | `/data/appdata/forge-pipeline` | Forge Pipeline state |
| `privacy-intake-pack` | `/data/appdata/privacy-intake` | Privacy intake data |

---

## Ambiguity Flags

1. **ForgeOrchestra naming collision**: Three directories (`forge-orchestra`, `forgeorchestra`, `forgeorchestrate`) with overlapping purpose. **Resolution:** `forgeorchestrate` is canonical active workspace; others appear to be earlier iterations or design docs. Consider consolidating or archiving.

2. **`trilium` directory**: Empty placeholder. Active Trilium config lives in `sso-home-lab/trilium/`. **Resolution:** Can be removed or repurposed.

3. **`projects/` substructure**: Contains three active sub-projects now documented separately in registry.

4. **`control-plane-what-next-v2-extracted`**: Extracted archive with `control-plane-what-next-pack` subfolder. **Resolution:** Cleanup candidate — archive or remove if no longer needed.

---

## Metadata

- Generated: 2026-03-28T01:36Z
- Updated: 2026-03-28T01:52Z
- Workspace root: `/home/stu/.openclaw/workspace`
- Status distribution: 3 live, 8 active, 5 planning, 9 dormant
- Ambiguity flags: 4 (2 resolved, 2 documented)