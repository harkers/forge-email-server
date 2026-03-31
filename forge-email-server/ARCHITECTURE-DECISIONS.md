# Forge Email Server — Architecture Decisions

**Status:** active decision record  
**Date:** 2026-03-31  
**Applies to:** `/home/stu/.openclaw/workspace/forge-email-server/`

---

## ADR-001 — Runtime lives in GCP, not Titan

**Decision**  
Run the relay workload in GCP and manage it through Forge Cloud Control Desk.

**Why**
- aligns with existing GCCD/GCP work already underway
- avoids turning Titan into a public mail host
- fits the control-plane/evidence model already established
- avoids residential / local-host assumptions from earlier concepts

**Implication**
The relay is treated as a governed GCP workload, not a Titan-native mail service.

---

## ADR-002 — Product scope is outbound relay only

**Decision**  
Forge Email Server is an outbound relay product, not a full mail platform.

**Why**
- actual need is outbound application/operational delivery
- full mailbox stacks add attack surface and operational drag
- inbound MX, mailbox hosting, IMAP, and webmail are separate problems

**Implication**
Anything implying inbound receive, mailbox hosting, or groupware is outside baseline scope unless explicitly re-approved later.

---

## ADR-003 — Postfix only as the core mail runtime

**Decision**  
Use Postfix only on the relay VM.

**Why**
- minimal component set for the actual requirement
- simpler to audit and operate
- avoids unnecessary Dovecot/Rspamd/webmail coupling
- cleaner relay-only posture

**Rejected alternatives**
- docker-mailserver as baseline
- full Postfix + Dovecot + Rspamd stack
- groupware/webmail-led product definition

**Implication**
The baseline runtime is Debian 12 + Postfix + supporting packages only.

---

## ADR-004 — Primary upstream is SendGrid on port 587

**Decision**  
The primary relay path is SendGrid SMTP on `587` with mandatory STARTTLS.

**Why**
- matches current SendGrid recommendation
- fits GCP constraints better than port 25
- straightforward Postfix relay pattern
- good default operational baseline

**Implication**
All baseline documentation assumes `smtp.sendgrid.net:587` first.

---

## ADR-005 — Controlled fallback ports are 465 and 2525

**Decision**  
Maintain explicit fallback profiles for:
- `465` with implicit TLS
- `2525` with STARTTLS

**Why**
- they are documented SendGrid alternatives
- keeps recovery options simple if 587 has path-specific issues
- avoids over-engineered automatic failover behaviour

**Implication**
Fallback is deliberate and operator-controlled, not clever and hidden.

---

## ADR-006 — Do not rely on outbound port 25 from GCP

**Decision**  
Port 25 is not part of the normal design.

**Why**
- GCP blocks outbound 25 to external IPs by default in normal cases
- designing around 25 would create a brittle baseline
- relay product does not need direct port-25 outbound as its primary path

**Implication**
Any future use of port 25 would be treated as an exception, not baseline behaviour.

---

## ADR-007 — No public inbound MX in baseline

**Decision**  
Do not configure this product as a public inbound mail host.

**Why**
- inbound delivery is a different operating problem
- requires broader security, spam, abuse, mailbox, and continuity decisions
- not needed for the current product objective

**Implication**
No baseline assumption of MX cutover, inbound mailbox reception, or public SMTP receive.

---

## ADR-008 — Disable local delivery on the relay host

**Decision**  
Postfix should be configured as relay-only with local delivery disabled.

**Why**
- prevents accidental mailbox behaviour on the host
- keeps the product boundary clear
- reduces confusion during testing and operation

**Implication**
`mydestination` stays empty and `local_transport` remains disabled in the baseline profile.

---

## ADR-009 — Strictest baseline is local submission only

**Decision**  
The clean baseline is local submission from workloads on the relay VM.

**Why**
- smallest trust surface
- easiest firewall posture
- simplest auditing story
- avoids premature remote submission exposure

**Implication**
Remote submitters are not assumed by default.

