# PARA.md - Durable Knowledge Conventions

Durable knowledge lives in a structured layer separate from chat residue and bootstrap rules.

## Purpose

Use PARA to store long-lived, structured knowledge that should survive session compaction and day-to-day noise.

This is **not** the same as:

- `memory/YYYY-MM-DD.md` — daily chronology, residue, working notes
- `MEMORY.md` — curated long-term memory / routing layer
- `AGENTS.md` — operating rules and behavioral guidance
- Forge Pipeline — active project/task tracking and prioritisation

PARA is for the durable stuff behind the work.

## Root

Default durable knowledge root:

`~/life`

If that path changes later, update this file rather than scattering the convention elsewhere.

## Structure

### `projects/`
Things with a clear outcome or endpoint.

Examples:
- product concept packs
- delivery notes for active builds
- decision logs for a specific initiative
- implementation context that outlives a chat session

### `areas/`
Ongoing responsibilities with no fixed finish line.

Examples:
- operations
- health/admin
- finance
- home
- infrastructure
- assistant governance

### `resources/`
Reference material worth keeping.

Examples:
- research notes
- vendor comparisons
- product references
- legal/process references
- architecture notes
- reusable templates

### `archives/`
Inactive or superseded material that should remain recoverable.

Examples:
- completed projects
- outdated plans
- replaced reference docs
- retired operating ideas

## File conventions

Within a PARA folder, prefer:

- `summary.md` for the cheap human-readable overview
- `items.json` for atomic facts, records, or machine-friendly detail

Use lighter structures when that’s enough; don’t create ceremony just to satisfy the framework.

## Rules

- Store **durable facts** here, not transient conversation residue.
- Keep entries **atomic and updateable**.
- **Supersede outdated facts** instead of silently deleting history.
- Prefer **clear summaries first**, then deeper detail.
- Do **not** store secrets here.
- Avoid duplicating what Forge Pipeline already tracks well.
- If something is only useful for the current day or current thread, it probably belongs in `memory/YYYY-MM-DD.md`, not PARA.

## Relationship to current workspace

Use this rough split:

- **Forge Pipeline** → what needs doing / current project status
- **`memory/YYYY-MM-DD.md`** → chronological log, residue, temporary notes
- **`MEMORY.md`** → curated long-term memory and important carry-forward context
- **PARA (`~/life`)** → structured durable knowledge base
- **`AGENTS.md`** → rules, boundaries, and operating behavior

## Adoption guidance

Start small.

Create PARA content only when something clearly wants durable structure, for example:
- a project accumulating stable context
- an ongoing area needing maintained facts
- a reference collection worth keeping tidy
- material that shouldn’t be lost in chat history or daily notes

Don’t force everything into PARA. Use it where structure actually helps.
