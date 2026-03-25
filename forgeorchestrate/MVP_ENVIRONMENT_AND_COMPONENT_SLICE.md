# ForgeOrchestrate — MVP Environment and Component Slice

## Status
Draft

## Purpose

This document defines the first real buildable slice of ForgeOrchestrate.

At this point the product has enough philosophy, governance, and architecture behind it. What it now needs is a disciplined answer to a very practical question:

**What exactly are we building first?**

This spec answers that.

---

## MVP Thesis

ForgeOrchestrate MVP should prove one thing clearly:

**AI work across multiple workspaces and workflows can be routed, governed, observed, and controlled through one coherent orchestration layer above OpenClaw.**

The MVP does not need to solve the entire estate.
It needs to prove the command layer works.

---

## MVP Goals

### Primary goals
- route requests through explicit workspace-aware logic
- enforce trust-boundary and workspace policy rules
- track execution from intake to output
- support approval-gated work where needed
- give operators visibility into active, blocked, failed, and review-bound work
- connect to OpenClaw as the execution runtime

### Secondary goals
- establish the product’s operator feel
- create reusable internal architecture for later expansion
- avoid overexposing the system publicly

---

## MVP Environment

### Recommended environment
**Internal / development-first deployment on titan**

### Why
- lower risk
- easier iteration
- easier policy/routing validation
- avoids pretending client-safe production exists before the system is ready

### Exposure rule
Keep ForgeOrchestrate internal behind the existing ingress/reverse-proxy pattern.
Do not create a second casual exposure path.

---

## First Supported Trust Boundaries

The MVP should support a small set of workspace boundary classes.

### Include in MVP
1. **internal-projects**
2. **personal-lab / forge-dev**
3. **ops-core**

### Defer for later
- full client production boundaries
- multi-client scaled tenancy
- broad federated environment management

### Why
The product should prove governance and routing on safer internal/workbench domains before claiming client-grade confidence.

---

## First Supported Workspace Classes

### MVP workspace classes
- internal project workspace
- personal/lab workspace
- operations workspace

### Out of scope for first slice
- many client-specific production workspaces
- highly customized industry-specific policy packs

---

## First Supported Request Classes

ForgeOrchestrate MVP should support a limited request taxonomy.

### Include
- general project intake
- research / analysis request
- reporting request
- operational/admin request
- approval-gated output review request

### Optional if easy
- vendor assessment route
- privacy incident route

### Why
These are enough to prove:
- workspace routing
- policy selection
- approval behavior
- run visibility
- output handling

Without forcing every domain workflow into MVP scope.

---

## First Supported Intake Sources

### Include in MVP
1. **internal API / web-app initiated requests**
2. **Discord-routed requests** (through ForgeDiscord or a simplified source adapter)
3. **internal triggers / scheduled jobs**

### Defer
- Telegram
- many heterogeneous external forms
- broad multi-channel federation

### Why
These three are enough to prove:
- human-driven intake
- orchestrated/chat-driven intake
- automation/schedule-driven intake

---

## Core MVP Components

The MVP should build these components first.

## 8.1 Workspace Registry
Purpose:
- authoritative store of workspace identity and governance metadata

### Must support
- workspace key
- trust boundary
- workspace class
- allowed request types
- allowed tools/connectors/models policy refs
- approval model
- retention rules
- output controls
- notification routes
- audit level

---

## 8.2 Policy Engine
Purpose:
- resolve what a route is allowed to do

### Must support
- workspace policy loading
- trust-boundary restrictions
- approval trigger evaluation
- connector/tool/model restrictions
- output restrictions

---

## 8.3 Routing Engine
Purpose:
- classify request and choose workspace/workflow/agent path

### Must support
- source-aware routing
- request classification
- confidence / ambiguity handling
- fallback to operator review
- deterministic route record creation

---

## 8.4 Execution Adapter to OpenClaw
Purpose:
- hand governed work to OpenClaw runtime

