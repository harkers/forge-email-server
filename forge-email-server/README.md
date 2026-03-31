# Forge Email Server

## Status
Planning / design locked for the outbound relay model.

This workspace no longer describes a full self-hosted mailbox stack.
It now defines a **GCP-hosted outbound relay service** managed through **Forge Cloud Control Desk** and backed by **SendGrid**.

## Product definition

**Primary path**

```text
application or internal system → Postfix relay on GCP VM → SendGrid on 587 (mandatory STARTTLS)
```

**Controlled fallbacks**
- 465 with implicit TLS
- 2525 with STARTTLS
- never 25 as the normal GCP design

## Scope

### In scope
- outbound transactional / operational mail relay
- GCP VM provisioned through Forge Cloud Control Desk
- Postfix-only relay role on Debian 12
- SendGrid SMTP relay with scoped API key
- SendGrid authenticated domain / DKIM / SPF / DMARC alignment
- delivery telemetry via SendGrid Event Webhook
- Cloudflare Access for human-facing HTTP surfaces related to the product

### Out of scope
- inbound MX hosting
- public internet-facing SMTP reception
- mailbox hosting / IMAP / POP
- Roundcube or other webmail as part of this baseline
- enterprise mailbox migration
- bulk / marketing mail

## Current architectural position

This product is an **extension of Forge Cloud Control Desk**.

- Base GCCD project: `project-20260330044222184857`
- Email extension project: `project-20260331202030761850`
- GCP baseline: `europe-west2` / `europe-west2-b`
- Existing evidence of GCP operations: `forge-test-vm` start success recorded in GCCD evidence

## Document map

- `DESIGN-BRIEF.md` — product intent, scope, requirements, and acceptance criteria
- `ARCHITECTURE.md` — target architecture and trust boundaries
- `ARCHITECTURE-DECISIONS.md` — ADR-style architecture decisions and rationale
- `DECISIONS.md` — decision record and rejected options
- `PHASED-BRIEF.md` — phased implementation plan
- `SECURITY-BASELINE.md` — hardened baseline for relay VM and SendGrid integration
- `PHASE-0-OUTCOME.md` — validated outcome of the discovery/design gate
- `SENDGRID_SETUP_GUIDE.md` — Debian 12 + Postfix + SendGrid implementation guide
- `CLOUDFLARE_ZERO_TRUST_CONFIG.md` — Cloudflare role for HTTP admin/CRM surfaces only

## Open implementation dependency

If Titan-hosted apps such as Nextcloud need to submit mail through this relay, that requires an explicit delivery path decision:

1. **preferred baseline:** app colocated on relay VM and submits locally, or
2. **controlled extension:** private/VPN-restricted submission from Titan to relay VM, or
3. **fallback:** app sends directly to SendGrid without using the relay VM

That decision is not treated as implemented until documented in config and validated.
