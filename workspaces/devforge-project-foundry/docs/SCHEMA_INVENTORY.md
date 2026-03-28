# DevForge: Project Foundry
## Schema Inventory

Status: Planning  
Date: 2026-03-28

## Purpose

List the likely core schemas needed for Project Foundry MVP and later phases.

## MVP Candidate Schemas

- `project-metadata.yaml` — core project identity and control metadata
- `pipeline-status.yaml` — canonical workflow states
- `control-registry.yaml` — top-line control inventory
- `comms-matrix.yaml` — event, audience, channel, owner, and response rules
- `training-pack.yaml` — Product Readiness Pack structure
- `risk-register.yaml` — risk entries and ownership
- `risk-evaluation.yaml` or markdown-backed equivalent — evaluation cycle record
- `mitigation-log.yaml` or markdown-backed equivalent — mitigation history

## Later Candidate Schemas

- `role-map.yaml`
- `workspace-domain-map.yaml`
- `release-readiness.yaml`
- `handoff-pack.yaml`
- `review-decision.yaml`
- `privacy-review.yaml`
- `security-review.yaml`
- `data-flow-record.yaml`

## Principle

Schemas should exist to reduce drift, improve consistency, and support eventual automation — not to create fake precision with no operational value.
