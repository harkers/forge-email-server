# Forge Email Server — Design Brief

**Status:** Design brief  
**Date:** 2026-03-31  
**Workspace:** `/home/stu/.openclaw/workspace/forge-email-server/`  
**Parent control plane:** Forge Cloud Control Desk (`project-20260330044222184857`)

---

## 1. Product summary

Forge Email Server is a **managed outbound email relay product** for operational and application mail.

It is intentionally narrow.
It is **not** a full mailbox platform, not a public inbound email system, and not a groupware suite.

### Core delivery path

```text
application or internal system → Postfix relay on GCP VM → SendGrid on 587 → recipient MX
```

### Controlled fallbacks
- SendGrid on `465` with implicit TLS
- SendGrid on `2525` with STARTTLS
- no normal dependency on outbound port `25` from GCP

---

## 2. Problem statement

The current environment needs a governed, observable, low-friction way to send email from systems and applications without:
- exposing Titan as a public mail host
- building a large self-hosted mail stack that exceeds the real requirement
- depending on ad hoc direct SMTP settings scattered across products
- losing evidence, delivery visibility, or configuration discipline

The product exists to solve **reliable outbound delivery** while keeping scope tight and operations auditable.

---

## 3. Why this product exists

### Primary need
Provide a stable outbound delivery path for:
- application notifications
- operational alerts
- workflow messages
- low-volume business/system mail

### Secondary need
Represent that relay service as a governed workload inside **Forge Cloud Control Desk**, so provisioning, evidence, and status handling follow the same model as other GCP workloads.

---

## 4. Goals

### Product goals
- deliver outbound mail reliably from GCP
- minimise attack surface
- preserve a clear audit/evidence trail
- keep DNS/authentication standards correct
- support staged onboarding of workloads
- remain simple enough to operate without drama

### Operational goals
- provisioned and tracked via GCCD
- evidence written for provisioning, config, and validation
- clear boundaries between implemented state and design intent
- clean rollback options if delivery or authentication breaks

---

## 5. Non-goals

This product does **not** aim to provide:
- inbound MX hosting
- mailbox hosting
- IMAP / POP service
- general-purpose webmail as baseline
- enterprise collaboration/groupware
- bulk/marketing email operations
- a public-facing SMTP receive service
- a Cloudflare-mediated SMTP path

---

## 6. Users and operators

### Primary operator
- Stuart / Forge operator

### Primary systems using the product
- GCCD-managed workloads
- internal applications
- selected Titan-hosted systems if a submission path is explicitly approved

### External dependency operators
- GCP for VM/runtime/network
- SendGrid for relay and delivery telemetry
- Cloudflare for selected HTTP protection surfaces only

---

## 7. Scope boundary

### In scope
- GCP Debian 12 relay VM
- Postfix relay-only configuration
- SendGrid SMTP relay authentication
- authenticated sending domain/subdomain
- SPF / DKIM / DMARC alignment
- delivery telemetry via SendGrid Event Webhook
- GCCD evidence and register integration

### Conditionally in scope
- Titan-hosted app submission to relay VM, if:
  - source trust model is documented
  - firewall/auth model is documented
  - validation is completed

### Out of scope by default
- remote open submission from arbitrary networks
- inbound mail reception
- mailbox storage and user administration

---

## 8. Design principles

1. **Do the smallest thing that works.**  
   Build the relay product actually needed, not an accidental mail platform.

2. **Keep the runtime narrow.**  
   Debian 12 + Postfix is preferred over a larger stack when the requirement is outbound relay only.

3. **Separate control plane from transport plane.**  
   GCCD governs the workload; SendGrid carries the mail.

4. **Treat SMTP and browser access as different problems.**  
   Cloudflare Access is for human-facing HTTP, not the SMTP relay path.

5. **Prefer explicit fallbacks over clever automation.**  
   Fallback port profiles should be deliberate and operator-readable.

6. **Don’t fake completion.**  
   Unresolved submission-path decisions stay documented as open, not implied done.

---

