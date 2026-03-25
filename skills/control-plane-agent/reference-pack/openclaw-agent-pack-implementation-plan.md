# Implementation Plan

## Phase 1 — Prove the pattern

Deliverables:
- OpenClaw multi-agent config
- queue directory structure
- manager + 2 specialists
- basic task/result JSON
- artifact storage
- manual review

Success criteria:
- manager can route tasks correctly
- specialists can claim, process, and complete tasks
- outputs are reproducible and inspectable
- no cross-agent state collision occurs

## Phase 2 — Add operational maturity

Deliverables:
- Postgres metadata store
- task registry and status transitions
- retry/dead-letter pattern
- dashboard or simple admin UI
- metrics and logging

Success criteria:
- queue remains stable under concurrent task volume
- failures are recoverable
- task histories are queryable
- review state is auditable

## Phase 3 — Harden for trust boundaries

Deliverables:
- optional per-client agent groups
- secret segregation
- egress/network controls per sandbox profile
- policy-based routing
- approval workflows for sensitive actions

Success criteria:
- client/environment separation is demonstrable
- privileged actions require explicit review/approval
- risk of cross-context contamination is materially reduced

## Recommended MVP scope

Use these initial agents only:
- manager
- privacy-incident
- vendor-assessor
- drafting

Keep research folded into manager or vendor-assessor at first if you want a lighter initial rollout.

## Avoid in MVP

- message bus before queue discipline is proven
- autonomous agent-to-agent freeform conversation as primary handoff
- one gateway per task
- fully automated outbound actions
- unbounded tool/network access

