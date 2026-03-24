# Forge Pipeline Review & Improvement Suggestions

**Reviewed:** 2026-03-24  
**Version:** v1.0.0

---

## Current State Assessment

### ✅ What's Working Well

1. **Clean architecture**: Two-container setup (API + web) is simple and maintainable
2. **SQLite backend**: No external database dependency, easy to backup/restore
3. **API key auth**: Optional write protection via `FORGE_PIPELINE_API_KEY`
4. **Healthchecks**: Both services have proper health monitoring
5. **MCP integration**: Project/task upsert endpoints for external automation
6. **Webhook support**: External systems can push events and updates
7. **ForgeOrchestra design**: Premium obsidian intelligence palette, platinum blue accents
8. **Version tracking**: VERSION.md, version badge in UI, build date in app.js

### ⚠️ Current Limitations

1. **Port conflict**: Host nginx occupies 4173, blocking web container startup
2. **No caching layer**: Every request hits SQLite directly
3. **No connection pooling**: SQLite is file-based, but concurrent writes could block
4. **No rate limiting**: API is open if no key is set
5. **No metrics/observability**: No request logging, no performance tracking
6. **No search indexing**: Full-text search is naive string matching
7. **No pagination**: `/api/projects` and `/api/tasks` return all results
8. **No background jobs**: No async processing for imports/exports
9. **No WebSocket**: UI polls every 30s instead of real-time updates
10. **No audit trail**: Events are stored but not exported/analyzed

---

## Priority Improvements

### 🔴 Critical (Do Now)

#### 1. Resolve Port Conflict
**Problem:** Host nginx occupies port 4173  
**Solution:** 
- Stop host nginx: `sudo systemctl stop nginx`
- Or change compose port to 4174
- Or configure host nginx to proxy_pass to container

**Impact:** Blocks deployment entirely

---

### 🟡 High (Next Sprint)

#### 2. Add Redis Cache Layer
**Problem:** Every request hits SQLite, no caching for hot paths  
**Solution:** Add Redis service for:
- Summary endpoint caching (project/task counts) — 60s TTL
- Event log read caching — 30s TTL
- Rate limiting keys (if internet-exposed)
- Session/token storage (future auth expansion)

**Implementation:**
```yaml
services:
  redis:
    image: redis:alpine
    container_name: forge-pipeline-redis
    restart: unless-stopped
    expose:
      - "6379"
    volumes:
      - ./redis-data:/data
    command: redis-server --appendonly yes
```

**API changes needed:**
- Cache `GET /api/summary` (60s TTL)
- Cache `GET /api/events` (30s TTL)
- Invalidate cache on write operations
- Add `X-Cache-Status` header for debugging

**Impact:** 10-100x faster reads, reduced SQLite contention

---

#### 3. Add Pagination
**Problem:** `/api/projects` and `/api/tasks` return all results — will break at scale  
**Solution:** Add `?limit=50&offset=0` query params

**Implementation:**
```python
# server.py
limit = int(q.get('limit', ['100'])[0])
offset = int(q.get('offset', ['0'])[0])
rows = conn.execute('SELECT * FROM projects ORDER BY updated_at DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
```

**Response envelope:**
```json
{
  "projects": [...],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "hasMore": true
}
```

**Impact:** Prevents OOM at 500+ projects, standard API pattern

---

#### 4. Add Full-Text Search
**Problem:** Current search is naive string matching in Python  
**Solution:** Use SQLite FTS5 virtual table

**Implementation:**
```sql
CREATE VIRTUAL TABLE projects_fts USING fts5(name, description, notes, tags_json);
-- Trigger to sync projects table to FTS
```

**Impact:** Fast, relevant search at scale

---

#### 5. Add Request Logging & Metrics
**Problem:** No visibility into API performance or errors  
**Solution:** 
- Log all requests to file (structured JSON)
- Track request latency, status codes, endpoints
- Add `GET /api/metrics` endpoint (Prometheus format)

**Implementation:**
```python
import logging
import time
from logging.handlers import RotatingFileHandler

# Configure rotating file handler
handler = RotatingFileHandler(STORAGE_DIR / 'access.log', maxBytes=10_000_000, backupCount=5)
```

