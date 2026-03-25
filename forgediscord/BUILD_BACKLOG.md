# ForgeDiscord — Build Backlog v1.0

## Purpose

This backlog translates the architecture pack, MVP technical spec, channel map, and routing matrix into buildable work.

The emphasis is on shipping a real MVP, not inventing an empire of tickets so elegant that nothing ever gets built.

---

## Delivery Model

### Build stages
- **Stage 0** — Foundations and environment
- **Stage 1** — Bot skeleton and command registration
- **Stage 2** — Intake workflows and thread creation
- **Stage 3** — Routing and orchestration handoff
- **Stage 4** — Status updates, approvals, and outputs
- **Stage 5** — Audit logging and hardening
- **Stage 6** — Multi-server / trust-boundary expansion

### Priority scale
- **P0** = critical for MVP
- **P1** = strongly recommended for MVP / immediate next
- **P2** = post-MVP enhancement

---

# Stage 0 — Foundations and Environment

## FD-000 Create workspace implementation skeleton
**Priority:** P0  
**Outcome:** ForgeDiscord has a concrete implementation structure, not just design documents.

### Tasks
- create implementation directories
- define runtime layout
- create config structure
- create docs and env template

### Deliverables
- source tree
- config folder
- env example
- README

---

## FD-001 Decide bot deployment model for MVP
**Priority:** P0  
**Outcome:** MVP uses one internal/dev Discord server and one bot token.

### Tasks
- document server key
- document bot token scope
- document guild registration strategy
- document admin owners

### Deliverables
- deployment note
- bot/guild mapping

---

## FD-002 Define environment variables and secrets model
**Priority:** P0  
**Outcome:** Stable runtime config model.

### Required variables
- Discord bot token
- Discord application ID
- Discord guild ID(s)
- OpenClaw endpoint or routing adapter config
- audit/log store config
- approval timeout values

### Deliverables
- `.env.example`
- config reference

---

## FD-003 Define canonical IDs / naming conventions
**Priority:** P1  
**Outcome:** Consistent IDs for jobs, workflows, routes, and threads.

### Deliverables
- job ID scheme
- route key naming
- workflow ID naming
- thread naming rules

---

# Stage 1 — Bot Skeleton and Commands

## FD-010 Build Discord bot skeleton
**Priority:** P0  
**Outcome:** Bot connects to Discord reliably and can respond to basic health/test actions.

### Tasks
- initialise bot runtime
- connect to guild
- implement health logging
- verify permissions

### Deliverables
- running bot
- startup logging
- basic command support

---

## FD-011 Register MVP slash commands
**Priority:** P0

### Commands
- `/incident new`
- `/vendor assess`
- `/job create`
- `/job status`
- `/approve`
- `/reject`
- `/close`
- `/help`

### Deliverables
- command registration layer
- command dispatcher

---

## FD-012 Build help and usage response layer
**Priority:** P1

### Outcome
Users can discover how to use the system without needing psychic powers.

### Deliverables
- `/help` output
- command usage summaries
- channel guidance references

---

# Stage 2 — Intake Workflows and Threads

## FD-020 Build incident intake modal
**Priority:** P0

### Fields
- title
- summary
- date/time
- data type
- individuals count
- jurisdictions
- containment status
- recipients
- immediate actions

### Deliverables
- modal schema
- validation
- submit handler

---

## FD-021 Build vendor assessment modal
**Priority:** P0

### Fields
- vendor name
- processing purpose
- jurisdictions
- subprocessors
- transfer concerns
- review objective

### Deliverables
- modal schema
- validation
- submit handler

---

## FD-022 Build general project intake modal/prompt flow
**Priority:** P0

### Fields
- title
- summary
- preferred workspace
- priority
- due context
- links/references

### Deliverables
- modal or guided prompt flow
- validation
- submit handler

---

## FD-023 Implement thread creation per request
**Priority:** P0

### Outcome
Every successful intake creates a dedicated working thread.

### Deliverables
- thread name formatter
- thread creation logic
- thread reference persistence
- acknowledgement post

---

## FD-024 Implement initial request acknowledgement cards
**Priority:** P1

### Outcome
Each job gets a clean initial response showing:
- job ID
- workflow selected
- current status
- next step

---

# Stage 3 — Routing and Orchestration Handoff

## FD-030 Implement routing engine
**Priority:** P0

### Inputs
- guild/server
- channel
- command
- role
- request type
- optional classifier result

### Outputs
- workspace
- workflow
- agent
- reviewer role
- audit level
- output template

### Deliverables
- routing service/module
- route lookup config
- fallback handling

---

## FD-031 Encode MVP routes from routing matrix
**Priority:** P0

### Required routes
- incident intake
- vendor assessment intake
- project intake
- general catch-all fallback

### Deliverables
- route config file
- route tests

---

## FD-032 Build OpenClaw orchestration adapter
**Priority:** P0

### Outcome
ForgeDiscord can hand jobs off to the orchestration runtime cleanly.

### Responsibilities
- create backend job payload
- route to correct workspace
- initiate run
- receive progress callbacks or poll state

### Deliverables
- runtime adapter
- payload formatter
- error handling

---

## FD-033 Implement allowed-tools and memory-scope enforcement
**Priority:** P1

