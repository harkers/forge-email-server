# ForgeOrchestrate — Execution Event and Audit Model v1.0

## Status
Draft

## Purpose

This document defines how ForgeOrchestrate should record, expose, and reason about execution history.

Execution visibility is one of the main reasons ForgeOrchestrate exists.
If the system cannot explain what happened, why it happened, who approved it, which route it took, and what came out the other end, then the orchestration layer is mostly theatre.

This model provides the spine for:
- execution oversight
- auditability
- operator trust
- exception handling
- performance analysis
- governance assurance

---

## Core Thesis

Every meaningful stage in a run should emit an event.

Those events should be:
- attributable
- time-stamped
- linked to request/workspace/route/run identity
- suitable for audit and operator visibility
- rich enough to reconstruct the path of execution

### Principle
You should be able to answer, from event history alone:
- what request came in?
- where did it go?
- what policy applied?
- which agents/tools/models were used?
- where did it fail or pause?
- who approved what?
- what output was produced?
- what was the final disposition?

---

## Core Objects

The execution and audit model should center on four core objects.

## 3.1 Request
The intake-side identity of work entering the estate.

### Typical request fields
- request_id
- source_system
- source_reference
- requester_id
- requester_role
- trust_boundary
- request_type
- created_at

---

## 3.2 Run
A concrete execution instance of a request.

### Why this matters
A single request may have:
- retries
- reruns
- escalated reruns
- rework cycles

### Typical run fields
- run_id
- request_id
- workspace_key
- workflow_id
- primary_agent
- route_id
- current_status
- started_at
- ended_at

---

## 3.3 Event
An immutable or append-oriented record of something that happened during the request/run lifecycle.

### Typical event fields
- event_id
- run_id
- request_id
- event_type
- timestamp
- actor_type
- actor_id_or_name
- summary
- metadata

---

## 3.4 Output
A produced artifact, message, report, update, or decision-ready result.

### Typical output fields
- output_id
- run_id
- output_type
- classification
- delivery_state
- created_at
- destination
- restricted_flag

---

## Event Model

ForgeOrchestrate should emit events throughout the lifecycle.

### Event classes
1. Intake events
2. Routing events
3. Policy events
4. Execution events
5. Approval events
6. Output events
7. Exception events
8. Closure events

---

## Intake Events

These describe how work entered the system.

### Examples
- `request.created`
- `request.validated`
- `request.classified`
- `request.awaiting_input`

### Useful metadata
- source system
- channel/form/API reference
- requester identity
- classification result
- confidence level

---

## Routing Events

These describe routing and ownership decisions.

### Examples
- `route.selected`
- `workspace.assigned`
- `workflow.assigned`
- `agent.primary_assigned`
- `agent.support_assigned`
- `route.ambiguous`
- `route.override_applied`

### Useful metadata
- route ID
- candidate routes
- final workspace/workflow
- confidence
- override actor

---

## Policy Events

These describe governance and control decisions.

### Examples
- `policy.applied`
- `policy.denied`
- `approval.required`
- `connector.denied`
- `tool.policy_resolved`
- `model.policy_resolved`

### Useful metadata
- policy set ID
- approval trigger reason
- denied capability
- memory scope
- allowed tool/model policy

---

## Execution Events

These describe what happened during work execution.

### Examples
- `run.started`
- `run.state_changed`
- `agent.handoff`
- `model.selected`
- `tool.invoked`
- `tool.failed`
- `run.retry_scheduled`
- `run.retry_started`
- `run.blocked`
- `run.resumed`

### Useful metadata
- previous/new state
- agent identity
- selected model
- tool name
- retry count
- block reason

---

## Approval Events

These describe review and release controls.

### Examples
- `approval.requested`
- `approval.granted`
- `approval.rejected`
- `approval.rework_requested`
- `approval.escalated`
- `approval.timed_out`

### Useful metadata
- approval model ID
- reviewer role
- reviewer identity
- reason for approval trigger
- decision note

---

## Output Events

These describe created results and delivery decisions.

### Examples
- `output.created`
- `output.restricted`
- `output.awaiting_release`
- `output.delivered`
- `output.delivery_denied`
- `output.archived`

### Useful metadata
- output type
- destination
- classification
- delivery method
- release approval status

---

## Exception Events

These describe things going wrong or requiring intervention.

### Examples
- `exception.routing_failure`
- `exception.policy_violation`
- `exception.connector_failure`
- `exception.execution_failure`
- `exception.operator_intervention_required`

### Useful metadata
- severity
- reason
- impacted workspace
- impacted run
- operator escalation path

---

## Closure Events

These describe how work concluded.

