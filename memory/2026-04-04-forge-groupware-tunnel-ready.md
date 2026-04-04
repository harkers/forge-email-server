# Forge Groupware - Cloudflare Tunnel Ready for Deployment

## Status: Awaiting Cloudflare Token

**Date:** 2026-04-04 08:41 UTC
**Prepared by:** Claw

## Current Infrastructure

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| nginx | ✅ Running | 8081/8443 | Working, SOGo accessible |
| Apache | ⚠️ Running | 80/443 | Unknown origin, being bypassed |
| SOGo | ✅ Running | 20000 | Via nginx proxy |
| Postgres | ✅ Healthy | 5432 | Database |
| Redis | ✅ Healthy | 6379 | Cache |
| Roundcube | ✅ Running | 8080 | Webmail (separate) |

## Files Ready for Deployment

### 1. `cloudflared-compose.yml`
```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: groupware-cloudflared
    restart: unless-stopped
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=${TUNNEL_TOKEN}
    networks:
      - groupware-net
```

### 2. `.env.example`
```bash
TUNNEL_TOKEN=eyJh...your-token-here...
```

### 3. Documentation
- `CLOUDFLARE_TUNNEL_SETUP.md` - Full setup guide
- `CLOUDFLARE_TUNNEL_WORKAROUND.md` - Apache workaround guide

## Deployment Command (Ready to Run)

Once you have the token:

```bash
ssh -i ~/.ssh/forge_groupware stuharker@35.214.38.182
cd /opt/forge-groupware

# Create .env with your token
echo "TUNNEL_TOKEN=eyJh...your-actual-token..." > .env

# Deploy
docker compose -f cloudflared-compose.yml up -d

# Verify
docker logs groupware-cloudflared
```

## Cloudflare Configuration Required

1. Go to https://one.dash.cloudflare.com
2. **Networks** → **Tunnels** → **Create a tunnel**
3. Select **Cloudflared**
4. Choose **Docker** as environment
5. Copy the token (starts with `eyJh...`)
6. Configure public hostnames:
   - `groupware.orderededge.co.uk` → `https://localhost:8443`
   - `mail.orderededge.co.uk` → `https://localhost:8443`

## Security Benefits After Deployment

| Feature | Current | After Tunnel |
|---------|---------|--------------|
| Open ports | Multiple (25, 587, 993, 8080, 8081, 8443) | **Zero** |
| Direct exposure | Yes (Apache on 80/443) | **None** |
| SSL management | Self-signed | **Cloudflare auto** |
| DDoS protection | None | **Cloudflare** |
| Access control | None | **Cloudflare Access** (optional) |

## Testing Plan

After deployment:
1. `docker logs groupware-cloudflared` - should show "Connected"
2. Visit https://groupware.orderededge.co.uk/SOGo/ - should load login page
3. Test email sending via tunnel

## Rollback

If needed:
```bash
docker stop groupware-cloudflared
docker rm groupware-cloudflared
rm .env
```

Then delete tunnel in Cloudflare dashboard.

---
**Ready to deploy once you provide the Cloudflare tunnel token!**
