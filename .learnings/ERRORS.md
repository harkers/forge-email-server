# Errors Log

Track command failures, exceptions, and unexpected errors for continuous improvement.

## Format

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
```
Actual error message or output
```

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (if recurring)

---
```

## Entries

## [ERR-20260324-001] forge_pipeline_nginx_port

**Logged**: 2026-03-24T16:35:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Nginx web container failed to start due to port conflict (80 vs 4173)

### Error
```
bind() to 0.0.0.0:80 failed (98: Address in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed
```

### Context
- Deployed via MCP deployer with `listen_port: 4173`
- Web image: `FROM nginx:alpine` with `EXPOSE 80`
- Config: `deploy/nginx/default.conf` had `listen 80;`
- Host network mode expects container on 4173, but nginx binds 80
- Port 80 already occupied on host

### Suggested Fix
Rebuild web image to listen on 4173:
1. Update Dockerfile: `EXPOSE 4173`
2. Update nginx config: `listen 4173;`
3. Rebuild and push: `docker build -f Dockerfile.web -t localhost:5000/ddh-web:latest .`
4. Redeploy via MCP deployer

### Resolution
- **Resolved**: 2026-03-24T16:31:00Z
- **Commit**: 683e7d2 (Dockerfile.web + default.conf updated)
- **Notes**: Rebuilt nginx to listen on 4173, redeployed successfully

### Resolution (Dashboard Fix)
- **Resolved**: 2026-03-24T17:05:00Z
- **Fix**: Changed `proxy_pass http://api:4181/` → `http://192.168.10.80:4181/`
- **Notes**: Dashboard now shows 12 projects, 54 tasks (was 0)

### Metadata
- Reproducible: yes
- Related Files: forge-pipeline/Dockerfile.web, forge-pipeline/deploy/nginx/default.conf
- See Also: None (first occurrence)

---

## [ERR-20260324-002] forge_pipeline_dashboard_empty

**Logged**: 2026-03-24T16:42:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Dashboard shows 0 projects/tasks due to nginx upstream DNS resolution failure

### Error
```
2026/03/24 16:38:33 [error] *53 no live upstreams while connecting to upstream
upstream: "http://172.67.220.18:4181/api/events"  ❌ (Cloudflare IP)
upstream: "http://104.21.45.235:4181/api/summary" ❌ (Cloudflare IP)
GET /api/projects → 502 Bad Gateway
GET /api/summary → 502 Bad Gateway
```

### Context
- Nginx config: `proxy_pass http://api:4181/api/;`
- Expected: `api` hostname resolves to ddh-api container (Docker network)
- Actual: DNS falls back to public resolvers, hits Cloudflare IPs
- Result: Connection timeout → 502 Bad Gateway
- Dashboard shows 0 projects, 0 tasks (all API calls fail)

### Suggested Fix
Update nginx config to use explicit host IP:
```nginx
location /api/ {
    proxy_pass http://192.168.10.80:4181/api/;
    ...
}
```
Then rebuild and redeploy web container.

### Metadata
- Reproducible: yes
- Related Files: forge-pipeline/deploy/nginx/default.conf
- See Also: ERR-20260324-001 (same deployment)

---

<!-- New entries appended above this line -->
