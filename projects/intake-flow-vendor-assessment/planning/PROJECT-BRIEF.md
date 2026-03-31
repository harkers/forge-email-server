# Project Brief: Intake Flow — Vendor Assessment

**Project ref:** OE-PRIV-IFV-001
**Product:** OrderedEDGE // Privacy // Intake Flow
**Client scope:** ProPharma Group (propharmagroup.com)
**Author:** Data DNA Privacy Ltd
**Classification:** INTERNAL — RESTRICTED
**Version:** 0.1 DRAFT
**Date:** 2026-03-31

---

## 1. Executive Summary

Intake Flow — Vendor Assessment is a multi-agent AI pipeline that automates the end-to-end vendor assessment lifecycle for ProPharma Group. It replaces a predominantly manual process with a structured, repeatable workflow in which each distinct assessment step is owned by a dedicated AI agent. The Data Protection Manager acts as orchestrator, coordinating five domain-specialist agents in parallel before the output passes through gap analysis, scoring, remediation planning, report synthesis, and a human review gate. The pipeline is designed to run on the Titan platform under the OrderedEDGE // Privacy namespace and integrates with CloakLLM for borderline-sensitive data routing.

The system is scoped to ProPharma Group's full service portfolio: Regulatory Affairs, Pharmacovigilance, Quality Assurance, Clinical Operations, Data Annotation and AI, Medical Writing, Biostatistics, and IT and Data Management.

---

## 2. Background and Business Context

### 2.1 Problem statement

ProPharma Group is a global contract research and regulatory affairs organisation processing significant volumes of personal data — including special category health data — across multiple jurisdictions. Vendor management at this scale requires rigorous, consistent assessment against a complex matrix of obligations: GDPR and UK GDPR, GxP regulatory frameworks, FDA requirements, EU AI Act provisions, and standard contractual and information security controls.

Existing assessment processes are time-intensive, inconsistently applied across vendor types, and do not adequately capture the intersection of pharma-specific regulatory obligations with data protection law. The AI Governance dimension — particularly relevant given ProPharma's data annotation services — is not currently assessed in a structured way.

### 2.2 Opportunity

A multi-agent pipeline can reduce assessment cycle time, enforce consistency across all vendor types, surface cross-domain conflicts that manual review misses, and produce a standardised evidence pack that satisfies both DPO sign-off requirements and client audit expectations. It also creates a defensible audit trail of how each assessment decision was reached.

### 2.3 Strategic fit

This project sits at the intersection of Data DNA Privacy Ltd's core GDPR consultancy capability and the Titan platform's AI orchestration infrastructure. It is a reference implementation for OrderedEDGE // Privacy and demonstrates the CloakLLM data-sensitivity routing model in a live client context.

---

## 3. Objectives

1. Automate the full vendor assessment lifecycle from intake trigger to approved output, with no manual intervention required except at the designated human review gate.
2. Deliver consistent, pharma-grade assessments covering data protection, regulatory compliance, information security, contractual obligations, and AI governance in a single pipeline run.
3. Produce machine-readable and human-readable outputs that pre-populate the ROPA, sub-processor register, and contractual action tracker.
4. Reduce average assessment cycle time by at least 70% compared to the current manual process.
5. Create a reusable agent architecture that can be extended to other client contexts beyond ProPharma Group.

---

## 4. Scope

### 4.1 In scope

- All eight ProPharma Group service lines: Regulatory Affairs, Pharmacovigilance, Quality Assurance, Clinical Operations, Data Annotation and AI, Medical Writing, Biostatistics, IT and Data Management.
- New vendor assessments triggered manually or via automated flag.
- Periodic review reassessments (annual cycle or triggered by material change).
- DPA adequacy checking against Data DNA's standard DPA template.
- Sub-processor chain review where applicable.
- Integration with Titan platform via FastAPI and Docker Compose.
- CloakLLM routing for borderline-sensitive data categories.
- Telegram notification to titan_eng_bot on pipeline completion or escalation.

