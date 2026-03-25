# ForgeDiscord — Routing Matrix v1.0

## Purpose

This document defines how ForgeDiscord routes requests from Discord into the correct workspace, workflow, agent, permission scope, and output pattern.

This is the backbone of the system.
Without a routing matrix, Discord is just a prettier way to create confusion.

---

## Routing Model

Each incoming request must resolve the following:
- trust boundary / server
- source channel
- command or intake type
- requester role
- request category
- destination workspace
- workflow ID
- primary agent
- reviewer role (if needed)
- approval requirement
- allowed tools / allowed context
- output pattern
- audit level

---

## Routing Priority Order

When processing an incoming request, apply routing in this order:

1. **Trust boundary / server**
2. **Channel / category**
3. **Slash command or explicit workflow trigger**
4. **Requester role**
5. **Content classification / tags**
6. **Fallback operator review if ambiguity remains**

This means server context always outranks user wording.
A personal-lab request should not accidentally route into client workflows because someone typed “incident” in a chatty way.

---

## Core Routing Fields

Every job record should store:
- `job_id`
- `guild_id`
- `guild_key`
- `channel_id`
- `channel_key`
- `thread_id`
- `request_type`
- `command_name`
- `requester_id`
- `requester_role`
- `trust_boundary`
- `workspace_key`
- `workflow_id`
- `primary_agent`
- `reviewer_role`
- `approval_required`
- `allowed_tools_policy`
- `allowed_memory_scope`
- `output_template`
- `audit_level`
- `status`

---

## Trust Boundary Layer

### Rule
A request can only route within the trust boundary of its server unless an explicit cross-boundary policy exists.

### Recommended server keys
- `forge-dev`
- `forge-projects`
- `client-propharma`
- `client-hsbc`

### Example
If `guild_key = client-propharma`, then:
- allowed workspaces are only ProPharma-approved workspaces
- only client-propharma routing config applies
- only approved tools/context for that client apply

---

## MVP Routing Matrix

## A. Development / Internal Server

### Guild: `forge-dev`
Purpose:
- internal development
- architecture testing
- workflow refinement
- non-client operations

---

### Route A1 — Privacy incident intake
| Field | Value |
|------|-------|
| Guild | `forge-dev` |
| Channel | `#intake-incidents` |
| Trigger | `/incident new` |
| Request type | `privacy_incident` |
| Workspace | `privacy-incidents` |
| Workflow | `incident-triage-v1` |
| Primary agent | `Privacy Incident Reporter` |
| Reviewer role | `Reviewer` or `Incident Lead` |
| Approval required | `true` when risk >= configured threshold |
| Allowed tools policy | incident templates, jurisdiction checker, risk engine, publishing templates |
| Allowed memory scope | `workspace:privacy-incidents` |
| Output template | triage summary + missing info + recommended next actions + draft statement |
| Audit level | `high` |
| Output destination | thread + `#completed-jobs` or `#awaiting-review` |

### Notes
- modal intake required
- thread created immediately
- if mandatory fields missing, status becomes `awaiting_input`
- if risk threshold exceeded, route to `#approvals` / `#awaiting-review`

---

### Route A2 — Vendor assessment intake
| Field | Value |
|------|-------|
| Guild | `forge-dev` |
| Channel | `#intake-assessments` |
| Trigger | `/vendor assess` |
| Request type | `vendor_assessment` |
| Workspace | `vendor-assessments` |
| Workflow | `vendor-review-v1` |
| Primary agent | `Privacy Vendor Assessor` |
| Reviewer role | `Reviewer` |
| Approval required | `optional / policy-based` |
| Allowed tools policy | assessment templates, transfer-risk logic, questionnaire generator |
| Allowed memory scope | `workspace:vendor-assessments` |
| Output template | assessment summary + gaps + recommended diligence questions + recommendation |
| Audit level | `high` |
| Output destination | thread + `#completed-jobs` |

### Notes
- modal intake required
- follow-up questions allowed in thread
- final result can post a concise summary with longer artifact linked separately

---

### Route A3 — General project intake
| Field | Value |
|------|-------|
| Guild | `forge-dev` |
| Channel | `#intake-projects` |
| Trigger | `/job create` |
| Request type | `general_project` |
| Workspace | `internal-projects` or Forge domain route |
| Workflow | `general-intake-v1` |
| Primary agent | `Orchestrator` |
| Reviewer role | `Operator` when needed |
| Approval required | `false` by default |
| Allowed tools policy | project intake, task creation, workspace routing, summary tools |
| Allowed memory scope | `workspace:internal-projects` or routed Forge workspace |
| Output template | created job summary + route chosen + next actions |
| Audit level | `medium` |
| Output destination | thread + `#completed-jobs` |

### Notes
- can route onward to ForgeHome / ForgeCar / ForgeGarden / internal-projects depending on intake fields
- ambiguity falls back to operator review

---

### Route A4 — Catch-all intake
| Field | Value |
|------|-------|
| Guild | `forge-dev` |
| Channel | `#intake-general` |
| Trigger | natural language or `/job create` |
| Request type | `unclassified` → classified |
| Workspace | determined by classifier/router |
| Workflow | classifier-led |
| Primary agent | `Orchestrator` |
| Reviewer role | `Operator` if ambiguous |
| Approval required | policy-based |
| Allowed tools policy | minimal routing tools until classified |
| Allowed memory scope | minimal until destination selected |
| Output template | classification result + route decision + thread status |
| Audit level | `medium` |
| Output destination | thread |

