# Planning — Intake Flow: Vendor Assessment

## Status

Brief loaded — 2026-03-31. Planning phase active.

## Project Reference

**OE-PRIV-IFV-001** — OrderedEDGE // Privacy // Intake Flow  
**Client:** ProPharma Group (propharmagroup.com)  
**Classification:** INTERNAL — RESTRICTED  
**Brief version:** 0.1 DRAFT

## Purpose

Multi-agent AI pipeline that automates the end-to-end vendor assessment lifecycle for ProPharma Group. Nine discrete agents cover intake, five specialist domains (Data Protection, Regulatory/GxP, InfoSec, Contractual, AI Governance), gap analysis, scoring, remediation, report synthesis, and human review gate.

## Architecture Summary

| Step | Agent | Role |
|------|-------|------|
| 1 | Intake Agent | Parse vendor brief, classify data tier, route to DPM |
| 2 | Data Protection Manager | Orchestrator — scopes, dispatches, holds state |
| 3 | Specialist Agents (×5, parallel) | DP, Regulatory, InfoSec, Contractual, AI Gov |
| 4 | Gap Analysis Agent | Cross-domain contradiction detection |
| 5 | Scoring Agent | Weighted risk matrix → tier 1–4 |
| 6 | Remediation Agent | Prioritised action plan |
| 7 | Report Synthesis Agent | Full output package (exec summary, report, redline DPA, ROPA, sub-processor row) |
| 8 | Review Gate Agent | Human review packaging, approve/rework routing |
| 9a/9b | Output Delivery / Rework Loop | Publish, update registers, rework return |

## Data Classification

| Tier | Routing |
|------|---------|
| PUBLIC | Local Ollama |
| INTERNAL | Local Ollama |
| SENSITIVE | CloakLLM (redact first, then cloud) |
| RESTRICTED | Hard block — local only |

## Open Questions (Must Resolve Before Full Build)

| Ref | Question | Blocks |
|-----|---------|--------|
| OQ-03 | SMTP provider for email output delivery | Step 9a |
| OQ-04 | Scoring methodology / risk matrix weights | Step 5 |
| OQ-06 | spaCy NER model tier for CloakLLM | CloakLLM integration |

## MVP Build Order

1. Step 1 (Intake) + Step 2 (DPM) — core scaffold, state, routing
2. Step 3 — Data Protection Agent first (validates framework)
3. Step 3 — Regulatory and Compliance Agent (highest pharma differentiation)
4. Step 4 + Step 5 — Gap Analysis + Scoring (placeholder weights)
5. Step 7 + Step 9a — Report Synthesis + Output Delivery (closes happy path)
6. Step 3 — InfoSec, Contractual, AI Governance agents
7. Step 6 + Step 8 — Remediation + Review Gate (completes pipeline)
8. CloakLLM + SMTP (blocked on OQ-03, OQ-06)

## Next Steps

- [ ] Resolve OQ-03, OQ-04, OQ-06
- [ ] Agree scoring methodology (OQ-04)
- [ ] Define vendor questionnaire template
- [ ] Define output templates (exec summary, report, DPA redline, ROPA row)
- [ ] Confirm FastAPI + React scaffold for Titan
- [ ] Define test vendor set for MVP validation
