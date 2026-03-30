# Email Server on Titan — Phased Implementation Brief

**Domains**: `orderededge.co.uk`, `rker.dev`  
**Host**: titan (`192.168.10.80`, `titan.tail1a2109.ts.net`)  
**Cloudflare Tunnel ID**: `18a78b3b-7b30-465f-b09f-4e6912daee1f`

---

## Overview

Build a hardened, self-hosted email server using `docker-mailserver` (Postfix/Dovecot + Rspamd), with webmail, DKIM/DMARC/SPF authentication, TLS via Let's Encrypt, and access through a Cloudflare Tunnel. Zero ports opened on titan — traffic flows `Cloudflare Tunnel → Nginx/Caddy proxy → container services`.

---

## Phase 0: Viability and Decision Gates

**Goal**: Decide whether self-hosting full email is viable from Titan.

### Tasks

1. **ISP and firewall check**
   - Confirm ISP allows inbound port 25 (SMTP)
   - Verify no firewall blocking inbound 25 (telnet test from external)
   - Document ISP's stance on residential/business port 25

2. **PTR/Reverse DNS verification**
   - Confirm public IP has PTR record configured
   - Check if PTR matches forward DNS (`mail.orderededge.co.uk`)
   - Document ISP's process for requesting PTR record

3. **Outbound mail model decision**
   - **Option A**: Direct send from Titan (port 25 outbound, no relay)
   - **Option B**: Smarthost/relay via trusted provider (e.g., SendGrid, Mailgun, ISP relay)
   - Document choice and rationale

4. **Domain role definition**
   - Which domains receive mail? (`orderededge.co.uk`, `rker.dev`)
   - Which domains send mail? (same, or subset)
   - Personal/low-volume vs business-facing (volume expectations)

5. **Host location decision**
   - **Option A**: Self-host on Titan (current setup)
     - Pros: Control, no recurring hosting cost, uses existing infrastructure
     - Cons: ISP/port 25 restrictions, no PTR on public IP, single point of failure
   - **Option B**: Hosted VPS on GCP (small server, ~1-2 vCPU, 1-2GB RAM)
     - Pros: Reliable hosting with PTR, BGP anycast, static IP, better deliverability, dedicated IP reputation
     - Cons: Recurring cost (~$5-20/month), less direct control, network latency to titan
   - **Recommendation**: GCP VPS for production — better email deliverability and reduced risk

6. **Exit criteria review**
   - Clear go/no-go on self-hosted public mail delivery
   - Chosen domain roles documented
   - Chosen outbound model documented
   - Host location decision documented (Titan vs GCP VPS)
   - Volume expectations set

### Deliverables
- Decision record in `DECISIONS.md`
- Outbound model choice confirmed
- Domain roles documented
- Host location decision documented (Titan vs GCP VPS)
- Volume expectations set
- Go/no-go decision for Phase 1+ deployment

---

## Phase 1: Architecture and Security Baseline

**Goal**: Lock the design before deployment.

### Tasks

1. **Finalize hostnames**
   - Separate mail. for SMTP/IMAP endpoints
   - Separate webmail. for browser access
   - Examples: `mail.orderededge.co.uk`, `webmail.orderededge.co.uk`

2. **Choose webmail product**
   - **Roundcube**: Actively maintained, mature, plugin ecosystem, PHP-based
   - **SnappyMail**: Modern, fast, built-in features, actively developed
   - **Avoid RainLoop**: Archived, no maintenance, security risk

3. **Define data locations**
   - Mail storage: `/data/appdata/docker-mailserver/mail/`
   - Logs: `/data/appdata/docker-mailserver/logs/`
   - Config: `/data/appdata/docker-mailserver/config/`
   - Backups: `/data/backups/docker-mailserver/`
   - Secrets (DKIM keys): `/data/appdata/docker-mailserver/secrets/`

4. **Define backup and restore approach**
   - Daily tarball of `/var/mail`, `/config`, `/secrets`
   - Incremental backups using rsync or Borg
   - Restore test: monthly, not just backup existence
   - Off-site copy: sync to GCP storage if hosted on GCP

5. **Define admin access model**
   - Rspamd admin: localhost-only, proxied via tunnel, basic auth only
   - Mailcow/Rainloop-style admin: not exposed unless absolutely needed
   - SSH access: key-based only, restricted to specific IPs via firewall
   - Webmail admin: password policy enforced, MFA optional

6. **Decide TLS posture**
   - **SMTP/IMAP**: TLS 1.2+, strong ciphers, STARTTLS required
   - **Webmail**: HTTPS only, HSTS, TLS 1.3 preferred
   - Separate certificates for mail vs webmail if needed

### Exit criteria
- One-page target architecture document
- Security baseline agreed
- Product selections frozen (Roundcube or SnappyMail)

---

## Phase 2: Mail Core Deployment

**Goal**: Get the mail platform running internally first.

### Tasks

