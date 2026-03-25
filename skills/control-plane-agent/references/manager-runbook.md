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

## Evidence examples

### Build/fix evidence
Valid evidence:
- `git log --oneline -5` showing commits in expected scope
- `git diff main --stat` showing changed files
- `npm run test` or equivalent passing with output
- `npm run build` or equivalent succeeding
- file paths confirmed to exist: `ls -la src/components/NewComponent.tsx`

Invalid evidence:
- "done" or "fixed" without specifics
- commit hash only without showing what changed
- test command that doesn't exist in repo
- claiming files exist without listing them

### Deployment evidence
Valid evidence:
- `curl -s http://localhost:4173/health` returning expected response
- `docker ps` showing container running
- screenshot or endpoint response confirming service is live
- rollback procedure documented before deployment

Invalid evidence:
- "deployed" without verification
- container started without health check
- no rollback plan for production

### Research/advisory evidence
Valid evidence:
- citations with source URLs
- quotes from original documents
- explicit "unknown" sections for gaps
- confidence level stated

Invalid evidence:
- findings without sources
- hiding uncertainty in polished language
- claiming expertise without evidence

## Failure handling

### When verification fails
1. **First pass:** Ask worker to tighten evidence
   - Request specific proof
   - Ask for missing files/commands/outputs
2. **Second pass:** If still ambiguous, escalate to manager
3. **Manager decision:**
   - Reject with clear defects
   - Reroute to different specialist
   - Accept with documented uncertainty
   - Escalate to human

### How many tightening passes?
- Maximum 2 passes before escalation
- If evidence is ambiguous after 2 passes, the task is not well-defined enough
- Escalate to human or decompose further

### Reject vs reroute
- **Reject:** Worker did the wrong thing or quality is insufficient
- **Reroute:** Worker is wrong role for the task (e.g., sent coding-worker for research task)
- **Escalate:** Manager cannot resolve ambiguity, needs human decision

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

## Companion documents

- **agent-catalog.md** — role definitions, ownership boundaries, workflow patterns
- **model-routing-matrix.md** — model assignments, escalation paths, cost guidance
- **openclaw-execution-playbook.md** — how to spawn/steer sessions in OpenClaw

Use the catalog for "what roles exist" and "what each owns".
Use the routing matrix for "which model for which role".
Use this runbook for "how to route work to agents".

## OpenClaw execution note

Use `openclaw-execution-playbook.md` with this runbook when actually spawning or steering worker sessions.
