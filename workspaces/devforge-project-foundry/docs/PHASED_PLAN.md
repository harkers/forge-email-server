# DevForge: Project Foundry
## Phased Plan

Status: Planning  
Date: 2026-03-28

## Flow Separation

Project Foundry uses two distinct flows:

### Planning flow
Used for strategy, scope, architecture, controls, risk framing, and approval readiness.

### Delivery flow
Used for repository bootstrap, implementation, review, release, validation, and closure once approval gates are satisfied.

A project must not drift from planning flow into delivery flow simply because planning documents are extensive.

## Phase 0 — Concept and Approval

Purpose: define the why, who, scope, controls, and approval basis before any build begins.

### Outputs
- problem statement
- success metrics
- project charter
- RACI matrix
- seed risk register
- named stakeholder list
- budget rough order of magnitude

### Gates
- G-0 Concept approval
- G-1 Charter approval
- G-2 Funding approval
- G-3 Staffing approval
- G-4 Repo initiation approval

### Rule
No repository bootstrap before Gates G-0 through G-4 are green.

## Phase 1 — Sprint 0 Foundation

Purpose: create the initial repository foundation once planning approval is complete.

### Planned deliverables
- private template repository `devforge-project-foundry`
- protected main branch
- CODEOWNERS
- initial skeleton tree
- core schemas
- bootstrap automation
- validation automation
- minimal templates

### Planned internal workspace pattern
Under the future repo root:
- workspaces/forge-flash-design
- workspaces/forge-architecture
- workspaces/forge-governance
- workspaces/forge-risk
- workspaces/forge-document-engine
- workspaces/forge-orchestrate
- workspaces/forge-pipeline
- workspaces/forge-whats-next
- workspaces/forge-control-plane
- workspaces/forge-review
- workspaces/forge-release
- workspaces/forge-deploy
- workspaces/forge-validate
- workspaces/forge-comms
- workspaces/forge-training
- workspaces/forge-close
- workspaces/forge-fix

## Phase 2 — Sprint 1 MVP Backbone

Purpose: prove the smallest complete governed loop.

### Planned MVP epics
- Forge Orchestrate v1
- ForgePipeline v1
- Forge Document Engine v1
- ForgeComms v1
- ForgeTraining v1
- ForgeRisk v1

### MVP proof points
- strategy can enter the system properly
- documents can be structured and linked
- workspace and repo foundation can be scaffolded
- work can move through controlled states
- risk can be logged and mitigated with history
- comms packs can be generated
- training readiness packs can be generated
- review pass/fail and fix loop can be governed

## Phase 3 — Pilot Project

Purpose: use the template on one real project and test whether the operating model holds under actual delivery conditions.

### Expected activities
- create first child project from template
- run bootstrap and metadata capture
- execute strategy to governance flow
- run delivery through pipeline, review, risk, comms, and training
- gather lessons learned

## Phase 4 — Hardening and Feature Wave

Purpose: deepen the system after MVP and pilot success.

### Candidate next items
- Persona Tailor v2
- Impact Analyzer v2
- pipeline API integration
- visual asset automation
- ISO/NIST control mapping
- stronger DLP and cross-boundary governance

## Planning Position

Project Foundry is still in planning. Current work should focus on documents, roles, controls, lifecycle, risk, and approval readiness rather than implementation.