---

## ADR-010 — Titan-hosted app submission remains an explicit open decision

**Decision**  
Do not pretend the Titan-to-relay submission model is solved until explicitly designed.

**Why**
- it changes trust, auth, and firewall posture
- it creates new failure and abuse surfaces
- several valid models exist, but they are not interchangeable

**Allowed options**
1. workload runs local to relay VM
2. workload submits over private/VPN-restricted path to relay VM
3. workload sends directly to SendGrid

**Implication**
Docs must continue to mark this as open until one option is selected and validated.

---

## ADR-011 — Use a sending subdomain as the preferred identity boundary

**Decision**  
Prefer an authenticated sending subdomain rather than coupling all mail to the bare root domain.

**Why**
- cleaner operational separation
- easier to reason about relay/auth scope
- better hygiene for transactional/system mail identities

**Examples**
- `noreply@mail.orderededge.co.uk`
- `alerts@mail.orderededge.co.uk`

**Implication**
SendGrid authentication and DNS should be designed around a sending subdomain where practical.

---

## ADR-012 — SendGrid API keys must be narrowly scoped

**Decision**  
Use a dedicated API key for this relay with `Mail Send` scope minimum by default.

**Why**
- reduces blast radius
- easier rotation and revocation
- better separation between products/workloads

**Implication**
Expanded scopes require explicit justification in docs/config.

---

## ADR-013 — Event Webhook is the delivery telemetry path

**Decision**  
Use SendGrid Event Webhook for delivery/event observability.

**Why**
- near-real-time event stream
- better operational visibility than SMTP logs alone
- fits GCCD evidence model

**Minimum tracked events**
- processed
- delivered
- deferred
- dropped
- bounce
- spamreport
- unsubscribe

**Implication**
Webhook handling belongs in the observability/evidence design.

---

## ADR-014 — Signed Event Webhook validation is required

**Decision**  
If Event Webhook is enabled, signature verification is mandatory.

**Why**
- webhook is machine-to-machine traffic
- interactive login is not appropriate protection for callbacks
- signed validation is the correct integrity control

**Implication**
Any webhook receiver design must include signature verification before accepting events.

---

## ADR-015 — Cloudflare Access is for browser-based HTTP only

**Decision**  
Use Cloudflare Access only for human-facing HTTP applications related to the product.

**Why**
- correct layer for identity-gated browser access
- not appropriate for SMTP transport
- not appropriate as the primary control for machine callback flows

**Implication**
Cloudflare Access protects CRM/admin HTTP surfaces, not the SMTP relay path.

---

## ADR-016 — Do not put sensitive data into SendGrid metadata fields

**Decision**  
Do not place PHI, personal data, or other sensitive identifiers into categories, unique args, or custom args.

**Why**
- those fields may be retained operationally
- they are not suitable as sensitive-data containers
- privacy posture requires keeping that metadata clean

**Implication**
Application integrations must be reviewed for metadata hygiene.

---

## ADR-017 — Evidence and status live with GCCD

**Decision**  
Provisioning/config/validation evidence should tie back into GCCD rather than sit as orphan product notes.

**Why**
- keeps the workload inside the same operational governance model
- improves visibility across GCP-managed products
- prevents a split-brain between infra and product docs

**Implication**
The email product remains a GCCD-governed extension, not an operational island.

---

## ADR-018 — Avoid “smart” automatic multi-port relay failover in Postfix

**Decision**  
Do not build an automatic port-negotiation contraption in vanilla Postfix for SendGrid.

**Why**
- adds complexity faster than value
- obscures operator understanding
- makes debugging worse under stress

**Implication**
Keep separate known-good fallback profiles and switch deliberately.

---

## Summary

The architecture decisions converge on one clear shape:

**small GCP relay VM + Postfix + SendGrid + GCCD governance**

That gives the product the thing it actually needs:
reliable outbound mail with evidence and discipline, without accidentally inventing a whole email platform.