### Examples
- `run.completed`
- `run.failed`
- `run.cancelled`
- `run.archived`
- `run.terminated`

### Useful metadata
- final disposition
- duration
- delivery state
- closure actor/source

---

## Run State Model

A run should move through explicit states.

### Recommended states
- `new`
- `validating`
- `routed`
- `in_progress`
- `awaiting_input`
- `awaiting_review`
- `approved`
- `completed`
- `failed`
- `blocked`
- `cancelled`
- `archived`

### State transition rule
Every state change should emit a `run.state_changed` event that includes:
- old state
- new state
- reason
- actor/source
- timestamp

---

## Actor Attribution Model

Every meaningful event should record who or what caused it.

### Actor types
- `user`
- `bot`
- `system`
- `agent`
- `operator`
- `reviewer`
- `admin`
- `scheduler`
- `integration`

### Why this matters
Without actor attribution, audit trails turn into decorative timestamps.

---

## Audit Requirements

Audit is not just logging more lines. It is logging the right things in a reconstructable way.

### Audit requirements
- append-oriented event history
- event IDs
- run/request linkage
- actor attribution
- workspace and trust-boundary linkage
- route/policy traceability
- approval traceability
- output disposition traceability

### Critical rule
Any override, reroute, approval, or sensitive output release should be attributable to a specific actor or actor role.

---

## Minimum Event Record Shape

```json
{
  "event_id": "evt_...",
  "request_id": "req_...",
  "run_id": "run_...",
  "workspace_key": "client-propharma:privacy-incidents",
  "trust_boundary": "client-propharma",
  "event_type": "approval.granted",
  "timestamp": "2026-03-24T20:35:00Z",
  "actor_type": "reviewer",
  "actor_id_or_name": "incident-lead",
  "summary": "Approval granted for external-facing incident draft",
  "metadata": {
    "approval_model": "high-risk-incident",
    "output_id": "out_123",
    "delivery_state": "approved_for_release"
  }
}
```

---

## Event Storage Principles

### Recommended principles
- append-first
- immutable where feasible
- queryable by request, run, workspace, boundary, agent, event type, and time
- suitable for operator views and later analytics

### Useful query slices
- all events for a run
- all failed runs in a workspace
- all approval events in a trust boundary
- all reroutes/overrides by actor
- all outputs awaiting release

---

## Visibility Layers

Events should support different visibility surfaces.

### 14.1 Operator visibility
Operators need:
- current run state
- recent events
- failures
- approvals pending
- escalations

### 14.2 Reviewer visibility
Reviewers need:
- approval request context
- relevant run/output summary
- prior decision history where appropriate

### 14.3 Stakeholder visibility
Stakeholders generally need:
- concise completion/review summaries
- not raw event firehose detail

### 14.4 Audit/admin visibility
Admins/auditors need:
- full event chain
- override and approval history
- route/policy traceability

---

## Derived Oversight Signals

The event model should support higher-level oversight signals.

### Examples
- repeated workflow failure rate
- most common approval bottleneck
- most frequently blocked workspaces
- most expensive model paths
- routes with the most overrides
- outputs most often held for review

These do not replace raw events. They emerge from them.

---

## Output Disposition Model

Every output should have a controlled delivery state.

### Example states
- created
- restricted
- awaiting_review
- approved_for_release
- delivered
- denied
- archived

### Rule
Output state should be independent enough to express that a run succeeded technically while the output is still withheld pending approval.

---

## Override and Exception Audit

Overrides and exceptions deserve special treatment.

### Must always be logged
- reroutes by operator/admin
- policy overrides
- restricted connector use
- output release override
- emergency or exceptional approvals

### Additional metadata should include
- reason
- actor
- original state
- resulting state
- scope and duration of override if applicable

---

## MVP Event and Audit Direction

A sensible MVP should support at least:
- request created
- route selected
- workspace/workflow assigned
- run started
- run state changed
- approval requested/granted/rejected
- output created/delivered
- run completed/failed
- exception events
- override events

That is enough to make the system explainable from day one.

---

## Non-Goals

This model is not intended to:
- log every microscopic token-level behavior
- become an unreadable firehose with no summary layer
- replace all higher-level reporting needs

It exists to preserve reconstructable execution truth.

---

## Recommended Next Docs

1. operator control surface specification
2. MVP environment and component slice
3. reporting / oversight signal model

---

## Final Recommendation

ForgeOrchestrate should treat execution events and audit history as first-class product infrastructure.

If the system cannot reconstruct the path from request to result — including route, policy, approvals, failures, and outputs — then it cannot claim to be an orchestration layer with real trustworthiness.

The event model is how ForgeOrchestrate earns that trust.
