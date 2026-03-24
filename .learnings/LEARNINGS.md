# Learnings Log

Track corrections, knowledge gaps, best practices, and user feedback for continuous improvement.

## Format

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001 (if related to existing entry)
- Pattern-Key: simplify.dead_code | harden.input_validation (optional)
- Recurrence-Count: 1 (optional)
- First-Seen: 2025-01-15 (optional)
- Last-Seen: 2025-01-15 (optional)

---
```

## Entries

## [LRN-20260324-001] trilium_etapi_auth

**Logged**: 2026-03-24T14:50:00Z
**Priority**: high
**Status**: promoted
**Area**: infra

### Summary
Trilium ETAPI uses plain `Authorization` header, NOT Bearer token auth

### Details
Initial attempts failed with various auth patterns:
- `Authorization: Bearer <token>` ❌
- `X-API-Key: <token>` ❌
- Password login with token ❌

Correct pattern discovered via OpenAPI spec:
- `Authorization: <token>` (plain, no "Bearer" prefix)
- Works on ETAPI endpoints: `/etapi/notes`, `/etapi/create-note`, `/etapi/branches`

### Suggested Action
Always use plain Authorization header for Trilium ETAPI calls:
```bash
curl -H "Authorization: <token>" http://host:8080/etapi/...
```

### Metadata
- Source: error
- Related Files: skills/trilium-etapi/SKILL.md
- Tags: trilium, etapi, auth
- Pattern-Key: trilium.etapi.auth
- Recurrence-Count: 1
- First-Seen: 2026-03-24

### Resolution
- **Promoted**: skills/trilium-etapi/SKILL.md
- **Notes**: Created complete ETAPI skill with auth pattern documented

### Resolution (Dashboard Fix)
- **Resolved**: 2026-03-24T17:05:00Z
- **Fix**: Use explicit host IP in nginx for host network mode
- **Promoted**: TOOLS.md (pending)

---

## [LRN-20260324-002] mcp_deployer_image_names

**Logged**: 2026-03-24T16:24:00Z
**Priority**: medium
**Status**: promoted
**Area**: infra

### Summary
MCP deployer expects `ddh-web` and `ddh-api` image names, not `forge-pipeline-*`

### Details
Built images as `localhost:5000/forge-pipeline-web:latest` and `localhost:5000/forge-pipeline-api:latest`.

MCP deployer payload requires:
```json
{
  "label": "ddh-web",
  "image": "localhost:5000/ddh-web:latest",
  ...
}
```

Must tag before deploy:
```bash
docker tag localhost:5000/forge-pipeline-web:latest localhost:5000/ddh-web:latest
docker push localhost:5000/ddh-web:latest
```

### Suggested Action
Always tag images as ddh-* before MCP deployment, or build with ddh-* names from start.

### Metadata
- Source: conversation
- Related Files: skills/forge-pipeline-deploy-mcp/SKILL.md
- Tags: mcp, deployer, docker
- Pattern-Key: mcp.deployer.image-names
- Recurrence-Count: 1
- First-Seen: 2026-03-24

### Resolution
- **Promoted**: skills/forge-pipeline-deploy-mcp/SKILL.md
- **Notes**: Skill documents exact tag/push commands

---

## [LRN-20260324-003] host_network_nginx_dns

**Logged**: 2026-03-24T16:42:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Nginx in host network mode can't resolve Docker network aliases (falls back to public DNS)

### Details
Deployed web container with host network mode. Nginx config:
```nginx
proxy_pass http://api:4181/api/;
```

Expected `api` to resolve to ddh-api container via Docker network.

Actual behavior:
- `api` hostname not found in container's DNS
- Falls back to public DNS resolvers
- Resolves to Cloudflare IPs (172.67.220.18, 104.21.45.235)
- Connection timeout → 502 Bad Gateway

Root cause: Host network mode bypasses Docker networking. Container uses host's DNS, not Docker's internal DNS.

### Suggested Action
Use explicit host IP in nginx config for host network mode:
```nginx
proxy_pass http://192.168.10.80:4181/api/;
```

Alternative: Use bridge network with proper alias, or pass API URL via env var.

### Metadata
- Source: error
- Related Files: forge-pipeline/deploy/nginx/default.conf
- Tags: nginx, dns, host-network, docker
- Pattern-Key: nginx.host-network.dns
- Recurrence-Count: 1
- First-Seen: 2026-03-24

---

## [LRN-20260324-004] quarto_bundled_deno

**Logged**: 2026-03-24T15:48:00Z
**Priority**: medium
**Status**: promoted
**Area**: infra

### Summary
Quarto CLI requires bundled Deno runtime, not system Deno

### Details
Attempted to run quarto with system Deno (v2.7.7):
```
error: Uncaught SyntaxError: Invalid flags supplied to RegExp constructor 'l'
```

Quarto v1.4.557 bundles Deno v2.3.1 at `bin/tools/x86_64/deno`.

The quarto.js script uses Deno-specific APIs incompatible with newer Deno versions.

Solution: Use bundled Deno via shell wrapper:
```bash
#!/bin/bash
QUARTO_HOME="$HOME/.local/quarto"
exec "$QUARTO_HOME/bin/tools/x86_64/deno" run --allow-all "$QUARTO_HOME/bin/quarto.js" "$@"
```

### Suggested Action
Always use quarto's bundled Deno, never system Deno. Install complete quarto package, not just quarto.js.

### Metadata
- Source: error
- Related Files: skills/ (none, manual install)
- Tags: quarto, deno, runtime
- Pattern-Key: quarto.bundled-deno
- Recurrence-Count: 1
- First-Seen: 2026-03-24

### Resolution
- **Promoted**: TOOLS.md (local notes)
- **Notes**: Documented install path and bundled Deno location

---

## [LRN-20260324-005] trillium_calendar_structure

**Logged**: 2026-03-24T16:05:00Z
**Priority**: low
**Status**: promoted
**Area**: docs

### Summary
Trilium calendar structure: Calendar → Year → Month → Day

### Details
Calendar hierarchy for filing daily notes:
```
Calendar (root)
└── 2026
    └── 03 - March
        └── 24 - Tuesday
            └── Daily Summary - 2026-03-24
