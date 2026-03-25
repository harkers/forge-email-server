# Architecture

## Source-of-truth alignment

This design respects the documented titan architecture and constraints:

- Leave the nginx -> lighttpd -> WordPress path unchanged.
- Do not duplicate security headers across nginx and lighttpd.
- Do not reuse existing MariaDB.
- Keep the new application path internal-only.
- Prefer minimal, surgical changes with low blast radius.

## High-level flow

1. You browse to `privacy-intake.example.com`
2. Cloudflare Access authenticates you
3. Cloudflare Tunnel forwards the request to the internal intake app
4. FastAPI validates and stores the case in PostgreSQL
5. FastAPI creates an initial task row and event rows
6. A worker processes queued tasks and appends commentary events
7. The UI shows the case timeline, task state, and full commentary feed

## Components

### privacy-intake-app
- FastAPI UI and API
- server-side validation
- case/task/event views
- internal-only service

### privacy-intake-db
- PostgreSQL
- system of record
- append-only event store for workflow traceability

### privacy-intake-worker
- background processor
- picks up queued tasks
- writes detailed events and commentary
- placeholder for OpenClaw/privacy skill integration

### cloudflared
- origin connector
- outbound-only connection to Cloudflare
- no public inbound app port required

## Security posture

- Cloudflare Access in front of the app
- no public exposure of postgres
- no direct coupling to WordPress
- least-privilege database user
- append-only task event trail
- upload and attachment controls can be added later

## Suggested internal network design

- dedicated Docker network: `privacy_intake_net`
- postgres only reachable on the internal Docker network
- app only reachable on the internal Docker network
- cloudflared joins the same network or runs on host and targets localhost

## Notes on reverse proxy strategy

This application intentionally does not ride through the existing nginx/lighttpd chain because:
- the current web stack has a distinct purpose
- header authority is already assigned to lighttpd
- this app is private and access-controlled at the edge by Cloudflare
- separation reduces the chance of breaking WordPress or fighting existing header/WAF behaviour
