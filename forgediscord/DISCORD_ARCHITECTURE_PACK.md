# ForgeDiscord — Intake and Coordination Layer Design Pack v1.0

## Purpose

This design defines ForgeDiscord as a Discord-based intake and coordination layer sitting in front of the wider Forge / OpenClaw agent and workflow environment.

Its role is not to do the deep work itself. Its role is to:
- collect requests from users
- classify and route them to the correct agent or workspace
- maintain job context and status
- report progress back into Discord
- present outputs, approvals, and next actions clearly
- preserve separation between trust boundaries

In simple terms:

**Discord is the front desk, dispatcher, and status board. The real work happens behind it.**

---

## Objectives

### Primary objectives
- Make it easy to submit structured or semi-structured requests
- Route requests to the right agent, workflow, and workspace automatically
- Keep all activity visible through status updates and threads
- Support approvals and human intervention where needed
- Enforce clear trust boundaries between clients, projects, and personal environments
- Provide an audit-friendly history of requests, actions, outputs, and decisions

### Secondary objectives
- Reduce friction for repeated operational work
- Standardise intake quality
- Prevent requests being lost in chat chaos
- Create a consistent operator experience across multiple domains
- Provide a path toward deeper orchestration later

---

## Non-Goals

This layer is not intended to be:
- the long-term system of record
- the primary data warehouse
- the place sensitive documents are permanently stored
- the intelligence engine itself
- a free-form shared memory space across clients

Discord should coordinate work, not become the entire estate with a broom cupboard full of secrets.

---

## Core Design Principles

### 4.1 Front-end, not core brain
Discord is the interface and coordination surface. The orchestration engine, agents, memory, and integrations sit behind it.

### 4.2 Strong trust separation
Requests must not bleed across clients, environments, or regulated contexts. Routing and permissions must enforce this.

### 4.3 Structured where it matters
Natural-language input is allowed, but important workflows should collect required fields through forms, buttons, or guided prompts.

### 4.4 Thread-per-request
Each intake becomes its own working thread to preserve clarity, context, and auditability.

### 4.5 Human review where needed
The system can recommend and draft, but sensitive actions should remain approval-gated unless explicitly designed otherwise.

### 4.6 Visible state
Users should always know whether a request is new, blocked, in progress, awaiting review, or complete.

---

## Recommended Operating Model

ForgeDiscord should start as:

**Intake and coordination layer**

Discord collects requests, routes them to the right agent/workspace, and reports progress back.

### Why this model first
- immediately useful
- easier to control than a full operations console
- easier to keep secure and auditable
- gives a clean path to grow into a fuller control room later

Recommended evolution:
1. **Stage 1:** intake and coordination layer
2. **Stage 2:** richer operational coordination and approvals
3. **Stage 3:** broader operations console / management surface

---

## Trust Boundary Model

This is the most important control in the design.

### Recommended model
Use **one Discord server per trust boundary or major context**.

Examples:
- ProPharma server
- HSBC server
- Projects server
- Personal / development / lab server

### Why this works
- cleaner data separation
- simpler permissions
- easier audit trail
- lower chance of cross-client leakage
- easier compliance explanation

### Architecture recommendation
- use **dedicated bot tokens and backend configs** for sensitive client environments
- use **shared bot/backend patterns only for internal or personal environments**
- if a central management layer is needed later, build it outside Discord rather than collapsing everything into one mixed server

---

## Bot / Tenant Model

### Preferred approach

#### Sensitive clients
**One bot per server**
- dedicated bot token
- dedicated backend config
- dedicated workspace mapping
- dedicated logging and permissions

#### Internal / personal / projects
**Shared bot, multi-tenant backend** is acceptable
- faster rollout
- easier maintenance
- central updates possible

### Recommendation
- **Dedicated bot per sensitive client**
- **Shared bot only for internal/personal/project environments**

---

## Main User Journeys

### Journey 1 — Submit a task
User says: “Assess this vendor”

Bot:
- creates assessment job
- assigns to Vendor Assessor workflow
- posts status updates
- returns summary and next actions

### Journey 2 — Report an incident
User says: “Potential confidentiality incident”

Bot:
- launches structured intake
- asks key questions
- classifies incident
- drafts update statement
- proposes risk rating and containment steps

