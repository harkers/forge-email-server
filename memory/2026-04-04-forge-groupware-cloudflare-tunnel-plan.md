# Forge Groupware - Cloudflare Tunnel Deployment

## Current Status: Transitioning to Zero-Trust Security Model

**Date:** 2026-04-04 08:30 UTC
**Goal:** Eliminate Apache security risk, hide all services behind Cloudflare Tunnel

## Security Issue Identified

**Apache processes running on VM:**
- Listening on 0.0.0.0:80 and 0.0.0.0:443
- Cannot be stopped without sudo
- Exposes attack surface directly to internet

**Risk:** Direct exposure of Apache with unknown configuration

## Solution: Cloudflare Tunnel (Zero Trust)

### Benefits
| Security Feature | Implementation |
|-----------------|----------------|
| No open ports | Outbound-only tunnel connection |
| No direct exposure | Services bind to localhost only |
| Automatic SSL | Cloudflare manages certificates |
| DDoS protection | Built into Cloudflare edge |
| Access logging | Cloudflare dashboard |

## Architecture Change

### Before (Current - At Risk)
```
Internet ─→ GCP Firewall ─→ Apache (0.0.0.0:80/443) ❌
                           ↓
                    Direct exposure
```

### After (Target - Secure)
```
Internet ─→ Cloudflare Edge ─→ Cloudflared ─→ Nginx (localhost) → SOGo
                         ↑                    (internal only)
                    SSL + WAF + DDoS
```

## Files Created

1. `cloudflared-compose.yml` - Tunnel container config
2. `.env.example` - Environment variable template
3. `CLOUDFLARE_TUNNEL_SETUP.md` - Full setup guide

## Next Actions Required

1. **Human action:** Stop/remove Apache on VM:
   ```bash
   sudo systemctl stop apache2
   sudo apt remove apache2
   ```

2. **Human action:** Create Cloudflare Tunnel at one.dash.cloudflare.com

3. **Get token** and add to `.env` file

4. **Deploy:** `docker compose -f cloudflared-compose.yml up -d`

5. **Configure** public hostnames in Cloudflare dashboard

6. **Update** nginx to bind to localhost only

## Decision Required

Do you want to:
- **Option A:** Stop Apache now and proceed with Cloudflare Tunnel setup?
- **Option B:** Investigate what Apache is serving first?
- **Option C:** Use Apache as the reverse proxy instead of nginx?

**Recommendation:** Option A - Cloudflare Tunnel is the most secure approach.