## 9. Functional requirements

### FR-1 Relay mail through SendGrid
The system must send outbound mail through SendGrid using authenticated SMTP.

### FR-2 Use secure primary path
The default upstream path must be SendGrid on port `587` with mandatory STARTTLS.

### FR-3 Maintain fallback profiles
The product must document usable fallback profiles for `465` and `2525`.

### FR-4 Prevent local delivery
The relay host must not behave like a local mailbox server by default.

### FR-5 Support evidence creation
Provisioning, configuration, and validation steps must produce evidence through GCCD or linked records.

### FR-6 Support domain authentication
The product must support SPF/DKIM/DMARC-aligned sending via SendGrid-authenticated domains.

### FR-7 Support delivery telemetry
The product must support SendGrid Event Webhook for operational visibility.

---

## 10. Non-functional requirements

### Security
- minimum credential scope
- TLS required to upstream relay
- no unnecessary public surfaces
- no PII/PHI in SendGrid metadata fields

### Reliability
- clear fallback paths
- queue behaviour visible to operator
- explicit alerting on auth/TLS/delivery issues

### Operability
- configs should be understandable by inspection
- no hidden dynamic failover logic that surprises operators
- validation steps should be scriptable and manual-friendly

### Governance
- no create action without register/evidence path
- no important change without documented evidence
- no success state without real validation

---

## 11. External constraints

### GCP constraint
Outbound port 25 to external IPs is restricted by default, so the design should not rely on it.

### SendGrid constraint
SMTP auth uses:
- username: `apikey`
- password: SendGrid API key

### Privacy constraint
SendGrid categories, unique args, and custom args must not be used to carry sensitive personal data.

### Cloudflare constraint
Cloudflare Access is appropriate for browser-based HTTP apps, not the SMTP relay path or interactive protection of webhook callbacks.

---

## 12. Target runtime

### Host
- GCP VM
- Debian 12
- provisioned via GCCD

### Recommended starter size
- `e2-small`

### Core packages
- postfix
- ca-certificates
- mailutils and/or swaks for validation

### Upstream relay
- `smtp.sendgrid.net:587`

---

## 13. Trust and integration model

### Baseline trust model
Workloads on the relay VM submit locally to Postfix.

### Open integration model
Titan-hosted systems may later use the relay if a private/restricted submission path is explicitly designed and validated.

### Fallback integration model
A workload may send directly to SendGrid if the relay host does not add sufficient value.

---

## 14. Observability model

### Evidence sources
- GCCD provisioning evidence
- local Postfix logs
- SendGrid dashboard
- SendGrid Event Webhook

### Minimum events to track
- processed
- delivered
- deferred
- dropped
- bounce
- spamreport
- unsubscribe

---

## 15. Delivery phases

### Phase 0 — design lock
Confirm product boundary and upstream strategy.

### Phase 1 — GCCD alignment
Represent the product cleanly inside GCCD.

### Phase 2 — relay VM provisioning
Provision `forge-mail-server` in GCP.

### Phase 3 — Postfix baseline
Install and validate relay-only Postfix configuration.

### Phase 4 — SendGrid auth + DNS
Authenticate sending subdomain and validate trust records.

### Phase 5 — telemetry
Enable and validate Event Webhook and evidence handling.

### Phase 6 — workload onboarding
Connect one real workload and verify end-to-end delivery.

---

## 16. Acceptance criteria

The product is ready for first use when:
- [ ] relay VM is provisioned via GCCD
- [ ] Postfix relay-only profile is applied
- [ ] SendGrid authenticated domain is verified
- [ ] test sends succeed on port 587
- [ ] fallback profiles for 465 and 2525 are documented
- [ ] Event Webhook security/validation approach is documented
- [ ] at least one workload is onboarded with evidence
- [ ] open submission-path decisions are explicitly resolved

---

## 17. Summary

Forge Email Server should stay boring in the best possible way:
- small
- explicit
- secure enough
- observable
- governed through GCCD
- and very clearly **not** a sprawling self-hosted mail empire
