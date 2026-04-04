# Forge Mail Server Build Document

**Generated:** 2026-04-04  
**Status:** ✅ Deployed and Operational  
**Project ID:** FORGE-GW-001

---

## Overview

Forge Mail Server is a privacy-first groupware deployment on Google Cloud Platform, providing email, calendar, and contacts management via SOGo. The architecture emphasizes zero-trust security with no exposed IP addresses—all traffic routes through Cloudflare Tunnel.

---

## Infrastructure Summary

| Component | Value |
|-----------|-------|
| **Host** | GCP VM `forge-mail-server` |
| **External IP** | 35.214.38.182 (not exposed to internet) |
| **Provider** | Google Cloud Platform |
| **Project** | `orderededge-groupware` |
| **Tailscale IP** | 100.117.50.105/32 |
| **Region** | Likely europe-west2 (London) |
| **Edge** | Cloudflare London (LHR) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER REQUESTS                               │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE ZERO TRUST                             │
│  • DNS: groupware.orderededge.co.uk → *.cfargotunnel.com            │
│  • Tunnel ID: 53d2b65c-60e0-4e1e-a20a-ce1a59deeb5a                  │
│  • Edge: Cloudflare LHR (London)                                     │
│  • Zero Trust policies (optional)                                    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARED (on VM)                               │
│  • Container: groupware-cloudflared                                  │
│  • Listens: localhost:8081                                          │
│  • Routes: *.orderededge.co.uk → internal services                  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      NGINX (Reverse Proxy)                           │
│  • Container: groupware-nginx                                       │
│  • SSL Termination                                                  │
│  • Routes /SOGo/ → SOGo backend                                      │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SOGo (Groupware)                             │
│  • Container: groupware-sogo                                        │
│  • Webmail, Calendar, Contacts                                      │
│  • Connects to: PostgreSQL, Redis, Mail Server                      │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES                                 │
│  • PostgreSQL: /data/appdata/groupware/postgres                    │
│  • Redis: /data/appdata/groupware/redis                             │
│  • Mail Server: /data/appdata/mail                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Services Deployed

### Core Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| **Cloudflared** | `groupware-cloudflared` | 8081 (internal) | Cloudflare Tunnel connector |
| **Nginx** | `groupware-nginx` | 80/443 | Reverse proxy, SSL termination |
| **SOGo** | `groupware-sogo` | Internal | Webmail, calendar, contacts |
| **Mail Server** | `groupware-mail` | 993/587 | IMAP/SMTP (via tunnel) |
| **PostgreSQL** | `groupware-postgres` | 5432 (internal) | Database backend |
| **Redis** | `groupware-redis` | 6379 (internal) | Session/cache storage |

### Access Points

| Service | URL | Protocol |
|---------|-----|----------|
| **Webmail** | `https://groupware.orderededge.co.uk/SOGo/` | HTTPS |
| **IMAP** | `mail.orderededge.co.uk:993` | IMAPS |
| **SMTP** | `mail.orderededge.co.uk:587` | Submission |

---

## Security Architecture

### Zero Trust Design

- **No exposed ports**: VM has no public firewall rules for services
- **Cloudflare Tunnel**: All traffic routes through Cloudflare Edge
- **Tailscale VPN**: Management access via Tailscale mesh network
- **No SSH keys on disk**: SSH key stored locally on Titan workstation

### Access Control

| Access Type | Method |
|-------------|--------|
| **Web Access** | Cloudflare Tunnel (Zero Trust policies optional) |
| **SSH Access** | Tailscale + SSH key (`~/.ssh/forge_groupware`) |
| **Mail Access** | TLS via Cloudflare Tunnel |

### Network Flow

```
Internet → Cloudflare Edge → Cloudflare Tunnel → Nginx → SOGo → Backend
```

---

## DNS Configuration

| Record | Type | Target |
|--------|------|--------|
| `groupware.orderededge.co.uk` | CNAME | `*.cfargotunnel.com` |
| `mail.orderededge.co.uk` | CNAME | `*.cfargotunnel.com` |

