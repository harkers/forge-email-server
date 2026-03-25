# Forge Pipeline Implementation Plan

**Version:** v1.0.3 → v2.0.0  
**Date:** 2026-03-24  
**Status:** Planning → Implementation

---

## Current State (v1.0.3)

### ✅ What's Working
- **UI:** Vanilla JS + HTML, ForgeOrchestra design system (obsidian palette, platinum accent)
- **API:** Python HTTP server (server.py), SQLite backend
- **Cache:** Redis layer (summary endpoint, 60s TTL, invalidation on writes)
- **Deployment:** Docker compose (3 containers: api, web, redis)
- **Integration:** MCP upsert endpoints, webhook ingestion, event logging
- **Version control:** VERSION.md, version badge, timestamps

### ⚠️ Gaps vs Pack Spec
- No `critical` priority (only low/medium/high)
- No risk state tracking (at_risk, watch, critical)
- No stale detection (5-day rule)
- No source health (healthy, delayed, error, paused)
- No insight strip (management intelligence)
- No KPI deltas (trends: "+4 today")
- No overdue visual state
- Filter bar incomplete (missing priority/risk/due window/sort/density)

---

## Target State (v2.0.0)

### Architecture
- **Database:** PostgreSQL (production) + SQLite (dev/single-user)
- **ORM:** SQLAlchemy with Alembic migrations
- **Cache:** Redis (all hot endpoints cached)
- **UI:** Vanilla JS enhanced with pack spec (no React rewrite)
- **Design:** ForgeOrchestra system + pack tokens aligned

---

## Phased Implementation

### Phase 1 — Foundation Refinement (v1.1.0)
**Sprint:** 2026-03-24 to 2026-03-26

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-001 | Add `critical` priority to data model | 1h | ✅ DONE |
| FP-002 | Add risk state enum (none, watch, at_risk, critical) | 1h | ✅ DONE |
| FP-010 | Rename KPI labels: Open → Active tasks, add At risk | 1h | ✅ DONE |
| FP-011 | Add KPI deltas (compare to yesterday/last week) | 2h | ✅ DONE |
| FP-020 | Reduce metadata chip overload in cards | 1h | ✅ DONE |
| FP-030 | Improve empty-state treatment | 1h | ✅ DONE |
| FP-003 | Add source health to status line | 2h | ✅ DONE |

**Deliverables:**
- Updated data models (priority, risk, source state)
- KPI strip with deltas
- Source health indicator
- Refined card metadata

---

### Phase 2 — Semantic Layout Upgrade (v1.2.0)
**Sprint:** 2026-03-26 to 2026-03-28

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-040 | Rebalance board column widths (1.15 / 0.85 / 1.0) | 1h | ✅ DONE |
| FP-041 | Add timestamps to Recently changed items | 1h | ✅ DONE |
| FP-021 | Add overdue visual state to cards | 2h | ✅ DONE |
| FP-022 | Add due-soon state (≤7 days) | 2h | ✅ DONE |
| FP-023 | Implement stale detection (5 working days) | 2h | ✅ DONE |
| FP-050 | Add risk state badges to cards | 1h | ✅ DONE |

**Deliverables:**
- Stale/overdue/due-soon detection logic
- Risk state visual indicators
- Improved board layout ratios
- Timestamps on activity items

---

### Phase 3 — Management Insight Layer (v1.3.0)
**Sprint:** 2026-03-28 to 2026-03-30

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-051 | Build insight strip component | 3h | ✅ DONE |
| FP-052 | Implement "Focus now" card (recommended next action) | 3h | ✅ DONE |
| FP-053 | Add stale-work detection logic | 2h | ✅ DONE |
| FP-054 | Add source-health awareness panel | 2h | ✅ DONE |
| FP-080 | Implement derived state rules engine | 4h | ✅ DONE |

**Deliverables:**
- Insight strip (high-priority due this week, active blockers, stale items)
- Focus-now recommendation card
- Source health summary panel
- Derived state rules in scoring logic

---

### Phase 4 — PostgreSQL Migration (v1.4.0)
**Sprint:** 2026-03-30 to 2026-04-02

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-DB1 | Add SQLAlchemy + Alembic to requirements | 1h | TODO |
| FP-DB2 | Add PostgreSQL service to docker-compose | 1h | TODO |
| FP-DB3 | Write migration scripts (SQLite → Postgres) | 3h | TODO |
| FP-DB4 | Update server.py to use DATABASE_URL | 2h | TODO |
| FP-DB5 | Add connection pooling (Postgres benefit) | 1h | TODO |
| FP-DB6 | Test dual mode (SQLite dev, Postgres prod) | 2h | TODO |

**Deliverables:**
- PostgreSQL container in compose
- SQLAlchemy ORM layer
- Alembic migration scripts
- Migration tool (SQLite export → Postgres import)
- DEPLOY.md updated with Postgres instructions

**Architecture:**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: forge
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-}
      POSTGRES_DB: forge_pipeline
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
  
  api:
    environment:
      DATABASE_URL: postgresql://forge:${POSTGRES_PASSWORD}@postgres:5432/forge_pipeline
      REDIS_HOST: redis
  
  web:
    # unchanged
