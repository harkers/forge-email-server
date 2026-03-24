# Display Forge — Technical Specification

## Product Definition

Display Forge is a self-managing digital signage platform designed to run inside a containerised Proxmox environment and drive a 55-inch TV over HDMI. It supports advert and announcement playback, RSS-driven content intake, manual campaign creation, scheduled activation and expiry, automated playlist generation, and resilient unattended playback.

## Core Architecture

Display Forge should be built as two logical layers:

### Control Plane

Responsible for:

- admin UI
- campaign management
- feed management
- content normalization
- schedule/rules engine
- playlist generation
- health monitoring
- audit logging

### Display Plane

Responsible for:

- full-screen playback
- local caching of active assets
- kiosk browser rendering
- recovery after restart/crash
- heartbeat and playback state reporting

## Deployment Architecture

Target environment:

- Proxmox host
- containerised application stack
- HDMI output passed through to physical display path
- 55-inch TV in landscape orientation

Recommended deployment model:

- Docker-based app stack inside VM or LXC
- browser-based signage renderer launched in kiosk mode
- persistent volumes for media, database, config, logs, and cache

Preferred early structure:

- control container
- display runtime container
- PostgreSQL container

Optional later:

- Redis
- Nginx reverse proxy
- object storage

## Functional Modules

1. Campaign management
2. Media asset handling
3. RSS intake
4. Content normalization
5. Scheduling and rules engine
6. Playlist engine
7. Rendering/template engine
8. Player runtime
9. Health/monitoring
10. Audit/logging

## Database Schema

Core tables:

- campaigns
- media_assets
- feeds
- feed_items
- campaign_schedules
- screens
- screen_profiles
- playlist_snapshots
- system_events
- users
- audit_logs

## API Surface

Suggested endpoints:

### Auth
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Campaigns
- `GET /api/campaigns`
- `POST /api/campaigns`
- `GET /api/campaigns/{id}`
- `PUT /api/campaigns/{id}`
- `DELETE /api/campaigns/{id}`
- `POST /api/campaigns/{id}/activate`
- `POST /api/campaigns/{id}/deactivate`
- `POST /api/campaigns/{id}/preview`

### Media
- `POST /api/media/upload`
- `GET /api/media`
- `GET /api/media/{id}`
- `DELETE /api/media/{id}`

### Feeds
- `GET /api/feeds`
- `POST /api/feeds`
- `PUT /api/feeds/{id}`
- `DELETE /api/feeds/{id}`
- `POST /api/feeds/{id}/poll`
- `GET /api/feeds/{id}/items`

### Schedules
- `GET /api/campaigns/{id}/schedule`
- `PUT /api/campaigns/{id}/schedule`

### Playlist
- `GET /api/screens/{id}/playlist`
- `POST /api/screens/{id}/refresh`
- `GET /api/screens/{id}/preview`

### Player / Health
- `POST /api/player/heartbeat`
- `POST /api/player/status`
- `GET /api/health`
- `GET /api/events`

## Display Runtime Behaviour

The player should:

- auto-launch on boot
- open signage URL in kiosk mode
- fetch current playlist snapshot
- cache referenced media locally
- continue playback from cache if API unavailable
- re-fetch playlist periodically
- report heartbeat at intervals
- reload signage view if browser crash is detected
- suppress pointer and OS chrome

## MVP Stack Recommendation

- Backend: FastAPI or Node.js
- Frontend/Admin: React
- Database: PostgreSQL
- Worker: language matched to backend
- Player: Chromium in kiosk mode
- Orchestration: Docker Compose inside Proxmox

## Proxmox-Specific Notes

- treat graphics/output path as part of infrastructure acceptance criteria
- keep playback runtime lightweight
- ensure display session launches unattended after boot
- use persistent mounts for media/logs/db backup
- make display route work locally even if admin access fails
