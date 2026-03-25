# ForgeOrchestrate — Routing and Policy Model v1.0

## Status
Draft

## Purpose

This document defines how ForgeOrchestrate should decide where work goes, what is allowed to happen, and under what conditions execution may proceed.

Routing and policy are the core nervous system of ForgeOrchestrate.
Without them, the product is just a more expensive way to guess.

---

## Core Thesis

Every request entering the AI estate should be resolved through two linked systems:

1. **Routing model** — decides where the work belongs and who should handle it
2. **Policy model** — decides what is permitted, what is restricted, and what approvals or controls apply

Together they answer:
- where should this go?
- who should do it?
- what tools/models/connectors are allowed?
- which workspace owns it?
- does it need approval?
- can the output be delivered?
- what happens if something is ambiguous or blocked?

---

## Routing Model

### Routing purpose
The routing model converts an incoming request into a governed execution path.

### A route decision should resolve at minimum
- trust boundary
- workspace
- request type
- workflow
- primary agent
- optional supporting agents
- model/tool policy
- connector policy
- approval requirement
- output handling policy
- audit level

---

## Inputs to Routing

Routing should be based on explicit inputs.

### 3.1 Source context
- source channel/system
- guild/server/chat/workspace origin
- API origin
- internal trigger origin
- schedule/cron origin

### 3.2 Request context
- command or request type
- user text/content
- attached metadata
- declared tags or labels
- structured form inputs

### 3.3 Identity context
- requester identity
- role
- permission tier
- ownership or stakeholder relationship

### 3.4 Trust context
- boundary from source environment
- workspace constraints implied by environment
- sensitivity level if known

### 3.5 Policy context
- allowed workspaces
- allowed workflows
- approval triggers
- connector restrictions
- output restrictions

---

## Routing Priority Order

Routing should not be based on freeform vibes.
Use this order of precedence:

1. **Trust boundary / environment**
2. **Source channel or intake surface**
3. **Explicit command or workflow trigger**
4. **Requester role / permissions**
5. **Structured request type / form data**
6. **Content classification**
7. **Fallback operator review if still ambiguous**

### Why this matters
The environment should constrain the route before the text gets clever.
That is how you avoid an internal-sounding prompt accidentally reaching a client workspace or vice versa.

---

## Request Classification Model

Before routing completes, each request should be classified.

### Minimum classification outputs
- request category
- sensitivity level
- confidence score or confidence band
- candidate workflows
- candidate workspace set
- ambiguity flag

### Example request categories
- privacy_incident
- vendor_assessment
- general_project
- research_request
- reporting_request
- scheduling_request
- publishing_request
- system_admin_request
- unknown

### Rule
If confidence is low and the route matters, route to clarification or operator review rather than pretending certainty.

---

## Workspace Selection Model

After classification, ForgeOrchestrate selects the owning workspace.

### Workspace selection must consider
- trust boundary
- domain/client/project ownership
- request type
- explicit destination if supplied
- role permissions
- policy restrictions

### Example
Input:
- source = ForgeDiscord in `client-propharma`
- request = privacy incident intake

Output:
- workspace = `client-propharma:privacy-incidents`

### Rule
A request must not be routed to a workspace outside its trust boundary unless a cross-boundary rule exists and is logged.

---

## Workflow Selection Model

Once workspace is selected, ForgeOrchestrate chooses the workflow.

### Workflow selection considers
- request category
- workspace-supported workflows
- explicit command
- policy requirements
- whether multi-step execution is needed

### Example
- `privacy_incident` → `incident-triage-v1`
- `vendor_assessment` → `vendor-review-v1`
- `general_project` → `general-intake-v1`

### Rule
Workflow selection should be deterministic wherever possible.

---

## Agent Selection Model

ForgeOrchestrate should choose who leads and who supports.

### Agent selection should determine
- primary agent
- optional supporting agents
- allowed handoff chain
- fallback/escalation path

### Example
For a privacy incident:
- primary = privacy-incident-reporter
- support = publisher (for draft output cleanup)
- reviewer = incident lead

### Rule
Agent collaboration should be explicit.
Do not smuggle hidden org charts into runtime behavior.

---

## Policy Model

### Policy purpose
Policy determines what a route is allowed to do.

### Policy should govern
- allowed tools
- allowed connectors
- allowed models
- memory/context scope
- approval requirements
- retention rules
- output controls
- notification rules
- override rights

### Principle
Routing says **where** the work goes.
Policy says **what it is allowed to do there**.

---

## Policy Layers

Policy should be evaluated across multiple layers.

## 9.1 Global policy
Applies across the estate.

### Examples
- no uncontrolled cross-boundary context sharing
- high-risk outputs require approval
- certain connectors restricted to approved workspaces

---

## 9.2 Trust-boundary policy
Applies to a class or domain boundary.

### Examples
- client workspaces cannot access personal-lab tools
- client outputs require stricter delivery controls
- internal ops workspaces have elevated audit expectations

