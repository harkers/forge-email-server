# DevForge: Project Foundry
## Review Pack

Status: Planning  
Date: 2026-03-28

## What this is

This review pack is the fast-entry document for human review of DevForge: Project Foundry.

Project Foundry is the master OpenClaw workspace and future GitHub template repository for creating governed project environments. It is designed as a governed AI operating model with a small human governance layer supervising a specialist AI operating stack.

## What problem it solves

Projects too often start as empty repositories, improvised notes, or loosely governed boards. That creates weak traceability, inconsistent structure, late privacy and security thinking, poor handoffs, weak stakeholder communication, and rushed training.

Project Foundry is intended to replace that with a reusable project foundation covering:
- strategy
- architecture
- governance
- documentation
- orchestration
- planning
- execution
- review
- release
- communications
- training
- risk
- closure

## Core design choices

- planning-first before implementation
- future repo name: `devforge-project-foundry`
- internal execution domains use `forge-*` naming
- ForgeComms, ForgeTraining, and ForgeRisk are first-class domains
- privacy is a dedicated specialist function
- the operating model is AI-first, but human-governed

## Operating model

### Human governance layer
The human layer exists for approval, accountability, and exception handling.

### AI operating layer
The AI layer contains specialist roles for planning, architecture, governance support, privacy analysis, risk analysis, orchestration, pipeline control, communications, training, review, and release support.

## Current state

Completed:
- planning workspace created
- planning pack drafted and indexed
- forge domain placeholders created
- role and skill mapping drafted
- approval pack drafted
- Forge Pipeline project entry cleaned and updated

Not started:
- repository bootstrap
- Sprint 0 execution
- implementation of custom specialist skills
- template repo creation

## Approval focus

Before moving into repository bootstrap, review should confirm:
- problem and purpose are sound
- governance model is acceptable
- AI operating model is understood
- privacy remains explicit
- approval gates are acceptable
- repo bootstrap planning is sufficient

## Recommended reading order

1. `EXEC_SUMMARY.md`
2. `PROJECT_BRIEF.md`
3. `CHARTER.md`
4. `PHASED_PLAN.md`
5. `LIFECYCLE_MODEL.md`
6. `TEAM_ROLES.md`
7. `CONTROLS.md`
8. `GATES.md`
9. `REPO_TREE_DRAFT.md`
10. `INDEX.md`

## Review questions

- Does the problem statement match reality?
- Is the AI operating model clear enough to govern?
- Is the human governance layer sufficient?
- Are ForgeComms, ForgeTraining, and ForgeRisk correctly treated as first-class domains?
- Is the planning pack sufficient to justify eventual Sprint 0 bootstrap?
- Are there any missing gates, controls, or structural domains?

## Immediate next step after review

If the review is positive, confirm the governance layer and move toward G-0 through G-4 approval readiness.
