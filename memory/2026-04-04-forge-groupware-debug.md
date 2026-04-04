# Memory: Forge Groupware — Deployment Debug Session

**Date:** 2026-04-04 09:17 UTC  
**VM:** forge-mail-server (35.214.38.182 / 100.70.13.38)  
**SSH Key:** ~/.ssh/forge_groupware (ED25519)

---

## Session Summary

Successfully accessed VM via SSH and identified deployment issues. Containerized services are running but nginx reverse proxy has configuration problems.

---

## Discovery: Partial Deployment Exists

The VM already had a Forge Groupware deployment from 2026-04-03:

**Files Present:**
- `/opt/forge-groupware/docker-compose.yml` — Main orchestration
- `/opt/forge-groupware/nginx.conf` — nginx configuration
- `/opt/forge-groupware/sogo.conf` — SOGo configuration
- `/opt/forge-groupware/secrets/` — Credentials directory
- `/data/appdata/mail/` — Mail storage
- `/data/appdata/groupware/postgres/` — PostgreSQL data
- `/data/appdata/groupware/redis/` — Redis data

---

## Container Status (as of 09:17 UTC)

| Container | Status | Ports | Issue |
|-----------|--------|-------|-------|
| **groupware-nginx** | 🔴 Restarting | None mapped | Port conflict + config error |
| **groupware-mail** | 🟡 Running (unhealthy) | 25, 587, 993/tcp | Postfix running but healthcheck failing |
| **groupware-sogo** | ✅ Healthy | None | Running fine |
| **groupware-postgres** | ✅ Healthy | 5432/tcp | Running fine |
| **groupware-redis** | ✅ Healthy | 6379/tcp | Running fine |
| **groupware-webmail** | ✅ Running | 8080→80 | Roundcube webmail |

---

## Issues Identified

### Issue 1: Port Conflict (RESOLVED)

**Problem:** System Apache was using ports 80/443, blocking nginx container.

```
LISTEN 0 511 *:443 *:* users:(("apache2",pid=38384,fd=6),...)
LISTEN 0 511 *:80  *:* users:(("apache2",pid=38384,fd=4),...)
```

**Action Taken:** Stopped Apache processes with `sudo pkill apache2`

**Result:** Apache stopped, nginx container attempted restart

---

### Issue 2: nginx Container Restart Loop (UNRESOLVED)

**Symptoms:**
- Container enters restart loop immediately after Apache stopped
- Logs show bind() failures on ports 80/443 (even after Apache stopped)
- Container state: `restarting - map[]` (no port mappings)

**Last Known Logs:**
```
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address still in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address still in use)
nginx: [emerg] still could not bind()
```

**Potential Causes:**
1. Another process still holding ports 80/443
2. nginx configuration syntax error
3. Missing SSL certificates
4. Docker port mapping conflict

**Next Steps:**
```bash
# Check what's using ports
sudo ss -tlnp | grep -E '(:80|:443)'
sudo lsof -i :80
sudo lsof -i :443

# Check nginx config syntax
docker exec groupware-nginx nginx -t

# Check SSL certificates exist
ls -la /data/appdata/mail-certs/

# View full nginx logs
docker logs groupware-nginx 2>&1 | tail -50
```

---

### Issue 3: Mail Container Unhealthy (INVESTIGATE)

**Symptoms:** Container running but marked unhealthy

**Observed Logs:**
- Postfix/postscreen connections from localhost
- HANGUP during SMTP handshake tests
- Appears to be normal postscreen behavior

**Mail Ports Status:**
- ✅ Port 25: Exposed and mapped
- ✅ Port 587: Exposed and mapped  
- ✅ Port 993: Exposed and mapped

**Healthcheck:** Likely timing out on Dovecot or Postfix health check

---

## SSH Connection Status

**Last Successful Connection:** 09:16 UTC  
**Connection Lost:** 09:17 UTC (Permission denied)  
**Possible Causes:**
- SSH session timeout
- Key removed from authorized_keys
- VM restarted
- Network issue

**To Reconnect:**
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/forge_groupware stuharker@35.214.38.182
```

---

## Deployment Files Location

**Local (Titan):**
- `/home/stu/.openclaw/workspace/projects/forge-groupware/`

**Remote (VM):**
- `/opt/forge-groupware/` (owned by stuharker:stuharker)

---

## GCP Firewall Rules Status

All 5 rules created earlier:
- ✅ `allow-smtp-inbound` (25/tcp)
- ✅ `allow-smtp-submission` (587/tcp)
- ✅ `allow-imap` (143/tcp)
- ✅ `allow-imaps` (993/tcp)
- ✅ `allow-http-redirect` (80/tcp)

---

## Remaining Work

1. **Fix nginx container** — Resolve bind/port/config issues
2. **Verify SSL certificates** — May need Let's Encrypt or self-signed
3. **Test mail services** — Confirm SMTP/IMAP working
4. **Configure SOGo** — Set up webmail/calendar
5. **Create mailboxes** — Add users to docker-mailserver
6. **Verify end-to-end** — Run full test suite

---

## Commands for Next Session

```bash
# Reconnect to VM
ssh -i ~/.ssh/forge_groupware stuharker@35.214.38.182

# Check port usage
sudo ss -tlnp | grep -E '(:80|:443)'

# Check container status
docker ps
docker-compose ps

# Debug nginx
docker logs groupware-nginx
docker exec groupware-nginx nginx -t

# Check SSL certs
ls -la /data/appdata/mail-certs/

# Restart stack if needed
cd /opt/forge-groupware
docker-compose down
docker-compose up -d
```

---

## Key Files

- `VM-STATUS-REPORT-2026-04-04.md` — Initial status
- `serial-console-setup.sh` — VM setup script
- `test-deployment.sh` — Connectivity tests
- This file — Debug session notes

---

*Saved to memory 2026-04-04 09:17 UTC*