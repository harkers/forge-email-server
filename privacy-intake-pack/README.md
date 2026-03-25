# Privacy Intake Pack for titan

This pack is a Postgres-first, audit-focused implementation blueprint for a self-hosted privacy intake system on `titan`.

## Design intent

- Keep the intake system separate from the existing WordPress stack.
- Do not expose a new public origin or database port.
- Publish the app only through Cloudflare Tunnel protected by Cloudflare Access.
- Use PostgreSQL as the system of record.
- Treat task commentary and workflow activity as append-only events for auditability.

## What is included

- Docker Compose stack
- FastAPI application skeleton
- PostgreSQL schema and indexes
- Cloudflare Tunnel configuration template
- Environment file template
- Installation guide
- Security hardening notes
- Backup script
- Systemd unit example for host-managed cloudflared
- Event model and workflow notes

## Intended host fit

This pack is tailored to the documented titan architecture:

- Debian 12
- existing nginx/lighttpd/WordPress stack remains untouched
- existing exposed ports remain unchanged
- new intake service runs on an internal Docker network
- no new inbound firewall openings required for the intake app

## Suggested hostname

`privacy-intake.example.com`

Replace with your actual Cloudflare-managed hostname.

## Suggested deployment pattern

Cloudflare Access
-> Cloudflare Tunnel
-> privacy-intake-app container
-> postgres container
-> worker container

## Important

This pack is a build-ready blueprint, not a live deployment. Review all secrets, DNS names, Access policies, and storage paths before running it on titan.