### Outcome
Routes carry explicit execution boundaries.

### Deliverables
- tools policy mapping
- memory scope mapping
- enforcement layer or validation checks

---

# Stage 4 — Status, Approvals, Outputs

## FD-040 Implement job lifecycle state model
**Priority:** P0

### Required states
- new
- validating
- routed
- in_progress
- awaiting_input
- awaiting_review
- approved
- completed
- archived

### Deliverables
- state enum/model
- state transition logic
- timestamps on every transition

---

## FD-041 Post status updates into threads
**Priority:** P0

### Outcome
Users see what is happening without chasing logs.

### Deliverables
- status message formatter
- thread posting logic
- update throttling / dedupe logic

---

## FD-042 Build reviewer approval flow
**Priority:** P0

### Actions
- approve
- reject
- request rework
- escalate

### Deliverables
- approval card/message format
- button or command handling
- reviewer permission checks
- state transition integration

---

## FD-043 Publish final summaries
**Priority:** P0

### Outcome
Final outputs are readable, concise, and linked to their thread/job.

### Deliverables
- final summary template
- output channel posting logic
- closure messaging

---

## FD-044 Archive / close completed threads
**Priority:** P1

### Outcome
Server stays clean.

### Deliverables
- close command behavior
- archive behavior
- final status marker

---

# Stage 5 — Audit Logging and Hardening

## FD-050 Implement job/audit store
**Priority:** P0

### Minimum stored records
- jobs
- audit events
- approval decisions
- Discord references

### Deliverables
- data schema
- persistence layer
- append-only event model where feasible

---

## FD-051 Post audit summaries to audit-log channel
**Priority:** P1

### Outcome
Human-readable audit visibility inside Discord.

### Deliverables
- audit event formatter
- channel posting logic

---

## FD-052 Implement routing failure and error handling
**Priority:** P0

### Cases
- bad command context
- validation failure
- routing ambiguity
- orchestration timeout
- backend unavailable
- permission failure

### Deliverables
- error states
- user-facing fallback messages
- alert emission

---

## FD-053 Add alerts channel integration
**Priority:** P1

### Outcome
Critical failures and blocked jobs get surfaced.

### Deliverables
- alert policy
- alerts formatter
- severity mapping

---

## FD-054 Add operator/admin runbook
**Priority:** P1

### Outcome
Humans know how to intervene when things wobble.

### Deliverables
- recovery procedures
- reroute guidance
- approval troubleshooting
- bot restart instructions

---

## FD-055 Security review for MVP deployment
**Priority:** P0

### Checks
- token handling
- channel permissions
- trust-boundary isolation
- sensitive-data guidance
- audit coverage
- route enforcement

### Deliverables
- review checklist
- signoff notes

---

# Stage 6 — Multi-Server Expansion

## FD-060 Add support for per-server trust-boundary config
**Priority:** P2

### Outcome
System can be cloned safely into client-specific environments.

---

## FD-061 Support dedicated bot/token per sensitive environment
**Priority:** P2

### Outcome
Cleaner separation for client deployments.

---

## FD-062 Add workspace isolation test suite
**Priority:** P2

### Outcome
Cross-boundary leakage risk is tested, not assumed away.

---

## FD-063 Add additional workflows
**Priority:** P2

Examples:
- publishing workflow
- ForgeHome intake
- ForgeCar intake
- knowledge/status query workflow

---

# MVP Milestone View

## Milestone M1 — Bot online
Includes:
- FD-000 to FD-012

## Milestone M2 — Intake working
Includes:
- FD-020 to FD-024

## Milestone M3 — Routed execution
Includes:
- FD-030 to FD-033

## Milestone M4 — Full request lifecycle
Includes:
- FD-040 to FD-044

## Milestone M5 — Audit + hardened MVP
Includes:
- FD-050 to FD-055

---

# Recommended Build Order

If building in the most practical order:

1. FD-000 workspace skeleton
2. FD-010 bot skeleton
3. FD-011 slash commands
4. FD-020 / FD-021 / FD-022 intake modals
5. FD-023 thread creation
6. FD-030 routing engine
7. FD-031 route config
8. FD-032 OpenClaw adapter
9. FD-040 lifecycle model
10. FD-041 status updates
11. FD-042 approvals
12. FD-043 final outputs
13. FD-050 audit store
14. FD-052 error handling
15. FD-055 security review

That gets you to a real MVP with minimal ceremonial nonsense.

---

# Suggested First Sprint

## Sprint 1
- FD-000
- FD-010
- FD-011
- FD-020
- FD-021
- FD-022
- FD-023

### Sprint 1 outcome
A user can start a workflow, submit intake, and get a working thread.

## Sprint 2
- FD-030
- FD-031
- FD-032
- FD-040
- FD-041

### Sprint 2 outcome
Requests route into the orchestrator and report status.

## Sprint 3
- FD-042
- FD-043
- FD-050
- FD-052
- FD-055

### Sprint 3 outcome
MVP is reviewable, auditable, and safe enough for controlled use.

---

# Final Recommendation

Treat this backlog as the build spine for ForgeDiscord.

Do not start by building every imagined channel and role permutation.
Build the narrow MVP:
- intake
- routing
- thread lifecycle
- approval
- audit

That is enough to make the system useful and real.
