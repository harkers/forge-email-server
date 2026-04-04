# Forge Groupware - Nginx Fixed - 2026-04-04

## Issue Fixed: Nginx Port Conflict
**Time:** 2026-04-04 08:28 UTC
**Problem:** Apache processes were holding ports 80/443, preventing nginx from starting

## Changes Made

### 1. Nginx Container Configuration
- Changed from bridge network to host network mode
- Changed ports from 80/443 to 8081/8443 (to avoid Apache conflict)
- Fixed upstream to use `127.0.0.1:20000` instead of `sogo:20000`
- Removed deprecated `proxy_redirect default` directives
- Updated SSL certificate paths to `/opt/forge-groupware/certs/`

### 2. Nginx Config Fixes
```bash
# Changed upstream to use localhost
upstream sogo {
    server 127.0.0.1:20000;
}

# Changed listen ports
listen 8081;           # was 80
listen 8443 ssl;       # was 443

# Removed proxy_redirect default lines
# Fixed SSL certificate paths
ssl_certificate /opt/forge-groupware/certs/groupware.crt;
ssl_certificate_key /opt/forge-groupware/certs/groupware.key;
```

### 3. Container Recreation
```bash
docker stop groupware-nginx
docker rm groupware-nginx
docker run -d --name groupware-nginx --restart unless-stopped \
  --network host \
  -v /opt/forge-groupware/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /opt/forge-groupware/certs:/opt/forge-groupware/certs:ro \
  nginx:alpine
```

## Current Status

| Component | Status | Endpoint |
|-----------|--------|----------|
| nginx | ✅ Running | http://localhost:8081, https://localhost:8443 |
| SOGo | ✅ Accessible via nginx | https://localhost:8443/SOGo/ |
| Apache | ⚠️ Still running on 80/443 | Cannot be stopped without sudo |

## Verification
```bash
curl -s -k -L https://localhost:8443/SOGo/
# Returns SOGo login page HTML ✓
```

## Remaining Issues
1. **Apache still running** - Needs sudo to kill, holding ports 80/443
2. **Self-signed cert** - Using groupware.crt/key instead of Let's Encrypt
3. **Port 8080 webmail** - Roundcube still running on port 8080

## Next Steps
- Add GCP firewall rules for ports 8081/8443 if external access needed
- Consider using Apache instead of nginx (since Apache is already running)
- Or obtain sudo to stop Apache and reclaim ports 80/443
