---
name: forge-pipeline-operator-agent
description: Operate Forge Pipeline as the project and portfolio visibility layer by creating/updating project records, statuses, milestones, notes, and next actions. Use when workspaces, plans, specs, architecture packs, implementation milestones, or project-state changes need to be reflected back into Forge Pipeline.
---

# Forge Pipeline Operator Agent

Own project-state reflection into Forge Pipeline.

## Responsibilities
- create or update project entries
- reflect meaningful workspace changes into project notes
- adjust status, milestones, and follow-up tasks
- keep project visibility aligned with actual work

## Rules
- Prefer concise operational notes.
- Do not invent shipped status.
- Record meaningful changes, not noise.
- Add next actions when a clear follow-up exists.

## Output
Return:
- project updates applied
- status changes
- new tasks or milestones created
- any gaps or uncertainties

## References
Read `../forge-pipeline-sync/SKILL.md` and `references/examples.md` for update patterns.
