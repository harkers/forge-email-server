# Forge Email Server — Phased Implementation Brief

**Status:** architecture validated, implementation not yet deployed  
**Runtime:** GCP via Forge Cloud Control Desk  
**Mail model:** outbound relay only

---

## Overview

Build a minimal outbound mail relay on a GCP Debian 12 VM using Postfix and SendGrid.
This product does **not** host inbound mailboxes.
It exists to provide a controlled, observable delivery path for application and operational mail.

Primary flow:

```text
application or internal system → Postfix relay on GCP VM → SendGrid on 587 → recipient MX
```

---

## Phase 0 — Discovery and design lock ✅

### Outcome
- GCP confirmed as runtime environment
- GCCD confirmed as control plane
- SendGrid chosen as upstream relay
- outbound-only design chosen over full mailbox stack
- primary relay port fixed to 587
- fallbacks fixed to 465 and 2525
- public inbound SMTP removed from baseline scope

### Remaining open point
- decide whether Titan-hosted applications use the relay through a private path or send directly to SendGrid

---

## Phase 1 — Control-plane alignment ✅

### Goal
Represent the relay service inside Forge Cloud Control Desk with the right records, evidence model, and runbook boundaries.

### Deliverables
- email extension documentation in GCCD
- relay VM specification
- mail domain register design
- webhook/evidence expectations

### Exit criteria
- GCCD docs updated to describe relay operations rather than mailbox hosting
- relay actions and evidence model agreed

---

## Phase 2 — Relay VM provisioning

### Goal
Provision the relay VM through GCCD.

### Target VM
- name: `forge-mail-server`
- region: `europe-west2`
- zone: `europe-west2-b`
- OS: Debian 12
- size: `e2-small` recommended for low-volume operational mail

### Tasks
- create VM via Compute Engine API / GCCD
- reserve static IP if required for surrounding ops controls
- apply firewall posture for outbound SMTP relay and operator access only
- write provisioning evidence
- update GCCD register

### Exit criteria
- VM exists and is reachable for admin operations
- GCCD evidence and register updated

---

## Phase 3 — Postfix relay baseline

### Goal
Install a hardened relay-only Postfix profile.

### Tasks
- install `postfix`, `ca-certificates`, `mailutils` / `swaks`
- configure `relayhost = [smtp.sendgrid.net]:587`
- enable SASL auth using `apikey` username format
- require TLS to upstream relay
- disable local delivery
- keep baseline listener posture minimal
- create documented fallback profiles for 465 and 2525

### Exit criteria
- Postfix validates locally
- config matches security baseline
- test submission to SendGrid succeeds

---

## Phase 4 — SendGrid authentication and DNS

### Goal
Authenticate the sending domain and complete trust setup.

### Tasks
- create scoped SendGrid API key
- authenticate sending subdomain
- publish SendGrid-provided DKIM CNAMEs
- publish SPF aligned with SendGrid
- publish DMARC at `p=none`
- enable Signed Event Webhook

### Exit criteria
- authenticated domain verified in SendGrid
- DKIM and SPF alignment validated
- event webhook signed mode enabled

---

## Phase 5 — Telemetry and evidence

### Goal
Make delivery outcomes observable and auditable.

### Tasks
- expose HTTPS webhook receiver if required
- validate SendGrid signatures before ingest
- store delivery events in GCCD evidence path or linked store
- capture at least processed/delivered/deferred/dropped/bounce/spamreport/unsubscribe
- create operator alerting for relay auth failures and abnormal event trends

### Exit criteria
- events received and verified
- evidence path documented
- failure signals surfaced without silent loss

---

## Phase 6 — Application onboarding

### Goal
Connect real workloads to the relay in a controlled way.

### Onboarding patterns
1. **baseline:** workload on relay VM submits locally
2. **controlled extension:** Titan-hosted app uses private/VPN-restricted submission
3. **fallback:** workload uses SendGrid directly

### Tasks
- choose submission model per application
- document source restrictions and auth model
- run test sends to Gmail / Outlook / Yahoo
- verify headers, TLS, deliverability, and suppression handling
- update GCCD evidence and register after validation

### Exit criteria
- at least one real application sends successfully
- headers show expected authentication results
- runbook updated for recurring operations

---

## Go / no-go rules

Do not mark the product complete unless:
- [ ] relay VM is provisioned via GCCD
- [ ] Postfix is configured as relay-only
- [ ] SendGrid domain authentication is verified
- [ ] Signed Event Webhook is enabled if webhook telemetry is in use
- [ ] app submission path is explicitly documented
- [ ] end-to-end mail tests pass
- [ ] evidence exists for provision, config, and test stages

---

## Explicit non-goals for this project

- inbound MX cutover
- Dovecot / mailbox storage
- full groupware deployment
- Roundcube baseline deployment
- public-facing SMTP receive design
