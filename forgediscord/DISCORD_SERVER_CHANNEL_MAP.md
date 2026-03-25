# ForgeDiscord — Discord Server & Channel Map v1.0

## Purpose

This document defines the recommended Discord server structure for ForgeDiscord as an intake and coordination layer.

The goal is to keep the environment:
- clear
- role-based
- scalable
- auditable
- low-noise
- thread-friendly

This is not meant to be a server full of random channels created during moments of enthusiasm and forgotten by breakfast.

---

## Design Principles

### 1. Channels should reflect function, not mood
Name channels by role in the system, not by whatever sounded clever at 23:47.

### 2. Intake starts in channels, work happens in threads
Channels are launch points. Threads are job workspaces.

### 3. Categories represent operational phases
The structure should move from:
- orientation
- intake
- active work
- outputs
- control
- audit

### 4. Sensitive work should be isolatable
The structure should support role-based restrictions and future client-specific server replication.

---

## Recommended MVP Server Layout

# Server: ForgeDiscord (Development / Internal)

## Category 1 — Start Here

### `#welcome`
Purpose:
- first landing point
- explain what ForgeDiscord is
- direct users to intake paths

Use for:
- welcome message
- links to how-to-use and command help
- high-level purpose statement

### `#how-to-use`
Purpose:
- instructions for request submission
- explain commands, threads, approvals, and expectations

Use for:
- workflow overview
- guidance on what to paste vs not paste
- trust and privacy expectations

### `#bot-help`
Purpose:
- command reference
- short examples
- troubleshooting basics

Use for:
- slash command index
- FAQ
- bot interaction patterns

### `#announcements`
Purpose:
- one-way updates from operators/admins

Use for:
- workflow changes
- maintenance notices
- rollout notes

---

## Category 2 — Intake

These are job entry points.
Each successful intake should create a thread.

### `#intake-incidents`
Purpose:
- intake for privacy/confidentiality/security-style incidents

Starts workflows such as:
- incident triage
- containment support
- draft update generation

Primary command:
- `/incident new`

Thread pattern:
- `[INC-####] short title`

### `#intake-assessments`
Purpose:
- vendor and due diligence requests

Starts workflows such as:
- vendor assessment
- processor review
- transfer-risk review

Primary command:
- `/vendor assess`

Thread pattern:
- `[VEN-####] vendor name`

### `#intake-projects`
Purpose:
- general project / work intake

Starts workflows such as:
- internal project request
- Forge domain task creation
- routed research/analysis request

Primary command:
- `/job create`

Thread pattern:
- `[JOB-####] short title`

### `#intake-general`
Purpose:
- catch-all intake channel for users who do not know where something belongs

Behavior:
- bot should classify and redirect/route
- if necessary, request structured follow-up via modal or thread questions

---

## Category 3 — Active Work

These channels provide operational visibility, but the real work still happens inside threads.

### `#jobs-active`
Purpose:
- visibility into jobs currently in progress

Use for:
- major status broadcasts
- active job summaries
- pinned operational guidance

Note:
- should not replace threads
- should remain summary-oriented, not noisy

### `#awaiting-input`
Purpose:
- show jobs blocked on requester or operator clarification

Use for:
- jobs missing required information
- queue of unresolved clarifications

### `#awaiting-review`
Purpose:
- visibility into outputs that need approval/review

Use for:
- reviewer queue
- pending sign-off summaries

### `#blocked`
Purpose:
- jobs blocked by missing systems, dependencies, permissions, or decisions

Use for:
- blocker visibility
- escalation context

---

## Category 4 — Outputs

### `#completed-jobs`
Purpose:
- final completion summaries for completed work

Use for:
- one final completion post per job where appropriate
- clean visibility of delivered outputs

### `#final-outputs`
Purpose:
- polished outputs or links to final deliverables

Use for:
- final summaries
- review-ready output references
- report links or exported docs where relevant

### `#summaries`
Purpose:
- periodic operational digests

Use for:
- daily summaries
- workload snapshots
- grouped system updates

---

## Category 5 — Control

### `#approvals`
Purpose:
- explicit approval surface for sensitive actions or outputs

