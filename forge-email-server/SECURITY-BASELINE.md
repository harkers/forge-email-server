# Forge Email Server — Security Baseline

**Product shape:** outbound relay only  
**Runtime:** Debian 12 on GCP  
**MTA:** Postfix  
**Upstream:** SendGrid

---

## 1. Security principles

1. minimize exposed surfaces
2. keep the relay role narrow
3. require TLS to upstream delivery
4. scope credentials to the minimum needed
5. keep evidence and alerts explicit
6. do not move sensitive data into relay metadata fields

---

## 2. Baseline host posture

| Control | Baseline |
|---------|----------|
| OS | Debian 12 |
| Product role | outbound relay only |
| Public inbound SMTP receive | disabled by scope |
| Local delivery | disabled |
| Unneeded services | not installed |
| SSH | key-only, operator-restricted |
| Patch policy | security updates applied before onboarding workloads |

---

## 3. Postfix baseline

### Required controls
- `relayhost = [smtp.sendgrid.net]:587`
- `smtp_sasl_auth_enable = yes`
- `smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd`
- `smtp_tls_security_level = encrypt`
- `smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt`
- `local_transport = error:local delivery disabled`
- `mydestination =`
- `disable_vrfy_command = yes`

### Preferred listener posture
The strictest baseline is local submission only.

```cf
inet_interfaces = loopback-only
```

If remote submitters are later required, that becomes a documented extension with source restriction and updated firewall rules. It is not part of the baseline by default.

---

## 4. SendGrid transport posture

| Setting | Baseline |
|---------|----------|
| Primary port | 587 |
| Primary TLS mode | STARTTLS mandatory |
| Fallback 1 | 465 implicit TLS |
| Fallback 2 | 2525 STARTTLS |
| Port 25 on GCP | not part of normal design |
| Auth username | `apikey` |
| Auth password | scoped SendGrid API key |

---

## 5. Secret handling

### SendGrid API key
- dedicated key for this relay only
- `Mail Send` scope minimum unless another scope is explicitly justified
- stored outside world-readable config
- permissions on secret files: `0600`
- rotate on suspicion of exposure or scheduled review

### Postfix credentials map
```text
/etc/postfix/sasl_passwd
/etc/postfix/sasl_passwd.db
```

After `postmap`, both files must remain restricted.

---

## 6. DNS and identity controls

| Control | Baseline |
|---------|----------|
| Sending identity | authenticated sending subdomain |
| DKIM | SendGrid domain authentication CNAMEs |
| SPF | include SendGrid-authorized path |
| DMARC | start with `p=none` |
| Public MX | not required for relay-only model |

---

## 7. Event webhook security

If Event Webhook is enabled:
- verify Signed Event Webhook signatures
- prefer a narrow HTTPS endpoint dedicated to event intake
- log validation failures explicitly
- do not rely on Cloudflare Access interactive auth for webhook ingestion

### Privacy rule
Do **not** place PHI, personal data, or sensitive identifiers in:
- categories
- unique args
- custom args
- other SendGrid metadata fields that may be retained or exposed operationally

---

## 8. Monitoring and alerting

Minimum signals:
- Postfix queue growth beyond normal baseline
- auth failures to SendGrid
- repeated TLS negotiation failures
- Event Webhook validation failures
- bounce/spamreport spikes
- certificate / CA trust issues on relay host

---

## 9. Firewall posture

### Default baseline
- allow outbound 587 to SendGrid
- keep admin access narrow
- do not expose public inbound SMTP receive as part of this product

### If remote submitters are added later
Only allow explicitly approved source ranges over the chosen submission port.
That change must be documented before rollout.

---

## 10. Pre-onboarding checklist

- [ ] Debian 12 relay host patched
- [ ] Postfix relay-only config applied
- [ ] local delivery disabled
- [ ] SendGrid API key scoped correctly
- [ ] SASL password files locked to `0600`
- [ ] DKIM/SPF/DMARC configured for sending subdomain
- [ ] Signed Event Webhook validation ready if using webhook telemetry
- [ ] no sensitive metadata passed to SendGrid fields
- [ ] evidence and alerting path documented

---

## 11. Operational caution

Earlier drafts assumed a much larger stack.
That is no longer the security baseline.
The trusted baseline is intentionally small: **Debian 12 + Postfix relay + SendGrid**, with Cloudflare used only where HTTP identity control is actually relevant.
