# Workspace Configuration Improvement Plan

Status: In Progress
Date: 2026-03-28
Last updated: 2026-03-28

## Completed

### Phase 1 — Canonical Control Layer ✅
- ✅ Workspace registry created (`REGISTRY.md`)
- ✅ Memory-promotion rule added to root `AGENTS.md`
- ✅ Clear boundary between `MEMORY.md`, `TOOLS.md`, and project docs established

### Phase 2 — Governance Model Clarification ✅
- ✅ Human governance vs AI operating roles rule added to root `AGENTS.md`
- ✅ Planning vs delivery separation rule added to root `AGENTS.md`
- ⏳ Future project doc alignment (ongoing, not a one-time deliverable)

### Phase 3 — Project Lifecycle Standardisation ✅
- ✅ Minimum serious-project pack defined in root `AGENTS.md`
- ✅ DevForge Project Foundry established as default template authority

### Phase 4 — Workspace Classification ✅
- ✅ Workspaces classified (planning, active, live, dormant) in `REGISTRY.md`
- ✅ State reflected in central registry
- ✅ Ambiguity flags noted for cleanup

## Pending

### Phase 5 — Environment Health and Drift Control
- ⏳ Define lightweight environment audit/heartbeat checklist
- ⏳ Periodic validation of:
  - Quarto
  - Forge Pipeline API
  - OpenClaw Usage Dashboard
  - Local model lanes
  - Stale paired devices
  - Memory search configuration

## Purpose

Turn current workspace configuration observations into a phased improvement plan focused on clarity, governance, consistency, and lower entropy as the workspace estate grows.

## Phase 1 — Canonical Control Layer

**Goal:** reduce ambiguity about what is authoritative.

### Deliverables
- create a workspace registry
- define a clear boundary between `MEMORY.md`, `TOOLS.md`, and project docs
- add a short memory-promotion rule to root `AGENTS.md`

### Outcomes
- easier navigation
- less duplication
- better long-term recall discipline

## Phase 2 — Governance Model Clarification

**Goal:** make the operating model explicit across the whole workspace.

### Deliverables
- add a root rule that distinguishes human governance roles from AI operating roles
- add a root rule separating planning flow from delivery flow
- align future project docs to those distinctions
- make approval and accountability language consistent

### Outcomes
- less confusion in future workspace designs
- cleaner governance model
- fewer fake staffing-chart patterns
- less blur between approval material and delivery readiness

## Phase 3 — Project Lifecycle Standardisation

**Goal:** make new workspaces start from a consistent minimum pack.

### Deliverables
- define a minimum serious-project pack:
  - README
  - STATUS
  - DECISIONS
  - NEXT_STEPS
  - memory
  - Forge Pipeline entry
  - validation and rollback notes if runtime exists
- promote DevForge: Project Foundry as the default template authority for governed work

### Outcomes
- fewer empty-folder projects
- stronger consistency across new work
- lower entropy over time

## Phase 4 — Workspace Classification

**Goal:** make the estate easier to reason about.

### Deliverables
- classify workspaces as planning, active, live/deployed, or dormant/archive
- reflect state in a central registry

### Outcomes
- clearer portfolio visibility
- less ambiguity about what is real vs exploratory
- easier prioritisation

## Phase 5 — Environment Health and Drift Control

**Goal:** catch silent configuration drift before it becomes pain.

### Deliverables
- define a lightweight environment audit or heartbeat checklist
- periodically validate:
  - Quarto
  - Forge Pipeline API
  - OpenClaw Usage Dashboard
  - local model lanes
  - stale paired devices
  - memory search configuration

### Outcomes
- more reliable environment
- fewer rediscovery loops
- better operational posture

## Priority Order

Recommended order:
1. Phase 1 — Canonical Control Layer
2. Phase 2 — Governance Model Clarification
3. Phase 3 — Project Lifecycle Standardisation
4. Phase 4 — Workspace Classification
5. Phase 5 — Environment Health and Drift Control

## MVP Cut

Smallest high-value set:
- workspace registry
- human governance vs AI operating rule in root `AGENTS.md`
- DevForge: Project Foundry as default template authority
- minimum serious-project pack rule

## Recommended Next Action

Begin with Phase 1.
