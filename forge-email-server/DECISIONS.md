# Forge Email Server — Decision Record

**Date:** 2026-03-31  
**Project:** Forge Email Server / GCCD extension

---

## 1. Runtime location

| Option | Decision | Rationale |
|--------|----------|-----------|
| GCP-hosted relay VM | chosen | consistent with existing GCCD infrastructure and avoids Titan public-mail constraints |
| Titan-hosted public mail | rejected | not suitable for this product baseline |

---

## 2. Product shape

| Option | Decision | Rationale |
|--------|----------|-----------|
| Full mailbox stack (Postfix + Dovecot + Rspamd + webmail) | rejected | too much attack surface for the actual need |
| Postfix outbound relay only | chosen | simpler, tighter, aligned with GCP + SendGrid plan |

---

## 3. Mail flow

| Choice | Decision |
|--------|----------|
| Primary relay path | Postfix → `smtp.sendgrid.net:587` with mandatory STARTTLS |
| Fallback A | `smtp.sendgrid.net:465` with implicit TLS |
| Fallback B | `smtp.sendgrid.net:2525` with STARTTLS |
| Normal use of port 25 from GCP | rejected |

Reason: Google Cloud blocks outbound 25 to external IPs by default, while 465 and 587 are excluded. SendGrid recommends 587 as the default SMTP submission port.

---

## 4. Internet exposure

| Surface | Decision |
|---------|----------|
| Public inbound MX | out of scope |
| Public inbound SMTP receive | out of scope |
| Public IMAP / POP | out of scope |
| Human-facing HTTP surfaces | allowed behind Cloudflare Access |

This product is an outbound relay service, not a public mailbox platform.

---

## 5. Sending identity

| Option | Decision | Rationale |
|--------|----------|-----------|
| Bare root sending domain only | not baseline | higher risk of coupling application mail to root identity |
| Authenticated sending subdomain | chosen | cleaner separation for SendGrid-authenticated mail |

Recommended examples:
- `noreply@mail.orderededge.co.uk`
- `alerts@mail.orderededge.co.uk`
- equivalent addresses under `mail.rker.dev` if needed

---

## 6. Cloudflare role

| Option | Decision | Rationale |
|--------|----------|-----------|
| Cloudflare in SMTP path | rejected | not appropriate for this relay design |
| Cloudflare Access for HTTP apps | chosen | correct layer for CRM/admin UIs |
| Cloudflare Access for SendGrid webhook callback | rejected | machine-to-machine webhook should use signature validation, not interactive access |

---

## 7. Authentication model

| Surface | Decision |
|---------|----------|
| SendGrid SMTP auth | username `apikey`, password = scoped SendGrid API key |
| SendGrid API key scope | Mail Send minimum by default |
| Expanded key scopes | only if explicitly required and documented |

---

## 8. Event telemetry model

| Option | Decision |
|--------|----------|
| SendGrid Event Webhook | chosen |
| Signed Event Webhook verification | required |
| PII in categories / unique args / custom args | prohibited |

Minimum tracked events:
- processed
- delivered
- deferred
- dropped
- bounce
- spamreport
- unsubscribe

---

## 9. Submission trust model

| Option | Status | Notes |
|--------|--------|-------|
| relay VM local submission only | baseline | simplest and safest |
| Titan-hosted app submits over private network / VPN | open design extension | allowed only if source restriction, auth, and logging are documented |
| Titan-hosted app sends directly to SendGrid | fallback | acceptable where relay VM does not add value |

This remains the main open integration decision for Titan-hosted systems.

---

## 10. Rejected assumptions from earlier drafts

The following are no longer part of the target design:
- docker-mailserver as the core runtime
- Dovecot / IMAP / mailbox hosting as baseline
- Roundcube as baseline webmail
- public MX and inbound mail delivery
- Cloudflare Tunnel as part of the SMTP delivery path

---

## 11. Immediate next actions

- [ ] provision `forge-mail-server` in GCP through GCCD
- [ ] install Debian 12 + Postfix relay profile
- [ ] create scoped SendGrid API key
- [ ] authenticate sending subdomain in SendGrid
- [ ] enable Signed Event Webhook
- [ ] decide Titan app submission model
- [ ] update GCCD register/evidence model for relay operations
