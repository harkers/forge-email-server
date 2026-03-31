# SendGrid Setup Guide for Forge Email Server

**Target runtime:** Debian 12 on GCP  
**Relay model:** Postfix outbound relay only  
**Primary upstream:** `smtp.sendgrid.net:587`

---

## 1. Design baseline

### Primary path

```text
application or internal system → local Postfix relay on the VM → SendGrid on 587 with mandatory STARTTLS
```

### Controlled fallbacks
- 465 with implicit TLS
- 2525 with STARTTLS
- never 25 as the normal GCP design

### Product boundary
This guide configures **outbound relay only**.
It does not configure mailbox hosting, IMAP, POP, or inbound MX.

---

## 2. Prerequisites

- [ ] GCP VM provisioned (Debian 12)
- [ ] Postfix installed
- [ ] SendGrid account created
- [ ] dedicated SendGrid API key created
- [ ] authenticated sending subdomain selected
- [ ] Cloudflare DNS access available
- [ ] `ca-certificates` installed on the VM
- [ ] `swaks` and `openssl` available for testing

---

## 3. SendGrid account and API key

### 3.1 Create the relay key
Create a dedicated SendGrid API key for this relay only.

**Minimum scope:**
- `Mail Send`

Do not grant broader permissions unless the product explicitly needs them.

### 3.2 SMTP auth model
SendGrid SMTP uses:
- username: `apikey`
- password: the SendGrid API key itself

---

## 4. Authenticated domain model

Use a sending subdomain rather than the bare root domain.

Examples:
- `mail.orderededge.co.uk`
- `mail.rker.dev`

Typical sender examples:
- `noreply@mail.orderededge.co.uk`
- `alerts@mail.orderededge.co.uk`

When SendGrid authenticated domain is enabled, SendGrid provides DNS records, typically 3 CNAMEs under Automated Security.

---

## 5. Debian 12 packages

```bash
sudo apt update
sudo apt install -y postfix libsasl2-modules ca-certificates mailutils swaks
```

Choose **Internet Site** during package prompts if needed, then replace the generated config with the relay profile below.

---

## 6. Main Postfix profile

### `/etc/postfix/main.cf`

```cf
myhostname = relay1.orderededge.co.uk
myorigin = orderededge.co.uk
inet_interfaces = loopback-only
inet_protocols = all

# Do not deliver locally; relay only
mydestination =
local_transport = error:local delivery disabled

# Trusted local submitters only
mynetworks = 127.0.0.0/8 [::1]/128

# SendGrid relay
relayhost = [smtp.sendgrid.net]:587

# SMTP auth
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_sasl_tls_security_options = noanonymous

# TLS: require encryption to upstream relay
smtp_tls_security_level = encrypt
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
smtp_tls_loglevel = 1
smtp_tls_note_starttls_offer = yes

# Sensible queue behaviour
maximal_queue_lifetime = 1d
bounce_queue_lifetime = 1d
delay_warning_time = 1h

# Message sizing
header_size_limit = 4096000

# Hygiene
disable_vrfy_command = yes
smtputf8_enable = yes
```

### Why this baseline
- relay-only role
- no local delivery
- no public receive role
- mandatory TLS to SendGrid
- minimal trusted submitter set

---

## 7. Credentials map

### `/etc/postfix/sasl_passwd`

```text
[smtp.sendgrid.net]:587 apikey:SG.xxxxx_your_sendgrid_api_key_xxxxx
```

Then run:

```bash
sudo postmap /etc/postfix/sasl_passwd
sudo chmod 600 /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db
sudo systemctl restart postfix
```

---

## 8. Fallback profiles

Do not try to make vanilla Postfix perform clever automatic failover between SendGrid ports.
Keep deliberate fallback snippets ready and switch intentionally.

### Fallback A — implicit TLS on 465

```cf
relayhost = [smtp.sendgrid.net]:465
smtp_tls_wrappermode = yes
smtp_tls_security_level = encrypt
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_sasl_tls_security_options = noanonymous
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
```

### Fallback B — STARTTLS on 2525

```cf
relayhost = [smtp.sendgrid.net]:2525
smtp_tls_wrappermode = no
smtp_tls_security_level = encrypt
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_sasl_tls_security_options = noanonymous
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
```

---

## 9. DNS checklist

### Required
- SendGrid authenticated domain CNAMEs published
- SPF aligned with SendGrid sending path
- DMARC published at `p=none` initially

### Example shape

```text
s1._domainkey.mail.orderededge.co.uk  CNAME  ...sendgrid.net
s2._domainkey.mail.orderededge.co.uk  CNAME  ...sendgrid.net
em1234.mail.orderededge.co.uk         CNAME  ...sendgrid.net
```

Use the exact values SendGrid provides.

---

## 10. Event Webhook

Enable SendGrid Event Webhook for:
- processed
- delivered
- deferred
- dropped
- bounce
- spamreport
- unsubscribe

### Security requirement
Enable **Signed Event Webhook** and verify signatures on receipt.
Do not put webhook callbacks behind interactive Cloudflare Access.

### Privacy rule
Do not place PHI, personal data, or sensitive identifiers in SendGrid categories, unique args, or custom args.

---

## 11. Validation steps

### 11.1 Test TLS 1.2 connectivity first

```bash
openssl s_client -starttls smtp -connect tls12.smtp.sendgrid.net:587 -tls1_2
```

### 11.2 Check Postfix config

```bash
postconf -n
```

### 11.3 Send a live test through Postfix

```bash
printf 'Subject: Forge relay test\n\nhello from Forge relay\n' | sendmail test@example.com
```

### 11.4 Send with swaks

```bash
swaks --server smtp.sendgrid.net:587 \
  --tls \
  --auth LOGIN \
  --auth-user apikey \
  --auth-password 'SG.xxxxx_your_sendgrid_api_key_xxxxx' \
  --to test@example.com \
  --from noreply@mail.orderededge.co.uk
```

### 11.5 Review headers
Confirm delivered mail shows expected authentication results and no obvious alignment problems.

---

## 12. Troubleshooting

### Auth failures
```bash
journalctl -u postfix -n 100 --no-pager
```

### TLS failures
```bash
openssl s_client -starttls smtp -connect smtp.sendgrid.net:587
```

### DNS / DKIM issues
```bash
dig s1._domainkey.mail.orderededge.co.uk CNAME +short
dig txt _dmarc.mail.orderededge.co.uk +short
```

### Queue inspection
```bash
mailq
postqueue -p
```

---

## 13. If Titan-hosted apps must use this relay

That is not covered by the strict loopback-only baseline.
Before changing the host to accept remote submissions, document:
- source restriction
- chosen submission port
- auth model
- firewall rules
- evidence and alerting updates

Until then, either:
- keep the workload local to the relay VM, or
- have the workload use SendGrid directly

---

## 14. Recommended order

1. provision VM
2. install Postfix relay profile
3. create scoped SendGrid API key
4. authenticate sending subdomain
5. test TLS 1.2 connectivity
6. send test mail via Postfix
7. enable Signed Event Webhook
8. onboard first real workload
