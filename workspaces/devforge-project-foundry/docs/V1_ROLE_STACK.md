# DevForge: Project Foundry
## V1 Role Stack

Status: Planning  
Date: 2026-03-28

## Purpose

Define which existing OpenClaw skills should be adopted first for Project Foundry MVP, and which new specialist domains should exist as placeholders until purpose-built skills are developed.

## V1 Reuse-First Stack

### Adopt existing skills directly for MVP

| Project Foundry Need | Recommended Existing Skill |
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

## Suggested MVP Operating Shape

### Base layer
Use existing skills for:
- planning
- orchestration
- governance support
- architecture review
- documentation
- drafting
- review
- security review
- research
- investigation

### Placeholder layer
Create planning placeholders for:
- ForgePrivacy
- ForgeComms
- ForgeTraining
- ForgeRisk

### Later custom build layer
Build dedicated skills for those placeholder domains once the planning model and MVP workflow are stable enough to justify specialization.

## Recommendation

Start Project Foundry MVP with a reuse-first operating stack and named placeholders for the high-value missing domains.

That gives you a practical path:
- enough capability to move forward now
- enough structure to avoid hand-wavy gaps
- no need to prematurely invent every specialist skill before the workflow is proven