**Notes:**
- DNS proxied through Cloudflare
- Cloudflare handles SSL/TLS termination at edge
- macOS + Tailscale users may need `/etc/hosts` workaround due to Tailscale DNS caching

---

## Storage Architecture

| Path | Purpose | Backup |
|------|---------|--------|
| `/data/appdata/mail` | Mail storage (Maildir format) | Recommended |
| `/data/appdata/groupware/postgres` | SOGo database | Recommended |
| `/data/appdata/groupware/redis` | Session cache | Non-critical |

---

## Deployment Files

**Location on VM:** `/opt/forge-groupware/`

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main service stack |
| `cloudflared-compose.yml` | Cloudflare Tunnel container |
| `.env` | Environment variables (secrets) |

---

## Cloudflare Tunnel Configuration

| Property | Value |
|----------|-------|
| **Tunnel ID** | `53d2b65c-60e0-4e1e-a20a-ce1a59deeb5a` |
| **Credentials** | `~/.cloudflared/53d2b65c-60e0-4e1e-a20a-ce1a59deeb5a.json` |
| **Config** | `~/.cloudflared/config.yml` |

---

## GCP Configuration

| Property | Value |
|----------|-------|
| **Project** | `orderededge-groupware` |
| **Service Account** | `forge-ccd-sa@orderededge-groupware.iam.gserviceaccount.com` |
| **Key Location** | `~/.config/gcp/forge-ccd-service-account.json` |

---

## Tailscale Integration

| Property | Value |
|----------|-------|
| **Device** | `forge-mail-server` |
| **Tailscale IP** | `100.117.50.105/32` |
| **Key Expiry** | 2026-05-04 (rotating) |

---

## Operational Commands

### SSH Access

```bash
# Connect via SSH (requires Tailscale and SSH key)
ssh -i ~/.ssh/forge_groupware stuharker@35.214.38.182

# Or via Tailscale IP
ssh -i ~/.ssh/forge_groupware stuharker@100.117.50.105
```

### Service Management (on VM)

```bash
cd /opt/forge-groupware

# Start all services
docker compose up -d
docker compose -f cloudflared-compose.yml up -d

# Stop all services
docker compose down
docker compose -f cloudflared-compose.yml down

# View logs
docker logs groupware-cloudflared --tail 50
docker logs groupware-nginx --tail 20
docker logs groupware-sogo --tail 20
docker logs groupware-mail --tail 20
```

### Health Checks

```bash
# Test tunnel endpoint locally
curl -I http://localhost:8081/SOGo/

# Test via Cloudflare
curl -I https://groupware.orderededge.co.uk/SOGo/

# Check container status
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

---

## Known Issues & Workarounds

### macOS + Tailscale DNS Caching

**Problem:** Tailscale DNS resolver (100.100.100.100) may cache old DNS records.

**Workaround:** Add entry to `/etc/hosts`:
```bash
sudo sh -c 'echo "172.67.220.18 groupware.orderededge.co.uk" >> /etc/hosts'
sudo dscacheutil -flushcache
```

**Remove later:**
```bash
sudo sed -i '' '/groupware.orderededge.co.uk/d' /etc/hosts
```

---

## Deployment Timeline

| Date | Milestone |
|------|-----------|
| 2026-04-04 | Status: ✅ Deployed and operational |
| 2026-04-04 | Usage Dashboard restarted and healthy |
| 2026-04-04 | DNS troubleshooting documented |

---

## Related Documentation

- `TOOLS.md` - Quick commands and tool registry
- `memory/2026-04-04-dns-troubleshooting.md` - DNS issue resolution
- `FORGE-GROUPWARE-DEPLOYMENT.md` - Detailed deployment guide (if exists)

---

## Contact & Ownership

- **Owner:** OrderedEdge
- **Maintainer:** OpenClaw (Claw)
- **Domain:** orderededge.co.uk
- **DNS Provider:** Cloudflare

---

*This document reflects the current state of the forge-mail-server deployment based on available configuration and operational data.*