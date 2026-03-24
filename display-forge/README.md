# Display Forge

A container-oriented digital signage platform scaffold for Proxmox-style deployment, built around an admin UI, API, worker, and player UI.

## Included

- architecture and planning docs
- repository/service layout
- docker-compose baseline
- environment template
- MVP admin UI stub
- MVP player UI stub
- file-backed API stub with playlist endpoint

## Repository Structure

- `apps/admin-ui/` — admin frontend
- `apps/player-ui/` — signage/player frontend
- `services/api/` — backend API service
- `services/worker/` — RSS polling and background jobs
- `packages/shared/` — shared types/helpers
- `infra/docker/` — container/runtime definitions
- `infra/scripts/` — ops/startup scripts
- `config/` — config templates
- `storage/` — media/cache/logs/backups
- `tests/` — test suites

## Runtime Baseline

- `docker-compose.yml` — local/proxmox container baseline
- `.env.example` — environment template
- `docs/architecture/service-map.md` — service responsibilities and flow

## Current MVP Skeleton

### API

Endpoints:
- `GET /api/health`
- `GET /api/dashboard/summary`
- `GET /api/campaigns`
- `POST /api/campaigns`
- `PUT /api/campaigns/{id}`
- `DELETE /api/campaigns/{id}`
- `GET /api/screens/default/playlist`

Persistence:
- JSON file store in `services/api/app/storage/campaigns.json`

Scheduling:
- `status`
- `activeFrom`
- `activeUntil`
- playlist returns only currently eligible campaigns

### Admin UI

Features:
- summary cards
- health panel
- create campaign form
- edit campaign from library
- delete campaign from library
- campaign library
- active playlist preview

### Player UI

Features:
- full-screen playlist playback view
- cycles active campaigns by duration
- refreshes playlist periodically

## Local Run

### 1. Run the API

```bash
cd services/api
python3 app/main.py
```

### 2. Serve the admin UI

```bash
cd apps/admin-ui
python3 -m http.server 3000
```

### 3. Serve the player UI

```bash
cd apps/player-ui
python3 -m http.server 3001
```

Then open:
- Admin UI: <http://localhost:3000>
- Player UI: <http://localhost:3001>
- API health: <http://localhost:8000/api/health>

## Docker Baseline

Copy env template first:

```bash
cp .env.example .env
```

Then start:

```bash
docker compose up --build
```

## Added Specification Docs

- `docs/specs/product-requirements.md`
- `docs/architecture/technical-spec.md`
- `docs/architecture/service-map.md`
- `docs/plans/phased-mvp-plan.md`
- `docs/plans/openclaw-execution-pack.md`