### Journey 3 — Create a project item
User says: “Track this for ForgeHome”

Bot:
- creates task/job
- files it to correct workspace
- optionally reminds or escalates later

### Journey 4 — Query knowledge / status
User says: “Show current status of open privacy incidents”

Bot:
- pulls from the system of record
- summarises in channel
- offers drill-down actions

These journeys should define the system before the system defines itself into a maze.

---

## Channel Architecture

Keep channels role-based and action-based.

### Recommended base structure per server

#### Category: Start Here
- `#welcome`
- `#how-to-use`
- `#bot-help`
- `#announcements`

#### Category: Intake
- `#intake-general`
- `#intake-incidents`
- `#intake-assessments`
- `#intake-projects`

#### Category: Work in Progress
- `#jobs-active`
- `#awaiting-input`
- `#awaiting-review`
- `#blocked`

#### Category: Outputs
- `#completed-jobs`
- `#final-outputs`
- `#summaries`

#### Category: Control
- `#approvals`
- `#alerts`
- `#integration-status`
- `#bot-admin`

#### Category: Audit
- `#audit-log`
- `#routing-log`
- `#system-events`

### Important pattern
The intake channels start jobs.
Each request becomes a dedicated **thread**.
That thread becomes the working space for that job.

---

## Interaction Model

### Slash commands
Examples:
- `/incident new`
- `/vendor assess`
- `/job create`
- `/job status`
- `/approve`
- `/close`

Best for:
- structure
- consistency
- permissions
- lower ambiguity

### Natural-language intake
Examples:
- “Assess this processor for GDPR and transfers”
- “Create a ForgeHome job for boiler servicing”

Best for:
- ease of use
- flexible input

Mitigation:
Bot follows with a modal or required questions.

### Modals / forms
Best for:
- incident details
- vendor review inputs
- task metadata
- approval justification

### Buttons / menus
Best for:
- approve
- reject
- escalate
- need more info
- mark blocked
- close job

### Best practice
Use all three:
- slash commands to start workflows
- modals for structured intake
- threaded conversation for follow-up
- buttons for approvals and status transitions

---

## Thread-per-Request Pattern

Each request should create a thread.

### Benefits
- contained conversation
- cleaner channels
- per-job audit trail
- easier status tracking

### Pattern
1. request appears in intake channel
2. bot creates thread
3. all working discussion happens there
4. bot posts final result to output channel
5. thread is archived when complete

This prevents the server becoming a digital shed.

---

## User Roles

### Core roles
- **Requester** — submits jobs, views own outputs, responds to clarification prompts
- **Operator** — manages jobs, intervenes on routing issues, reassigns/escalates
- **Reviewer** — reviews high-risk outputs, approves/rejects actions, requests rework
- **Admin** — configures routing, permissions, integrations, bot behavior
- **Bot / Service role** — creates threads, posts updates, executes workflow actions

### Optional specialist roles
- Incident Lead
- Vendor Review Lead
- Project Lead
- Read-only Stakeholder

---

## Routing Model

Every message or command should resolve:
- which workspace/project does this belong to?
- which agent handles it?
- what tools are allowed?
- what memory/context is allowed?
- what output format is expected?

### Example routing logic
Input:
- Server = ProPharma
- Channel = `#intake-incidents`
- Command = `/incident new`
- Tag = confidentiality

Route:
- Workspace = `privacy-incidents`
- Workflow = `incident-triage-v1`
- Primary agent = `Privacy Incident Reporter`
- Reviewer role = `Incident Lead`
- Output channel = `#completed-jobs`
- Audit channel = `#audit-log`

Second example:
- Server = Personal
- Message = “Create a ForgeCar task for MOT and tyres”

Route:
- Workspace = `forgecar`
- Workflow = `household-task-intake-v1`
- Primary agent = `Forge Operations Coordinator`
- Output = task summary + due dates + next actions

---

## Workspace Model

A workspace is the backend operational domain where the job belongs.

### Example workspaces
- `privacy-incidents`
- `vendor-assessments`
- `privacy-publishing`
- `forgehome`
- `forgecar`
- `forgegarden`
- `internal-projects`

