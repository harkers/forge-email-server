# Changelog — v1 Concept to v2 Hardened Design

## Added

- formal persisted state schema
- deterministic weighted scoring model
- tie-break rules
- explicit safety gates
- approval-window semantics
- token ceiling enforcement
- failure classification and quarantine behavior
- standard operator output format
- test plan

## Clarified

- difference between session history and approval-window history
- when a jobs-mode slot is consumed
- how until-empty behaves with newly added jobs
- how model routing should escalate based on complexity and sensitivity

## Strengthened

- auditability
- operational safety
- predictability
- restart resilience
- cost control

## Kept from original concept

- Forge Pipeline as the task source
- P0-P3 operator-facing priority view
- auto-approve windows
- task-to-model routing intent
- completion and token tracking
- control-plane role as next-step selector and dispatcher
