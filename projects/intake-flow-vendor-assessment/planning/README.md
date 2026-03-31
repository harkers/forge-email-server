# Planning — Intake Flow: Vendor Assessment

## Status

**OQs resolved** — 2026-03-31. Ready to begin MVP build.

## Project Reference

**OE-PRIV-IFV-001** — OrderedEDGE // Privacy // Intake Flow  
**Client:** ProPharma Group (propharmagroup.com)  
**Classification:** INTERNAL — RESTRICTED

## Open Questions

| Ref | Question | Status | Resolution |
|-----|---------|--------|-----------|
| OQ-03 | SMTP provider for email delivery | ✅ **RESOLVED** | Postmark Starter ($15/mo, port 587, notifications@datadnaprivacy.com) |
| OQ-04 | Scoring methodology / risk matrix | ✅ **RESOLVED** | Weighted sum model — severity × domain weight, 4-tier roll-up; MVP placeholder = equal weights |
| OQ-06 | spaCy NER model tier | ✅ **RESOLVED** | `sm` for MVP; `trf` for production after GPU/container runtime resolved |

## Architecture Summary

| Step | Agent | Role |
|------|-------|------|
| 1 | Intake Agent | Parse vendor brief, classify data tier, route to DPM |
| 2 | Data Protection Manager | Orchestrator — scopes, dispatches, holds state |
| 3 | Specialist Agents (×5, parallel) | Data Protection, Regulatory/GxP, InfoSec, Contractual, AI Governance |
| 4 | Gap Analysis Agent | Cross-domain contradiction detection |
| 5 | Scoring Agent | Weighted risk matrix → tier 1–4 |
| 6 | Remediation Agent | Prioritised action plan |
| 7 | Report Synthesis Agent | Full output package |
| 8 | Review Gate Agent | Human review packaging, approve/rework routing |
| 9a | Output Delivery Agent | Publish, update registers, notify |
| 9b | Rework Loop | Return to Step 4 with reviewer notes |

## Data Classification

| Tier | Routing |
|------|---------|
| PUBLIC | Local Ollama |
| INTERNAL | Local Ollama |
| SENSITIVE | CloakLLM (spaCy NER redact → cloud LLM) |
| RESTRICTED | Hard block — local processing only, no cloud routing |

## MVP Build Order

1. ✅ Step 1 (Intake) + Step 2 (DPM) — core scaffold, state, routing
2. ✅ Step 3 — Data Protection Agent first (validates framework)
3. ✅ Step 3 — Regulatory and Compliance Agent (highest pharma differentiation)
4. ✅ Step 4 + Step 5 — Gap Analysis + Scoring (placeholder weights; OQ-04 resolved)
5. ✅ Step 7 + Step 9a — Report Synthesis + Output Delivery (OQ-03 resolved; code unblocked)
6. ✅ Step 3 — InfoSec, Contractual, AI Governance agents
7. ✅ Step 6 + Step 8 — Remediation + Review Gate
8. ✅ CloakLLM (OQ-06 resolved: `sm` for MVP; `trf` pending GPU question)

## Next Steps

- [ ] Set up FastAPI + React + PostgreSQL + Redis scaffold on Titan
- [ ] Implement Step 1 (Intake Agent) with data tier classification
- [ ] Implement Step 2 (DPM Orchestrator) with async task dispatch
- [ ] Implement Step 3 — Data Protection Agent (first specialist)
- [ ] Define vendor questionnaire template
- [ ] Define output templates (exec summary, report, DPA redline, ROPA row)
- [ ] Agree test vendor set for MVP validation
