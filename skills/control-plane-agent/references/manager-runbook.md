# Manager Runbook

Use this runbook to map incoming work to the agent estate.

## Purpose

Help the manager/control-plane role answer four questions quickly:
1. What kind of work is this?
2. Which agent should own the first pass?
3. What evidence is needed before acceptance?
4. What is the likely next handoff?

## Quick routing table

| Work pattern | First owner | Typical next owner | Acceptance gate |
|---|---|---|---|
| multi-step build | planner or coding-worker | reviewer / architecture-reviewer / security-reviewer | repo truth + relevant validation |
| bug or failure diagnosis | investigator | coding-worker / deployment-diagnosis-agent | evidence-backed diagnosis |
| deployment issue | deployment-diagnosis-agent | deployer / reviewer | health-check or runtime proof |
| deployment execution | deployer | reviewer / manager | post-deploy verification |
| spec / architecture pack | planner / architecture-reviewer | documentation-writer / reviewer | coherent output + no invented state |
| portfolio/roadmap shaping | portfolio-planning-agent | forge-pipeline-operator-agent | plan grounded in real project state |
| workspace governance | workspace-governor-agent | forge-pipeline-operator-agent / manager | local rules updated coherently |
| Forge Pipeline update | forge-pipeline-operator-agent | manager | state reflected accurately |
| privacy incident | privacy-incident-agent | researcher / drafting / manager | clear chronology + open questions visible |
| vendor assessment | vendor-assessor-agent | researcher / drafting / manager | evidence-backed recommendation |
| ForgeWordPress suite coordination | forge-wordpress-suite-agent | coding-worker / architecture-reviewer / reviewer | suite boundaries preserved |
| external research | researcher-agent | drafting-agent / manager | findings tied to sources |
| polished final writing | drafting-agent | reviewer / manager | preserves meaning without inventing facts |

## Routing playbooks

### 1. Multi-step coding task
Use when:
- implementation is non-trivial
- there may be boundary or security risk
- the task is larger than a simple edit

Suggested flow:
1. manager classifies task as build/fix
2. if scope is unclear -> planner-agent
3. coding-worker-agent owns implementation
4. reviewer-agent checks correctness
5. architecture-reviewer-agent if boundary risk exists
6. security-reviewer-agent if trust/input/exposure risk exists
7. manager accepts or rejects

Minimum evidence before acceptance:
- files exist where claimed
- validation is relevant and actually runnable
- claims match repo state

### 2. Deployment problem
Use when:
- app deployed but is unhealthy, unreachable, or misconfigured

Suggested flow:
1. manager routes to deployment-diagnosis-agent
2. if fix is identified -> deployer-agent or coding-worker-agent depending on scope
3. manager verifies runtime state
4. reviewer if needed for config correctness

Minimum evidence before acceptance:
- diagnosis tied to logs/config/endpoints/runtime state
- service health or endpoint proof after fix

### 3. ForgeWordPress task
Use when:
- the task touches plugin boundaries, shared foundation, or suite coherence

Suggested flow:
1. manager routes first to forge-wordpress-suite-agent for suite-level framing when boundaries are at issue
2. coding-worker-agent owns one plugin or shared-layer scope
3. architecture-reviewer-agent checks coupling/contracts if needed
4. reviewer-agent checks implementation truthfulness
5. manager accepts or reroutes

Minimum evidence before acceptance:
- no hidden cross-plugin coupling
- shared-layer work stays infra-focused
- scope boundary preserved

### 4. Privacy or vendor advisory work
Suggested flow:
- privacy issue -> privacy-incident-agent
- vendor/tool review -> vendor-assessor-agent
- add researcher-agent when external evidence is needed
- add drafting-agent when polished deliverable is needed
- manager reviews before anything external-facing

Minimum evidence before acceptance:
- facts separated from assumptions
- unresolved questions visible
- recommendation confidence is honest

### 5. Portfolio / Forge ecosystem planning
Use when:
- multiple projects need structuring or reprioritisation
- a new workspace or product line appears

Suggested flow:
1. portfolio-planning-agent shapes grouping, sequencing, and priorities
2. workspace-governor-agent updates workspace rules if needed
3. forge-pipeline-operator-agent reflects the plan/status into Forge Pipeline
4. manager verifies that planning and tracking align

Minimum evidence before acceptance:
- project state reflects actual work
- roadmap distinctions between idea/planning/implementation are clear
- next actions are concrete

## Triage questions for the manager

Ask internally:
- Is this mostly implementation, diagnosis, research, planning, deployment, or drafting?
- What is the dominant risk: scope drift, runtime failure, security exposure, poor evidence, or weak communication?
- What is the smallest truthful first owner?
- What proof would convince me this step is actually done?

## Escalation cues

Escalate to human when:
- task requires strategic tradeoff
- production/destructive action is unclear
- multiple agent paths are equally plausible
- evidence remains ambiguous after one tightening pass

## Anti-patterns

Do not:
- send a coding task to three writers in the same directory
- accept “done” with only a commit hash
- let drafting hide uncertainty from research or incident work
- mark Forge Pipeline or roadmap status ahead of reality
- turn deployment diagnosis into speculative guesswork

## OpenClaw execution note

Use `openclaw-execution-playbook.md` with this runbook when actually spawning or steering worker sessions.
