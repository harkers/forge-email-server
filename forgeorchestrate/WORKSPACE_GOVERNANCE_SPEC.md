# ForgeOrchestrate — Workspace Governance Specification v1.0

## Status
Draft

## Purpose

This document defines how ForgeOrchestrate should govern workspaces across the AI estate.

Workspace governance is one of the most important parts of the system because it is what prevents the estate from becoming a blurred mess of clients, labs, projects, tools, prompts, and permissions.

ForgeOrchestrate only works properly if workspace boundaries are explicit, enforced, and operationally visible.

---

## Governance Thesis

A workspace is not just a folder or a label.

A workspace is a governed operational domain with its own:
- trust boundary
- prompts and agent context
- tools and connectors
- routing rules
- approval rules
- retention rules
- notification paths
- audit expectations
- output controls

### Principle
If two domains should not casually share context, they should not live inside the same effective workspace boundary.

---

## What Workspace Governance Must Solve

Workspace governance exists to solve these risks:
- cross-client leakage
- accidental tool misuse
- wrong workflow routing
- weak approval control
- mixed retention behavior
- poor audit attribution
- notification spillover
- policy ambiguity

Without workspace governance, orchestration becomes unsafe theatre.

---

## Workspace Definition

Each workspace should be treated as a first-class governed object.

### Minimum workspace record
A workspace should define:
- workspace key
- display name
- trust boundary
- owning domain/client/project
- description/purpose
- allowed request types
- default workflows
- allowed agents
- allowed tools
- allowed connectors
- memory/context scope
- approval model
- retention rules
- notification routes
- output restrictions
- audit level
- operator/admin owners

---

## Trust Boundary Model

### Recommended trust boundary categories
- client
- internal operations
- project
- personal lab
- development/test

### Example boundary set
- `client-propharma`
- `client-hsbc`
- `internal-projects`
- `personal-lab`
- `ops-core`

### Rule
A workspace inherits its trust boundary from its governing domain.

### Critical principle
Cross-boundary access should be explicit, exceptional, and logged.
It should not happen by accident through vague defaults.

---

## Workspace Classes

ForgeOrchestrate should support different classes of workspace.

## 5.1 Client Workspace
Used for specific client or regulated-party work.

### Characteristics
- strict isolation
- client-specific policies
- client-specific connectors/tools where needed
- high audit expectations
- explicit approval controls
- tight notification paths

### Example
- `client-propharma:privacy-incidents`
- `client-hsbc:vendor-assessment`

---

## 5.2 Internal Project Workspace
Used for product/project execution inside the Forge estate.

### Characteristics
- lower isolation than client work
- can share some internal tooling
- may still need product-specific boundaries
- medium to high audit visibility depending on use

### Example
- `internal-projects:forgedeck`
- `internal-projects:forgepipeline`

---

## 5.3 Operations Workspace
Used for orchestration/operations/system governance work.

### Characteristics
- high privilege
- high audit expectations
- strong approval and admin controls
- should not be casually reachable from low-trust request surfaces

### Example
- `ops-core`
- `ops-routing-control`

---

## 5.4 Personal / Lab Workspace
Used for experimentation and personal work.

### Characteristics
- lower compliance burden
- should remain isolated from client work
- may allow broader experimentation
- still should not contaminate serious environments

### Example
- `personal-lab`
- `forge-dev`

---

## Governance Dimensions

Every workspace should be governed across multiple dimensions.

## 6.1 Prompt and Context Governance
A workspace may define:
- system behaviors
- domain prompts
- specialized skills
- context/memory boundaries

### Rule
Workspace prompts and memory should not implicitly bleed into other workspaces.

---

## 6.2 Tool Governance
A workspace must define what tools are allowed.

### Examples
- privacy incident workspace may allow incident templates, risk logic, and controlled ticket update tools
- client workspace may disallow general personal tools
- ops workspace may allow only admin-grade operational tools

### Rule
Tool access should be least privilege by default.

---

## 6.3 Connector Governance
A workspace must define which external systems it may talk to.

### Examples
- client-specific document stores
- GitHub repos
- ticketing systems
- email/webhook integrations
- messaging channels

### Rule
Connectors should be scoped to workspace need, not globally exposed because it is convenient.

---

## 6.4 Routing Governance
A workspace must define what kinds of requests it is allowed to receive.

### This includes
- allowed request types
- allowed intake surfaces
- fallback behavior if routing is ambiguous
- handoff rules to other workspaces

### Rule
Routing should be explicit and explainable.

---

## 6.5 Approval Governance
A workspace should define:
- which actions need approval
- who may approve them
- how approval is requested
- what happens if approval is missing or times out

### Example
A high-risk incident workspace may require reviewer signoff before final output is released.

---