1. **Deploy docker-mailserver with persistent storage**
   - Host mount: `/data/appdata/docker-mailserver/`
   - Container: `dockermailserver/docker-mailserver:latest`
   - Health check: SMTP on 25, IMAP on 993

2. **Configure domains, mailboxes, aliases, and submission/authentication**
   - domains: `orderededge.co.uk`, `rker.dev`
   - mailboxes: admin, postmaster, abuse, user aliases
   - SMTP submission: port 587 with TLS
   - IMAP: port 993 with SSL
   - SASL authentication via Dovecot

3. **Enable Rspamd and DKIM signing**
   - Rspamd: `ENABLE_RSPAMD=1`, `ENABLE_SPAMASSASSIN=0`
   - DKIM: Generate keys per domain, publish public keys in DNS
   - Rspamd scoring: spam threshold 15, greylist 7

4. **Validate local SMTP, IMAP, mailbox login, and message flow inside the environment**
   - Test: `swaks --to test@orderededge.co.uk --from test@orderededge.co.uk --server localhost`
   - Test IMAP login: `openssl s_client -connect localhost:993`
   - Check logs: `docker-compose logs dms`

### Exit criteria
- Mailboxes can send and receive internally
- DKIM signing is working
- Logs and health checks are visible

---

## Phase 3: DNS and Trust Configuration

**Goal**: Make the domains trustworthy before public use.

### Tasks

1. **Publish DNS-only A/AAAA for each mail host**
   - `mail.orderededge.co.uk` → `192.168.10.80` (A record)
   - `mail.rker.dev` → `192.168.10.80` (A record)

2. **Publish MX records for each sending/receiving domain**
   - `orderededge.co.uk` MX: `10 mail.orderededge.co.uk`
   - `rker.dev` MX: `10 mail.rker.dev`

3. **Publish DKIM public keys**
   - `mail._domainkey.orderededge.co.uk` → TXT with public key
   - `mail._domainkey.rker.dev` → TXT with public key

4. **Publish one SPF record per domain, listing actual sending sources**
   - `orderededge.co.uk` TXT: `v=spf1 ip4:192.168.10.80 include:_spf.orderededge.co.uk ~all`
   - `rker.dev` TXT: `v=spf1 ip4:192.168.10.80 include:_spf.rker.dev ~all`

5. **Publish DMARC with reporting first**
   - `_dmarc.orderededge.co.uk` TXT: `v=DMARC1; p=none; rua=mailto:dmarc@orderededge.co.uk;`
   - `_dmarc.rker.dev` TXT: `v=DMARC1; p=none; rua=mailto:dmarc@rker.dev;`

6. **Configure PTR/reverse DNS for the sending IP to the chosen mail hostname**
   - Request PTR from ISP or GCP for public IP
   - PTR must match forward DNS (`mail.orderededge.co.uk` or `mail.rker.dev`)

7. **Verify forward and reverse DNS alignment**
   - `dig -x <IP>` should return mail hostname
   - `dig mail.orderededge.co.uk A` should return same IP

### Exit criteria
- SPF, DKIM, DMARC, MX, A/AAAA, and PTR all validate cleanly
- DMARC reports are received
- No circular SPF design remains

---

## Phase 4: Webmail and Access Layer

**Goal**: Provide safe browser access without exposing the whole mail stack.

### Tasks

1. **Deploy reverse proxy locally on Titan**
   - Nginx or Caddy on `127.0.0.1:8080`
   - Only webmail hostname proxied
   - Mail/IMAP ports NOT exposed

2. **Put only the webmail hostname behind Cloudflare Tunnel**
   - `webmail.orderededge.co.uk` → `http://127.0.0.1:8081`
   - `webmail.rker.dev` → `http://127.0.0.1:8081`
   - Mail hostname NOT behind tunnel (must be reachable by other mail servers)

3. **Protect admin endpoints; do not expose Rspamd admin publicly unless there is a strong reason**
   - Rspamd admin: localhost-only, not proxied externally
   - Webmail admin: basic auth only, if enabled at all

4. **Use Cloudflare Origin CA or another appropriate origin certificate for the proxied web origin**
   - Cloudflare Origin CA for webmail hostnames
   - Certificates renewed automatically

### Exit criteria
- Webmail reachable externally over HTTPS
- Admin surfaces are restricted
- Webmail is completely separated from raw mail delivery ports

---

## Phase 5: Hardening

**Goal**: Move from "it runs" to "it survives the Internet".

### Tasks

1. **Rate limiting, postscreen/fail2ban or equivalent controls**
   - Fail2ban jail for SMTP authentication failures
   - Postscreen for connection rate limiting
   - Rspamd rate limiting for submissions

2. **Strong auth policies and mailbox password policy**
   - Minimum password length: 16 characters
   - Require complexity: upper, lower, number, symbol
   - Password history: 12 passwords
   - Account lockout: 5 failed attempts

