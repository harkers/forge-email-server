# Forge Pipeline Sync Process

## Policy
Forge Pipeline is the central portfolio, planning, and visibility layer for Forge work.

That means meaningful changes in any Forge workspace should be propagated back into Forge Pipeline.

## What counts as meaningful
- Workspace creation
- Project identity clarified
- Architecture/spec/review created
- Roadmap/backlog created
- Implementation skeleton created
- Deployment status changed
- Integration pattern clarified
- New strategic decision made
- Major milestone completed
- Risk/blocker identified

## Minimum update expectations
For each meaningful change, update the matching Forge Pipeline project with:
- updated notes
- updated timestamp
- status if changed
- one or more next tasks if appropriate

## New workspace propagation rule
This rule should be copied into every new Forge workspace in a visible local file.

Recommended text:

Forge Pipeline is the central portfolio/project layer. When significant changes happen in this workspace — new docs, architecture changes, roadmap updates, deployment changes, important decisions, or new implementation milestones — update the relevant Forge Pipeline project entry so portfolio visibility stays current.

## Good note pattern
Capture:
- location: where the project/workspace lives
- type: what the project is
- changes: what was created or decided
- status: current project state
- next move: likely next action

## Example update
"Created ARCHITECTURE_SPEC.md defining the service as a premium deck-generation engine using HTML/CSS -> Playwright -> PPTX. Clarified product boundary vs PowerPoint MCP and added implementation backlog."

## Default expectation
Do not wait for the user to separately remind you if the workspace/project work clearly affects portfolio visibility. Update Forge Pipeline as part of completing the work, unless the user says not to.
