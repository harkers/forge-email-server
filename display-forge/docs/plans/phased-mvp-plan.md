# Display Forge — Phased MVP Build Plan

## Deployment Assumption

Display Forge runs as a containerised application hosted inside Proxmox. HDMI output is passed through to the physical display path, driving a 55-inch TV in landscape mode.

## Runtime Model

### Proxmox host
- hosts the workload
- manages lifecycle and restart behaviour
- passes display capability through

### Display Forge stack
- admin UI
- content/API ingestion
- RSS polling service
- scheduling and rules engine
- rendering service
- playback controller
- local asset cache
- database

## Phase 1 — Foundations and Core Playback

Goal: stable single-screen signage engine.

Scope:
- deploy in container(s)
- establish HDMI display path
- auto-launch full-screen signage view
- support uploaded static image campaigns
- add basic timing fields
- loop active content
- cache assets locally
- restart cleanly after reboot
- provide minimal admin UI

## Phase 2 — RSS Ingestion and Automated Intake

Goal: dynamic feed-driven campaigns.

Scope:
- RSS registration UI
- polling
- parse title/summary/date/media/categories
- map to templates
- deduplicate items
- default expiry rules
- feed-level rules and approval controls
- feed health reporting

## Phase 3 — Scheduling Engine and Smart Playlist Logic

Goal: intelligent self-managing rotation.

Scope:
- dynamic playlist generation
- priority-based rotation
- time-of-day windows
- day-of-week rules
- recurring campaigns
- category balancing
- fallback content
- emergency override

## Phase 4 — Operational Hardening and Device Stability

Goal: robust unattended operation.

Scope:
- watchdog and health checks
- player heartbeat monitoring
- automatic browser/player restart
- alerts for feed/screen/storage issues
- asset preloading
- offline-safe playback mode
- logs and diagnostics

## Phase 5 — Extended Intake and Control Surface

Goal: support broader campaign flows.

Scope:
- JSON/API intake
- webhooks
- shared-folder watch
- Google Sheet import (optional)
- QR code support
- richer templates
- video support
- roles and approvals
- archive/search library

## Phase 6 — Multi-Screen Estate Management

Goal: scale from one TV to many.

Scope:
- multiple screens
- screen groups
- location targeting
- different playlists per screen
- central monitoring
- proof-of-play logging