```

Navigate via ETAPI:
1. Search for "calendar" → get root
2. Search for year → get 2026 note
3. Search for "03 - March" → get month note
4. Search for "24 - Tuesday" → get day note
5. Create daily summary under day note

### Suggested Action
Use this structure for all daily summaries. Create year/month/day notes if they don't exist.

### Metadata
- Source: conversation
- Related Files: skills/trilium-daily-summary/SKILL.md
- Tags: trilium, calendar, organization
- Pattern-Key: trilium.calendar.structure
- Recurrence-Count: 1
- First-Seen: 2026-03-24

### Resolution
- **Promoted**: skills/trilium-daily-summary/SKILL.md
- **Notes**: Skill automates nightly filing under calendar

---

## [LRN-20260324-006] conversation_archive_qmd

**Logged**: 2026-03-24T15:52:00Z
**Priority**: medium
**Status**: promoted
**Area**: docs

### Summary
Store conversations as executable .qmd documents for searchable, versioned archive

### Details
Created convention:
```
memory/conversations/
├── YYYY-MM-DD-session-NNN.qmd
├── index.qmd
├── render.sh
└── _site/ (rendered HTML)
```

Benefits:
- Executable: code chunks can be re-run
- Multi-format: render to HTML, PDF, or site
- Versioned: git-tracked with full history
- Structured: YAML metadata (date, topics, model, outcomes)

### Suggested Action
Capture every session as .qmd file. Render via `./render.sh` for HTML archive.

### Metadata
- Source: conversation
- Related Files: memory/conversations/
- Tags: quarto, archive, documentation
- Pattern-Key: conversation.archive.qmd
- Recurrence-Count: 1
- First-Seen: 2026-03-24

### Resolution
- **Promoted**: AGENTS.md (workspace convention)
- **Notes**: First session captured: 2026-03-24-session-001.qmd

---

## [LRN-20260324-007] vite_hardcoded_api_url

**Logged**: 2026-03-24T16:21:00Z
**Priority**: medium
**Status**: resolved
**Area**: frontend

### Summary
Vite build bakes API URL into static assets - must set at build time for cross-machine access

### Details
Web app built with `VITE_API_URL=http://localhost:4181`.

When deployed, browser fetches fail from other machines because:
- Hardcoded `localhost` only works on titan
- LAN clients need `http://192.168.10.80:4181`
- Tailscale clients need `http://100.117.50.105:4181`

Solution: Rebuild with correct URL:
```bash
VITE_API_URL=http://192.168.10.80:4181 npm run build
```

Or use runtime config (depends on framework).

### Suggested Action
Set VITE_API_URL at build time based on deployment target. Consider runtime config for multi-tenant deploys.

### Metadata
- Source: conversation
- Related Files: forge-pipeline/Dockerfile.web
- Tags: vite, api, build, configuration
- Pattern-Key: vite.hardcoded-api-url
- Recurrence-Count: 1
- First-Seen: 2026-03-24

---

<!-- New entries appended above this line -->
