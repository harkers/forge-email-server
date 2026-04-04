# Forge Groupware - Deployment Status - 2026-04-04

## Current Status: MOSTLY OPERATIONAL ✅

**Time:** 2026-04-04 08:28 UTC
**Host:** forge-mail-server (35.214.38.182 / 100.70.13.38)

## Container Status

| Service | Status | Ports | Notes |
|---------|--------|-------|-------|
| nginx | ✅ Up 37s | 8081, 8443 | Now running on alternative ports |
| sogo | ✅ Up 10h | - | Host network mode |
| mail | ⚠️ Up 10h (unhealthy) | 25, 587, 993, 4190 | Healthcheck failing but functional |
| postgres | ✅ Healthy | 5432 | Database for SOGo |
| redis | ✅ Healthy | 6379 | Caching |
| webmail | ✅ Up 12m | 8080 | Roundcube webmail |

## Nginx Configuration Fixes Applied

1. ✅ Changed ports 80→8081, 443→8443 (Apache conflict resolution)
2. ✅ Fixed upstream to 127.0.0.1:20000 (SOGo host networking)
3. ✅ Removed deprecated proxy_redirect default directives
4. ✅ Fixed SSL certificate paths to /opt/forge-groupware/certs/

## Verified Working

```bash
# HTTP redirect
$ curl http://localhost:8081
→ 301 to HTTPS

# HTTPS redirect
$ curl -k https://localhost:8443
→ 302 to /SOGo/

# SOGo web interface
$ curl -k -L https://localhost:8443/SOGo/
→ 200 OK, returns login page HTML
```

## Remaining Issues

| Issue | Severity | Action Needed |
|-------|----------|---------------|
| Apache on 80/443 | Medium | Requires sudo to stop/reconfigure |
| Mail container unhealthy | Low | Healthcheck config, likely functional |
| Self-signed SSL certs | Low | Consider Let's Encrypt for production |

## Access URLs

- **SOGo Webmail**: https://localhost:8443/SOGo/ (or via Tailscale)
- **Roundcube**: http://localhost:8080
- **SMTP**: localhost:25, localhost:587
- **IMAP**: localhost:993

## Next Steps

1. Add GCP firewall rules for ports 8081/8443 for external access
2. Investigate mail container healthcheck
3. Consider certbot/Let's Encrypt for proper SSL