Use for:
- approve / reject / rework / escalate decisions
- reviewer decision prompts

### `#alerts`
Purpose:
- system and workflow alerts that require operator awareness

Use for:
- failed jobs
- timeouts
- escalations
- routing failures

### `#integration-status`
Purpose:
- visibility into backend health and external connections

Use for:
- bot connectivity
- orchestration layer status
- external system availability

### `#bot-admin`
Purpose:
- bot configuration and admin-only operational changes

Use for:
- routing config notes
- controlled admin interventions
- maintenance actions

---

## Category 6 — Audit

### `#audit-log`
Purpose:
- human-readable operational audit summaries

Use for:
- request created
- route selected
- status changed
- approval recorded
- output published
- closure recorded

### `#routing-log`
Purpose:
- routing decision visibility for debugging and assurance

Use for:
- route chosen
- workflow selected
- workspace selected
- fallback cases

### `#system-events`
Purpose:
- lower-level system event summaries

Use for:
- backend restarts
- dispatch failures
- integration reconnects
- exceptional runtime events

---

## Threading Rules

### Mandatory rule
Every request creates a thread.

### Thread naming
Format:
`[JOB-ID] short title`

Examples:
- `[INC-0042] Misdirected spreadsheet`
- `[VEN-0017] Splash Clinical assessment`
- `[JOB-0088] ForgeHome maintenance intake`

### What happens in thread
- status updates
- clarification prompts
- approvals if thread-scoped
- intermediate outputs
- final summary
- closure note

### What should not happen in main channels
- long back-and-forth on single jobs
- repeated status spam
- giant walls of intermediate reasoning

---

## Recommended Role Visibility

### Everyone / basic users
Access to:
- `#welcome`
- `#how-to-use`
- `#bot-help`
- intake channels
- limited output visibility depending on environment

### Operators
Access to:
- intake
- active work
- outputs
- alerts
- review queues
- audit visibility as appropriate

### Reviewers
Access to:
- relevant intake threads
- `#awaiting-review`
- `#approvals`
- relevant outputs

### Admins
Access to all channels including:
- `#bot-admin`
- `#integration-status`
- full audit/control surfaces

### Bot
Requires permissions for:
- slash commands
- sending messages
- creating/managing threads
- using embeds/buttons/modals
- reading relevant channels

---

## Channel Lifecycle Rules

### Intake channels
- remain clean
- new requests start here
- long work migrates to thread immediately

### Active work channels
- summary visibility only
- no replacing thread behavior

### Output channels
- high signal only
- concise final status and links

### Audit channels
- append-only style where practical
- no casual chat

### Admin/control channels
- restricted access
- operational, not conversational

---

## Suggested MVP Minimal Set

If you want the leanest usable first version, start with only:

### Start Here
- `#welcome`
- `#how-to-use`

### Intake
- `#intake-incidents`
- `#intake-assessments`
- `#intake-projects`

### Work / Output
- `#awaiting-review`
- `#completed-jobs`

### Control
- `#approvals`
- `#alerts`
- `#bot-admin`

### Audit
- `#audit-log`

That is enough to prove the model before adding more structure.

---

## Recommended Expansion Model

### Internal / development server
Use the full layout above.

### Client-specific production server
Trim to what is necessary for that client context, for example:
- keep only relevant intake channels
- keep approvals and outputs restricted
- hide admin/control internals from normal users
- keep audit visibility tight

### Separate server per trust boundary
Recommended for:
- clients
- regulated contexts
- sensitive operational environments

---

## Naming Rules

### Use
- `intake-*`
- `awaiting-*`
- `completed-*`
- `final-*`
- `audit-*`
- `integration-*`

### Avoid
- vague names
- joke names for real operational channels
- duplicate-purpose channels
- random historical leftovers

ForgeDiscord should feel like an operator environment, not a forgotten gaming clan.

---

## Final Recommendation

Best first server shape:
- clear intake channels
- thread-per-request workflow
- lightweight active work visibility
- explicit approvals surface
- explicit audit surface
- tight role controls

This gives ForgeDiscord a structure that is calm, scalable, and fit for coordination work from day one.
