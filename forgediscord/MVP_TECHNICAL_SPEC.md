# ForgeDiscord — MVP Technical Specification v1.0

## Status
Draft

## Purpose

This specification defines the MVP implementation for ForgeDiscord as an **intake and coordination layer** in front of the Forge / OpenClaw execution environment.

The MVP is deliberately narrow.
It is designed to prove that Discord can reliably:
- collect requests
- structure intake
- create a thread per job
- route to the correct workspace and workflow
- report progress back to users
- present final outputs clearly
- preserve trust boundaries and auditability

The MVP is not intended to be a grand all-purpose operations empire on day one.

---

## Product Role

ForgeDiscord MVP role:

**Discord collects requests, routes them to the correct agent/workspace, and reports progress back.**

### In architecture terms
- **Discord** = interface + intake + coordination surface
- **OpenClaw** = agent runtime and orchestrator
- **External systems** = systems of record where applicable

---

## MVP Scope

### Included
- one development Discord server
- one ForgeDiscord bot
- one orchestration backend
- slash-command-led workflow entry
- modal/form intake for structured jobs
- automatic thread creation per request
- routing to the correct workspace and workflow
- status updates inside the request thread
- final result posting in thread and output channel
- basic approval workflow for sensitive actions
- audit log channel
- three initial workflows:
  1. Privacy incident intake
  2. Vendor assessment intake
  3. General project intake

### Excluded
- cross-server federation
- multi-client production tenancy in MVP
- autonomous external action-taking without approval
- large-scale knowledge retrieval
- long-term document repository behavior inside Discord
- advanced analytics dashboards
- adaptive self-learning behavior
- complex multi-agent mesh orchestration beyond orchestrator-led routing

---

## Success Criteria

The MVP is successful if:
- users know where to submit requests
- each request gets a dedicated thread
- routing is correct and explainable
- missing information is identified early
- status is visible in Discord without manual chasing
- outputs are clear and usable
- approvals work for sensitive cases
- audit history is visible and attributable
- the system does not leak context across workspaces or trust boundaries

---

## Deployment Context

### MVP environment
- **Server type:** one internal/personal development Discord server
- **Bot model:** one ForgeDiscord bot token
- **Backend model:** one orchestration backend connected to OpenClaw
- **Trust model:** single non-client dev trust boundary for initial rollout

### Expansion after MVP
After stability is proven:
- clone the pattern into client-specific servers
- use dedicated bot token + config per sensitive environment
- enforce workspace and permission isolation per trust boundary

---

## Core User Journeys

### Journey A — Privacy incident intake
1. User invokes `/incident new`
2. Bot opens modal and captures incident details
3. Bot creates job ID and thread
4. Router maps job to `privacy-incidents` workspace and `incident-triage-v1` workflow
5. Orchestrator dispatches to Privacy Incident Reporter
6. Status updates are posted to thread
7. If needed, reviewer approval is requested
8. Final triage summary is posted

### Journey B — Vendor assessment intake
1. User invokes `/vendor assess`
2. Modal captures vendor name, processing purpose, geography, subprocessors, concerns
3. Bot creates job thread
4. Router maps to `vendor-assessments` workspace
5. Vendor Assessor workflow runs
6. Results and recommendations return to thread

### Journey C — General project intake
1. User invokes `/job create`
2. Modal or guided prompt captures request metadata
3. Bot creates thread
4. Router selects destination workspace (e.g. internal-projects / Forge domain)
5. Orchestrator routes task
6. Thread shows lifecycle until final output

---

## Functional Requirements

## 7.1 Discord Command Layer
The bot must provide these initial slash commands:
- `/incident new`
- `/vendor assess`
- `/job create`
- `/job status`
- `/approve`
- `/reject`
- `/close`
- `/help`

### Command requirements
- commands must be permission-aware
- commands must validate required context
- commands must create structured backend payloads
- commands must return immediate acknowledgement

---

## 7.2 Modal / Intake Layer
The bot must support structured modal-based intake.

### Incident modal fields
- incident title
- summary
- incident date/time
- data type involved
- approximate number of individuals
- jurisdictions
- containment status
- recipients involved
- immediate actions taken

### Vendor modal fields
- vendor name
- service / processing purpose
- jurisdictions involved
- subprocessors known
- transfer concerns
- review objective

