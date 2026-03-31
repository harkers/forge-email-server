# Forge Email Server — Target Architecture

**Project:** Forge Email Server / outbound relay extension to Forge Cloud Control Desk  
**Last updated:** 2026-03-31

---

## 1. Architecture summary

The validated design is a **GCP-hosted outbound relay**.
It is not a full inbound mail platform.

### Primary delivery path

```text
application or internal system
  → Postfix relay on GCP VM
  → smtp.sendgrid.net:587
  → recipient MX
```

### Controlled fallbacks
- `smtp.sendgrid.net:465` with implicit TLS
- `smtp.sendgrid.net:2525` with STARTTLS
- no normal design dependency on outbound port 25 from GCP

---

## 2. Current product boundary

### In scope
- outbound operational / transactional mail
- Debian 12 relay VM in GCP
- Postfix as relay only
- SendGrid authenticated sending
- event telemetry from SendGrid
- Forge Cloud Control Desk provisioning, evidence, and register updates
- Cloudflare Access for human-facing HTTP applications related to the workflow

### Out of scope
- inbound MX
- mailbox hosting
- IMAP / POP / webmail baseline
- public SMTP receive on the Internet
- local mail delivery on the relay VM

---

## 3. System context

```text
+--------------------------------------------------------------+
|                   Forge Cloud Control Desk                   |
|  Compute Engine API | Sheets register | Evidence | Alerts    |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
|                     GCP relay VM (target)                    |
|  Debian 12                                                   |
|  Postfix only                                                |
|  relay role only                                             |
|  no local mailbox delivery                                   |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
|                          SendGrid                            |
|  SMTP relay on 587                                           |
|  fallbacks on 465 / 2525                                     |
|  authenticated domain + DKIM                                 |
|  Event Webhook telemetry                                     |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
|                     External recipient MX                    |
+--------------------------------------------------------------+
```

---

## 4. Trust boundaries

### Boundary A — operator control
Forge Cloud Control Desk governs:
- VM provisioning
- evidence creation
- register updates
- operator-facing status and alerts

### Boundary B — relay VM
The relay VM should:
- accept submission only from explicitly trusted paths
- avoid local delivery
- avoid public inbound SMTP receive as part of baseline
- require TLS to SendGrid

### Boundary C — SendGrid
SendGrid is responsible for:
- outbound transfer to recipient domains
- domain authentication support
- event telemetry
- reputation and suppression handling on its platform

### Boundary D — HTTP admin surfaces
Cloudflare Access is relevant only for **human-facing HTTP apps** such as CRM/admin dashboards.
It is **not** part of the SMTP relay path.

---

## 5. Components

| Component | Role | Status | Notes |
|-----------|------|--------|-------|
| Forge Cloud Control Desk | control plane | existing | GCP operations already evidenced via `forge-test-vm` |
| GCP project `301823798218` | hosting environment | existing | baseline region/zone documented in GCCD config |
| Relay VM `forge-mail-server` | outbound relay host | planned | target Debian 12 VM |
| Postfix | outbound relay MTA | planned | relay-only, no local delivery |
| SendGrid | upstream relay | planned | primary 587, fallbacks 465/2525 |
| Cloudflare Access | protect human HTTP surfaces | planned | not used for SMTP or webhook auth challenges |
| Nextcloud / other apps | mail submitters | dependent | submission path decision still must be finalised |

---

## 6. Submission models

### Baseline model
Applications running on the relay VM submit locally to Postfix.

```text
app → 127.0.0.1:25 or local submission path → Postfix → SendGrid
```

### Controlled extension model
If Titan-hosted apps must use the relay, use a **private or VPN-restricted submission path**.
That is a design extension, not yet treated as implemented.

Requirements for that extension:
- no open public submission listener by default
- source restriction to approved private addresses only
- explicit auth and logging design
- updated firewall and runbook documentation

### Direct-to-SendGrid fallback
For some apps, direct SendGrid SMTP/API integration may be simpler than remote relay submission.
That remains an allowed fallback if the relay path is not justified.

---

## 7. DNS and identity model

### Sending identity
Use an authenticated **sending subdomain**, not the bare root domain, as the operational baseline.

Examples:
- `noreply@mail.orderededge.co.uk`
- `alerts@mail.orderededge.co.uk`
- `noreply@mail.rker.dev`

### DNS responsibilities
- SPF alignment with SendGrid
- DKIM via SendGrid-provided CNAMEs
- DMARC starting at `p=none`
- no public MX required for the baseline relay-only design

---

## 8. Observability model

Primary observability comes from:
- GCCD evidence records
- local Postfix logs on the relay VM
- SendGrid Event Webhook events
- SendGrid dashboard / suppression insight

Minimum event set:
- processed
- delivered
- deferred
- dropped
- bounce
- spamreport
- unsubscribe

---

## 9. Network posture

### Relay path
- outbound from GCP VM to SendGrid on 587
- fallback ports 465 / 2525 available but not primary

### Non-goals
- no dependence on outbound port 25
- no public inbound SMTP receive
- no IMAP exposure as part of this product baseline

### Cloudflare role
- protects HTTP apps only
- does not front SMTP
- does not front SendGrid Event Webhook with interactive Access login

---

## 10. Exit criteria for architecture lock

- [x] outbound relay chosen over full mailbox stack
- [x] GCP chosen as the runtime environment
- [x] SendGrid chosen as upstream relay
- [x] primary port fixed to 587 with TLS required
- [x] fallback ports fixed to 465 and 2525
- [x] public inbound SMTP removed from baseline scope
- [x] Cloudflare Access limited to HTTP surfaces
- [ ] app-to-relay submission path finalised for Titan-hosted systems
