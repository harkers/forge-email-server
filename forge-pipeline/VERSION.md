# Forge Pipeline Version

## Current Version
**v1.2.0** — 2026-03-25

## Changelog

### v1.2.0 (2026-03-25)
- FP-040: Rebalance board column widths (1.15 / 0.85 / 1.0 / 1.0)
- FP-041: Add relative timestamps to Recently changed items
- FP-021: Add overdue visual state (red border, pulsing badge)
- FP-022: Add due-soon state (≤7 days, orange highlight)
- FP-023: Implement stale detection (>7 days since update, faded)
- FP-050: Add risk state badges to task cards and metadata
- Add risk state dropdown to task editor
- Include critical priority in scoring

### v1.1.0 (2026-03-25)
- FP-001: Add `critical` priority to tasks
- FP-002: Add `risk_state` to tasks (none/watch/at-risk/critical)
- FP-010: Rename KPI labels (Open → Active, add At Risk/Blocked)
- FP-011: Add KPI deltas with visual indicators
- FP-020: Reduce metadata chip overload in mini-lists
- FP-030: Improve empty-state treatment with guidance
- FP-003: Add source health indicator (freshness)
- Fix default project status bug

### v1.0.3 (2026-03-24)
- Redis cache layer deployed

### v1.0.1 (2026-03-24)
- Port conflict resolved

### v1.0.0 (2026-03-24)
- ForgeOrchestra design system integration
- Portfolio section grouping
- Kanban board view
- Source-aware filtering

---

## Design System
ForgeOrchestra Obsidian Intelligence — see `/forgeorchestra/DESIGN_GUIDE.md`