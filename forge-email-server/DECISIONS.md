# Forge Mail Platform — Project Decision Record

**Date**: 2026-03-30  
**Project**: Forge Mail Platform – VPS-Hosted Email Service  
**Domains**: `orderededge.co.uk`, `rker.dev`

---

## Decisions Made

### 1. Hosting Model

| Option | Decision | Rationale |
|--------|----------|-----------|
| **VPS-hosted mail** | **Chosen** | Stable public IP, better deliverability, cloud-friendly outbound |
| **Titan-hosted mail** | Rejected | Dynamic IP, no PTR, port 25 restrictions on consumer ISP |

### 2. VPS Provider

| Provider | Status | Notes |
|----------|--------|-------|
| **GCP** | Chosen | Known infrastructure, easy PTR setup, SendGrid integration |
| AWS | Rejected | Not currently in use, more complex DNS |
| DigitalOcean | Rejected | Good option, but GCP preferred for consistency |

### 3. Outbound Mail Strategy

| Option | Decision | Rationale |
|--------|----------|-----------|
| **Direct send (port 25)** | Rejected | GCP restricts port 25, deliverability risk |
| **Relay on 587/465** | **Chosen** | GCP compliant, better deliverability, SendGrid recommended |

### 4. Domain Roles

| Domain | Mail Receiving | Mail Sending | Notes |
|--------|----------------|--------------|-------|
| `orderededge.co.uk` | ✅ Yes | ✅ Yes | Primary business domain |
| `rker.dev` | ✅ Yes | ✅ Yes | Secondary domain |

### 5. Mailbox Scope

| Scope | Decision |
|-------|----------|
| **Personal/admin only** | **Chosen** |
| **Business-wide** | Rejected (post-M1) |
| **Enterprise migration** | Out of scope |

### 6. Webmail Product

| Product | Status | Rationale |
|---------|--------|-----------|
| **Roundcube** | **Chosen** | Actively maintained, plugin ecosystem |
| RainLoop | Rejected | Archived, security risk |
| SquirrelMail | Rejected | Legacy, security concerns |
| SOGO | Rejected | Heavy, overkill for scope |

---

## Dependencies Confirmed

- [x] VPS with static public IP (GCP, to be provisioned)
- [x] DNS control for both domains (Cloudflare)
- [x] PTR/reverse DNS capability (GCP supports)
- [x] Relay provider (SendGrid recommended via GCP integration)
- [x] Backup destination (Titan `/data/backups/`)
- [x] Monitoring destination (Titan `/data/appdata/`)
- [x] Admin access to domain mailboxes (for validation testing)

---

## Out-of-Scope Confirmations

- [x] No public mail transport on Titan
- [x] No Cloudflare Tunnel for SMTP/IMAP
- [x] No enterprise mailbox migration
- [x] No marketing/bulk mail handling
- [x] No archival/legal hold/eDiscovery

---

## Risk Register

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| Port 25 blocked on GCP | High | Use relay on 587/465 | Mitigated |
| PTR misalignment | Medium | Match PTR to `mail.*` hostname | Mitigated |
| Roundcube archived | High | Use Roundcube, not RainLoop | Mitigated |
| Admin overexposed | Medium | Keep admin local/private | Mitigated |
| Backup failure late discovered | Medium | Monthly restore testing | Mitigated |
| Project drift (Titan vs VPS) | Medium | Titan support only, not public | Mitigated |

---

## Next Actions

- [ ] Provision GCP VPS with static IP
- [ ] Allocate static IP and configure PTR
- [ ] Choose and configure relay provider (SendGrid)
- [ ] Freeze hostname scheme (`mail.*`, `webmail.*`)
- [ ] Create final DNS change list
- [ ] Begin Phase 1: Architecture and Security Baseline (already complete)

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| **Project sponsor** | — | — | — |
| **Technical lead** | — | — | — |
| **Security reviewer** | — | — | — |

*Record created: 2026-03-30 05:28 GMT+1*

---

*Last updated: 2026-03-30*