3. **Disable unnecessary services and admin surfaces**
   - POP3 disabled (only IMAP)
   - SMTP without authentication disabled
   - Admin interfaces not exposed externally

4. **Monitoring and alerting for queue growth, disk, auth failures, and reputation issues**
   - Prometheus/Grafana for metrics
   - Alerts: queue > 100, disk > 80%, auth failures > 10/min
   - DKIM/DMARC reports weekly

5. **Backup restore test, not just backup existence**
   - Monthly restore test from backup location
   - Validate mailbox integrity after restore
   - Document restore procedure

6. **Document incident recovery steps**
   - Mail queue stuck: flush queue, check logs, restart container
   - DKIM key lost: regenerate, update DNS, notify recipients
   - Compromised mailbox: disable, rotate passwords, audit logs

### Exit criteria
- Security checklist completed
- Restore test passed
- Monitoring alerts tested

---

## Phase 6: Staged Rollout

**Goal**: Avoid a dramatic first day on the public Internet.

### Tasks

1. **Start with test mailboxes only**
   - Create internal test accounts only
   - Do not publish public contact methods yet

2. **Send to major receivers and validate authentication**
   - Send to Gmail, Outlook, Yahoo test accounts
   - Verify SPF/DKIM/DMARC passing in headers
   - Check spam folder placement (should be inbox)

3. **Watch DMARC reports and spam-folder placement**
   - Monitor DMARC reports for 7-14 days
   - Adjust SPF/DKIM if issues found
   - Only proceed when deliverability is stable

4. **Only after stable validation, move DMARC from none to quarantine, then reject**
   - Phase 1: `p=none` (monitoring)
   - Phase 2: `p=quarantine` (move failures to spam)
   - Phase 3: `p=reject` (reject all failures)
   - Wait 14+ days between phases

### Exit criteria
- Deliverability acceptable
- Authentication stable
- DMARC policy tightened intentionally, not heroically

---

## Key Risks to Track

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Reachability risk** | No inbound port 25 or no public IP path means true self-hosted inbound mail is dead on arrival | Verify ISP allows port 25; test from external with telnet |
| **Deliverability risk** | No PTR/reverse DNS alignment will hurt outbound trust quickly | Request PTR from ISP/GCP; align with forward DNS |
| **Product risk** | RainLoop is archived, so using it would bake obsolescence into day one | Use Roundcube or SnappyMail only |
| **Configuration risk** | Current SPF draft is structurally risky | Use single SPF record per domain, avoid nested includes |
| **Operational risk** | Mail is not like most self-hosted apps; once public, the Internet starts grading your homework immediately and usually with a red pen | Staged rollout with DMARC monitoring; wait for validation before full launch |

---

## What "Done" Should Look Like

- Titan hosts docker-mailserver as the mail core
- Public mail delivery uses real public DNS and a reachable public IP
- Webmail is exposed through Cloudflare Tunnel on separate `webmail.` hostnames
- SPF, DKIM, DMARC, MX, A/AAAA, and PTR are valid and aligned
- DMARC starts at monitoring mode and is later enforced
- Webmail product is Roundcube or SnappyMail, not RainLoop
- Backups, restore, logging, and admin access controls are documented and tested

---

## My Recommendation in One Line

Build this as a two-lane project — public mail delivery on standard Internet mail plumbing, and webmail/admin behind Cloudflare Tunnel — rather than trying to make the tunnel do both jobs.

---

## Rollback Plan

If something fails:
1. `docker-compose down -v` — removes containers, **not** data volumes
2. `git checkout .` — restore previous config (if versioned)
3. Delete Cloudflare Tunnel endpoints for affected domains
4. DNS records: set MX record priority to 20 or delete temporarily

---

## Estimated Timeline

| Phase | Duration | Risk |
|-------|----------|------|
| Phase 0: Viability | 1 hour | Critical (go/no-go) |
| Phase 1: Architecture | 2 hours | Low |
| Phase 2: Mail Core | 4 hours | Medium |
| Phase 3: DNS/Trust | 2 hours | Medium (propagation delays) |
| Phase 4: Webmail | 2 hours | Low |
| Phase 5: Hardening | 3 hours | Medium |
| Phase 6: Staged Rollout | 14+ days | Low (but time-intensive) |
| **Total active work** | ~14 hours | |
| **Total timeline (with testing)** | 2-3 weeks | |

---

## Notes

- **No external ports opened** on titan — traffic flows entirely through Cloudflare Tunnel for webmail only
- **SMTP/IMAP must be publicly reachable** — cannot rely on tunnel for inbound mail delivery
- **Container isolation**: `dms` uses custom Docker network, no host bridge exposure
- **State persistence**: `/var/mail`, `/config`, `/secrets` bound to `/data/appdata/docker-mailserver/`
- **Future expansion**: Can add secondary MX via `backup-mx` service if needed
- **Webmail separation**: Webmail is separate hostname and container, never exposed to raw mail ports

---

*Last updated: 2026-03-30 05:16 GMT+1*
