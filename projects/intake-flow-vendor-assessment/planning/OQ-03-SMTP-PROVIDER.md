# OQ-03 — SMTP Provider for Email Delivery

**Status:** RESOLVED  
**Resolved:** 2026-03-31  
**Resolution source:** Planning subagent (ollama/qwen3-coder-next:cloud)

---

## Decision

**Provider:** Postmark — Starter Plan ($15/month, 25,000 emails/month)  
**Protocol:** SMTP submission on port 587 with TLS  
**Sender address:** `notifications@datadnaprivacy.com`  
**Call method:** Python `smtplib` (async wrapper in FastAPI)

---

## Rationale

1. **Port 25 blocked** — Postmark accepts SMTP on port 587 (Submission port) with mandatory TLS, which bypasses the BT Business residential block.
2. **Low volume** — 20–50 emails/month is well within Starter plan headroom.
3. **Branded sender** — Domain verification required (TXT record); once verified, any `from:` address on that domain is permitted.
4. **Deliverability** — Postmark maintains IP reputation proactively; critical for vendor and client-facing communications.
5. **Cost** — $15/month is modest; alternatives (SendGrid, Mailgun) introduce more operational overhead or warm-up complexity.

---

## DNS Configuration

Required on `datadnaprivacy.com` (Cloudflare DNS):

```
# Domain verification TXT record
postmark._domainkey.datadnaprivacy.com.  IN  TXT  "postmark-verification=<token>"

# SPF record
datadnaprivacy.com.  IN  TXT  "v=spf1 include:spf.postmarkapp.com ~all"

# DMARC (optional but recommended)
_dmarc.datadnaprivacy.com.  IN  TXT  "v=DMARC1; p=none; rua=mailto:dmarc@datadnaprivacy.com"
```

DKIM is configured automatically after domain verification.

---

## Titan Environment Variables

```bash
SMTP_HOST=smtp.postmarkapp.com
SMTP_PORT=587
SMTP_USER=server-api-token
SMTP_PASS=<postmark_server_api_token>
SMTP_FROM=notifications@datadnaprivacy.com
```

---

## Output Delivery Agent Implementation

```python
import smtplib
import os
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart

async def send_assessment_report(
    recipient: str,
    subject: str,
    body_html: str,
    body_text: str,
    attachment: bytes = None,
    filename: str = None
) -> bool:
    """
    Send approved assessment report via Postmark SMTP.
    Called by Output Delivery Agent (Step 9a).
    """
    msg = EmailMessage()
    msg['From'] = os.getenv('SMTP_FROM', 'notifications@datadnaprivacy.com')
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype='html')

    if attachment and filename:
        msg.add_attachment(
            attachment,
            maintype='application',
            subtype='pdf',
            filename=filename
        )

    try:
        with smtplib.SMTP(
            os.getenv('SMTP_HOST', 'smtp.postmarkapp.com'),
            int(os.getenv('SMTP_PORT', '587'))
        ) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(
                os.getenv('SMTP_USER', 'server-api-token'),
                os.getenv('SMTP_PASS')
            )
            server.send_message(msg)
        return True
    except smtplib.SMTPException as e:
        # Log and raise — pipeline should not silently fail
        raise RuntimeError(f"SMTP send failed: {e}")
```

---

## Blocked Work

| Work Item | Status |
|-----------|--------|
| Output Delivery Agent email client (code) | ✅ Unblocked — can implement now |
| Postmark account setup + DNS verification | ⏳ Blocked — 24–48hr DNS propagation |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Domain sending reputation before first use | Postmark warms shared IPs automatically |
| DNS propagation delay blocking go-live | Use Postmark's test mode until verified |
