# Forge Mail Platform — Target Architecture

**Project**: Forge Mail Platform – VPS-Hosted Email Service  
**Domains**: `orderededge.co.uk`, `rker.dev`  
**Last updated**: 2026-03-30

---

## High-Level Architecture

```
+-------------------------------------------------------------------+
|                         Internet Public Mail Plane                |
|                                                                   |
|   orderededge.co.uk / rker.dev  →  mail.* hostnames             |
|                                   →  VPS (GCP) public IP        |
|                                   →  docker-mailserver (Postfix, |
|                                      Dovecot, Rspamd, DKIM)     |
|                                                                   |
|   Webmail Access (optional tunnel)                              |
|   webmail.* hostnames  →  Reverse Proxy  →  Roundcube           |
|                                                                   |
+-------------------------------------------------------------------+

+-------------------------------------------------------------------+
|                         Titan Support Infrastructure              |
|                                                                   |
|   Backup destination: /data/backups/forge-mail-platform/        |
|   Monitoring intake:  /data/appdata/forge-mail-platform/logs/   |
|   Admin workstation:  Local development & config generation     |
|   NOT public mail endpoint                                      |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## Components

| Component | Role | Host | Notes |
|-----------|------|------|-------|
| **VPS** | Public mail host | GCP | Static IP, docker-mailserver, Roundcube |
| **docker-mailserver** | Mail stack | VPS | Postfix, Dovecot, Rspamd, DKIM |
| **Roundcube** | Webmail UI | VPS | Browser-based mailbox access |
| **Cloudflare** | DNS management | Cloudflare dashboard | A, MX, SPF, DKIM, DMARC, PTR |
| **Titan** | Support infrastructure | titan.harker.systems | Backups, monitoring, admin |
| **Cloudflare Tunnel** | Optional webmail protection | VPS → Tunnel | Only for webmail, NOT mail delivery |

---

## Hostname Scheme

| Purpose | Hostname | DNS Record | Target |
|---------|----------|------------|--------|
| **Mail SMTP/IMAP** | `mail.orderededge.co.uk` | A | VPS static IP |
| **Mail SMTP/IMAP** | `mail.rker.dev` | A | VPS static IP |
| **Webmail** | `webmail.orderededge.co.uk` | A | VPS static IP (or Tunnel) |
| **Webmail** | `webmail.rker.dev` | A | VPS static IP (or Tunnel) |

**Notes**:
- Public mail transport uses direct A records (no tunnel)
- Webmail may use Cloudflare Tunnel only if admin protection is needed
- Titan does NOT appear in any public DNS records

---

## Data Storage

| Path | Purpose | Location | Persistence |
|------|---------|----------|-------------|
| `/var/mail/virtual/` | Mailbox storage | VPS container | Docker volume |
| `/var/log/` | Mail logs | VPS container | Rotated |
| `/etc/opendkim/keys/` | DKIM private keys | VPS container | Encrypted backup |
| `/etc/postfix/` | Postfix config | VPS container | Config management |
| `/etc/dovecot/` | Dovecot config | VPS container | Config management |
| `/data/backups/forge-mail-platform/` | Daily backups | Titan | Off-site |
| `/data/appdata/forge-mail-platform/logs/` | Monitoring intake | Titan | Local |

---

## Outbound Mail Model

**Recommended**: Smarthost/Relay on port 587 (GCP friendly)

| Option | Pros | Cons | Status |
|--------|------|------|--------|
| Direct send (port 25) | No relay cost, full control | GCP restricts port 25 | Not recommended |
| Relay on 587/465 | GCP compliant, better deliverability | Relay cost, dependency | **Recommended** |

**Relay candidates**:
- GCP SendGrid (integrated)
- SendGrid standalone
- Mailgun
- SparkPost

---

## Security Baseline

| Layer | Control | Target State |
|-------|---------|--------------|
| **Container** | `cap_drop: ALL`, `read_only: true` | Minimal privileges |
| **Postfix** | TLS 1.2+, strong ciphers, STARTTLS required | `smtpd_tls_protocols = !SSLv2 !SSLv3 !TLSv1 !TLSv1.1` |
| **Dovecot** | SSL/TLS required, no plaintext auth | `ssl = required`, `disable_plaintext_auth = yes` |
| **Rspamd** | Local-only admin, rate limiting | Admin not exposed externally |
| **Authentication** | SASL via Dovecot, strong passwords | Minimum 16 chars, complexity |
| **Monitoring** | Queue, disk, auth-failure alerts | Prometheus/Grafana or simple cron |

---

## Product Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Mail server** | `dockermailserver/docker-mailserver` | Actively maintained, production-ready |
| **Webmail** | Roundcube | Actively maintained, plugin ecosystem |
| **Spam filter** | Rspamd | Built into docker-mailserver, efficient |
| **DNS** | Cloudflare | Control, analytics, optional tunnel |
| **Certificate** | Let's Encrypt / Cloudflare Origin CA | Free, automated |

---

## Operations Model

| Task | Responsibility | Tool/Method |
|------|----------------|-------------|
| **Mailbox creation** | Admin | `docker-mailserver` CLI / config |
| **User password change** | User / Admin | Dovecot SASL / admin portal |
| **Backup** | Titan | Daily tarball + off-site copy |
| **Monitoring** | Titan | Cron + alerting webhook |
| **Log review** | Admin | `docker-compose logs` / log shipper |
| **Incident response** | Admin | Runbook-driven |

---

## Deployment Phases

| Phase | Goal | Key Output |
|-------|------|------------|
| Phase 0 | VPS + static IP chosen | Hosting model approved |
| Phase 1 | Architecture frozen | One-page architecture document |
| Phase 2 | Mail stack operational internally | SMTP/IMAP working |
| Phase 3 | DNS/SPF/DKIM/DMARC/PTR live | Trust configuration complete |
| Phase 4 | Roundcube accessible | Webmail live |
| Phase 5 | Hardening complete | Monitoring active, restore tested |
| Phase 6 | DMARC enforcement | Production ready |

---

## Dependencies Checklist

- [ ] VPS provisioned on GCP (small, static IP)
- [ ] DNS control for both domains
- [ ] PTR/reverse DNS capability
- [ ] Relay provider chosen (587/465)
- [ ] Backup destination on Titan
- [ ] Monitoring destination and alert method
- [ ] Access to domain mailboxes for validation

---

## Exit Criteria

- [ ] VPS running docker-mailserver with persistent storage
- [ ] Both domains configured and accepting mail
- [ ] Roundcube webmail accessible over HTTPS
- [ ] DKIM signing working on outbound
- [ ] SPF/DKIM/DMARC/PTR all valid and aligned
- [ ] Backup completes successfully
- [ ] Restore test passed
- [ ] Monitoring alerts configured

---

*Last updated: 2026-03-30*