### Must support
- execution payload generation
- workspace/workflow linkage
- event/status feedback path
- policy-selected capability constraints carried downstream

---

## 8.5 Execution Event Store
Purpose:
- preserve request/run/event/output history

### Must support
- request record
- run record
- event history
- output disposition
- approval events
- exception events

---

## 8.6 Approval Engine / Review State
Purpose:
- represent and manage approval-gated work

### Must support
- approval requested
- approval granted/rejected
- rework requested
- timeout/escalation path

---

## 8.7 Operator Control Surface (MVP UI)
Purpose:
- give operators the minimum useful command view

### MVP screens
- Overview
- Runs
- Workspaces
- Approvals
- Alerts

### Deferred detail views
- deeper analytics
- advanced graph views
- predictive insights

---

## MVP Screen Definitions

## 9.1 Overview
Must show:
- active runs
- queued runs
- failed runs
- approvals pending
- recent completions
- latest critical alert

### Goal
Answer: what needs attention now?

---

## 9.2 Runs
Must show:
- list of recent/active runs
- state
- workspace
- workflow
- agent path summary
- duration / age
- drill-down entry into run detail

### Goal
Answer: what happened in each run?

---

## 9.3 Workspaces
Must show:
- workspace identity
- trust boundary
- active load
- policy summary
- recent exceptions

### Goal
Answer: which governed domains are active and healthy?

---

## 9.4 Approvals
Must show:
- pending approvals
- trigger reason
- linked run/output
- age / urgency
- approve / reject / rework actions

### Goal
Answer: what is waiting on human decision?

---

## 9.5 Alerts
Must show:
- failures
- policy violations
- blocked outputs
- approval timeouts
- connector failures

### Goal
Answer: what is broken or risky right now?

---

## Deferred from MVP

Do not build these in the first slice unless something surprisingly easy falls out naturally.

### Defer
- full client-scale multi-tenant estate management
- deep analytics dashboards
- predictive failure warnings
- anomaly detection
- replay/simulation mode
- large graph-based agent maps as main UI
- broad external exposure
- every intake channel under the sun

### Why
The MVP should prove orchestration and control, not perform ambition.

---

## Suggested MVP Request Flow

1. Request enters from API, Discord, or scheduler
2. Request is classified
3. Workspace is selected
4. Policy is applied
5. Workflow + agent path resolved
6. OpenClaw execution starts
7. Events are recorded throughout
8. Approval is requested if needed
9. Output is released or held according to policy
10. Operator surfaces reflect state throughout

This is the cleanest “first loop” to prove the product.

---

## Suggested Initial Data Models

### Must exist in MVP
- workspace
- policy
- request
- route decision
- run
- event
- approval
- output
- alert

### Why
These are the minimum objects needed for governed orchestration with visibility.

---

## Suggested MVP Build Order

1. workspace registry
2. policy object model
3. request classification + route decision model
4. OpenClaw execution adapter
5. event store + run state model
6. approval model
7. overview / runs / approvals / alerts UI
8. workspace screen

This gets the command layer functional before cosmetic expansion.

---

## Success Criteria for MVP

The MVP is successful if:
- requests can be routed into the correct workspace
- trust boundaries are enforced
- operators can see active, failed, blocked, and review-bound work
- approvals actually gate outputs/actions when required
- every run leaves a visible event trail
- OpenClaw execution is governable through ForgeOrchestrate rather than directly opaque

---

## Recommended Immediate Next Step After This Doc

1. translate MVP slice into concrete screen definitions and component contracts
2. define workspace registry schema and route decision schema concretely
3. create implementation skeleton for ForgeOrchestrate

---

## Final Recommendation

ForgeOrchestrate MVP should not try to be the entire AI estate on day one.

It should prove a sharper claim:

**Requests can enter through controlled surfaces, be routed into governed workspaces, execute through OpenClaw under explicit policy, and remain visible and controllable from one premium operator environment.**

That is enough to make the product real.
