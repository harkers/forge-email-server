# Cloudflare Setup Notes

## Tunnel
Create a Cloudflare Tunnel for the intake hostname.

Recommended hostname:
- `privacy-intake.example.com`

Origin target:
- `http://app:8000` if cloudflared runs in the same Docker network
- `http://127.0.0.1:18080` if cloudflared runs on the host and the app is bound to localhost

## Access
Create a self-hosted application in Cloudflare Access for the hostname.

Recommended initial policy:
- action: allow
- include: your email address only
- session duration: short
- no bypass policy

## Later options
- service tokens for automation
- device posture checks if you want them
- browser isolation if ever needed for sensitive access

## Notes
The app itself should still do normal validation and audit logging. Edge auth is not a substitute for application correctness.
