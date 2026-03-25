# Forge Pipeline Version

## Current Version
**v2.0.0** — 2026-03-25

## Changelog

### v2.0.0 (2026-03-25)
- FP-090: Enhanced Focus Now recommendation engine with scoring
- FP-091: Task dependency visualization (blockedBy, blocking fields)
- FP-093: Executive summary mode (Full View / Executive toggle)
- FP-094: WebSocket infrastructure (disabled, polling fallback)

**Task Dependencies (FP-091):**
- Added `blockedBy` and `blocking` fields to task schema
- Database migration for dependency columns
- Dependency graph API endpoint (`/api/dependencies`)
- Dependency panel UI with clickable task links
- Visual indicators for blocked/done/active status

**Focus Now Improvements:**
- Task scoring algorithm (priority, status, risk, due date, staleness)
- Weighted focus score (0-125 points)
- Click-to-scroll to highlighted task
- Visual focus score badge on tasks

**Executive Summary:**
- Condensed high-level project view
- Project cards with key metrics (total/active/blocked/at-risk)
- Highlight panels for blocked/critical/overdue
- View mode toggle (Full View / Executive)

**WebSocket (Infrastructure):**
- websocket_server.py module for real-time push
- Redis pub/sub for event broadcasting
- Frontend WebSocket client with polling fallback
- nginx proxy configuration for /ws endpoint

### v1.6.0 (2026-03-25)
- FP-070-073: Design System Alignment

### v1.5.0 (2026-03-25)
- FP-060-064: Filters & Interaction

### v1.4.0 (2026-03-25)
- FP-DB1-DB6: PostgreSQL migration (disabled pending pool fix)

### v1.3.0 (2026-03-25)
- FP-051-054: Management Insight Layer

### v1.2.0 (2026-03-25)
- FP-040-050: Semantic Layout Upgrade

### v1.1.0 (2026-03-25)
- FP-001-011: Foundation Refinement

---

## Design System
ForgeOrchestra Obsidian Intelligence — see `/forgeorchestra/DESIGN_GUIDE.md`
Component Tokens — see `DESIGN_TOKENS.md`