**Impact:** Debug production issues, track performance trends

---

### 🟢 Medium (Future)

#### 6. Add WebSocket for Real-Time Updates
**Problem:** UI polls every 30s — wasteful, laggy  
**Solution:** WebSocket endpoint for live updates

**Implementation:**
- Use `websockets` library in Python
- Broadcast events to connected clients
- UI subscribes to `/ws/events`

**Impact:** Instant UI updates, no polling overhead

---

#### 7. Add Background Job Queue
**Problem:** Bulk imports/exports block HTTP request  
**Solution:** Use RQ (Redis Queue) or Celery

**Implementation:**
```yaml
services:
  worker:
    build:
      context: .
      dockerfile: Dockerfile.api
    command: python3 worker.py
    depends_on:
      - redis
    volumes:
      - ./api/storage:/app/storage
```

**Impact:** Non-blocking imports/exports, better UX

---

#### 8. Add PostgreSQL Option
**Problem:** SQLite doesn't scale for multi-writer scenarios  
**Solution:** Add PostgreSQL support as alternative backend

**Implementation:**
- Add `DATABASE_URL` env var
- Use SQLAlchemy for ORM abstraction
- Migrate schema on startup

**Impact:** Horizontal scale, ACID guarantees, replication

---

#### 9. Add API Versioning
**Problem:** No version in API paths — breaking changes will break clients  
**Solution:** Version all endpoints: `/api/v1/projects`

**Implementation:**
- Add `Accept: application/vnd.forge.v1+json` header support
- Deprecate old versions with `Sunset` header

**Impact:** Safe evolution of API, backward compatibility

---

#### 10. Add OpenAPI Spec
**Problem:** No machine-readable API documentation  
**Solution:** Generate OpenAPI 3.0 spec

**Implementation:**
- Use `apispec` or `flasgger` library
- Serve at `/api/openapi.json`
- Add Swagger UI at `/api/docs`

**Impact:** Auto-generated docs, client SDK generation

---

## Redis Integration Plan

### Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web UI    │────▶│   API       │────▶│   SQLite    │
│  (port 4173)│     │ (port 4181) │     │   (file)    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Redis     │
                    │ (port 6379) │
                    └─────────────┘
```

### Cache Strategy

| Endpoint | Cache TTL | Invalidation |
|----------|-----------|--------------|
| `GET /api/summary` | 60s | On any project/task write |
| `GET /api/events` | 30s | On new event |
| `GET /api/projects` | 120s | On project write |
| `GET /api/projects/:id` | 120s | On project write |
| `GET /api/export` | 300s | On any write |

### Rate Limiting (if internet-exposed)
```python
from redis import Redis
from functools import wraps

redis = Redis(host='redis', port=6379)

def rate_limit(max_requests=100, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = self.client_address[0]
            key = f'ratelimit:{client_ip}'
            current = redis.incr(key)
            if current == 1:
                redis.expire(key, window)
            if current > max_requests:
                self.send_json(429, {'error': 'rate_limit_exceeded'})
                return
            return f(*args, **kwargs)
        return wrapped
    return decorator
```

### Redis Key Naming Convention
```
cache:summary              # Summary endpoint
cache:events:{limit}       # Events with limit param
cache:projects             # All projects list
cache:project:{id}         # Single project
ratelimit:{ip}             # Rate limit counter
session:{token}            # Future session storage
```

---

## Implementation Priority

1. **Port conflict** — blocks deployment
2. **Redis cache** — immediate performance gain
3. **Pagination** — prevents future breakage
4. **Request logging** — observability
5. **Full-text search** — better UX
6. **WebSocket** — real-time updates
7. **Background jobs** — async processing
8. **OpenAPI spec** — documentation
9. **API versioning** — future-proofing
10. **PostgreSQL option** — horizontal scale

---

## Next Actions

1. Fix port conflict (stop host nginx or change port)
2. Add Redis service to docker-compose
3. Implement summary caching in server.py
4. Add pagination to list endpoints
5. Add access logging

---

**ForgeOrchestra Design System:** All improvements should follow the obsidian intelligence aesthetic — calm, powerful, ruthlessly coherent.