### General project intake fields
- request title
- request summary
- desired workspace/project
- priority
- due context
- relevant links or references

### Modal requirements
- required fields enforced for critical workflows
- field length caps
- clear validation messaging
- ability to request follow-up details in thread if incomplete

---

## 7.3 Thread Management
Every intake request must create a dedicated thread.

### Thread behavior
- thread created in originating intake channel
- thread name format: `[JOB-ID] short title`
- thread used for all status updates and follow-up questions
- thread archived when lifecycle reaches completed/archived

### Requirements
- thread ID stored in backend state
- thread linked to job record
- bot must be able to post progress updates, approval prompts, and final output into thread

---

## 7.4 Routing Engine
The routing layer must resolve:
- trust boundary / server context
- channel context
- command type
- requested workflow
- destination workspace
- assigned agent(s)
- required reviewer role
- allowed tools set

### Routing inputs
- Discord server/guild ID
- channel ID
- command type
- optional tags
- modal payload
- requester role

### Routing outputs
- workspace key
- workflow ID
- primary agent
- reviewer role if required
- output template
- audit policy

### MVP routing rule examples
- `/incident new` → `privacy-incidents` → `incident-triage-v1` → `Privacy Incident Reporter`
- `/vendor assess` → `vendor-assessments` → `vendor-review-v1` → `Privacy Vendor Assessor`
- `/job create` → `internal-projects` or Forge domain route → `general-intake-v1` → `Orchestrator`

---

## 7.5 Workflow Orchestration
ForgeDiscord does not execute domain logic directly. It hands off to OpenClaw / backend orchestration.

### MVP orchestration responsibilities
- create a job record
- assign workflow and workspace
- dispatch to appropriate agent path
- track state transitions
- post status messages back to Discord
- request human approval if workflow requires it
- deliver final summary to thread

### Workflow engine must support
- synchronous acknowledgement
- asynchronous progress updates
- failure handling and retry logic
- reviewer gating
- final result publication

---

## 7.6 State Model
Each job must have a consistent lifecycle.

### Required statuses
- `new`
- `validating`
- `routed`
- `in_progress`
- `awaiting_input`
- `awaiting_review`
- `approved`
- `completed`
- `archived`

### Optional statuses
- `failed`
- `escalated`
- `cancelled`

### Status requirements
- every transition is time-stamped
- actor/source for transition is recorded
- status updates are visible in thread
- approval states are explicit

---

## 7.7 Approval Flow
Sensitive workflows must support review.

### Approval triggers in MVP
- high-risk incident outputs
- sensitive client-facing draft wording
- workflows configured with mandatory review

### Approval actions
- approve
- reject
- request rework
- escalate

### Approval UX
- bot posts structured approval summary into thread or approvals channel
- reviewer uses button or command action
- decision is written to backend audit log
- thread updates reflect decision

---

## 7.8 Audit Logging
The MVP must emit an audit trail.

### Events to record
- request created
- modal submitted
- route chosen
- workspace assigned
- workflow assigned
- agent dispatched
- state changes
- clarification requested
- approval requested
- approval given/rejected
- output published
- closure/archival
- failures/errors

### Minimum audit fields
- job ID
- timestamp
- actor (user, bot, backend, reviewer)
- event type
- payload summary
- Discord references (server/channel/thread/message where relevant)

### Visibility
- summary events posted to `#audit-log`
- durable logs stored in backend/state store outside Discord where appropriate

---

## Channel Model for MVP

### Required channels
#### Start Here
- `#welcome`
- `#how-to-use`
- `#bot-help`

#### Intake
- `#intake-incidents`
- `#intake-assessments`
- `#intake-projects`

#### Work / Review
- `#jobs-active`
- `#awaiting-review`
- `#blocked`

#### Outputs
- `#completed-jobs`
- `#summaries`

#### Control
- `#approvals`
- `#bot-admin`
- `#integration-status`

#### Audit
- `#audit-log`

### Channel rule
The intake channels start jobs; the thread does the job conversation.

---

## Role Model for MVP

### Required roles
- **Requester**
- **Operator**
- **Reviewer**
- **Admin**
- **Bot**