```

---

### Phase 5 — Filters & Interaction (v1.5.0)
**Sprint:** 2026-04-02 to 2026-04-05

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-060 | Build full filter bar (priority, risk, due window, sort, density) | 4h | ✅ DONE |
| FP-061 | Task detail drawer | 2h | ✅ DONE |
| FP-062 | Quick actions menu on task cards | 2h | ✅ DONE |
| FP-063 | Sorting logic | 2h | ✅ DONE |
| FP-064 | Density modes (comfortable/compact/tight) | 2h | ✅ DONE |
| FP-061 | Add task detail drawer (expandable card) | 3h | TODO |
| FP-062 | Add quick actions menu to task cards | 2h | TODO |
| FP-063 | Add sorting logic (priority, due date, updated, created) | 2h | TODO |
| FP-064 | Add density modes (comfortable, compact, tight) | 2h | TODO |

**Deliverables:**
- Complete filter bar
- Task detail drawer
- Quick actions (edit, change status, assign, delete)
- Sort controls
- Density toggle

---

### Phase 6 — Design System Alignment (v1.6.0)
**Sprint:** 2026-04-05 to 2026-04-07

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-070 | Define Forge Pipeline design tokens | 2h | ✅ DONE |
| FP-071 | Align tokens with ForgeOrchestra parent | 2h | ✅ DONE |
| FP-072 | Document component specs for reuse | 3h | ✅ DONE |
| FP-073 | Implement semantic color system | 2h | ✅ DONE |

**Deliverables:**
- Design tokens (colors, spacing, typography, radii)
- Component specification document
- Alignment with ForgeOrchestra parent system
- Token documentation in TOOLS.md

---

### Phase 7 — Advanced Orchestration (v2.0.0)
**Sprint:** 2026-04-07 to 2026-04-12

| Ticket | Feature | Effort | Status |
|--------|---------|--------|--------|
| FP-090 | Build recommendation engine (Focus now algorithm) | 4h | ✅ DONE |
| FP-091 | Add dependency visualisation (task links, blockers) | 4h | TODO |
| FP-092 | Implement multi-workspace rollups | 4h | TODO |
| FP-093 | Build executive summary mode | 3h | ✅ DONE |
| FP-094 | Add WebSocket for real-time updates (replace polling) | 3h | TODO |

**Deliverables:**
- Recommendation engine (derived operational intelligence)
- Dependency graph visualisation
- Multi-workspace dashboard
- Executive summary view
- Real-time updates via WebSocket

---

## Technical Debt & Improvements

### Performance
- ✅ Redis cache (summary endpoint) — DONE v1.0.3
- ⏳ Cache projects list (120s TTL) — Phase 1
- ⏳ Cache events (30s TTL) — Phase 1
- ⏳ Add pagination to list endpoints — Phase 2
- ⏳ Add full-text search (SQLite FTS5 / Postgres tsvector) — Phase 4

### Observability
- ⏳ Add request logging (structured JSON) — Phase 4
- ⏳ Add `/api/metrics` endpoint (Prometheus format) — Phase 4
- ⏳ Add request latency tracking — Phase 4

### API
- ⏳ Add API versioning (`/api/v1/`) — Phase 5
- ⏳ Generate OpenAPI spec — Phase 5
- ⏳ Add rate limiting (Redis-based) — Phase 4

### UX
- ⏳ Add WebSocket for real-time updates — Phase 7
- ⏳ Add background job queue (RQ/Celery) — Phase 7
- ⏳ Add export improvements (async, scheduled) — Phase 6

---

## Migration Path

### SQLite → PostgreSQL
```bash
# 1. Export SQLite data
python3 scripts/export_db.py > migration-export.json

# 2. Start Postgres container
docker-compose up -d postgres

# 3. Run migration script
python3 scripts/migrate_sqlite_to_postgres.py migration-export.json

# 4. Update .env
DATABASE_URL=postgresql://forge:${POSTGRES_PASSWORD}@postgres:5432/forge_pipeline

# 5. Restart API
docker-compose restart api

# 6. Verify
curl http://localhost:4174/api/health | jq '.database'
```

### Data Model Changes
```sql
-- Add critical priority
ALTER TABLE tasks ADD COLUMN priority CHECK (priority IN ('low', 'medium', 'high', 'critical'));

-- Add risk state
ALTER TABLE tasks ADD COLUMN risk_state VARCHAR(32) DEFAULT 'none';
ALTER TABLE tasks ADD COLUMN due_date DATE;
ALTER TABLE tasks ADD COLUMN last_updated DATE;

-- Add source state
ALTER TABLE projects ADD COLUMN source_state VARCHAR(32) DEFAULT 'healthy';
```

---

## Success Metrics

### Performance
- Summary endpoint: <50ms (cached) vs ~500ms (uncached)
- Page load: <1s initial, <200ms cached
- Concurrent writers: 10+ without SQLite lock contention

### UX
- Time-to-insight: <5s to see "what needs attention now"
- Stale detection accuracy: >90% (5-day rule)
- Filter usability: <3 clicks to find specific task

### Reliability
- Uptime: >99% (healthchecks + auto-restart)
- Data durability: Postgres WAL + daily backups
- Cache hit rate: >80% on hot endpoints

---

## Rollback Plan

If PostgreSQL migration fails:
1. Stop API container
2. Revert DATABASE_URL to SQLite path
3. Restart API
4. Data intact (SQLite unchanged)

If UI changes break:
1. Revert git commit
2. Rebuild web container
3. Restart

---

## Definition of Done

Each phase is complete when:
- ✅ All tickets implemented
- ✅ Tests passing (manual + automated if added)
- ✅ DEPLOY.md updated
- ✅ VERSION.md bumped
- ✅ Git committed with changelog
- ✅ Running in production (Docker)

---

## Next Action

**Starting Phase 1** — Foundation Refinement.

First tickets:
1. FP-001: Add `critical` priority
2. FP-002: Add risk state enum
3. FP-010: Rename KPI labels
4. FP-011: Add KPI deltas
5. FP-003: Add source health

**Begin implementation?**
