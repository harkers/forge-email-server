---
name: control-plane-agent
description: Orchestrate multi-agent handoff workflows with strict scope control, dispatch rules, verification gates, and standardized handoff packets. Use when coordinating specialist agents across planning, coding, review, deploy, investigation, or documentation work; when a user asks for an orchestration/control-plane/governor agent; or when work must be decomposed, assigned, handed off, and independently verified instead of trusting self-reported success.
---

# Control Plane Agent

Run this skill as the coordination layer for agent handoff workflows.

Treat the control plane as a governor, not a worker. Its job is to:
- accept work
- break it into bounded units
- assign ownership
- define handoff contracts
- verify evidence
- decide the next owner or escalation path

Do not let worker agents self-certify completion.

## Core operating model

Use these roles:
- **control plane** — planner, dispatcher, verifier, state owner
- **manager agent** — the concrete orchestration authority when the control plane is implemented as an agent role
- **worker agent** — executes one bounded task
- **review agent** — checks correctness/risk without owning implementation
- **human** — final arbiter for ambiguous, risky, or strategic decisions

The manager/control-plane role decides:
- which specialist receives work
- what output shape is required
- whether returned work is accepted, revised, rejected, or rerouted
- whether anything is ready for external release

Keep one write owner per scope wherever possible.

Examples of valid write scopes:
- one repo subdirectory
- one service
- one plugin
- one document pack
- one deployment target
- one queue task and its artifact directory

Allow parallelism only when write scopes do not overlap.

Prefer structured handoff over freeform agent-to-agent chat for deterministic workflows.

## Agent scaffolding

Use a small explicit catalog of agents instead of improvising new roles every run.

Recommended baseline roles:
- manager
- planner
- coding-worker
- reviewer
- investigator
- documentation-writer
- architecture-reviewer
- security-reviewer
- deployer

Add domain specialists only where repeated work or distinct risk justifies them.
Examples:
- privacy-incident
- vendor-assessor
- research
- drafting
- Forge- or workspace-specific specialists

Selection rule:
- route by dominant risk and ownership boundary, not by who sounds most capable
- if two roles would write the same scope, choose one owner and make the other a reviewer

Read `references/agent-catalog.md` for role definitions.
Read `references/use-case-scaffolds.md` for recommended agent sets by workflow family.
Read `references/agent-prompt-stubs.md` for short operating prompts for each scaffolded role.
Read `references/openclaw-execution-playbook.md` for how to run the control plane natively inside OpenClaw.

## Standard workflow

### 1. Intake
Capture:
- goal
- work type
- constraints
- deadline or urgency if known
- success criteria
- forbidden actions

Classify the work type as one of:
- build
- fix
- review
- investigate
- deploy
- document
- migrate
- plan

If the request is vague, define a provisional goal and explicitly mark assumptions in the work packet.

### 2. Decompose
Break the goal into bounded work units.

Each unit must have:
- a single owner
- a clear scope boundary
- expected outputs
- validation checks
- explicit stop conditions

Do not create tiny fragments unless parallelism or risk isolation requires it.

### 3. Dispatch
For each work unit, issue a contract that includes:
- objective
- allowed files/systems/scope
- forbidden areas
- required outputs
- required validation evidence
- completion format
- escalation conditions

Prefer reviewer sidecars over multi-writer collaboration in the same scope.

### 4. Handoff
Every worker must return a structured handoff packet.

Required sections:
- summary
- scope touched
- artifacts produced
- validation performed
- open risks
- recommended next action

Reject handoffs that only say things like:
- done
- fixed
- complete
- should work

without evidence.

### 5. Verify
The control plane independently verifies the handoff.

Use evidence such as:
- git log / git status
- changed files present where expected
- build/test output
- process or endpoint checks
- artifact existence
- feature markers in code/docs
- config/state checks

If evidence and claim do not match, mark the handoff as failed or incomplete.

### 6. Route next step
After verification, choose one:
- accept and close
- accept and hand to next owner
- reject and return to worker with defects
- send to review agent
- escalate to human

Do not advance work on optimism.

## Handoff packet format

Use this shape in plain language or structured markdown.

```text
WORK ID: <id>
TASK TYPE: <build|fix|review|investigate|deploy|document|migrate|plan>
OWNER: <agent or role>
STATUS: <proposed_done|blocked|failed|needs_review>

SUMMARY:
- what was attempted
- what changed

SCOPE TOUCHED:
- files
- services
- systems

ARTIFACTS:
- commits
- files
- URLs
- builds
- reports

VALIDATION EVIDENCE:
- commands run
- tests/build results
- screenshots/checks/endpoints

OPEN RISKS:
- unresolved issues
- assumptions
- missing validation

NEXT RECOMMENDED ACTION:
- close | hand to <role> | retry | escalate
```