### Notes
- use conservative routing
- if unclear, ask for structured clarification instead of guessing

---

## B. Future Client Server Example — ProPharma

### Guild: `client-propharma`
Purpose:
- privacy/compliance workflows for ProPharma trust boundary

### Route B1 — Client privacy incident
| Field | Value |
|------|-------|
| Guild | `client-propharma` |
| Channel | `#intake-incidents` |
| Trigger | `/incident new` |
| Request type | `privacy_incident` |
| Workspace | `client-propharma:privacy-incidents` |
| Workflow | `incident-triage-v1` |
| Primary agent | `Privacy Incident Reporter` |
| Reviewer role | `ProPharma Incident Lead` |
| Approval required | `true` |
| Allowed tools policy | client-approved incident tools only |
| Allowed memory scope | `workspace:client-propharma:privacy-incidents` |
| Output template | incident triage summary + actions + draft update |
| Audit level | `critical` |
| Output destination | thread + restricted outputs/review channels |

### Key rule
No routing from this server may reach internal/personal workspaces by default.

---

## Role-Based Routing Adjustments

Routing can be influenced by requester role, but only inside allowed boundaries.

### Requester
- can submit workflows
- cannot override route
- sees limited admin detail

### Operator
- can re-route manually where permitted
- can escalate ambiguous requests
- can invoke operator-only commands

### Reviewer
- can review or reject outputs
- can trigger rework state
- should not silently re-route sensitive requests without audit entry

### Admin
- can override route during troubleshooting
- override must be logged to audit trail

---

## Approval Decision Matrix

| Request Type | Default Approval Requirement | Notes |
|-------------|------------------------------|-------|
| Privacy incident | Conditional / often yes | Required for high-risk outputs, external-facing drafts |
| Vendor assessment | Optional / policy-based | Approval may be required for external sharing |
| General project intake | No | Unless route enters sensitive workflow |
| Sensitive publishing action | Yes | Always review-gated |

---

## Allowed Tools Policy Model

Each route should map to an explicit tool policy.

### Example policies
- `policy.incident_triage`
- `policy.vendor_assessment`
- `policy.general_project_intake`
- `policy.publisher_review`

### Principle
A route should expose only the tools needed for that workflow.

Examples:
- incident workflow should not suddenly gain unrelated household/project tools
- general project intake should not access client incident memory by mistake

---

## Allowed Memory Scope Model

Each route must define memory/context scope explicitly.

### Example scopes
- `workspace:privacy-incidents`
- `workspace:vendor-assessments`
- `workspace:internal-projects`
- `workspace:client-propharma:privacy-incidents`

### Rule
No route should inherit broad/global context by accident.

---

## Output Pattern Matrix

| Request Type | Thread Output | Channel Output | Review Surface |
|-------------|---------------|----------------|----------------|
| Privacy incident | full working conversation + status | completion/review summary | `#approvals`, `#awaiting-review` |
| Vendor assessment | structured updates + final summary | concise result post | optional review |
| General project intake | route chosen + next actions | optional completion note | usually none |

### Principle
- detailed working state in thread
- concise summary in shared channels
- no channel spam for every intermediate step

---

## Audit Level Model

### `medium`
Used for:
- general internal project intake
- low-risk coordination requests

### `high`
Used for:
- vendor assessments
- structured compliance workflows

### `critical`
Used for:
- incidents
- high-sensitivity client workflows
- any route involving regulated or sensitive actions

Audit level determines:
- event verbosity
- retention expectations
- approval strictness
- review visibility

---

## Fallback / Ambiguity Rules

If routing is ambiguous:
1. do not guess if the guess crosses a sensitive boundary
2. keep route in a safe minimal state
3. ask for clarification in thread
4. optionally escalate to Operator review
5. record ambiguity event in routing log

### Examples of ambiguity
- user submits vendor-style request in `#intake-general`
- natural language references multiple domains
- requested workspace does not exist
- requester lacks permissions for desired route

---

## Error Routing

If normal routing fails, route to an explicit error path.

### Error route behavior
- create or keep thread
- mark status `failed` or `awaiting_operator`
- post explanation
- log to `#alerts` and `#routing-log` as appropriate
- preserve original request payload reference

---

## Suggested Config Representation

A practical config structure could look like:

```yaml
routes:
  - guild: forge-dev
    channel: intake-incidents
    command: incident.new
    request_type: privacy_incident
    workspace: privacy-incidents
    workflow: incident-triage-v1
    primary_agent: privacy-incident-reporter
    reviewer_role: reviewer
    approval_required: conditional
    allowed_tools_policy: policy.incident_triage
    allowed_memory_scope: workspace:privacy-incidents
    output_template: incident-triage-summary
    audit_level: high
```

This is preferable to hardcoding every rule deep inside bot logic.

---

## MVP Required Routes

The MVP must support at least these:
1. `forge-dev / #intake-incidents / /incident new`
2. `forge-dev / #intake-assessments / /vendor assess`
3. `forge-dev / #intake-projects / /job create`
4. `forge-dev / #intake-general / natural language fallback`

Anything else can be deferred until the first routing model is proven stable.

---

## Final Recommendation

The routing matrix should be treated as a first-class configuration artifact, not an afterthought.

Best practice:
- server decides trust boundary
- channel narrows intent
- command specifies workflow entry
- role constrains permission
- content only fine-tunes inside that safe boundary

That gives you routing that is explainable, auditable, and much less likely to become haunted.
