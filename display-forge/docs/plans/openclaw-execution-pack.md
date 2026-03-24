# Display Forge — OpenClaw Execution Pack

## Master Build Goal

Build Display Forge as a containerised Proxmox-hosted signage platform with HDMI-driven playback, campaign scheduling, RSS ingestion, and self-managing playlist logic.

## Agent Tracks

### Agent 1 — Architecture
Responsibilities:
- define service boundaries
- define repo structure
- define docker-compose layout
- define env vars
- define startup order

Outputs:
- architecture.md
- docker-compose.yml
- env.example
- service map

### Agent 2 — Backend
Responsibilities:
- build API
- define database models
- implement campaign/feed/schedule endpoints
- build playlist logic
- build health endpoints

### Agent 3 — Frontend/Admin
Responsibilities:
- build admin dashboard
- campaign library/editor
- feed manager
- health panel
- playlist preview

### Agent 4 — Player Runtime
Responsibilities:
- signage route
- rendering loop
- playback state management
- kiosk-mode assumptions
- cache-aware refresh logic

### Agent 5 — RSS/Normalization
Responsibilities:
- build feed poller
- parse RSS/Atom
- deduplicate entries
- normalize feed items
- create auto-campaign records

### Agent 6 — Ops/Hardening
Responsibilities:
- health checks
- watchdogs
- restart behaviour
- logging
- backup/export
- recovery playbooks

## Prompt Set

1. Design the full repository and service architecture for Display Forge, a Proxmox-hosted, containerised digital signage platform with admin UI, backend API, worker service, PostgreSQL, and kiosk-based signage player. Include service boundaries, data flow, env vars, and Docker Compose structure.

2. Build the backend schema and REST API for Display Forge. Include campaigns, media assets, feeds, feed items, schedules, screens, playlist snapshots, audit logs, and system events. Implement campaign CRUD, feed CRUD, and a playlist endpoint for a screen.

3. Implement a scheduling engine for Display Forge that evaluates campaign eligibility based on active_from, active_until, day-of-week, time-window, priority, recurrence, fallback flag, and override flag. Return explainable rule outcomes for debugging.

4. Build the RSS ingestion worker for Display Forge. It should poll registered feeds, parse items, deduplicate using source GUID/link, normalize data into campaigns, apply feed-level rules, set default expiry, and record failures without interrupting playback.

5. Build a React-based admin UI for Display Forge with dashboard, campaign editor, campaign list, feed manager, playlist preview, and system health panel.

6. Build the signage playback route for Display Forge. It should fetch a playlist snapshot, preload assets, rotate items by duration, recover from API failure using cached data, and operate cleanly in kiosk mode on a 55-inch landscape display.

7. Design operational hardening for Display Forge, including heartbeat reporting, feed failure alerts, browser/player recovery, disk usage monitoring, and service health endpoints suitable for unattended signage operation.

## Definition of Done

MVP is done when:

- a campaign can be uploaded through the admin UI
- the campaign can be scheduled with start/end times
- the screen displays active campaigns automatically
- expired campaigns disappear without manual action
- RSS items can be ingested into campaigns
- the playlist is generated dynamically based on rules
- the system survives reboot and resumes playback
- fallback content prevents blank screen states
- admin can see health and current playback state

## Immediate Build Order

1. architecture and repo skeleton
2. docker-compose and persistence volumes
3. PostgreSQL schema
4. campaign/media CRUD
5. playlist endpoint
6. signage route and kiosk playback
7. reboot/recovery path
8. RSS ingestion
9. smart scheduling
10. health monitoring
