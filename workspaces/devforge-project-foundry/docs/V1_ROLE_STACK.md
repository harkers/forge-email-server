# DevForge: Project Foundry
## V1 AI Role Stack

Status: Planning  
Date: 2026-03-28

## Purpose

Define which existing OpenClaw skills should be adopted first for the Project Foundry AI operating model, and which new specialist domains should exist as placeholders until purpose-built skills are developed.

## V1 Reuse-First Stack

### Adopt existing skills directly for MVP

| AI Operating Need | Recommended Existing Skill |
|---|---|
| orchestration authority | `control-plane-agent` |
| manager / routing authority | `manager-agent` |
| planning and decomposition | `planner-agent` |
| workspace governance | `workspace-governor-agent` |
| architecture critique | `architecture-reviewer-agent` |
| structured documentation | `documentation-writer-agent` |
| polished drafting | `drafting-agent` |
| read-only correctness review | `reviewer-agent` |
| security review | `security-reviewer-agent` |
| external standards / source research | `researcher-agent` |
| diagnosis and blockers | `investigator-agent` |
| post-task reflection | `self-reflection` |
| learning capture | `self-improvement` |

## Placeholder Specialist Domains To Build Separately

These should exist now as named placeholders, but their dedicated skills can be built separately later.

| Planned Custom Domain | Why it still needs dedicated skill logic |
|---|---|
| Privacy specialist | privacy-by-design, governance, review, DLP framing, and privacy-specific lifecycle logic are not fully covered by current skills |
| ForgeComms specialist | comms distillation, audience shaping, handoff packaging, and lifecycle-specific output rules need a dedicated layer |
| ForgeTraining specialist | input engine, impact analysis, persona tailoring, and readiness pack generation need purpose-built logic |
| ForgeRisk specialist | live risk cycle, evaluation, mitigation history, and re-entry triggers need dedicated operational patterns |

## Operating Principle

Project Foundry should start by reusing strong existing OpenClaw skills for the AI operating layer, then add new specialist domains only where the current skill base is clearly incomplete.
