# Forge Pipeline Version

## Current Version
**v1.0.1** — 2026-03-24

## Changelog

### v1.0.1 (2026-03-24)
- Port conflict resolved
  - Changed web container port from 4173 to 4174
  - Host nginx was occupying 4173, blocking deployment
  - Updated app.js API base URL to handle port change
  - Updated DEPLOY.md with new default port

### v1.0.0 (2026-03-24)
- ForgeOrchestra design system integration
  - Obsidian Intelligence colour palette (#07090D, #0B1020, #111827 base)
  - Luminous Platinum Blue accent (#7AA6FF)
  - Architectural glass material language
  - Premium typography (Inter, SF Pro Display)
  - Refined radii system (12px/20px/24px/28px)
  - Soft shadows and diffused glow effects
  - Motion transitions on hover/focus
- Version control and timestamp display
  - Version badge in hero header
  - Last updated timestamp with locale formatting
  - VERSION.md for release tracking
- Portfolio section grouping
- Kanban board view
- Hidden cancelled projects from default view
- Source-aware filtering
- Live refresh/polling status indicator
- Webhook endpoint for external systems
- MCP-friendly project/task upsert endpoints
- Richer project status model
- Audit/activity feed in sidebar

---

## Design System
ForgeOrchestra Obsidian Intelligence — see `/forgeorchestra/DESIGN_GUIDE.md`
