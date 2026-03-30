# Phase 0: Viability and Design Lock — Outcome

**Date**: 2026-03-30  
**Project**: Forge Mail, Calendar & Contacts Platform

---

## Host Location Decision

### VPS Provider: **GCP**
- **Region**: `us-central1` (default, near existing infrastructure)
- **Instance type**: `e2-medium` (2 vCPU, 4GB RAM) — start small, scale if needed
- **Static IP**: To be allocated (`us-central1` region)
- **Rationale**: Known infrastructure, GCP SendGrid integration, easy PTR setup

### titan Role: **Support Infrastructure Only**
- Backups (`/data/backups/forge-mail-platform/`)
- Monitoring intake (`/data/appdata/forge-mail-platform/logs/`)
- Admin workstation (local config generation)
- **NOT** public mail endpoint
- No public DNS records pointing to `192.168.10.80`

---

## Outbound Mail Strategy

### Chosen: **Relay on Port 587**
- **Provider**: SendGrid (via GCP integration)
- **Port**: 587 (submission with TLS)
- **Rationale**: GCP restricts port 25; relay is standard for cloud-hosted mail
- **Alternatives considered**:
  - Direct send (port 25) — Rejected (GCP blocks)
  - Other relays (Mailgun, SparkPost) — Rejected (SendGrid preferred for GCP integration)

---

## Domain Roles

| Domain | Mail Receiving | Mail Sending | Notes |
|--------|----------------|--------------|-------|
| `orderededge.co.uk` | ✅ Yes | ✅ Yes | Primary business domain |
| `rker.dev` | ✅ Yes | ✅ Yes | Secondary domain |

---

## Mailbox Scope

### Chosen: **Personal/Admin Only**
- Internal users, admins, contact form recipients
- **Not**: Business-wide user mailboxes (post-M1)
- **Not**: Marketing/bulk mail sending (out of scope)

---

## Hostname Scheme (Finalized)

| Purpose | Hostname | Access Pattern |
|---------|----------|----------------|
| **SMTP/IMAP (mail core)** | `mail.orderededge.co.uk` | Public Internet |
| **SMTP/IMAP (mail core)** | `mail.rker.dev` | Public Internet |
| **Groupware UI (SOGo)** | `groupware.orderededge.co.uk` | Public or Tunnel-protected |
| **Groupware UI (SOGo)** | `groupware.rker.dev` | Public or Tunnel-protected |

**Notes**:
- `groupware.*` chosen over `webmail.*` — SOGo is full groupware, not just webmail
- Mail transport (`mail.*`) is **public Internet only** (not behind Cloudflare Tunnel)
- Webmail/groupware (`groupware.*`) can use Cloudflare Tunnel if admin protection desired

---

## DNS Configuration (Planned)

| Record Type | Name | Value | Purpose |
|-------------|------|-------|---------|
| **A** | `mail.orderededge.co.uk` | VPS static IP | Mail delivery endpoint |
| **A** | `mail.rker.dev` | VPS static IP | Mail delivery endpoint |
| **A** | `groupware.orderededge.co.uk` | VPS static IP | SOGo UI endpoint |
| **A** | `groupware.rker.dev` | VPS static IP | SOGo UI endpoint |
| **MX** | `orderededge.co.uk` | `10 mail.orderededge.co.uk` | Mail exchange |
| **MX** | `rker.dev` | `10 mail.rker.dev` | Mail exchange |
| **TXT** | `orderededge.co.uk` | `v=spf1 include:_spf.gcp.google.com ~all` | SPF record |
| **TXT** | `rker.dev` | `v=spf1 include:_spf.gcp.google.com ~all` | SPF record |
| **TXT** | `mail._domainkey.orderededge.co.uk` | DKIM public key | DKIM verification |
| **TXT** | `mail._domainkey.rker.dev` | DKIM public key | DKIM verification |
| **TXT** | `_dmarc.orderededge.co.uk` | `v=DMARC1; p=none; rua=mailto:dmarc@orderededge.co.uk;` | DMARC monitoring |
| **TXT** | `_dmarc.rker.dev` | `v=DMARC1; p=none; rua=mailto:dmarc@rker.dev;` | DMARC monitoring |
| **PTR** | VPS public IP | `mail.orderededge.co.uk` | Reverse DNS alignment |

**Note**: PTR must match `mail.*` hostname, not `groupware.*`.

---

## dependencies Confirmed

- [x] VPS with static public IP (GCP, to be provisioned)
- [x] DNS control for both domains (Cloudflare)
- [x] PTR/reverse DNS capability (GCP supports)
- [x] Relay provider (SendGrid via GCP integration)
- [x] Backup destination (Titan `/data/backups/`)
- [x] Monitoring destination (Titan `/data/appdata/`)
- [x] Admin access to domain mailboxes (for validation testing)

---

## Out-of-Scope Confirmations

- [x] No public mail transport on Titan
- [x] No Cloudflare Tunnel for SMTP/IMAP
- [x] No bulk or marketing mail
- [x] No enterprise mailbox migration
- [x] No archival/legal hold/eDiscovery

---

## Risks Identified

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| Port 25 blocked on GCP | High | Use relay on 587/465 | ✅ Mitigated |
| PTR misalignment | Medium | Match PTR to `mail.*` hostname | ✅ Mitigated |
| SOGo database choice | Low | PostgreSQL recommended | ✅ Ready |
| Image version drift | Medium | Pin image versions during implementation | ✅ Planned |

---

## Next Actions (Ready for Approval)

1. **Provision GCP VPS**
   - Region: `us-central1`
   - Instance: `e2-medium` (2 vCPU, 4GB RAM)
   - OS: Debian 12
   - Static IP: Reserve before instance creation

2. **Allocate Static IP**
   - Region: `us-central1`
   - Name: `forge-mail-platform-static-ip`
   - Assign after VPS creation

3. **Configure PTR/reverse DNS**
   - Set to `mail.orderededge.co.uk`
   - GCP requires domain ownership verification

4. **Set up SendGrid relay**
   - Create SendGrid account via GCP Marketplace
   - Configure SMTP relay on port 587
   - Obtain relay hostname and credentials

5. **Freeze hostname scheme**
   - Confirmed: `mail.*`, `groupware.*`
   - No `webmail.*` (SOGo is groupware, not just webmail)

6. **Begin Phase 1: Architecture and Security Baseline**
   - Document SOGo + docker-mailserver service map
   - Decide SOGo database backend (PostgreSQL)
   - Define storage, secrets, logs, backups
   - Define admin access boundaries

---

## Exit Criteria — Phase 0

- [x] VPS provider chosen (GCP)
- [x] Region chosen (`us-central1`)
- [x] Instance type chosen (`e2-medium`)
- [x] Static IP allocation planned
- [x] Outbound strategy chosen (SendGrid relay on 587)
- [x] Domain roles confirmed (both receive and send)
- [x] Mailbox scope defined (personal/admin only)
- [x] Hostname scheme finalized (`mail.*`, `groupware.*`)
- [x] Dependencies listed (VPS, DNS, PTR, relay, backups, monitoring)

**Status**: Phase 0 **Complete** — Ready to proceed to Phase 1.

---

*Last updated: 2026-03-30 05:34 GMT+1*