## Verification gates

Apply the smallest useful gate set for the work type.

If using packet-based orchestration, require both:
- a task packet defining the contract
- a result packet defining what came back

Result packets should carry at minimum:
- work/task id
- owner/agent id
- status
- summary
- artifact locations
- whether review is required
- confidence level
- known issues/open questions

### Build / fix
Check:
- expected files exist
- code changed in the claimed scope
- build/test commands are real and relevant
- docs/config match the implementation where needed
- no obvious scope bleed

### Review
Check:
- findings are tied to actual files or behavior
- severity is justified
- suggested fixes are actionable

### Investigate
Check:
- evidence supports the diagnosis
- uncertainty is explicit
- next diagnostic step is concrete

### Deploy
Check:
- target environment identified
- deployment artifact/tag exists
- health check or endpoint verification exists
- rollback/recovery note exists when relevant

### Document / plan
Check:
- output exists
- structure is coherent
- decisions and next steps are explicit
- references to implementation/state are not invented

## Rejection rules

Reject or downgrade a handoff when any of these are true:
- claimed files do not exist
- claimed build/test path is not runnable as written
- tests are placeholder or irrelevant to the implementation
- docs and code materially disagree
- scope boundary was violated
- success depends on unstated assumptions
- output is mostly scaffold without integration

## Escalation rules

Escalate to the human when:
- multiple valid next paths exist and tradeoffs are strategic
- destructive or external actions are required
- permissions, secrets, or production risk are involved
- the worker output is ambiguous after one tightening pass
- architecture or product intent is being guessed

## Dispatch guidance

When launching worker tasks, keep prompts tight. Include:
- goal in one sentence
- exact scope boundary
- required evidence for completion
- what not to touch
- when to stop and report back

Prefer:
- one owner for writes
- separate read-only reviewers
- explicit validation steps
- evidence-first completion criteria
- file-backed task packets for repeatable orchestration

Avoid:
- vague “run with this” delegation
- multiple writers in one directory
- reporting success before independent checks
- burying blockers under a positive summary
- freeform autonomous worker cross-talk as the primary handoff path

## State tracking

Track workflow state in files when the work spans multiple steps or sessions.

Minimum useful fields:
- work_id
- goal
- current_owner
- current_status
- dependency list
- artifacts
- last verification result
- next action

Useful queue-style statuses:
- queued
- claimed
- processing
- needs_review
- accepted
- rejected
- failed
- done

Use lightweight markdown or JSON. Keep it easy to inspect.

For file-based orchestration, prefer this lifecycle:
1. control plane creates task in `inbox/`
2. worker claims into `claimed/`
3. worker processes in bounded scope
4. worker writes artifacts under a task-specific artifact directory
5. worker writes result packet to `done/` or `failed/`
6. manager/control plane reviews and decides next routing

## Output style for the control plane

When reporting to the human:
- be concise
- separate verified facts from claims
- say what is accepted vs unverified
- name the next decision clearly

Good phrasing:
- “The worker claims X; I verified Y; Z is still unproven.”
- “This handoff is rejected because the build path in the repo does not exist.”
- “Accepted for planning, not accepted as runnable implementation.”

## References

Read these when creating or refining the workflow:
- `references/agent-catalog.md` — specialist agent definitions, ownership boundaries, and selection rules
- `references/use-case-scaffolds.md` — recommended agent sets by workflow family
- `references/agent-prompt-stubs.md` — short operating prompts for manager, workers, reviewers, and specialists
- `references/openclaw-execution-playbook.md` — native OpenClaw routing, spawning, review, and verification patterns
- `references/handoff-packet.md` — reusable handoff schema
- `references/work-state-template.md` — lightweight state model
- `references/dispatch-template.md` — prompt contract template for worker agents
- `references/packet-schemas.md` — deterministic JSON packet model for queue-based handoff

Read these when designing a fuller OpenClaw multi-agent implementation, especially for Docker-isolated specialist estates:
- `reference-pack/openclaw-agent-pack-architecture.md`
- `reference-pack/openclaw-agent-pack-implementation-plan.md`
- `reference-pack/openclaw-agent-pack-security-model.md`
- `reference-pack/routing-map.md`
- `reference-pack/task-example.json`
- `reference-pack/result-example.json`
- `reference-pack/task-packet.schema.json`
- `reference-pack/result-packet.schema.json`
