# Forge Pipeline Version

## Current Version
**v1.4.0** — 2026-03-25

## Changelog

### v1.4.0 (2026-03-25)
- FP-DB1: Add SQLAlchemy + psycopg2-binary to requirements
- FP-DB2: Add PostgreSQL service to docker-compose
- FP-DB3: Implement dual-mode database layer (SQLite/PostgreSQL)
- FP-DB4: Configure DATABASE_URL for PostgreSQL in docker-compose
- FP-DB5: Add connection pooling for PostgreSQL
- FP-DB6: PostgreSQL operational with health check showing storage: postgresql

**Database Architecture:**
- SQLite for development (default)
- PostgreSQL for production (via DATABASE_URL env var)
- PostgresConnection wrapper provides sqlite3-compatible interface
- PostgresRow class supports both dict and attribute access

### v1.3.0 (2026-03-25)
- FP-051-054: Management Insight Layer

### v1.2.0 (2026-03-25)
- FP-040-050: Semantic Layout Upgrade

### v1.1.0 (2026-03-25)
- FP-001-011: Foundation Refinement

---

## Design System
ForgeOrchestra Obsidian Intelligence — see `/forgeorchestra/DESIGN_GUIDE.md`