## 6.6 Retention Governance
A workspace should define:
- what records are retained
- how long they are retained
- whether outputs are ephemeral or durable
- whether audit trails need stronger persistence

### Rule
Retention policy should follow domain risk, not vague habit.

---

## 6.7 Notification Governance
A workspace should define:
- who gets notified
- through which channels
- at what severity or lifecycle point
- who receives failures/escalations/approvals

### Rule
Notifications should be scoped and intentional, not sprayed everywhere.

---

## 6.8 Output Governance
A workspace should define:
- allowed output destinations
- export restrictions
- review requirements
- whether outputs can leave the boundary automatically

### Rule
Sensitive outputs should not escape because a route forgot to care.

---

## Default Workspace Policy Shape

Each workspace should ideally have a policy object like:

```yaml
workspace:
  key: client-propharma-privacy-incidents
  trust_boundary: client-propharma
  class: client
  allowed_request_types:
    - privacy_incident
  allowed_agents:
    - privacy-incident-reporter
    - publisher
  allowed_tools_policy: policy.client_propharma_incidents
  allowed_connectors:
    - pro_pharma_ticketing
    - pro_pharma_docs
  memory_scope: workspace:client-propharma:privacy-incidents
  approval_model:
    required_for:
      - external-facing drafts
      - high-risk assessments
    reviewer_roles:
      - incident-lead
  retention:
    events: durable
    outputs: policy-based
  notifications:
    approvals: approvals-channel
    failures: ops-alerts
    completions: restricted-output-channel
  audit_level: critical
```

This is better than hidden governance logic spread across code and tribal memory.

---

## Workspace Ownership Model

Each workspace should have clear ownership.

### Required ownership roles
- **Workspace owner** — accountable for purpose and boundaries
- **Operator owner** — accountable for day-to-day execution handling
- **Policy owner** — accountable for approval/tool/connector rules

In smaller deployments these may collapse into one person, but the conceptual distinction still matters.

---

## Cross-Workspace Handoffs

Work sometimes legitimately crosses workspaces.
This must be controlled.

### Allowed handoff conditions
- destination workspace is explicitly defined
- handoff type is permitted by policy
- event is logged
- sensitive context is filtered to what is necessary
- approvals are required where policy says so

### Examples
- intake workspace → specialist workspace
- specialist workspace → publishing workspace
- reporting workspace → executive output workspace

### Rule
Handoffs are governed transitions, not free teleportation.

---

## Governance for Shared Services

Some services may be shared across workspaces, such as:
- orchestration runtime
- metrics store
- monitoring systems
- shared template engines like ForgeDeck

### Rule
Shared services are allowed, but shared services do not imply shared context.

Example:
ForgeDeck may be shared by many workspaces, but the workspace payload, approval policy, metadata, and output rules still remain boundary-specific.

---

## Visibility and Audit Requirements

Workspace governance should be visible to operators.

### Operators should be able to see
- workspace identity
- trust boundary
- allowed route types
- approval model
- active policy state
- current workload
- recent exceptions

### Audit should record
- workspace selected
- policy applied
- handoffs between workspaces
- approvals by role/person
- outputs delivered
- exceptions and overrides

---

## Override Model

Sometimes operators/admins need to override defaults.

### Override rules
- overrides must be explicit
- overrides must be attributable
- overrides must be logged
- high-risk overrides may require second approval

### Examples
- rerouting a job
- granting temporary connector access
- releasing a blocked output

---

## Workspace Lifecycle

Workspaces should have a lifecycle.

### Recommended states
- proposed
- active
- restricted
- archived
- retired

### Why
This supports governance over time and avoids dead or stale workspaces lingering invisibly.

---

## MVP Governance Direction

A sensible initial MVP should support:
- explicit workspace registry
- trust boundary field per workspace
- allowed tools policy per workspace
- allowed connectors list per workspace
- approval model per workspace
- notification routes per workspace
- audit level per workspace
- visible operator-facing workspace metadata

### Good first workspace classes to support
- internal project
- client
- personal/lab
- ops core

---

## Non-Goals

Workspace governance is not about:
- making every small variation a new workspace unnecessarily
- burying the system in policy bureaucracy
- creating compliance theatre with no operational effect

It is about making boundaries real and useful.

---

## Recommended Next Docs

1. routing and policy model specification
2. execution event and audit model
3. operator control surface specification
4. roadmap and implementation backlog

---

## Final Recommendation

ForgeOrchestrate should treat workspaces as governed operating domains, not casual containers.

That means every workspace should carry explicit rules for:
- boundary
- tools
- connectors
- memory
- approvals
- retention
- notifications
- outputs
- audit

This is the architecture that keeps the estate structured, trustworthy, and actually controllable at scale.
