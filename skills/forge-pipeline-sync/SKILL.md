---
name: forge-pipeline-sync
description: Keep Forge Pipeline updated when workspaces, projects, plans, architecture packs, specs, reviews, roadmaps, or significant implementation changes are created or updated. Use when spinning up a new workspace, adding a new Forge product/project, changing project status, creating planning/spec documentation, or when the user asks to record progress in Forge Pipeline. Also use to document the standard process so every workspace knows that meaningful changes must be reflected back into Forge Pipeline.
---

# Forge Pipeline Sync

Treat Forge Pipeline as the central portfolio and project visibility layer for Forge work.

## Core rule
When a workspace is created or meaningful work happens, update Forge Pipeline.

Meaningful work includes:
- new workspace created
- new product or project identified
- architecture/spec/review/roadmap/backlog document created
- significant feature shipped
- deployment state changed
- project role or strategy clarified
- important risks or blockers discovered
- implementation phase or milestone changed

## What to update in Forge Pipeline
Update the relevant project entry with:
- project name
- description
- status
- notes summarising what changed
- relevant tags
- updated timestamp
- starter or follow-up tasks when useful

If the project does not exist yet, add it.

## Standard workflow
1. Identify whether the work belongs to an existing Forge Pipeline project.
2. If yes, update that project’s notes/status/tasks.
3. If no, create a new project entry.
4. Record the most important documents created (architecture pack, spec, roadmap, backlog, review, implementation skeleton, deployment notes).
5. Add at least one useful next-step task if the work opens a clear next move.

## Notes style
Notes should be concise but operationally useful.
Capture:
- where the workspace/project lives
- what it is
- what was created or changed
- what decisions were made
- what remains next

## Workspace rule to copy into local docs
Every new Forge workspace should include a local instruction that meaningful changes and updates must be processed into Forge Pipeline.

Recommended wording:

"Forge Pipeline is the central portfolio/project layer. When significant changes happen in this workspace — new docs, architecture changes, roadmap updates, deployment changes, important decisions, or new implementation milestones — update the relevant Forge Pipeline project entry so portfolio visibility stays current."

## Implementation guidance
When creating a new workspace:
- add the local rule to `AGENTS.md`, `TOOLS.md`, or another clearly visible local doc
- add/update the corresponding Forge Pipeline entry immediately

When updating an existing workspace:
- reflect major milestones, product-definition docs, architecture decisions, and status changes into Forge Pipeline

## References
Read `references/process.md` for the exact update policy and workspace propagation rule.
