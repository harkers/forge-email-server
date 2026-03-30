# Forge Mail Platform — Security Baseline

**Project**: Forge Mail Platform – VPS-Hosted Email Service  
**Last updated**: 2026-03-30

---

## Security Principles

1. **Minimal attack surface** — Only necessary services exposed
2. **Defense in depth** — Container isolation, TLS, rate limiting
3. **least privilege** — Non-root containers, capability drops
4. **Immutable infrastructure** — Configuration as code, state in bind mounts
5. **Secure defaults** — TLS required, plaintext disabled, strong auth

---

## Container Security

| Control | Setting | Target |
|---------|---------|--------|
| **Privileged** | `false` | Explicit deny |
| **cap_drop** | `[ALL]` | Drop all capabilities |
| **cap_add** | `[]` (or `NET_BIND_SERVICE` only) | Minimal add |
| **read_only** | `true` (config volume) | Prevent runtime changes |
| **user** | Non-root (`1000:1000`) | Prevent container escape |
| **tmpfs** | `/tmp`, `/run` | Ephemeral data only |

---

## Postfix Security

| Control | Setting | Purpose |
|---------|---------|---------|
| **TLS protocols** | `!SSLv2 !SSLv3 !TLSv1 !TLSv1.1` | TLS 1.2+ only |
| **TLS ciphers** | `high` | Strong ciphers only |
| **TLS session cache** | `btree:${data_directory}/smtpd_scache` | Session resumption |
| **STARTTLS** | `smtpd_tls_security_level = may` or `encrypt` | TLS preferred |
| **No plaintext auth** | `smtpd_tls_auth_only = yes` | Require TLS for auth |
| **recipient restrictions** | Rspamd policy + reject_unauth | Spam filtering |
| **smtputf8** | `no` (if relay doesn't support) | Avoid UTF-8 issues |

---

## Dovecot Security

| Control | Setting | Purpose |
|---------|---------|---------|
| **SSL** | `required` | All connections TLS |
| **disable_plaintext_auth** | `yes` | No auth without TLS |
| **mail_location** | `maildir:/var/mail/%d/%n` | Standard, portable |
| **IMAP port** | `993 only` | No plaintext IMAP |
| **SASL auth** | `dovecot` | Secure authentication |
| **auth_mechanisms** | `plain login` (or just `plain`) | Minimal mechanisms |
| **password_scheme** | `SHA512-CRYPT` | Strong hashing |

---

## Rspamd Security

| Control | Setting | Purpose |
|---------|---------|---------|
| **Admin port** | `11334` (localhost only) | Not exposed externally |
| **Rate limiting** | `enabled` | Prevent abuse |
| **Spam threshold** | `15` | Balanced filtering |
| **Greylist** | `enabled`, delay `7` | Delayed spam delivery |
| **Internal IPs** | Whitelist `10.0.0.0/8`, `192.168.0.0/16` | Local delivery trusted |

---

## Authentication

| Layer | Control | Standard |
|-------|---------|----------|
| **SMTP submission** | SASL via Dovecot | RFC 4954 |
| **IMAP login** | SASL via Dovecot | RFC 5802 |
| **Password policy** | Minimum 16 chars, complexity | NIST SP 800-63B |
| **Account lockout** | 5 failed attempts | Brute force mitigation |
| **Password history** | 12 passwords | Prevent reuse |

---

## TLS Configuration

| Service | Port | TLS Version | Certificate |
|---------|------|-------------|-------------|
| **SMTP (submission)** | 587 | TLS 1.2+ | Let's Encrypt / Origin CA |
| **SMTP (implicit)** | 465 | TLS 1.2+ | Let's Encrypt / Origin CA |
| **IMAP** | 993 | TLS 1.2+ | Let's Encrypt / Origin CA |
| **Webmail** | 443 | TLS 1.3 | Let's Encrypt / Origin CA |

**Certificate management**:
- Let's Encrypt for public mail hostnames
- Cloudflare Origin CA for webmail (optional, if tunnel used)
- Auto-renewal via certbot + container reload

---

## Monitoring & Alerting

| Metric | Threshold | Alert Method |
|--------|-----------|--------------|
| **Mail queue** | > 100 | Telegram / webhook |
| **Disk usage** | > 80% | Telegram / webhook |
| **Auth failures** | > 10/min | Telegram / webhook |
| **Certificate expiry** | < 7 days | Telegram / webhook |
| **DKIM signing failures** | > 0 | Telegram / webhook |
| **Rspamd score spikes** | > 5 above normal | Telegram / webhook |

---

## Backup Security

| Control | Setting | Location |
|---------|---------|----------|
| **Encrypted backup** | GPG / age | Titan `/data/backups/` |
| **Key management** | Separate from VPS | Titan, encrypted |
| **Off-site copy** | GCP Storage / S3 | Cloud redundancy |
| **Restore test** | Monthly | Scheduled task |
| **Key rotation** | Quarterly | Scheduled task |

---

## Admin Access

| Surface | Access | Protection |
|---------|--------|------------|
| **VPS SSH** | Key-only, restricted IPs | Fail2ban |
| **Rspamd admin** | Localhost only, not exposed | Network namespace |
| **Postfix/Dovecot config** | Local file edit | Git versioned |
| **Webmail admin** | Disabled unless needed | Basic auth if enabled |
| **Container CLI** | Docker socket access | Restricted to admin group |

---

## Incident Response

| Scenario | Action | Tool |
|----------|--------|------|
| **Compromised mailbox** | Disable, rotate password, audit logs | Dovecot CLI |
| **DKIM key lost** | Regenerate, update DNS, notify recipients | `docker-mailserver setup` |
| **Mail queue stuck** | Flush queue, check logs, restart container | `postqueue`, `docker-compose` |
| **Rspamd misfiltering** | Adjust scores, check logs, whitelist | Rspamd CLI |
| **Certificate expiry** | Renew, reload containers | Certbot + Docker reload |

---

## Compliance Considerations

| Requirement | Status | Notes |
|-------------|--------|-------|
| **GDPR** | Basic compliance | Mail storage in EU, no automated processing |
| **PIPA** | Not applicable | UK-based personal data, no PIPA scope |
| **CCPA** | Basic compliance | No "selling" of personal data |
| **SOC 2** | Not applicable | Internal use only, no service org |

---

## Security Checklist (Pre-Launch)

- [ ] All containers run non-root
- [ ] All containers drop ALL capabilities
- [ ] All services use TLS 1.2+ only
- [ ] No plaintext auth enabled
- [ ] Rspamd admin not exposed externally
- [ ] Mailbox passwords meet 16-char minimum
- [ ] DKIM keys stored encrypted in backup
- [ ] Backup encryption keys separate from VPS
- [ ] Monitoring alerts configured
- [ ] Restore test passed
- [ ] DMARC policy starts at `p=none`
- [ ] PTR/reverse DNS aligned with mail hostname

---

## Exit Criteria

- [ ] All security controls implemented
- [ ] Container hardening applied
- [ ] TLS 1.2+ enforced on all services
- [ ] Admin interfaces restricted or disabled
- [ ] Monitoring active and tested
- [ ] Backup encryption verified
- [ ] Restore test passed
- [ ] Security checklist signed off

---

*Last updated: 2026-03-30*