Each workspace should define:
- allowed request types
- allowed agents
- permitted tools
- data sensitivity level
- reviewer roles
- output templates
- logging requirements

---

## Initial Agent Set

Do not start with twenty agents.
Start with three or four with hard boundaries.

### 1. Orchestrator
Purpose:
- receives request
- chooses workflow
- routes to specialist agent
- keeps thread updated

### 2. Privacy Incident Reporter
Purpose:
- incident triage
- missing info detection
- containment review
- risk analysis
- update statement drafting

### 3. Privacy Vendor Assessor
Purpose:
- vendor due diligence
- question generation
- gap analysis
- risk summary
- recommendations

### 4. Privacy Publisher
Purpose:
- polished summaries
- stakeholder-ready wording
- structure and tone standardisation

### 5. Forge Coordinator
Purpose:
- household/personal Forge task intake
- classify tasks into Forge domains
- update schedules and outputs

That is enough to build real value without corporate cosplay.

---

## Standard Request Lifecycle

Recommended lifecycle:
- **New**
- **Validating**
- **Routed**
- **In Progress**
- **Awaiting Input**
- **Awaiting Review**
- **Approved**
- **Completed**
- **Archived**

Optional:
- Failed
- Escalated
- Cancelled

### Good status language
- “Incident triage started”
- “Missing required fields: number of individuals, recipient confirmation, jurisdiction”
- “Draft update prepared”
- “Awaiting reviewer approval”

Visible, legible, and not magical in the bad sense.

---

## Approval Model

Not every workflow needs approval, but sensitive ones should.

### Approval triggers
- high-risk incident
- client-facing communication draft
- sensitive cross-border assessment
- workflow involving external side effects
- deletion/archive/send actions

### Approval actions
- approve
- reject
- return for rework
- escalate

### UX shape
- approval summary card/message
- buttons for actions
- reviewer identity logged
- timestamp recorded
- decision posted back into thread

---

## Audit and Logging

This system should produce an audit-friendly trail.

### Events to log
- request created
- route selected
- workspace assigned
- agent assigned
- state changes
- clarifications requested
- approvals
- outputs published
- failures/errors
- closure/archive

### Minimum audit record quality
- time-stamped
- actor attributed
- linked to job ID
- append-only where feasible

Discord can show summary logs, but durable logging should live in the backend.

---

## Security and Governance Controls

### Key controls
1. Permission-based channel access
2. Workspace isolation across trust boundaries
3. Sensitive data minimisation in Discord
4. Approval gates for sensitive actions
5. Audit retention outside Discord if needed
6. Separate tokens/integrations for sensitive deployments
7. Allowed-tool policy per workspace

Discord should be the interface, notifier, decision surface, and operator console — not the permanent record or uncontrolled file warehouse.

---

## Error Handling

The bot should never fail mysteriously.

Examples:
- routing failure
- missing permissions
- missing mandatory fields
- external system unavailable
- workflow timeout
- approval not received

### Response pattern
- explain what happened
- show current state
- say what is needed next
- offer retry or escalation path

No mysterious silence. Nothing destroys trust faster.

---

## MVP Scope

### Recommended MVP
- one development Discord server
- one orchestration backend
- one Orchestrator bot
- three workflows:
  - incident intake
  - vendor assessment intake
  - general project intake

### MVP features
- slash command to start workflow
- modal for structured intake
- thread per request
- routing to correct agent/workspace
- simple status updates
- final summary output
- audit log channel

### Explicitly not in MVP
- cross-server federation
- self-learning
- giant memory layer
- autonomous external actions without approval
- broad analytics suite

Keep the MVP narrow and workflow-led.

---

## Future Roadmap

### Phase 2
- approvals via buttons
- role-based output visibility
- external system integration
- knowledge retrieval
- templated reports
- GitHub/project sync
- scheduled summaries
- alerts and monitoring
- analytics dashboard

### Phase 3
- multi-server management console
- per-client bot packages
- compliance rule engines by jurisdiction
- adaptive routing based on incident type
- reusable skills/playbooks
- learning from reviewed outputs
- evidence pack generation
- fuller orchestration with OpenClaw

The key rule:
Learning should come from reviewed outcomes, not the bot teaching itself nonsense at 2 AM.

---

## Technical Architecture

