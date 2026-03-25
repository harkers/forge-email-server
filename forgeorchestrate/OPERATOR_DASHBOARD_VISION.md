# ForgeOrchestrate — Operator Dashboard Vision

## Status
Draft

## Purpose

This document captures the intended dashboard direction for ForgeOrchestrate as an operator-grade orchestration environment.

The dashboard should not be treated as “yet another admin panel.”
It should function as the command surface for the AI estate.

Its job is to help operators answer four questions quickly:
- What is running?
- What is stuck?
- What is costing time or tokens?
- What needs intervention?

If it cannot answer those quickly, it is decoration.

---

## Core Dashboard Thesis

ForgeOrchestrate’s dashboard should feel like mission control for intelligent work.

Not:
- dashboard soup
- a toy monitoring panel
- a chat transcript with sidebars
- a Grafana palette explosion

It should feel:
- calm
- premium
- precise
- operationally serious
- high-signal
- dense in capability, light in appearance

---

## Three-Surface Model

The dashboard should be structured as three primary surfaces plus one supporting infrastructure view.

## 3.1 Command Surface
This is the main operational view.

### Purpose
Show what ForgeOrchestrate is doing now and whether it is healthy.

### Core panels
- active jobs queue
- running agents/workspaces
- recent completions
- failed tasks needing review
- human approval items
- system health summary strip

### Best top-row metrics
- active runs
- queued runs
- failed runs
- average completion time
- token/model usage today
- human reviews pending

### Visual feel
- dark, restrained, premium
- deep navy / graphite base
- amber/gold used sparingly for caution and pending review
- strong hierarchy
- one dominant “current work” panel

---

## 3.2 Work Intelligence Surface
This is where the dashboard explains why things are happening.

### Purpose
Show the execution shape of work, not just counts.

### Key elements
- workflow timeline view
- agent handoff map
- prompt/run trace summary
- retry history
- selected model vs fallback model
- tool usage per run
- duration by step

### Recommended primary visual
Represent each run as a pipeline:

Intake → Planner → Specialist agent(s) → Tool calls → Validation → Output → Publish/Notify

Each stage should show:
- status
- duration
- model used
- tools touched
- cost/weight
- errors/warnings

### Why this matters
This lets weak points show up instantly without forcing operators to read raw logs like a Victorian detective.

---

## 3.3 Governance Surface
This is where ForgeOrchestrate becomes a real command layer rather than a flashy runtime viewer.

### Purpose
Make control and trust boundaries visible.

### Key panels
- workspace/client boundary view
- connector access by workspace
- secrets present / missing
- approval-required automations
- audit log
- policy exceptions
- export/download events
- scheduled jobs status

### Design rule
Do not mix governance telemetry and operational telemetry into one noisy screen.
Governance deserves its own surface.

---

## 3.4 Infrastructure Surface (Supporting)
Infrastructure matters, but it is not the main story.

### Purpose
Show whether the underlying execution estate is healthy enough to support orchestration.

### Likely panels
- OpenClaw gateway health
- Ollama availability
- queue worker health
- storage state
- logs/errors pointers
- reverse proxy/public endpoint health

### Design rule
Infrastructure should be a supporting surface, not the front page unless something is broken.

---

## Information Architecture

Recommended navigation structure:

- Overview
- Runs
- Workspaces
- Agents
- Models
- Tools
- Schedules
- Approvals
- Audit
- Infra

### Top-level navigation meaning
#### Overview
Single-screen operational summary.

#### Runs
Execution list and drill-down.

#### Workspaces
Trust-boundary and domain-level views.

#### Agents
Registry and performance view of orchestrator and specialists.

#### Models
Model usage, fallback, latency, token/cost profile, reliability.

#### Tools
Connector and tool health, auth, errors, latency.

#### Schedules
Planned automations, next run, last result, misses.

#### Approvals
Human decisions waiting in queue.

#### Audit
Event trace and accountability view.

#### Infra
Underlying runtime health.

---

## Recommended Layout Pattern

### Desktop layout
- left rail: navigation
- top bar: workspace switcher, search, alerts, quick actions
- center: main operational surface
- right drawer/rail: contextual drill-down

### Suggested top-right quick actions
- New orchestration
- Retry failed run
- Pause schedules
- Open logs
- Switch workspace

---

## Best Visual Patterns

## 6.1 Hero Panel
Large central “Current orchestration state” card showing:
- runs active now
- jobs blocked
- next scheduled automation
- latest critical error

## 6.2 Swimlane Timeline
Runs shown horizontally across stages.

This is one of the strongest possible views for agent systems because it lets the operator see flow, delay, handoff, and breakage in one glance.

## 6.3 Node Graph (Secondary only)
Useful as an explainer, not as the default operational surface.

