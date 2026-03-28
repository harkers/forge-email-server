# DevForge: Project Foundry
## Skill-to-Role Mapping

Status: Planning  
Date: 2026-03-28

## Purpose

Map the current OpenClaw skill estate to the planned Project Foundry roles so the operating model can reuse existing specialist skills where they fit, instead of inventing unnecessary new role logic from scratch.

## Top-Level Fit

Project Foundry should prefer existing specialist skills where the responsibility already matches. New Project Foundry-specific role logic should only be created where the current skill database does not cover the need well enough.

## Role Mapping

| Project Foundry Role / Domain | Best Current Skill Match | Fit | Notes |
|---|---|---|---|
| Control / orchestration authority | `control-plane-agent` + `manager-agent` | Strong | Best fit for multi-agent routing, handoffs, verification gates, and bounded scope control |
| Planning / decomposition | `planner-agent` | Strong | Natural fit for phased plans, work units, sequencing, dependencies, stop conditions |
| Workspace governance | `workspace-governor-agent` | Strong | Good fit for workspace defaults, local rules, governance drift, and structure hygiene |
| Architecture review | `architecture-reviewer-agent` | Strong | Good fit for boundaries, ownership, layering, coupling, and sequencing critique |
| Structured documentation | `documentation-writer-agent` | Strong | Best fit for specs, packs, runbooks, lifecycle docs, review docs, and structured write-ups |
| Polished drafting / stakeholder-facing docs | `drafting-agent` | Strong | Good fit for executive summaries, handoff packs, briefings, and polished outputs from structured findings |
| Independent review | `reviewer-agent` | Strong | Good fit for read-only correctness review and accept / revise / reject guidance |
| Security review | `security-reviewer-agent` | Strong | Direct fit for trust boundaries, auth, secrets, input risk, exposure, unsafe automation |
| Research / external standards mapping | `researcher-agent` | Strong | Best fit for ISO/NIST lookup, external evidence gathering, standards and policy references |
| Investigation / diagnosis | `investigator-agent` | Strong | Good fit for diagnosing blockers, unclear failures, root causes, and uncertainty reduction |
| Post-task evaluation | `self-reflection` | Strong | Good fit after meaningful multi-step work to compare intent vs outcome |
| Learning capture / recurring improvement | `self-improvement` | Strong | Good fit for logging better patterns, corrections, tool failures, and reusable lessons |

## Partial or Adjacent Fits

| Project Foundry Role / Domain | Closest Current Skill | Fit | Notes |
|---|---|---|---|
| Privacy role / privacy design authority | `privacy-incident-agent` | Partial | Useful for privacy incident chronology and impact framing, but not a full privacy-by-design or privacy architecture role |
| ForgeComms domain | `drafting-agent` + `documentation-writer-agent` | Partial | Good base for polished summaries and structured outputs, but ForgeComms likely needs its own domain-specific directives |
| ForgeTraining domain | `drafting-agent` + `documentation-writer-agent` + `researcher-agent` | Partial | Existing skills help with writing and synthesis, but training logic, persona tailoring, and readiness pack generation need their own specific layer |
| ForgeRisk domain | `investigator-agent` + `reviewer-agent` + `documentation-writer-agent` | Partial | Existing skills can support analysis, review, and writing, but a dedicated live risk-cycle model still makes sense |
| Privacy review in delivery flow | `security-reviewer-agent` + `privacy-incident-agent` | Partial | Helpful, but still not enough to replace a dedicated privacy lead / privacy specialist role |

## Recommended Reuse Strategy

### Reuse directly
Use current skills directly for:
- planning
- orchestration
- workspace governance
- architecture review
- documentation
- drafting
- security review
- independent review
- research
- investigation
- reflection and learning capture

### Extend with Project Foundry directives
Use the current skills as the base layer, but add Project Foundry-specific directives for:
- ForgeComms
- ForgeTraining
- ForgeRisk
- privacy-specific governance and review patterns

### Create new dedicated role logic only where needed
The biggest likely gaps in the current skill estate are:
- privacy-by-design / privacy governance specialist
- ForgeTraining operational logic
- ForgeComms lifecycle distillation rules
- ForgeRisk structured risk-cycle handling

## Practical Mapping by Planned Domain

| Planned Domain | Suggested Skill Base |
|---|---|
| forge-flash-design | `planner-agent`, `researcher-agent`, `drafting-agent` |
| forge-architecture | `architecture-reviewer-agent`, `documentation-writer-agent`, `security-reviewer-agent` |
| forge-governance | `manager-agent`, `workspace-governor-agent`, `reviewer-agent` |
| forge-risk | `investigator-agent`, `reviewer-agent`, `documentation-writer-agent` |
| forge-document-engine | `documentation-writer-agent`, `drafting-agent` |
| forge-orchestrate | `control-plane-agent`, `manager-agent`, `workspace-governor-agent` |
| forge-pipeline | `manager-agent`, `planner-agent`, `reviewer-agent` |
| forge-whats-next | `planner-agent`, `manager-agent` |
| forge-control-plane | `control-plane-agent`, `manager-agent` |
| forge-review | `reviewer-agent`, `security-reviewer-agent`, `architecture-reviewer-agent` |
| forge-release | `reviewer-agent`, `documentation-writer-agent`, `security-reviewer-agent` |
| forge-comms | `drafting-agent`, `documentation-writer-agent` |
| forge-training | `documentation-writer-agent`, `drafting-agent`, `researcher-agent` |
| forge-close | `documentation-writer-agent`, `drafting-agent`, `reviewer-agent` |
| forge-fix | `investigator-agent`, `planner-agent`, `manager-agent` |

## Recommendation

Project Foundry should not start by inventing a whole new agent universe.

It should:
1. reuse the strong existing skills where fit is high
2. add Project Foundry-specific directives and templates on top
3. create truly new specialist role logic only where the current skill base is clearly incomplete

That gives you more precision with less reinvention.