A good backend shape:

Discord bot layer  
→ Command/router service  
→ Workflow engine  
→ Agent services  
→ Data store for state/logs  
→ Integration layer for external systems  
→ Policy/permissions layer  
→ Audit log

If using OpenClaw:
- **Discord = interface**
- **OpenClaw = agent runtime / orchestrator**
- **External systems = systems of record**

---

## Example Workflow — Privacy Incident Intake

1. User triggers `/incident new` in `#intake-incidents`
2. Modal collects:
   - incident title
   - summary
   - date/time
   - data type
   - number of individuals
   - jurisdictions
   - containment status
   - external recipients known
   - next actions
3. Bot creates thread:
   - `INC-2026-0042 | Confidentiality Incident`
4. Router assigns:
   - workspace = `privacy-incidents`
   - workflow = `incident-triage-v1`
   - agent = `Incident Reporter`
5. Thread updates:
   - job created
   - triage started
   - missing inputs identified
   - risk proposal prepared
   - draft update statement ready
6. If risk exceeds threshold:
   - approval request sent to reviewer
7. Final output posted:
   - triage summary
   - missing evidence
   - recommended actions
   - draft ticket update
   - status = awaiting review or completed

---

## Example Workflow — ForgeHome Task Intake

1. User types:
   - “Create a ForgeHome job for boiler service and gutter check”
2. Bot classifies:
   - domain = ForgeHome
   - type = maintenance
   - priority = normal
3. Bot opens thread and asks for:
   - property
   - target month
   - whether quote is needed
   - urgency/safety context
4. Job routed to ForgeHome workspace
5. Thread returns:
   - created task card
   - suggested schedule
   - next actions
   - reminders/dependencies

---

## Recommended Build Sequence

### Stage 1 — Design and control model
- define trust boundaries
- define roles and permissions
- define channels and thread pattern
- define first three workflows
- define job status model

### Stage 2 — Routing and intake
- implement slash commands
- build intake modals
- create router rules
- map channels to workflows/workspaces

### Stage 3 — Workflow execution
- connect Discord to orchestrator
- support thread updates
- support final outputs
- support approval actions

### Stage 4 — Logging and hardening
- external audit log
- role testing
- routing tests
- failure handling
- security review

### Stage 5 — Expansion
- more agents
- more workspaces
- more integrations
- more servers

---

## Naming Standard

### Channels
- `intake-*`
- `jobs-*`
- `outputs-*`
- `approvals`
- `alerts`
- `audit-log`

### Threads
`[JOB-ID] short title`

Examples:
- `[INC-0042] Misdirected email`
- `[VEN-0017] Splash Clinical review`
- `[FGH-0021] Boiler service`

### Commands
- `/incident new`
- `/vendor new`
- `/job create`
- `/job status`
- `/approve`
- `/escalate`
- `/close`

---

## Success Criteria

You know this is working if:
- users know where to submit work
- requests are consistently routed correctly
- every job gets a clear working thread
- missing info is identified early
- status is visible without chasing people
- outputs are predictable and usable
- sensitive actions are review-gated
- audit history is easy to follow
- client boundaries remain intact

---

## Key Risks and Mitigations

### Risk: Discord becomes messy and unstructured
Mitigation:
- strict intake channels
- thread-per-request
- command-led workflows

### Risk: cross-client leakage
Mitigation:
- separate servers
- separate configs
- workspace isolation
- role controls

### Risk: bad routing
Mitigation:
- explicit routing tables
- fallback operator review
- audit logs

### Risk: users paste too much sensitive data into chat
Mitigation:
- clear instructions
- modal constraints
- external document references where appropriate

### Risk: overengineering too early
Mitigation:
- narrow MVP
- workflow-led build
- staged rollout

---

## Final Recommendation

Best first implementation:
- one personal/dev Discord server
- one orchestrator bot
- channels for intake, jobs, outputs, alerts, admin
- three initial workflows:
  - Privacy Incident Reporter
  - Privacy Vendor Assessor
  - General Project Intake
- one thread per request
- slash command + modal intake
- outputs posted back into thread and results channel
- later clone pattern to client-specific servers with dedicated bot/token/config/workspace separation

This gives you something practical, secure, auditable, and expandable.
