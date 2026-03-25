# ForgeOrchestrate — Operator Control Surface Specification v1.0

## Status
Draft

## Purpose

This document defines the operator-facing control surfaces for ForgeOrchestrate.

If ForgeOrchestrate is the command layer for the AI estate, the operator control surface is where that command becomes usable.

It is the layer that lets a human see:
- what is entering the system
- where work is going
- what is blocked
- what needs approval
- what failed
- what completed
- what can be trusted

Without this, the orchestration layer remains intellectually interesting but operationally half-blind.

---

## Operator Surface Thesis

The operator surface should not be a dashboard made of panic.

It should feel:
- calm
- precise
- high-signal
- trust-aware
- operationally serious
- dense in capability, light in appearance

### The operator should be able to answer quickly
- what needs attention now?
- what is blocked?
- what is awaiting review?
- what failed?
- what is happening inside a workspace?
- why did a run behave the way it did?

---

## Primary Operator Views

ForgeOrchestrate MVP should define five core operator views.

1. Request / Work Queue
2. Approval Inbox
3. Run Detail View
4. Workspace Overview
5. Alerts / Exceptions View

These are the minimum viable control surfaces.

---

## 3.1 Request / Work Queue

### Purpose
Give the operator a clear picture of active work across the estate.

### Questions it answers
- what just arrived?
- what is in progress?
- what is blocked?
- what is waiting for input?
- what is awaiting review?
- what needs intervention first?

### Data shown per item
- request ID / run ID
- source
- workspace
- workflow
- primary agent
- current state
- priority / severity
- approval state if relevant
- age / last updated
- trust boundary indicator

### Suggested groupings
- New
- In Progress
- Awaiting Input
- Awaiting Review
- Blocked
- Failed / Escalated

### Key actions
- open run detail
- request clarification
- re-route (if allowed)
- escalate
- filter by workspace / trust boundary / state

---

## 3.2 Approval Inbox

### Purpose
Show work that requires human decision before proceeding or releasing output.

### Questions it answers
- what is waiting on me or a reviewer?
- why is approval required?
- what happens if I approve or reject?
- how urgent is this?

### Data shown per approval item
- approval request ID
- linked request/run/output
- workspace
- approval trigger reason
- reviewer role required
- current SLA / age
- output classification
- summary of proposed output/action

### Required actions
- approve
- reject
- request rework
- escalate
- view supporting context

### Design rule
Approval inbox should emphasize confidence and context, not only button rows.
The operator should understand what they are approving.

---

## 3.3 Run Detail View

### Purpose
Provide a reconstructable, inspectable view of one run from intake to disposition.

### Questions it answers
- what happened in this run?
- why did it route this way?
- which agents/models/tools were used?
- where did it pause/fail?
- what outputs were produced?
- what approvals or overrides occurred?

### Sections
#### A. Summary
- request ID / run ID
- source
- workspace
- workflow
- primary agent
- current state
- trust boundary
- created / updated timestamps

#### B. Route and policy summary
- route selected
- policy set applied
- allowed tools/connectors/models
- approval model applied
- override flags if any

#### C. Event timeline
- chronological event stream
- state changes
- approvals
- failures
- retries
- output events

#### D. Outputs
- output artifacts/messages
- delivery state
- restrictions/release state

#### E. Exceptions and overrides
- exceptions triggered
- operator/admin overrides
- reason and actor attribution

### Key actions
- retry / rerun where allowed
- re-route where allowed
- trigger escalation
- inspect audit chain
- open workspace view

---

## 3.4 Workspace Overview

### Purpose
Give the operator a clear view of one workspace as a governed operational domain.

### Questions it answers
- what is this workspace responsible for?
- what is its current workload?
- what policies apply here?
- what tools/connectors are allowed?
- are there recent failures or exceptions?
- is this workspace healthy?

### Data shown
- workspace identity
- trust boundary
- workspace class
- active workload counts
- common request types
- allowed tool/connectors summary
- approval model summary
- audit level
- recent failures / exceptions
- recent outputs / reviews / escalations

### Key actions
- filter active work to this workspace
- inspect policy summary
- inspect recent exceptions
- inspect pending approvals for the workspace

---

## 3.5 Alerts / Exceptions View

### Purpose
Surface urgent operational problems and anomalies.

### Questions it answers
- what is failing right now?
- what is blocked or degraded?
- what needs intervention?
- is a policy violation occurring?