### Rule
Agent graphs are seductive. They become wallpaper if overused.

## 6.4 Status Chips
Consistent semantic states such as:
- healthy
- running
- queued
- delayed
- needs review
- failed
- paused

## 6.5 Side Drawer Drill-Down
Clicking a run should open contextual detail showing:
- input source
- prompt/request summary
- agent chain
- model used
- tools called
- outputs
- warnings
- raw logs link

## 6.6 Heatmaps
Useful for:
- busiest hours
- failing workflows by type
- model reliability by task class

---

## OpenClaw-Specific Telemetry Requirements

Because ForgeOrchestrate sits above OpenClaw, the dashboard should expose domain-specific telemetry tied to execution reality.

## 7.1 Run state telemetry
Required states include:
- queued
- planning
- executing
- waiting_on_tool
- waiting_on_human
- validating
- complete
- failed

## 7.2 Model telemetry
Show:
- selected model
- fallback model
- runtime duration
- context size
- token count
- failure/fallback reason

## 7.3 Tool telemetry
Show:
- connector invoked
- latency
- success/failure
- permission denied
- rate limited
- empty result
- parse failure

## 7.4 Output telemetry
Show:
- artifact created?
- notification sent?
- publish status
- approval status
- export/download state

This is what makes the system feel like a conductor’s console rather than a chat transcript with a gym membership.

---

## Sections and Their Main Questions

## Overview
Answers:
- what is live now?
- where are the alerts?
- is throughput healthy?
- is the queue healthy?

## Runs
Answers:
- what executions exist?
- what is their state?
- what happened in each?

## Workspaces
Answers:
- which domains are active?
- what policies/connectors/health states apply?

## Agents
Answers:
- what each agent does
- success rate
- average runtime
- common failure reasons

## Models
Answers:
- model use volume
- latency
- fallback patterns
- reliability
- GPU pressure signals where relevant

## Tools
Answers:
- auth status
- last success
- error count
- rate-limit / timeout warnings

## Schedules
Answers:
- next run
- last result
- missed executions
- delivery status

## Approvals
Answers:
- what is awaiting human decision?
- what is blocked by review?

## Audit
Answers:
- who triggered what?
- which workspace?
- which tool?
- what changed?

## Infra
Answers:
- is the underlying runtime healthy enough to support orchestration?

---

## Color and Typography Logic

### Color logic
- neutral dark base
- muted blue for informational state
- amber for caution / pending review
- red only for actionable failure
- green used sparingly for healthy confirmation

### Typography
- clean geometric sans
- large numeric metrics
- compact secondary metadata
- monospace only for IDs and log snippets where useful

---

## What to Avoid

### 1. Do not make logs the product
Operators need summaries first, logs second.

### 2. Do not lead with infra-only metrics
CPU/GPU/RAM matter, but for ForgeOrchestrate they are supporting signals, not the main story.

### 3. Do not overuse graph views
Graphs look clever until they become spaghetti wallpaper.

### 4. Do not make every workspace look equally important
Business-critical or active workspaces should rise to the top.

### 5. Do not put dangerous controls on the main screen
Restart, purge, force retry, secret rotation, and similar actions should stay behind admin-scoped views.

---

## Recommended v1 Dashboard

A sensible v1 should ship only these six blocks first:
- global status strip
- active / queued / failed run cards
- recent run timeline
- workspace health table
- model/tool health summary
- approval queue

This alone would already make the product useful.

---

## Recommended v2 Additions

Then add:
- drill-down run trace
- agent dependency map
- scheduling calendar
- audit explorer
- cost/performance analytics
- SLA / completion-time trend reporting

---

## Recommended v3 Premium Features

Later add:
- predictive failure warnings
- anomaly detection on workflows
- suggested model right-sizing
- workload routing recommendations
- “why this run failed” explanation layer
- replay/simulation mode for orchestrations

---

## Exposure and Deployment Guidance

### Recommended architecture position
Keep the dashboard as an internal application surfaced through the existing ingress/reverse-proxy control model.

### Why
This fits:
- minimal-change preference
- reverse-proxy-aware deployment
- controlled exposure
- stable maintainable stack
- no unnecessary second doorway into the castle

### Rule
If remote access is needed later, expose it through the same controlled access pattern already used for OpenClaw rather than inventing a second public path.

---

## Final Recommendation

ForgeOrchestrate’s dashboard should be treated as the operator-grade mission control layer for the AI estate.

It should answer four questions fast:
- what is running?
- what is stuck?
- what is costing time or tokens?
- what needs intervention?

And it should do that with:
- calm command-surface design
- separated operational / workflow / governance / infrastructure views
- OpenClaw-specific telemetry
- high-signal drill-down paths
- controlled internal exposure

That is how the dashboard becomes worthy of the product above it.
