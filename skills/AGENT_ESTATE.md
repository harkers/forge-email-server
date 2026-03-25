# Agent Estate Index

This workspace now contains a coordinated agent family centered on `control-plane-agent`.

## Purpose

Use this file as the quick index for what exists, what each role owns, and how the family fits together.

## Core orchestration layer

### `control-plane-agent`
Role:
- orchestration governor
- handoff schema owner
- verification model
- routing/runbook reference

Use when:
- work spans multiple agents or stages
- a manager needs evidence-driven routing and acceptance
- handoffs must be structured and independently verified

### `control-plane-what-next`
Role:
- pipeline-driven work selection
- auto-approve window management
- priority evaluation
- token/model tracking

Use when:
- control-plane finishes work and needs next item
- user wants to set auto-approve windows
- need to query Forge Pipeline for pending tasks

### `manager-agent`
Role:
- concrete orchestration authority
- intake, routing, verification, acceptance/rejection

## Core generic specialist roles

### `planner-agent`
Owns:
- task-level decomposition
- sequencing within a workstream
- bounded work-unit planning

### `coding-worker-agent`
Owns:
- one bounded implementation scope at a time

### `reviewer-agent`
Owns:
- read-only correctness review

### `investigator-agent`
Owns:
- diagnosis and uncertainty reduction

### `documentation-writer-agent`
Owns:
- specs, runbooks, architecture docs, structured summaries

### `architecture-reviewer-agent`
Owns:
- boundary and coupling review

### `security-reviewer-agent`
Owns:
- trust-boundary and exposure review

### `deployer-agent`
Owns:
- deployment execution and post-deploy verification

### `researcher-agent`
Owns:
- source-backed external evidence gathering

### `drafting-agent`
Owns:
- polished final writing from structured findings

## Domain specialists

### `privacy-incident-agent`
Use for:
- incident chronology
- impact/risk framing
- containment/recovery summaries
- notification support

### `vendor-assessor-agent`
Use for:
- vendor privacy/security posture
- residency/access extraction
- subprocessor/evidence-gap analysis

### `forge-pipeline-operator-agent`
Use for:
- reflecting project and portfolio state into Forge Pipeline

### `workspace-governor-agent`
Use for:
- workspace-local rules, defaults, and governance hygiene

### `forge-wordpress-suite-agent`
Use for:
- suite-level ForgeWordPress governance
- plugin/shared-layer boundary discipline
- release coherence

### `deployment-diagnosis-agent`
Use for:
- diagnosing deployment/runtime failures before execution fixes

### `portfolio-planning-agent`
Use for:
- roadmap and portfolio-level grouping, sequencing, and priorities

## Routing principles

- one write owner per scope
- route by dominant risk
- prefer reviewers over multiple writers
- separate diagnosis from execution when uncertainty is high
- separate planning from state-reflection from local governance
- do not accept self-reported completion without evidence

## Recommended high-level flows

### Build / fix
- manager -> planner (optional) -> coding-worker -> reviewer -> manager
- add architecture/security reviewers as needed

### Diagnose deployment
- manager -> deployment-diagnosis-agent -> deployer or coding-worker -> manager

### ForgeWordPress work
- manager -> forge-wordpress-suite-agent when boundaries matter -> coding-worker -> reviewer -> manager

### Privacy / vendor advisory
- manager -> privacy-incident-agent or vendor-assessor-agent -> researcher/drafting as needed -> manager

### Portfolio / governance
- manager -> portfolio-planning-agent -> workspace-governor-agent and/or forge-pipeline-operator-agent -> manager

## Best starting points

If you only read three things:
1. `control-plane-agent/SKILL.md`
2. `control-plane-agent/references/openclaw-execution-playbook.md`
3. `control-plane-agent/references/manager-runbook.md`

## Current intent of the estate

This is not a swarm.
It is a governed agent family with:
- explicit roles
- bounded ownership
- structured handoff
- evidence-based acceptance

That is the whole point.
