# Forge Email Server — Cloudflare Zero Trust Role

**Status:** design guidance  
**Scope:** HTTP surfaces only  
**Not in scope:** SMTP relay path

---

## 1. What Cloudflare is for here

Cloudflare remains useful for **human-facing HTTP applications** associated with the product.
Examples:
- `crm.orderededge.co.uk` for Nextcloud or CRM access
- a future operator dashboard for mail evidence / status
- other browser-based admin surfaces

Cloudflare is **not** part of the validated SMTP relay design.

---

## 2. What Cloudflare is not for here

Do not route these through Cloudflare Access interactive login:
- SMTP relay traffic to SendGrid
- SendGrid SMTP authentication
- SendGrid Event Webhook callbacks

Reason:
- SMTP is outside this product’s Access design
- webhook callbacks are machine-to-machine and should be protected with signature verification, not human login

---

## 3. Two-layer model for HTTP apps

For browser-based apps only:

```text
Internet
  → Cloudflare proxy / network protection
  → Cloudflare Access
  → origin HTTP service
```

Recommended identity:
- IdP: `auth.harker.systems`
- allowed user: `stuart.harker@orderededge.co.uk`
- session duration: 12 hours

---

## 4. Recommended policy stance

### Access policy
- allow only explicitly named operator identities
- prefer IdP-backed login
- default deny for everyone else

### Session policy
- 12h operator session is acceptable for this internal admin use
- require re-auth after expiry

### Logging
- preserve Access logs for operator activity review

---

## 5. DNS guidance

### Protected HTTP apps
Use proxied CNAMEs to the existing tunnel where appropriate.

Example pattern:
- `crm.orderededge.co.uk` → proxied / Access-protected

### Relay hostname
The SMTP relay host should **not** be treated as an Access-protected web application.
If a relay hostname exists for operational DNS purposes, it remains outside the Access login flow.

### Event webhook hostname
If SendGrid Event Webhook is exposed on a public HTTPS endpoint:
- do not put it behind interactive Cloudflare Access
- secure it with Signed Event Webhook validation
- optionally use standard Cloudflare proxy/WAF behavior if compatible with the receiver

---

## 6. Minimal config checklist

### For `crm.orderededge.co.uk`
- [ ] proxied through Cloudflare
- [ ] Access application created
- [ ] `auth.harker.systems` configured as IdP
- [ ] `stuart.harker@orderededge.co.uk` allow rule configured
- [ ] session duration set to 12h
- [ ] origin verified after login

### For any future admin UI
- [ ] confirm it is human-facing HTTP
- [ ] confirm it is not a webhook receiver
- [ ] place behind Access only after origin path is confirmed

---

## 7. Rollback posture

If Access causes operator lockout on an HTTP app:
1. temporarily bypass Access for that HTTP hostname
2. restore operator access
3. fix IdP / policy configuration
4. re-enable Access

This rollback guidance does not apply to the SMTP path because SMTP is not routed through Access.

---

## 8. Final rule

For this product, Cloudflare Access protects **people using browsers**.
SendGrid handles **mail transport**.
The two should not be conflated.
