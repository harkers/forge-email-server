# Forge Pipeline Version

## Current Version
**v1.1.0** — 2026-03-25

## Changelog

### v1.1.0 (2026-03-25)
- FP-001: Add `critical` priority to tasks
  - ALLOWED_PRIORITY now includes: low, medium, high, critical
- FP-002: Add `risk_state` to tasks
  - ALLOWED_RISK_STATE: none, watch, at-risk, critical
  - Database migration for existing tables
  - Full CRUD support for risk_state
- FP-010: Rename KPI labels
  - Open → Active tasks
  - Added At Risk and Blocked metrics
  - Added Critical task count
- FP-011: Add KPI deltas
  - Compare current vs previous snapshot (5-min intervals)
  - Visual +N/-N indicators on metrics
- FP-020: Reduce metadata chip overload
  - Mini-lists show only critical/high priority badges
  - Only show blocked status, not all statuses
  - Risk state badges for at-risk/critical items
- FP-030: Improve empty-state treatment
  - Better visual hierarchy with icon and guidance
  - Contextual help text for new users
- FP-003: Add source health indicator
  - Shows refresh freshness (✓ healthy / ⏳ delayed / ⚠ stale)
  - Visual indicator next to last update timestamp
- Fix default project status bug
  - Changed invalid `'active'` default to `'not-started'`
  - Fixed all status validation errors on POST requests

### v1.0.3 (2026-03-24)
- Redis cache layer deployed
  - Summary endpoint cached (60s TTL)
  - Cache invalidation on all write operations
  - Redis health status in /api/health
  - Dedicated redis:7-alpine service with AOF persistence

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