### 4.2 Out of scope

- Vendor onboarding beyond the assessment output (procurement, contract execution).
- Real-time monitoring of vendor compliance post-assessment (future phase).
- Assessment of ProPharma Group's own internal data processing activities.
- Jurisdictions outside UK, EU, and US in the MVP phase (APAC, LATAM, China to follow).

---

## 5. Pipeline Architecture

The pipeline is composed of nine discrete agents, each owning exactly one step. No agent performs work outside its defined step. The Data Protection Manager orchestrates but does not assess.

### Step 1 — Intake Agent

Receives the assessment trigger, which may originate from a manual request, a periodic review scheduler, or an automated flag raised by another system. Parses the vendor brief to extract: vendor name, registered jurisdiction, services in scope, data categories involved, and whether any ProPharma service line involves special category data or cross-border transfers. Classifies the intake against the eight ProPharma service lines and produces a structured brief that is passed to the Data Protection Manager. No assessment logic runs at this step.

### Step 2 — Data Protection Manager (Orchestrator)

Named to reflect the DPO-equivalent function it performs within the pipeline. Receives the structured brief from the Intake Agent and takes responsibility for the overall assessment run. Sets the assessment scope, determines which specialist agents are required (all five are activated by default for ProPharma assessments), initiates parallel execution, holds state across all agent outputs, and controls sequencing through subsequent steps. Does not produce any assessment content itself. Returns control to the next step once all specialist agents have completed.

### Step 3 — Specialist Agents (parallel execution)

All five specialist agents run concurrently under instruction from the Data Protection Manager. Each operates against its own domain-specific question set and evidence checklist, drawing on vendor-submitted documentation, questionnaire responses, and publicly available information (certifications, regulatory standing, published AI system cards).

**Data Protection Agent**

Assesses the GDPR and UK GDPR layer. Maps vendor data flows, identifies lawful basis for each processing activity, evaluates Standard Contractual Clauses applicability and adequacy, conducts transfer impact assessment for any cross-border transfers, and checks the vendor's DPA against Data DNA's standard template. Flags any RESTRICTED data categories that trigger a hard block on cloud routing via CloakLLM. Particular attention is given to special category health data given ProPharma's pharmacovigilance and clinical operations scope.

**Regulatory and Compliance Agent**

Assesses obligations specific to the life sciences and pharma regulatory context. Covers GxP framework compliance, FDA 21 CFR Part 11 requirements for electronic records and signatures, EU GMP Annex 11 for computerised systems, ICH guidelines relevant to clinical data handling, and pharmacovigilance audit trail requirements under EU PV legislation. This agent is the primary differentiator for pharma-grade assessment — it surfaces obligations that a generic data protection assessment would not reach.

**InfoSec and Cyber Agent**

Assesses the vendor's information security posture. Reviews ISO 27001 certification status and scope, SOC 2 Type II reports, Cyber Essentials or Cyber Essentials Plus certification, and any vendor-submitted penetration test summaries. Flags certificate expiry dates, cloud sub-processor chains and their certification status, encryption-at-rest and in-transit implementation, and any gaps identified in penetration test findings that remain unresolved. Cross-references against ProPharma's data classification requirements.

**Contractual and Legal Agent**

Reviews the vendor's Data Processing Agreement against Data DNA's standard DPA template. Assesses liability cap adequacy relative to the data volumes and sensitivity involved, audit rights provisions, breach notification SLA compliance with the 72-hour GDPR requirement, and sub-processor change notice obligations. Surfaces material deviations from standard terms and categorises them as blocking, negotiable, or informational.

**AI Governance Agent**

Assesses EU AI Act obligations where the vendor deploys or provides AI systems as part of their service delivery. Determines the risk classification of any AI systems used (minimal, limited, high, or unacceptable risk), reviews human oversight provisions, assesses training data provenance claims for vendors involved in data annotation, and checks for conformity assessment obligations. This agent is specifically activated for ProPharma's Data Annotation and AI service line but runs for all vendors given the breadth of AI tooling now embedded in CRO operations.

