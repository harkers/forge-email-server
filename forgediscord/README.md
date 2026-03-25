# ForgeDiscord

ForgeDiscord is the Discord intake and coordination layer for the Forge ecosystem.

## Role
Discord is the interface and coordination surface.
OpenClaw is the execution/orchestration layer.

ForgeDiscord MVP is designed to:
- collect requests through slash commands and modals
- create a thread per request
- route requests to the correct workspace and workflow
- post status updates back into Discord
- handle approvals for sensitive work
- maintain an audit-friendly operational trail

## Current State
This workspace currently contains:
- design documentation
- architecture pack
- MVP technical spec
- server/channel map
- routing matrix
- build backlog
- implementation skeleton

## Top-Level Structure
- `src/bot/` — Discord runtime bootstrap
- `src/commands/` — slash command handlers
- `src/modals/` — intake modal schemas + handlers
- `src/router/` — routing logic + route evaluation
- `src/workflows/` — workflow entrypoints / orchestration definitions
- `src/adapters/` — OpenClaw and external system adapters
- `src/services/` — audit, job store, approvals, status posting
- `src/models/` — data shapes and state enums
- `src/config/` — config loading and route config
- `src/utils/` — shared helpers
- `config/` — environment and route config files
- `docs/` — implementation notes and operator docs
- `tests/` — unit and integration tests
- `data/` — local runtime state for MVP
- `scripts/` — helpers for setup/dev tasks

## MVP Build Sequence
1. Bot skeleton and slash command registration
2. Modal intake flows
3. Thread creation per request
4. Routing engine
5. OpenClaw orchestration adapter
6. Status updates
7. Approval flow
8. Audit logging

## Notes
- Keep trust boundaries explicit.
- Do not allow routes to inherit broad memory or tool access accidentally.
- Discord should coordinate work, not become the system of record.
