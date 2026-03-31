# Forge Email Server — Phase 0 Outcome

**Date:** 2026-03-31  
**Result:** validated direction chosen, not yet deployed

---

## Outcome summary

Phase 0 finished with a clear product correction:

**Chosen design:** a GCP-hosted outbound relay managed through Forge Cloud Control Desk and backed by SendGrid.

**Rejected design:** a full self-hosted inbound mailbox stack.

---

## Confirmed foundations

### GCP control-plane baseline
- GCCD project exists: `project-20260330044222184857`
- GCP baseline config already documented under GCCD
- current documented region: `europe-west2`
- current documented zone: `europe-west2-b`
- evidence already exists for a successful VM start action on `forge-test-vm`

### Email delivery baseline
- SendGrid chosen as upstream relay
- primary path uses port 587 with STARTTLS
- controlled fallbacks are 465 and 2525
- normal design does not depend on outbound port 25 from GCP

---

## Key decisions locked in Phase 0

1. **Runtime**: GCP, not Titan
2. **Control plane**: Forge Cloud Control Desk
3. **Mail role**: outbound relay only
4. **MTA**: Postfix only
5. **Upstream**: SendGrid using `apikey` username + API key password
6. **Internet posture**: no public inbound MX / SMTP receive in baseline
7. **Identity posture**: authenticated sending subdomain preferred over bare root domain
8. **Cloudflare role**: HTTP admin/CRM surfaces only, not SMTP path
9. **Telemetry**: SendGrid Event Webhook with signature validation

---

## Explicitly removed from baseline scope

- Dovecot / mailbox storage
- Roundcube baseline deployment
- docker-mailserver as core runtime
- public MX cutover
- inbound IMAP/POP delivery model
- Cloudflare Tunnel in the SMTP delivery path

---

## Open integration decision

The remaining design choice is how Titan-hosted apps submit mail:

### Option A — local-to-relay baseline
Workload runs on the relay VM and submits locally.

### Option B — controlled private submission
Titan-hosted workload submits over private/VPN-restricted path to relay VM.

### Option C — direct SendGrid fallback
Titan-hosted workload sends directly to SendGrid.

No option should be treated as implemented until documented and tested.

---

## Ready-for-next-phase actions

- [ ] provision `forge-mail-server` in `europe-west2-b`
- [ ] install Postfix relay profile on Debian 12
- [ ] create scoped SendGrid API key
- [ ] authenticate sending subdomain in SendGrid
- [ ] enable Signed Event Webhook
- [ ] decide Titan app submission model
- [ ] update GCCD register/evidence model for relay operations

---

## Exit state

Phase 0 is complete because the project now has:
- a stable runtime decision
- a stable upstream relay decision
- a corrected product boundary
- a reduced attack surface
- a clear next implementation sequence