### Step 4 — Gap Analysis Agent

Receives all five specialist agent outputs simultaneously. Reconciles findings across domains, identifies contradictions (for example, a vendor claiming ISO 27001 certification that is not reflected in the InfoSec Agent's findings, or a DPA gap that conflicts with a Regulatory Agent finding about audit trail requirements). Raises formal clarification queries where evidence is missing or ambiguous. Does not score or remediate — its sole function is to ensure the evidence base is coherent and complete before scoring proceeds. If clarification queries cannot be resolved automatically, it escalates to the Data Protection Manager, which notifies the human reviewer via Telegram.

### Step 5 — Scoring Agent

Applies a weighted risk matrix to the reconciled output from the Gap Analysis Agent. Each finding is scored by severity (Critical, High, Medium, Low, Informational) and weighted by domain criticality for the specific vendor type and service line in scope. Produces an overall vendor risk tier from 1 (low risk, approve) to 4 (high risk, do not engage), a RAG status per domain, and a ranked list of findings. Scoring methodology follows the benchmark approach to be confirmed under OQ-04.

### Step 6 — Remediation Agent

Translates scored findings into a prioritised action plan. For each finding above Informational severity, assigns a recommended action, a responsible owner (vendor, Data DNA, or ProPharma), a target deadline, and maps the action to the specific contractual or regulatory obligation it addresses. Distinguishes between pre-engagement conditions (items that must be resolved before the vendor relationship proceeds) and ongoing monitoring items.

### Step 7 — Report Synthesis Agent

Composes the full assessment output package. Produces the executive summary for DPO and senior stakeholder consumption, the detailed assessment report covering all five domains, a redline DPA where contractual deviations have been identified, a pre-populated ROPA entry for the vendor relationship, and a sub-processor register row. All outputs are templated to Data DNA's standard formats. The report package is passed to the Review Gate Agent.

### Step 8 — Review Gate Agent

Packages the report for human review and sign-off. Flags any findings that require mandatory human judgement — specifically: any RESTRICTED data category involvement, any Critical-severity findings, any vendor risk tier of 3 or 4, and any unresolved clarification queries from Step 4. Routes the assessment to one of two paths: approved (proceeds to Step 9) or rework (returns to Step 4 with reviewer notes attached). DPO sign-off is required for all assessments regardless of tier. The Review Gate Agent does not make approval decisions — it structures the information for the human reviewer and enforces the routing logic.

### Step 9a — Output Delivery Agent (approved path)

Publishes the approved assessment report to the designated output location, updates the ROPA and sub-processor register, triggers any contractual actions with defined deadlines, and notifies relevant stakeholders via the configured channel. Sends a completion notification to titan_eng_bot with assessment summary metadata.

### Step 9b — Rework Loop (rejected path)

Returns the assessment to Step 4 (Gap Analysis Agent) with the reviewer's notes and rejection reasoning attached as structured input. Does not restart from Step 1 or Step 3. The specialist agents are not re-run unless the reviewer explicitly flags that new vendor evidence has been submitted, in which case the Data Protection Manager re-scopes and re-triggers only the affected specialist agents.

---

## 6. Data Classification and CloakLLM Routing

All data processed within the pipeline is classified at intake by the Intake Agent against the following tiers:

| Tier | Definition | Routing |
|------|-----------|---------|
| PUBLIC | Non-personal, publicly available vendor information | Standard LLM (local Ollama) |
| INTERNAL | Vendor questionnaire responses, non-special category personal data | Standard LLM (local Ollama) |
| SENSITIVE | Special category data indicators, financial data, commercially sensitive information | CloakLLM — PII redaction and pseudonymisation before cloud routing |
| RESTRICTED | Data explicitly identifying data subjects, unredacted clinical trial data, raw pharmacovigilance records | Hard block — local processing only, no cloud routing |

CloakLLM handles redaction and pseudonymisation for SENSITIVE tier data before any cloud model is invoked. The spaCy model tier for CloakLLM NER is subject to resolution under OQ-06.

---

## 7. ProPharma Group Service Line Matrix

The following matrix maps each ProPharma service line to the specialist agents most likely to produce material findings. All five agents run for all assessments; this matrix identifies elevated-scrutiny areas.

| Service line | Data Protection | Regulatory | InfoSec | Contractual | AI Governance |
|---|:---:|:---:|:---:|:---:|:---:|
| Regulatory Affairs | ● | ●● | ● | ● | ○ |
| Pharmacovigilance | ●● | ●● | ●● | ●● | ● |
| Quality Assurance | ● | ●● | ● | ● | ○ |
| Clinical Operations | ●● | ●● | ●● | ●● | ● |
| Data Annotation and AI | ●● | ● | ● | ● | ●● |
| Medical Writing | ● | ● | ○ | ● | ● |
| Biostatistics | ● | ●● | ● | ● | ● |
| IT and Data Management | ●● | ● | ●● | ●● | ● |

●● Elevated scrutiny ● Standard scrutiny ○ Reduced scrutiny

---

## 8. Technical Implementation

### 8.1 Platform

The pipeline runs on Titan (Debian 12, LAN IP 192.168.10.80) under the OrderedEDGE // Privacy namespace. It is implemented as a FastAPI service with a React frontend, backed by PostgreSQL 16 and Redis 7, deployed via Docker Compose. Nginx handles reverse proxy. Public ingress is via flow-control.orderededge.co.uk. Webhook ingress for automated triggers is via hooks.orderededge.co.uk.

### 8.2 LLM configuration

Local inference runs on Ollama (NVIDIA RTX 4080 SUPER). Recommended model for assessment agents: `qwen3:14b` with `num_ctx=32768` and temperature 0.3 for consistent, low-hallucination output. The Report Synthesis Agent may use a higher context window for full report composition. CloakLLM handles SENSITIVE tier routing to cloud models after redaction.

### 8.3 Notifications

Pipeline completion, escalation events, and rework loop activations are notified to:
- **Ops channel:** flow_control_orderededge_bot (Telegram)
- **Engineering channel:** titan_eng_bot (Telegram)

Email notification for external stakeholder delivery is subject to SMTP provider selection under OQ-03.

### 8.4 Agent framework

Each agent is implemented as a discrete FastAPI endpoint. The Data Protection Manager orchestrates via asynchronous task dispatch. Agent outputs are stored as structured JSON in PostgreSQL 16. Redis 7 handles state management across the pipeline run. All agent-to-agent communication passes through the Data Protection Manager — agents do not communicate directly with each other.

---

## 9. Outputs

The pipeline produces the following outputs for each completed assessment:

| Output | Format | Consumer |
|--------|--------|---------|
| Executive summary | Markdown / PDF | DPO, senior stakeholders |
| Full assessment report | Markdown / PDF | DPO, legal team |
| Redline DPA | DOCX | Legal team, vendor |
| ROPA entry | JSON / CSV | Data Protection team |
| Sub-processor register row | JSON / CSV | Data Protection team |
| Remediation action plan | Markdown / JSON | Data Protection team, vendor relationship owner |
| Risk score and tier | JSON | Dashboard, Titan |
| Clarification query log | Markdown | Assessment audit trail |

---

## 10. Open Questions

| Ref | Question | Impact | Owner |
|-----|---------|--------|-------|
| OQ-03 | SMTP provider for email delivery of outputs and notifications | Output Delivery Agent (Step 9a) cannot send external notifications until resolved | Stuart / Data DNA |
| OQ-04 | Benchmark scoring methodology for the risk matrix | Scoring Agent (Step 5) cannot be implemented until the weighting model is defined | Stuart / Data DNA |
| OQ-06 | spaCy model tier for CloakLLM NER (en_core_web_sm vs en_core_web_trf) | Affects redaction accuracy for SENSITIVE tier data; wrong choice creates either false positives or missed PII | Stuart / Titan platform |

---

## 11. MVP Build Order

1. Intake Agent and Data Protection Manager (Step 1 and Step 2) — core pipeline scaffold, state management, routing logic.
2. Data Protection Agent (Step 3, first specialist) — highest domain priority, validates agent framework before parallel execution is built.
3. Regulatory and Compliance Agent (Step 3) — highest differentiation value for ProPharma scope.
4. Gap Analysis Agent (Step 4) and Scoring Agent (Step 5) with placeholder scoring weights pending OQ-04 resolution.
5. Report Synthesis Agent (Step 7) and Output Delivery Agent (Step 9a) — closes the happy path end-to-end.
6. Remaining specialist agents: InfoSec, Contractual, AI Governance (Step 3).
7. Remediation Agent (Step 6) and Review Gate Agent (Step 8) — completes the full pipeline including human review gate and rework loop.
8. CloakLLM integration (blocked on OQ-06), SMTP integration (blocked on OQ-03).

---

## 12. Success Criteria

The MVP is considered complete when:

- A new vendor assessment can be initiated via the Intake Flow interface and proceed to a DPO-reviewable output without manual intervention at any step except the Review Gate.
- All five specialist agents produce structured, domain-appropriate output for at least one vendor from each of the eight ProPharma service lines.
- The Gap Analysis Agent correctly identifies at least one cross-domain conflict in a test assessment containing a seeded contradiction.
- The Scoring Agent produces a risk tier that is consistent with a manual expert assessment of the same vendor for a minimum of three test cases.
- CloakLLM correctly routes SENSITIVE tier data and hard-blocks RESTRICTED tier data in all test cases.
- Assessment cycle time from trigger to DPO-reviewable output is under four hours for a standard vendor with complete documentation.

---

## 13. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| OQ-04 scoring methodology not agreed before Step 5 build | Medium | High — blocks scoring agent implementation | Use placeholder equal-weight model for MVP; swap in agreed weights post-resolution |
| Vendor documentation is incomplete at intake | High | Medium — Gap Analysis Agent raises clarification queries that cannot be auto-resolved | Design Intake Agent to flag incomplete packs before pipeline runs; surface to human reviewer early |
| CloakLLM misclassifies RESTRICTED data as SENSITIVE | Low | Critical — risk of personal data leaving Titan boundary | Default to RESTRICTED classification for any ambiguous special category indicators; OQ-06 resolution must validate against clinical data test set |
| Agent outputs are verbose and exceed Report Synthesis Agent context window | Medium | Medium — synthesis quality degrades | Set structured output schemas for all specialist agents; enforce token budgets per finding |
| ProPharma service line scope changes mid-build | Low | Low — matrix adjustments only | Service line matrix is config-driven; no code changes required for new lines |

---

## 14. Glossary

| Term | Definition |
|------|-----------|
| CloakLLM | Titan subsystem that redacts and pseudonymises PII before routing borderline-sensitive jobs to cloud LLMs |
| Data Protection Manager | The orchestrator agent; named to reflect its DPO-equivalent coordination function |
| DPA | Data Processing Agreement |
| GxP | Good Practice guidelines applicable across pharmaceutical development (GMP, GCP, GVP, etc.) |
| Intake Flow | The OrderedEDGE // Privacy product family to which this pipeline belongs |
| ROPA | Record of Processing Activities |
| Titan | Self-hosted Linux server (Debian 12) running the OrderedEDGE platform |

---

*Data DNA Privacy Ltd · Stuart · CIPP/E · datadnaprivacy.com*
*Document classification: INTERNAL — RESTRICTED*
*Next review: on OQ-03, OQ-04, OQ-06 resolution or MVP milestone, whichever is sooner*
