# Privacy - DSAR Processing

Workspace for data subject access request (DSAR) handling.

## Structure

- `inbox/` — raw incoming requests and source material
- `requests/` — one folder per DSAR case
- `templates/` — reusable response/request templates
- `notes/` — process notes, guidance, checklists
- `exports/` — generated bundles and redacted outputs
- `logs/` — audit trail and handling notes
- `scripts/` — helper scripts for repeatable processing

## Suggested case folder layout

Create folders like:

- `requests/2026-001-jane-doe/`
- `requests/2026-002-acme-employee/`

Inside each case folder:

- `request.md`
- `identity-check.md`
- `scope.md`
- `search-log.md`
- `review-notes.md`
- `response.md`
- `attachments/`

## Core principles

- Keep an audit trail.
- Preserve originals.
- Redact third-party data where needed.
- Track deadlines clearly.
- Separate raw inputs from reviewed outputs.
