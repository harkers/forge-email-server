# Work Packet: privacy-intake-001

## Identity
- **WORK ID:** privacy-intake-001
- **TASK TYPE:** build
- **CREATED:** 2026-03-25T13:58:00+00:00
- **STATUS:** accepted

## Goal
Deploy Privacy Intake application on titan following the recommended build order, starting with local postgres and app deployment.

## Context
Privacy intake is a Postgres-first, audit-focused FastAPI application for handling privacy intake requests. It's designed to run on titan (192.168.10.80 LAN / 100.117.50.105 Tailscale) with Cloudflare Tunnel + Access authentication.

**Workspace:** `/home/stu/.openclaw/workspace/privacy-intake-pack/`

**Key constraints:**
- Leave existing nginx/lighttpd/WordPress stack untouched
- No new public inbound ports
- Internal Docker network only
- Cloudflare Access for authentication (later phase)

**Recommended build order:**
1. Deploy postgres and app locally only ← **START HERE**
2. Validate schema and event creation
3. Validate worker commentary flow
4. Add Cloudflare Tunnel
5. Add Cloudflare Access policy
6. Add access audit for authenticated identity headers
7. Integrate real privacy skill handoff
8. Add exports and attachment handling
9. Add dashboards and search
10. Add backup verification and restore test

## Current Phase: 1 (Deploy postgres and app locally)

### Allowed Scope
- `/home/stu/.openclaw/workspace/privacy-intake-pack/`
- Docker Compose configuration
- PostgreSQL container and app container
- Local network binding only (no external exposure)

### Forbidden Scope
- Modifying anything outside the privacy-intake-pack directory
- Opening firewall ports
- Modifying nginx/lighttpd/WordPress configuration
- Production Cloudflare configuration

### Required Outputs
1. Working `docker-compose.yml` configured for local deployment
2. `.env` file with development-appropriate secrets (not production)
3. PostgreSQL container running and healthy
4. FastAPI app container running and healthy
5. Verification that schema is initialized correctly

### Required Validation Evidence
- `docker ps` showing both containers running
- `docker compose logs` showing successful startup
- `curl` or similar to internal app endpoint confirming it responds
- Database connection verified (app can connect to postgres)

### Stop Conditions
- If postgres fails to start, stop and report
- If app fails to connect to postgres, stop and report
- If any external network access is required, stop and ask for clarification
- If secrets/production credentials are needed, stop and ask

### Success Criteria
- Both containers healthy on internal Docker network
- App responds to local requests
- No external ports exposed
- Schema initialization confirmed

## Handoff Packet Required
Worker must return:
- Summary of what was done
- Scope touched (files, services)
- Artifacts produced
- Validation performed with output
- Open risks or blockers
- Recommended next action

## Routing
- **First owner:** coding-worker-agent
- **Expected handoff:** deployment verification → security-reviewer (for Cloudflare phase) → manager acceptance