### Permissions conceptually
| Role | Can Submit | Can View Own Threads | Can Review | Can Administer |
|------|------------|----------------------|------------|----------------|
| Requester | Yes | Yes | No | No |
| Operator | Yes | Yes | Limited | No |
| Reviewer | Yes | Yes | Yes | No |
| Admin | Yes | Yes | Yes | Yes |
| Bot | Service | Service | Service | Service |

---

## Backend Architecture

### MVP architecture
Discord Server  
→ Discord Bot Layer  
→ Command / Intake Router  
→ Workflow Orchestrator  
→ OpenClaw Agent Runtime  
→ State / Audit Store  
→ Discord Thread Updates + Output Messages

### Logical components
1. **Discord Bot Layer**
   - slash commands
   - modals
   - thread creation
   - buttons / approval actions

2. **Router Service**
   - command classification
   - routing decision
   - workspace and workflow mapping

3. **Workflow Orchestrator**
   - job lifecycle management
   - handoff to OpenClaw runtime
   - state updates

4. **State / Audit Store**
   - jobs
   - event history
   - approval records
   - Discord references

5. **Integration Layer**
   - OpenClaw sessions/workspaces
   - optional ticketing/docs later

---

## Data Model

### Minimum job record
- job_id
- request_type
- guild_id
- channel_id
- thread_id
- requester_id
- requester_role_context
- trust_boundary
- workspace_key
- workflow_id
- assigned_agent
- priority
- current_status
- created_at
- updated_at
- review_required
- risk_level
- output_reference

### Minimum audit event record
- event_id
- job_id
- timestamp
- actor_type
- actor_id_or_name
- event_type
- summary
- metadata

---

## Error Handling Requirements

The MVP must fail visibly and clearly.

### Error classes
- invalid command context
- modal validation failure
- routing failure
- missing required permissions
- workflow execution error
- backend timeout
- approval timeout
- Discord API error

### UX requirement
Every failure must:
- explain what happened
- indicate current status
- say what is needed next
- offer retry, escalation, or admin path where possible

No silent failure behavior.

---

## Security Requirements

### MVP security rules
- bot token stored securely, never in repo
- role-based channel visibility
- no cross-workspace routing by default
- sensitive actions must be review-gated where configured
- Discord is not treated as long-term sensitive record storage
- backend logs retained outside Discord where needed
- per-environment config separation supported from the start

### Trust-boundary rule
The MVP starts in a dev/internal server, but the architecture must be designed so it can be cloned into separate client-specific deployments without redesign.

---

## Implementation Sequence

### Step 1 — Environment and bot skeleton
- create bot app and token
- connect to dev Discord server
- register slash commands
- verify permissions and channel access

### Step 2 — Intake commands and modals
- implement `/incident new`
- implement `/vendor assess`
- implement `/job create`
- create modal capture flows

### Step 3 — Thread and state creation
- generate job IDs
- create request thread
- write initial job + audit record
- post acknowledgement/status message

### Step 4 — Routing and orchestration handoff
- map workflow routes
- connect to OpenClaw/backend dispatcher
- start jobs asynchronously
- push status updates back into thread

### Step 5 — Approval flow
- add approval message format
- add reviewer actions
- record approval state

### Step 6 — Output and closure
- publish final summary
- mirror to outputs channel if appropriate
- archive thread when complete

### Step 7 — Audit and hardening
- post to `#audit-log`
- test failure cases
- test permissions
- verify routing isolation

---

## MVP Deliverables

### Core deliverables
- bot with working slash commands
- modal intake flows for 3 workflows
- per-request thread creation
- working routing map
- OpenClaw orchestration handoff
- visible status updates
- final output flow
- approvals channel flow
- audit logging

### Documentation deliverables
- setup instructions
- environment variable reference
- routing table reference
- server/channel setup guide
- permission model guide
- operator runbook

---

## Future-Compatible Hooks

The MVP should leave room for:
- multi-server deployment
- dedicated bot per client
- additional workflows
- richer approval policies
- file/report integrations
- scheduled digests
- GitHub/project sync
- external systems of record
- management dashboard layer

---

## Final Recommendation

The correct MVP is intentionally narrow:
- one development server
- one bot
- three workflows
- one thread per request
- Discord as intake + coordination surface
- OpenClaw as orchestrator/runtime
- approvals for sensitive work
- audit-first design

That is enough to make ForgeDiscord real without turning it into a haunted wiring cupboard.