### Alert categories
- routing failure
- policy violation
- approval timeout
- connector failure
- execution failure
- blocked output
- repeated retry loop
- cross-boundary risk / override event

### Data shown per alert
- severity
- workspace
- affected run/request
- summary
- timestamp
- whether acknowledged
- whether escalated

### Key actions
- acknowledge
- open run detail
- escalate
- inspect related workspace/policy

---

## Supporting Operator Surfaces

These may follow after the core five views.

## 4.1 Search / Trace View
Used to find:
- request IDs
- run IDs
- workspace history
- approval history
- outputs by classification or state

## 4.2 Reporting / Summary View
Used for:
- operational summaries
- workload snapshots
- approval bottlenecks
- failure trends
- workspace activity summaries

## 4.3 Policy / Configuration Inspection View
Used by more advanced operators/designers to inspect:
- workspace policy
- route logic
- allowed capabilities
- approval triggers

---

## Information Hierarchy Rules

The control surface should privilege signal over decorative clutter.

### Operators need to see first
1. attention-worthy work
2. blocked/review-needed items
3. failures/exceptions
4. recent changes
5. contextual policy/route detail on drill-down

### Avoid
- raw event spam by default
- equal visual weight for trivial and urgent information
- pretty charts that replace operational clarity

---

## Visual Design Principles

ForgeOrchestrate should look like a premium command environment.

### It should feel
- architectural
- restrained
- premium
- dense but breathable
- confidence-inducing

### It should not feel like
- an incident dashboard in permanent panic mode
- a BI tool from 2017
- a developer debug page pretending to be a product
- dashboard soup

### Visual implications
- dark-forward command surface
- premium spacing
- clear grouping
- restrained semantic color
- role-aware status indicators
- crisp hierarchy

---

## State and Signal Design

The UI should clearly represent state.

### Important state categories
- queue state
- run state
- approval state
- output disposition state
- workspace health state
- alert severity state

### Rule
The operator should never need to infer whether something is waiting, blocked, approved, or failed from ambiguous wording.

---

## Filtering and Segmentation

The operator surface should support filtering by:
- workspace
- trust boundary
- request type
- current state
- priority/severity
- approval status
- agent/workflow
- time window

### Why
Operators need to move between estate-wide oversight and workspace-specific control quickly.

---

## Action Model

Operator surfaces should not just display data. They should support controlled action.

### Example actions
- inspect details
- request clarification
- retry / rerun
- re-route
- escalate
- approve / reject / rework
- acknowledge alert
- open related workspace policy

### Rule
Actions must respect policy and role permissions.
The control surface should not become a loophole that bypasses governance.

---

## Relationship to Roles

### Operator
Primary user of queue, alerts, run detail, and workspace overview.

### Reviewer
Primary user of approval inbox and approval context views.

### Designer / Admin
Needs deeper access to policy/config inspection and override history.

### Stakeholder
May consume summary/reporting surfaces, not raw operational controls.

---

## MVP Control Surface Direction

A sensible MVP should include:
- request/work queue
- approval inbox
- run detail view
- workspace overview
- alerts/exceptions view

### MVP goal
Not to display everything.
To make the most important work, failures, and approvals visible and actionable.

---

## Surface-to-Model Mapping

### Queue view uses
- request classification
- run state
- trust boundary
- workspace
- age/priority

### Approval inbox uses
- approval model
- output disposition
- reviewer role
- supporting summary

### Run detail uses
- route decision record
- event history
- audit data
- output state

### Workspace overview uses
- workspace registry
- policy object
- recent runs/exceptions
- workload summaries

### Alerts view uses
- exception events
- severity model
- workspace/run linkage

---

## Non-Goals

The operator control surface is not intended to:
- replace all analytics/reporting forever
- expose every low-level internal event all the time
- bypass routing/policy/approval logic
- turn operators into accidental shadow developers

It is a command surface, not a debugging junk drawer.

---

## Recommended Next Step After This Spec

1. define MVP environment and component slice
2. expand ForgeOrchestrate tasks in Forge Pipeline
3. identify first operator workflows to simulate/test

---

## Final Recommendation

ForgeOrchestrate’s operator control surface should be treated as a first-class product layer.

If ForgeOrchestrate is the bridge above the engine room, this is where operators stand to steer, inspect, approve, intervene, and trust what the system is doing.

That means the surface must be:
- calm
- high-signal
- policy-aware
- action-capable
- audit-connected
- worthy of the role it claims to play
