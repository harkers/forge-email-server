# ForgeOrchestrate — Product Definition

## What it is
ForgeOrchestrate is the command layer for the AI estate.

It is the operating system above the tools.

Where OpenClaw is the execution engine for agents, models, tools, and workflows, ForgeOrchestrate is the control framework that governs how those capabilities are organized, routed, monitored, and trusted.

In practical terms, ForgeOrchestrate is the environment that:
- receives work from different intake channels
- decides which workspace, agent, model, or tool should handle it
- enforces trust boundaries between clients, projects, or domains
- tracks execution from intake to output
- manages approvals, handoffs, and exceptions
- provides visibility, auditability, and operational control

## Clean definition
ForgeOrchestrate is a premium orchestration and oversight layer that coordinates AI work across agents, workspaces, tools, models, and automations, while preserving structure, governance, and operational clarity.

## Another framing
If Forge products are instruments, ForgeOrchestrate is the conductor.
If OpenClaw is the engine room, ForgeOrchestrate is the bridge.

## What it is not
- not just a chatbot
- not just a dashboard
- not just an automation runner
- not only an admin console

It is the system that turns separate AI capabilities into a managed operating environment.

## Core purpose
ForgeOrchestrate exists to solve a very specific problem:
AI systems become chaotic when you have multiple agents, multiple clients, multiple connectors, and multiple workflows all running without a governing layer.

So ForgeOrchestrate gives you:
- order over sprawl
- routing over randomness
- policy over improvisation
- visibility over black-box execution
- controlled autonomy instead of agent anarchy

## Core functions
### 1. Intake and routing
Requests can come from Discord, Telegram, web UI, scheduled jobs, APIs, forms, or internal triggers.
ForgeOrchestrate decides:
- where the request belongs
- which workspace owns it
- which agent should act
- whether it needs human approval
- what tools and models are allowed

### 2. Workspace governance
Different clients or domains should not blur into one another.
ForgeOrchestrate maintains boundaries between:
- ProPharma
- HSBC
- Projects
- personal labs
- internal operations

Each workspace can have its own:
- prompts
- tools
- connectors
- policies
- retention rules
- approval rules
- notification paths

### 3. Agent coordination
It manages a family of specialist agents rather than forcing one generalist to do everything badly.
Examples:
- intake triage agent
- privacy incident agent
- vendor assessment agent
- research agent
- publishing agent
- reporting agent
- scheduling agent

### 4. Execution oversight
It tracks what happened in each run:
- request source
- agent path
- model selection
- tool calls
- outputs created
- failures
- retries
- approvals
- final disposition

### 5. Governance and assurance
This is where it becomes enterprise-grade rather than hobby-grade.
ForgeOrchestrate can provide:
- audit trails
- access control logic
- connector scoping
- policy enforcement
- approval checkpoints
- exception logging
- export and delivery controls

### 6. Performance and optimisation
Over time it helps improve the whole system by showing:
- which agents succeed most often
- which models are too slow or too costly
- which workflows fail repeatedly
- where human intervention is most often needed
- where better prompts or skills are required

## Stack position
### Foundation layer
- infrastructure
- Docker
- reverse proxy
- storage
- GPU / Ollama / databases

### Execution layer
- OpenClaw
- models
- tools
- connectors
- agents
- workflow runners

### Orchestration layer
- ForgeOrchestrate

### Experience layer
- dashboards
- operator views
- notifications
- reports
- approval interfaces
- admin controls

ForgeOrchestrate is not a replacement for OpenClaw.
It is the governing layer above it.

## Relationship to OpenClaw
OpenClaw is the machinery that does the work.
ForgeOrchestrate is the framework that decides how that machinery is used.

OpenClaw gives you:
- models
- agent execution
- tools
- workflows
- runtime capability

ForgeOrchestrate gives you:
- structure
- operating rules
- role separation
- workspace control
- observability
- governance
- premium operator experience

In simple terms:
OpenClaw answers “can the system do this?”
ForgeOrchestrate answers “how should the system do this, under whose authority, with what controls, and where do I see it?”

## Who it is for
### Operator
Needs visibility, queues, failures, approvals, schedules, and health.

### Designer
Needs architecture, boundaries, tool mapping, policy logic, and workspace shaping.

### Stakeholder
Needs reports, approvals, summaries, and confidence that the right work happened in the right place.