---

## 9.3 Workspace policy
Applies to a specific workspace.

### Examples
- allowed tools policy
- connector list
- approval model
- retention rules
- notification destinations

---

## 9.4 Workflow policy
Applies to a specific workflow.

### Examples
- vendor review may require structured intake fields
- publishing workflow may require reviewer signoff before release
- incident triage may require high audit level and escalation conditions

---

## 9.5 Action policy
Applies to a specific action/output/event.

### Examples
- deliver output externally
- send notification to stakeholder
- escalate issue
- export artifact
- invoke restricted connector

---

## Tool / Connector / Model Governance

Each route should resolve an explicit allowed capability set.

### 10.1 Tool policy
Defines which tools can be used.

### 10.2 Connector policy
Defines which external systems can be accessed.

### 10.3 Model policy
Defines which models are allowed or preferred, potentially including:
- default model
- premium model allowed only for certain routes
- low-cost model for low-risk triage

### Rule
Execution should receive an explicit allowed capability set, not a vague assumption that everything is available.

---

## Approval Model

Approvals should be policy-driven, not improvised mid-run.

### Approval trigger categories
- sensitive outputs
- external-facing drafts
- high-risk incidents
- privileged connector use
- exceptional overrides
- restricted artifact delivery

### Approval should specify
- trigger reason
- required reviewer role(s)
- timeout behavior
- escalation path
- output state while pending

### Possible approval outcomes
- approved
- rejected
- rework required
- escalated
- timed out

---

## Output Policy

Routing/policy should determine what happens to outputs.

### Output policy should control
- whether output can be delivered automatically
- whether review is required first
- where output can be sent
- whether output is internal-only
- whether export/download is restricted
- retention handling for generated artifacts

### Example
A generated client-facing deck may be:
- built successfully
- marked `awaiting_review`
- withheld from external delivery until signoff

---

## Notification Policy

Policy should determine who gets told what.

### Notification events might include
- request accepted
- blocked for input
- awaiting review
- failed
- completed
- escalated

### Notification policy should specify
- destination
- severity
- channel type
- whether requester-only or broader audience

---

## Exception and Override Model

Not every real-world case fits the normal path.
ForgeOrchestrate needs structured exception handling.

### Exceptions include
- no valid workspace match
- multiple conflicting route candidates
- missing required information
- connector unavailable
- approval absent or rejected
- restricted action requested by unauthorized role

### Override examples
- manual re-route by operator
- temporary connector access by admin
- emergency release with explicit override approval

### Override rules
- explicit
- attributable
- logged
- bounded by policy
- second approval where risk is high

---

## Fallback Behavior

If routing is uncertain or blocked:
1. keep request in safe state
2. do not expand access just to make it work
3. request clarification or escalate to operator
4. log ambiguity/exception event
5. preserve request context for review

### Recommended fallback states
- `awaiting_input`
- `awaiting_operator`
- `awaiting_review`
- `failed`

---

## Data Model Requirements

A route decision record should include:
- route_id
- request_id
- trust_boundary
- workspace_key
- workflow_id
- primary_agent
- supporting_agents
- classification_result
- confidence
- approval_required
- allowed_tools_policy
- allowed_connectors
- allowed_models_policy
- output_policy
- notification_policy
- audit_level
- override_applied (bool)
- decision_timestamp

---

## Config Representation

Routing and policy should be treated as config, not hidden magic.

### Example route + policy config
```yaml
routes:
  - source: discord
    boundary: client-propharma
    channel: intake-incidents
    command: incident.new
    request_type: privacy_incident
    workspace: client-propharma:privacy-incidents
    workflow: incident-triage-v1
    primary_agent: privacy-incident-reporter
    approval_model: high-risk-incident
    allowed_tools_policy: policy.client_propharma_incident_tools
    allowed_models_policy: policy.client_propharma_models
    output_policy: restricted-review-first
    audit_level: critical
```

This should be human-readable, versionable, and auditable.

---

## MVP Routing and Policy Direction

A sensible MVP should support:
- a limited request taxonomy
- explicit trust-boundary-aware workspace routing
- deterministic workflow selection
- policy-selected tools/connectors/models
- approval trigger support
- exception/override logging
- clear fallback states

### Recommended first supported request classes
- incident
- vendor assessment
- general project intake
- research/reporting requests

---

## Non-Goals

This model is not intended to:
- remove all human judgment
- replace operator intervention where ambiguity matters
- become a giant opaque rules engine no one can read
- let policy sprawl into decorative bureaucracy

The purpose is clarity and control.

---

## Recommended Next Docs

1. execution event and audit model
2. operator control surface specification
3. MVP environment and component spec

---

## Final Recommendation

ForgeOrchestrate should treat routing and policy as first-class operating logic.

That means:
- routes decide ownership and execution path
- policy decides what is allowed
- approvals decide what may proceed or be released
- exceptions and overrides remain visible and governed

This is how the system becomes trustworthy, not just technically capable.
