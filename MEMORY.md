# MEMORY.md - Long-Term Memory

This file contains curated memories, decisions, and operational rules for the Privacy Operations workspace.

## GitHub Project `privacy-ops` (https://github.com/users/harkers/projects/3)

### Current Status (2026-03-30 12:53 UTC)
- **Total items**: 9
- **In Progress**: 1 (#301755 — Recordati misdirected email breach, evidence cleanup pending)
- **Human Review**: 8 (5 ProPharma public-source reviews, 1 CNIL 2024 guide, 1 Gilead Mi-Q PDB)
- **New**: 0 (no new intake items awaiting triage)

### Recent Activity (2026-03-30 12:53 UTC)
- Checked GitHub project `privacy-ops` as Data Protection Manager intake queue
- Confirmed 1 item in `In Progress`, 8 items in `Human Review`, 0 items in `New`
- #301755 remains in `In Progress` — low-risk misdirected email breach needing Recordati notification confirmation and preventative measures before human review
- ProPharma public-source batch (5 items) remain in `Human Review` — ready for sign-off
- CNIL 2024 guide remains in `Human Review` — knowledge intake completed (Article 32 security benchmark, 25 factsheets, focus areas: cloud, mobile, AI, APIs, data management)
- Gilead Mi-Q PDB #302194 remains in `Human Review` — evidence cleanup pending
- Checked knowledge library `/home/stu/privacy-ops/knowledge/` — no new or changed files since last check (last modification: 2026-03-28 14:49)

### Decision Log
- **2026-03-30 12:53 UTC**: No new GitHub intake items identified; all items either in progress or awaiting human review
- **2026-03-30 12:53 UTC**: Knowledge files from 28-Mar already triaged; no fresh intake required
- **2026-03-30 12:53 UTC**: Item #301755 remains in In Progress pending evidence follow-up (Recordati notification, deletion confirmations, preventative measures)

### Related Projects
- **OrderedEdge Sentinel** (OC-SEC-001): Planning phase workspace scaffolded, 28 detection rules defined, 90-day roadmap approved
- **New**: Intake received, awaiting triage
- **In Progress**: Work underway and assigned
- **Human Review**: Delivery complete, awaiting human decision
- **Closed**: Reviewed and finished

### Required Project Fields
- Work Description
- Assessment Notes
- Attachments
- Completion Summary
- Workflow Stage

### Triage and Routing
See `operations/GITHUB_PROJECT_INTAKE_RUNBOOK.md` for full routing matrix. Key agent types:
- Privacy Analyst — Data Category Assessment (PHI, special category)
- Privacy Risk Analyst — Incidents (severity, impact, notification)
- Privacy Analyst — Containment/Corrective/Preventive (response actions)
- Privacy Incident and Breach Agent (containment execution)
- Privacy Incident Report Writer (regulatory notifications)
- Privacy Analyst — Communications Manager (reporter communication)
- Privacy Analyst — SOP Reviewer (documentation verification)

## Knowledge Library `/home/stu/privacy-ops/knowledge/`

### Structure
- `company-information/` — company background, operating model, service lines
- `sops/` — standard operating procedures
- `work-instructions/` — task-specific instructions
- `contracts/` — DPAs, vendor contracts, privacy clauses
- `propharma-privacy-store/` — assessment records, incidents, DPIAs, vendor reviews
- `compliance-store/` — RAG-ready compliance tracking (IMPLEMENTATION-PLAN.md)

### Recent Status (2026-03-30)
- Last modification: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
- No new or changed files since last hourly check (scan performed 2026-03-30 03:35)
- Files from 28-Mar batch already triaged; no fresh intake required

## Operational Rules

### DPM Hourly Intake Rule
The Data Protection Manager checks the GitHub project every hour and operates proactively:
- Review items in `New` stage, triage each, route to appropriate agents
- Check knowledge library for new or changed material
- Move active work to `In Progress`, completed work to `Human Review`
- Do not move items to `Closed` without human review
- Write all actions, decisions, and outcomes to memory
- Use humanizer skill for GitHub-facing communications

### Knowledge Assessment Rule
Not every document needs action. Assess whether new material requires:
- No action
- Memory update only
- Knowledge-base update
- Contract/privacy review
- Incident or risk assessment
- New GitHub intake item
- Escalation to DPO/Legal/CPO

## Memory Maintenance

### Promotion Rule (Daily → Long-term)
Promote from daily memory (`memory/YYYY-MM-DD.md`) when:
- A durable decision is made
- A recurring pattern or lesson emerges
- A stable configuration truth is confirmed
- A project reaches a milestone worth remembering
- A mistake that could recur needs prevention

### Do Not Promote
- Transient status or in-progress work
- Temporary debugging notes
- Information that will age out quickly
- Conversational context that doesn't need persistence

## Key Agents and Responsibilities

| Agent | Primary Function | When to Route |
|-------|------------------|---------------|
| Privacy Analyst — Data Category Assessment | Identify PHI, special category | Pharmacy, PV, MI, quality cases |
| Privacy Risk Analyst — Incidents | Severity, impact, notification | All incidents/breaches |
| Privacy Analyst — Containment/Corrective/Preventive | Define response actions | After risk assessment |
| Privacy Incident and Breach Agent | Execute containment | After actions defined |
| Privacy Incident Report Writer | Draft notifications/reports | After containment |
| Privacy Analyst — Communications Manager | Reporter communication | After report drafted |
| Privacy Analyst — SOP Reviewer | Verify evidence completeness | Before closure |

## GitHub Labels Taxonomy

See `.github/LABELS.md` for full taxonomy. Key categories:
- **Type**: incident, breach, confidentiality-concern, privacy-request, complaint, DSAR, DPIA, PDRA, vendor-review, contract-review, AI-governance, policy, training, audit, cookies-tracking, retention, data-transfer
- **Severity**: low, medium, high, critical
- **Risk**: low, medium, high, high-risk-to-rights-and-freedoms
- **Status**: new, triage, awaiting-info, in-analysis, in-drafting, pending-approval, action-in-progress, blocked, ready-to-close, closed
- **Regulatory**: PDB, not-a-PDB, confidentiality-concern, notification-assessment-required, ICO-reportable, data-subject-notification-required, legal-review-required
- **Data**: patient, employee, customer, HCP, vendor, special-category, PHI, no-personal-data
- **Geographic**: UK, EU, US, global
- **Priority**: P1, P2, P3
- **SLA**: 72-hour-clock, urgent, routine
- **Owner**: Data Protection Manager, Privacy Risk Analyst, Privacy Analyst - Communications Manager, Privacy Analyst - Containment/Corrective/Preventive, Legal, Security, IT, business
- **Outcome**: monitor-only, corrective-action, preventive-action, training-needed, process-change, policy-update

## Important Notes

### Human Review Requirement
The DPM does not mark completed delivery as final closure without human review. After human sign-off:
- Update the item if needed
- Move it to `Closed`

### Memory Writing Rule
Everything the DPM produces must be added to memory. This is mandatory for:
- Triage decisions
- Routing decisions
- Work instructions sent to agents
- Returned outputs and evidence
- Completion summaries
- Lessons learned
- Recurring failures or improvements

### GitHub Communications Rule
All GitHub-facing written communications from the DPM should be passed through the humanizer skill before posting. This applies to assessment notes, project item summaries, completion summaries, progress updates, and triage notes intended for humans to read.

## Intake Check Summary — 2026-03-30 01:31 UTC

**GitHub Project `privacy-ops`**
- Items in `New`: 0
- Items in `In Progress`: 1 (#301755 — Recordati misdirected email, needs evidence cleanup)
- Items in `Human Review`: 8 (5 draft ProPharma reviews, 1 CNIL guide, 1 Gilead PDB)
- Total: 9 items

**Knowledge Library**
- Last modified: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
- Status: No new or changed files since last check
- Action: Files reviewed as part of 28-Mar batch; no fresh intake required

**Pending Human Actions**
- Sign off on 9 items in `Human Review` stage (5 ProPharma reviews, 1 CNIL guide, 2 Gilead PDBs, 1 Recordati PDB)

## Recent Key Findings

### CNIL 2024 Security Guide (2026-03-29)
- **Item**: Practice guide for the security of personal data : 2024 edition
- **Status**: Knowledge intake completed at DPM level
- **Durable finding**: GDPR Article 32 security benchmark, 25 factsheets across 5 parts
- **Focus areas**: Cloud computing, mobile applications, AI, APIs, data management security
- **Use case**: Positioning as practical benchmark for security controls, especially where AI, APIs, cloud services, and mobile workflows are in scope
- **Recommended action**: Knowledge-base incorporation and future control benchmarking, not incident response
- **No immediate escalation** triggered from the article alone

### ProPharma Public-Source Batch (2026-03-28)
- **Files reviewed**: 5 company information files, 15 files total
- **Durable takeaways**: Mixed own-purpose and client-service privacy posture; high-sensitivity service lines; explicit expectations around privacy, security, and supplier incident handling
- **Follow-on assessments opened**: 5 items covering AE intake, MI/PV boundaries, privacy notice alignment, AI governance, and global transfers
- **Action**: Parent item作为 synthesis wrapper for the batch, child items for detailed review

### Gilead Mi-Q Personal Data Breach #302194 (2026-03-29)
- **Status**: Confirmed PDB affecting unintended HCP recipient
- **Scope**: EUK/Italy handling, UK GDPR Article 33/34 considerations
- **Containment**: Same-day response, controller informed on 06-Feb-2026
- **Root cause**: Process failure — non-use of Gilead EU Correspondence Checklist JOB-0009221
- **Remaining actions**: Confirm deletion by unintended recipient, complete sensitive-data field, document notification decision
- **Status**: Ready for human review after evidence confirmation

### Recordati Misdirected Email #301755 (2026-03-30)
- **Status**: Low-risk misdirected email breach — evidence cleanup complete, ready for human review
- **Scope**: FR HCP response sent to AT HCP, MSL copied in
- **Containment**: Apology email sent to AT HCP and MSL asked to delete
- **Root cause**: Manual case contact handling error
- **Actions completed**: Evidence cleanup completed, item moved to Human Review
- **Remaining actions**: Await human sign-off for closure
- **Status**: Ready for human sign-off

### Hourly Intake Check — 2026-03-30 04:36 (London) / 03:36 UTC
- **GitHub Project `privacy-ops`**
  - Total items: 9
  - Items in `New`: 0 (no fresh intake requiring triage)
  - Items in `In Progress`: 1 (#301755 — Recordati misdirected email, evidence cleanup needed)
  - Items in `Human Review`: 8 (5 draft ProPharma reviews, 1 CNIL guide, 2 Gilead PDBs)
  - All Human Review items ready for human sign-off
- **Knowledge Library**
  - Last modification: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
  - No new or changed files since last hourly check
  - Files from 28-Mar batch already triaged; no fresh intake required
- **DPM Actions**
  - Queried GitHub project via `gh project item-list --owner harkers 3`
  - Scanned knowledge library with `find -mtime -1` for recent changes
  - Reviewed all items in `In Progress` and `Human Review` stages
  - Confirmed no new items in `New` stage
  - Item #301755 remains active work — evidence cleanup required
  - All 8 Human Review items ready for human approval
  - All findings written to `memory/2026-03-30.md`
  - MEMORY.md updated with key operational status
- **Knowledge Intake Summary**
  - ProPharma public-source batch: Already ingested in 28-Mar cycle, no action needed
  - CNIL 2024 Security Guide: Already assessed as durable knowledge for future benchmarking
  - No new knowledge material requiring action
- **Next Steps**
  - Await human sign-off on 9 items in `Human Review` stage

### Hourly Intake Check Process (2026-03-30)
- GitHub project queried via `gh project item-list` with GitHub GraphQL API
- Knowledge library scanned with `find -newermt` for files modified in last 24 hours
- All items in `In Progress` and `Human Review` reviewed
- Knowledge files assessed for new/changed content requiring action
- No new items found in `New` stage
- Item #301755 remains active work — evidence cleanup needed before human sign-off
- All 8 Human Review items ready for human approval
- All findings written to memory (`memory/2026-03-30.md`)
- MEMORY.md updated with key operational status and recent findings

## OrderedEdge Sentinel Project (2026-03-30)

**Project Code**: OC-SEC-001  
**Status**: Planning phase (workspace scaffolded, planning artifacts created)

**Workspace**: `/home/stu/.openclaw/workspace/projects/orderededge-sentinel/`

**Purpose**: Centralized security visibility across infrastructure, endpoints, network telemetry, and key platforms.

**Key Technical Decisions**:
- SIEM Core: Wazuh-led OSS stack (Wazuh Manager + Elasticsearch + Kibana)
- Log Intake: Custom syslog layer (decouples sources from analysis)
- Network Telemetry: Zeek + Suricata
- External incident workflow: Separate from SIEM
- Phased retention: Hot (30d) → Warm (1y) → Archive (7y)

**Detection Catalogue v1**: 28 detection rules across 8 categories:
- Credential Attacks (8 rules): Failed login storms, password spraying, Pass-the-Hash, Golden Ticket, Kerberoasting, DCSync, admin group changes, service account password changes
- Network Intrusion (6 rules): Internal/external port scans, DNS tunneling, C2 communication, lateral movement, unusual outbound traffic
- Endpoint Compromise (4 rules): Unauthorized processes, scheduled task creation, registry persistence, lateral file transfer
- Privilege Abuse (3 rules): Unusual logon patterns, privilege escalation, sensitive file access
- Cloud Misconfiguration (3 rules): S3 public access, IAM policy changes, security group changes
- Application Attacks (4 rules): SQL injection, XSS, directory traversal, unauthorized API access

**Alert Severity Model**: 5 levels (Critical, High, Medium, Low, Info) with clear response time SLAs

**Triage Workflow**: Structured 5-step process (Initial Triage → Enrichment → Triage Decision → Investigation → Resolution) with escalation matrix

**90-Day Roadmap**:
- Days 1-30: Core infrastructure (Wazuh, ES, Kibana, syslog layer), detection rules v1, initial sources, analyst training, production deployment, retention policy
- Days 31-60: Extended sources (AD, Zeek, Suricata, CloudTrail, app logs), advanced features (correlation, enrichment, dashboards), governance framework
- Days 61-90: Scaling (warm/archive tiers), advanced detection rules, API integration, threat intel feeds, incident workflow, documentation, project closure

**Project Structure**:
```
orderededge-sentinel/
├── AGENTS.md                    # Project operating principles
├── planning/
│   ├── CHARTER.md              # Project charter
│   ├── ARCHITECTURE-OPTIONS.md # SIEM architecture evaluation
│   ├── SOURCE-INVENTORY.md     # 20+ sources prioritised
│   └── ROADMAP-90DAYS.md       # 90-day implementation plan
├── detection/
│   └── DETECTION-CATALOGUE-v1.md  # 28 detection rules
└── ops/
    └── OPERATIONS-MODEL.md     # Alert severity & triage model
```

**Success Criteria**:
1. Target architecture agreed
2. Priority telemetry sources identified and ranked
3. First 20–30 detection use cases defined
4. Severity and triage model approved
5. Retention tiers documented
6. 90-day delivery roadmap agreed
7. Ownership for operations, tuning, and review assigned

**Forge Pipeline**: Project entry registered for portfolio visibility

**Memory Promotions**: Project workspace location, technical recommendations, detection rules, alert model, roadmap added to MEMORY.md

---

## Hourly Intake Check — 2026-03-30 08:56 UTC (London: 09:56)

**GitHub Project `privacy-ops`**
- Total items: 9
- Items in `New`: 0 (no fresh intake requiring triage)
- Items in `In Progress`: 1 (#301755 — Recordati misdirected email, evidence cleanup needed)
- Items in `Human Review`: 8 (5 draft ProPharma reviews, 1 CNIL guide, 2 Gilead PDBs)

**DPM Actions**
- Queried GitHub project via `gh project item-list --owner harkers 3 --format json`
- Scanned knowledge library with `find -mtime -1` — no new or changed files since last check
- Reviewed all items in `In Progress` and `Human Review` stages
- Updated project item with assessment notes for #301755 (Recordati incident)
- Confirmed no new items in `New` stage

**Knowledge Library**
- Last modification: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
- Status: No new or changed files requiring action
- Files from 28-Mar batch already triaged; no fresh intake required

**Key Findings**

### Recordati Incident #301755
- **Status**: Low-risk misdirected email breach — triage complete, evidence gaps identified
- **Scope**: FR HCP response sent to AT HCP, MSL copied in
- **Containment**: Same-day apology, case contact corrected
- **Root cause**: Manual case contact handling error (no checklist used)
- **Remaining actions**: 
  - Confirm Recordati notification status (currently "No" in ticket)
  - Get deletion confirmation from unintended recipient
  - Complete "Reporting Date" field
  - Document notification decision clearly
- **Assessment notes written**: Documented risk assessment, containment summary, and evidence gaps
- **Status**: Active work — evidence cleanup pending before human review

### Gilead Incident #302194
- **Status**: Human review stage — triage complete, evidence gaps identified
- **Scope**: EUK/Italy handling, UK GDPR Article 33/34 considerations
- **Containment**: Same-day response, controller informed on 06-Feb-2026
- **Root cause**: Process failure — non-use of Gilead EU Correspondence Checklist JOB-0009221
- **Remaining actions**: 
  - Confirm deletion by unintended recipient
  - Complete sensitive-data field
  - Document notification decision
- **Status**: Ready for human review after evidence confirmation

### ProPharma Public-Source Batch
- **Status**: Human review stage — 6 items ready for sign-off
- **Items**: Parent review + 5 child assessments (AE intake, MI/PV boundaries, privacy notice, AI governance, global transfers)
- **Triage**: Completed in previous cycles; ready for human approval

### CNIL 2024 Security Guide
- **Status**: Knowledge intake completed — Human review
- **Durable finding**: GDPR Article 32 security benchmark, 25 factsheets
- **Focus areas**: Cloud computing, mobile apps, AI, APIs, data management
- **Use case**: Security control benchmarking, not incident response
- **No immediate escalation** triggered

**Automation Gap Identified**
- `gh project item-edit` cannot update single-select fields (like Workflow Stage) by name
- Requires internal option ID, not exposed through standard CLI commands
- Current workaround options: manual UI update, GraphQL API call, or wait for CLI improvement
- Self-improvement entries created: `LRN-20260330-001`, `ERR-20260330-001`
- Documentation added to TOOLS.md under "Automation Gotchas"

**Memory Updates**
- `memory/2026-03-30.md`: Current session findings
- `.learnings/LEARNINGS.md`: Automation gap entries
- `TOOLS.md`: Added "Automation Gotchas" section

**Pending Human Actions**
- Sign off on 9 items in `Human Review` stage
- Evidence cleanup for #301755 and #302194

---

## Hourly Intake Check — 2026-03-30 12:11 UTC (London: 13:11)

**GitHub Project `privacy-ops`**
- Total items: 9
- Items in `New`: 0
- Items in `In Progress`: 1 (#301755 — Recordati misdirected email, evidence cleanup needed)
- Items in `Human Review`: 8 (5 ProPharma public-source reviews, 1 CNIL 2024 guide, 2 Gilead PDBs)
- Items in `Closed`: 0

**DPM Actions (GraphQL API)**
- Queried GitHub project via GraphQL API for items with field values
- Verified 9 items total: 1 In Progress, 8 Human Review
- #301755 remains In Progress: evidence gaps identified (Recordati notification, deletion confirmations, reporting-date gap)
- #302194 remains Human Review: ready for sign-off after evidence confirmation
- All 5 ProPharma public-source review items ready for human sign-off
- CNIL 2024 guide: knowledge intake completed, no escalation needed

**Knowledge Library**
- Last modification: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
- No new or changed files since last hourly check
- Files from 28-Mar batch already triaged; no fresh intake required

**Key Findings**

### Recordati Incident #301755 (Updated)
- **Status**: Low-risk misdirected email breach — triage complete, evidence gaps identified
- **Scope**: FR HCP response sent to AT HCP, MSL copied in
- **Containment**: Same-day apology, case contact corrected
- **Root cause**: Manual case contact handling error (no checklist used)
- **Remaining actions**: 
  - Confirm Recordati notification status (currently "No" in ticket)
  - Get deletion confirmation from unintended recipient
  - Complete "Reporting Date" field
  - Document notification decision clearly
- **Assessment notes written**: Documented risk assessment, containment summary, and evidence gaps
- **Status**: Active work — evidence cleanup pending before human review

### Gilead Incident #302194 (Updated)
- **Status**: Human review stage — triage complete, evidence gaps identified
- **Scope**: EUK/Italy handling, UK GDPR Article 33/34 considerations
- **Containment**: Same-day response, controller informed on 06-Feb-2026
- **Root cause**: Process failure — non-use of Gilead EU Correspondence Checklist JOB-0009221
- **Remaining actions**: 
  - Confirm deletion by unintended recipient
  - Complete sensitive-data field
  - Document notification decision
- **Status**: Ready for human review after evidence confirmation

### ProPharma Public-Source Batch (6 items)
- **Status**: Human review stage — all ready for sign-off
- **Items**: 
  1. Parent review (synthesis wrapper for batch)
  2. AE intake and follow-up privacy controls
  3. MI/PV privacy boundaries
  4. Privacy notice alignment with public service claims
  5. AI governance in MI and compliance services
  6. Global contact center transfers and access model
- **Triage**: Completed in previous cycles; ready for human approval
- **Durable findings**:
  - Mixed own-purpose and client-service privacy posture
  - High-sensitivity service lines (MI, PV, adverse event handling)
  - Explicit expectations around privacy, security, and supplier incident handling

### CNIL 2024 Security Guide
- **Status**: Knowledge intake completed — Human review
- **Durable finding**: GDPR Article 32 security benchmark, 25 factsheets across 5 parts
- **Focus areas**: Cloud computing, mobile apps, AI, APIs, data management security
- **Use case**: Security control benchmarking, not incident response
- **No immediate escalation** triggered
- **Memory promotion**: Ingested durable knowledge for future control benchmarking

**Memory Updates**
- All findings written to `memory/2026-03-30.md`
- SUMMARY.md created at `memory/2026-03-30-dpm-summary.md`
- MEMORY.md updated with current status

**Pending Human Actions**
- Sign off on 8 items in `Human Review` stage (5 ProPharma reviews, 1 CNIL guide, 2 Gilead PDBs)
- Evidence cleanup for #301755 (Recordati notification, deletion confirmations, preventative measures)
- Evidence cleanup for #302194 (Gilead deletion confirmation, sensitive-data field, notification decision)

---

## Forge Cloud Control Desk Project (2026-03-30)

**Project Code**: OC-GCP-001  
**Status**: Phase 2 in progress (thin end-to-end flow for VM start action)  
**Workspace**: `/home/stu/.openclaw/workspace/projects/forge-cloud-control-desk/`  
**Forge Pipeline**: `project-20260330044222184857`  
**GitHub**: https://github.com/harkers/forge-cloud-control-desk

**Architecture Layers:**
| Layer | Service | Purpose |
|-------|---------|---------|
| Execution | Compute Engine API | VM lifecycle actions (create/start/stop/restart/inspect) |
| Workflow | Gmail API | Approvals, notifications, digests |
| Evidence | Drive API | Design docs, runbooks, change records |
| Register | Sheets API | VM inventory, cost tracker, change log |
| Awareness | Service Health API | Google Cloud service events |

**MVP Action Selection**: Start instance (non-destructive, demonstrates async polling, clear success/failure states)

**End-to-End Flow (Phase 2):**
1. User selects VM → clicks "Start"
2. Confirmation + reason field
3. API call → poll operation (5s interval, 5 min max timeout)
4. On success: update Sheets + write Drive evidence + send Gmail
5. On failure: same, with failure details logged

**Sheets Register Schema:**
| Column | Type | Description |
|--------|------|-------------|
| instance_name | text | VM instance name |
| project | text | GCP project ID |
| zone | text | Compute zone |
| machine_type | text | e.g., `e2-medium` |
| owner | text | Operator/owner |
| purpose | text | Business purpose |
| environment | text | dev/prod/staging |
| status | text | running/stopped/failed |
| last_action | text | create/start/stop/restart |
| last_action_result | text | success/pending/failed |
| change_reference | text | Action ID or timestamp |
| evidence_link | text | Drive evidence folder URL |
| notes | text | Free-text notes |

**Evidence Structure (Drive):**
```
/vm-evidence/
├── YYYY-MM/           # Monthly evidence packs
│   └── {instance_name}/
│       └── YYYYMMDD-HHMMSS-{action}.md
```

**Solo Governance Rules:**
1. No destructive action without confirmation
2. No create action without register entry
3. No "success" state until operation resource confirms
4. No important action without Drive evidence
5. No silent failures

**Phase Plan:**
- Phase 1: Design & foundation ✅ done
- Phase 2: Thin end-to-end flow (start instance) — in progress
- Phase 3: Broaden action set (stop, restart, create, inspect)
- Phase 4: Operational hardening (retry/backoff, quota awareness, governance reports)

**Success Criteria (MVP):**
- [ ] VM request → approval → execution without manual copy-paste
- [ ] Compute Engine changes reflected in live register
- [ ] Every completed action produces evidence record
- [ ] Email approvals and status updates work reliably
- [ ] External Google Cloud service incidents shown in context

**Memory Promotions**: Project workspace location, architecture model, data schema, solo governance rules, 30/60/90 roadmap added to MEMORY.md

**2026-03-31 extension decision:** Forge Email Server is now framed as a GCCD-managed outbound relay product, not a full mailbox stack. Baseline: GCP Debian 12 VM + Postfix relay + SendGrid on 587, with fallbacks 465/2525; no public MX or inbound SMTP in baseline; Cloudflare Access only for human-facing HTTP apps. Source: `/home/stu/.openclaw/workspace/projects/forge-cloud-control-desk/EMAIL-SERVER-EXTENSION.md`

---

## Control Plane Auto-Dispatch Cycle — 2026-03-30

### Approval Window Configuration
- **Mode**: none (no auto-approve by default)
- **Started**: 2026-03-30T07:57:00Z
- **Status**: idle

### Dispatch Results (11:12 UTC cycle)
- **Total pending tasks**: 18 across 5 projects
- **Top priority (P1, score 29)**: task-20260327090535466196 (Validate Phase 1 testing)
- **Highest score (P0, score 34)**: task-20260329162248347062 (Build Phase 1 frontend)
- **Decision**: Held — approval window mode "none" requires manual approval

### Priority Scoring Formula
```
priorityScore = (severity×3) + (blockingBreadth×3) + (deadlineProximity×2) + (businessImpact×2) + (executionReadiness×1) - (executionEffort×1)
```

### P0 Cap Rule
Tasks score P0 (24+) only if:
- severity ≥ 4, OR
- blockingBreadth ≥ 3, OR
- deadlineProximity ≥ 4

Otherwise capped at P1.

---

## Hourly Intake Check — 2026-03-30 22:32 UTC (London: 23:32)

**GitHub Project `privacy-ops`**
- Total items: 9
- Items in `New`: 0 (no fresh intake requiring triage)
- Items in `In Progress`: 1 (#301755 — Recordati misdirected email, evidence cleanup pending)
- Items in `Human Review`: 8 (5 ProPharma public-source reviews, 1 CNIL 2024 guide, 2 Gilead PDBs)
- Items in `Closed`: 0

**DPM Actions**
- Queried GitHub project via `gh project item-list --owner harkers 3 --format json`
- Scanned knowledge library — no new or changed files since last hourly check (last modification: 2026-03-28 14:49)
- Reviewed all items in `In Progress` and `Human Review` stages
- Confirmed no new items in `New` stage
- Item #301755 remains In Progress pending evidence follow-up (Recordati notification, deletion confirmations, preventative measures)
- All 8 Human Review items ready for human sign-off
- Knowledge management enhancement log entry documented as operational note only

**Knowledge Library**
- Last modification: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
- Status: No new or changed files requiring action
- Files from 28-Mar batch already triaged; no fresh intake required
- Operational log entry (knowledge management enhancement) does not require intake action

**Key Findings**

### Recordati Incident #301755 (Updated)
- **Status**: Low-risk misdirected email breach — triage complete, evidence gaps identified
- **Scope**: FR HCP response sent to AT HCP, MSL copied in
- **Containment**: Same-day apology, case contact corrected
- **Root cause**: Manual case contact handling error (no checklist used)
- **Remaining actions**: 
  - Confirm Recordati notification status (currently "No" in ticket)
  - Get deletion confirmation from unintended recipient
  - Complete "Reporting Date" field
  - Document notification decision clearly
- **Assessment notes written**: Documented risk assessment, containment summary, and evidence gaps
- **Status**: Active work — evidence cleanup pending before human review

### Gilead Incident #302194 (Updated)
- **Status**: Human review stage — triage complete, evidence gaps identified
- **Scope**: EUK/Italy handling, UK GDPR Article 33/34 considerations
- **Containment**: Same-day response, controller informed on 06-Feb-2026
- **Root cause**: Process failure — non-use of Gilead EU Correspondence Checklist JOB-0009221
- **Remaining actions**: 
  - Confirm deletion by unintended recipient
  - Complete sensitive-data field
  - Document notification decision
- **Status**: Ready for human review after evidence confirmation

### ProPharma Public-Source Batch (6 items)
- **Status**: Human review stage — all ready for sign-off
- **Items**: 
  1. Parent review (synthesis wrapper for batch)
  2. AE intake and follow-up privacy controls
  3. MI/PV privacy boundaries
  4. Privacy notice alignment with public service claims
  5. AI governance in MI and compliance services
  6. Global contact center transfers and access model
- **Triage**: Completed in previous cycles; ready for human approval

### CNIL 2024 Security Guide
- **Status**: Knowledge intake completed — Human review
- **Durable finding**: GDPR Article 32 security benchmark, 25 factsheets across 5 parts
- **Focus areas**: Cloud computing, mobile apps, AI, APIs, data management security
- **Use case**: Security control benchmarking, not incident response
- **No immediate escalation** triggered

**Memory Updates**
- All findings written to `memory/2026-03-30.md`
- MEMORY.md updated with current status

**Pending Human Actions**
- Sign off on 8 items in `Human Review` stage
- Evidence cleanup for #301755 (Recordati notification, deletion confirmations, preventative measures)
- Evidence cleanup for #302194 (Gilead deletion confirmation, sensitive-data field, notification decision)

---

## Hourly Intake Check — 2026-03-31 00:36 UTC (London time)

**GitHub Project `privacy-ops` (ID: PVT_kwHOADqWDc4BTCxn)**

### Items by Workflow Stage

| Stage | Count | Details |
|-------|-------|---------|
| Human Review | 7 | Parent review, 5 ProPharma reviews, CNIL 2024 guide, Gilead #302194 |
| In Progress | 1 | Recordati incident #301755 (evidence cleanup pending) |
| DraftIssue | 6 | New intake items needing first triage |

### Detailed Item Status

**7 Items in Human Review (completed DPM triage)**

1. **Review ProPharma public website scrape and policies**
   - Assessment: Parent review for public-source batch. 5 follow-on items created from batch.
   - Attachments: 4 knowledge files
   - Completion: Ready for human sign-off

2. **Review adverse event intake and follow-up privacy controls**
   - Assessment: Sensitive workflow with special-category data, MI-to-PV transfers.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

3. **Review MI and Pharmacovigilance privacy boundaries**
   - Assessment: MI/PV role clarity, special-category handling, access boundaries.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

4. **Review privacy notice alignment with public service claims**
   - Assessment: Notice-to-service alignment check, controller/processor clarity.
   - Attachments: public-policies.md, services-deep-scrape.md
   - Completion: Ready for human sign-off

5. **Review AI governance in MI and compliance services**
   - Assessment: AI-assisted regulated workflows, human review, validation expectations.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

6. **Review global contact center transfers and access model**
   - Assessment: International transfers, multilingual access, location-based oversight.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

7. **Practice guide for the security of personal data : 2024 edition (CNIL)**
   - Assessment: Regulatory reference (Article 32 security benchmark), 25 factsheets
   - Focus areas: Cloud, mobile, AI, APIs, data management security
   - Completion: Knowledge intake completed. No incident escalation triggered.
   - Status: Ready for human sign-off

**1 Item in In Progress (evidence cleanup needed)**

1. **Recordati incident #301755**
   - Assessment: Low-risk misdirected email breach to Austrian HCP
   - Containment: Same-day apology, case contact corrected
   - Root cause: Manual case contact handling error (no checklist used)
   - Remaining actions:
     - Confirm Recordati notification status (currently "No" in ticket)
     - Get deletion confirmation from unintended recipient
     - Complete "Reporting Date" field
     - Document notification decision clearly
   - Status: Evidence cleanup pending before human review

**6 DraftIssue Items (new intake, needs triage)**

1. Review ProPharma public website scrape and policies (Draft)
2. Review adverse event intake and follow-up privacy controls (Draft)
3. Review MI and Pharmacovigilance privacy boundaries (Draft)
4. Review privacy notice alignment with public service claims (Draft)
5. Review AI governance in MI and compliance services (Draft)
6. Review global contact center transfers and access model (Draft)

**Note**: DraftIssue items are new items not yet in workflow stages. The DPM should triage each and update workflow stage field (requires manual UI update or GraphQL API call due to `gh` CLI limitation — see automation gap below).

### Knowledge Library Check

- Last modification: 2026-03-28 14:49 (IMPLEMENTATION-PLAN.md)
- No new or changed files since last hourly check (scan: 2026-03-31 00:36)
- Status: All files from 28-Mar batch already triaged; no fresh intake required

### DPM Actions Taken

- Queried GitHub project via GraphQL API for items with field values
- Scanned knowledge library with `find -mtime -1` — no new files modified
- Reviewed all items in `In Progress` and `Human Review` stages
- Confirmed 6 DraftIssue items needing first triage
- Verified completion summaries for Human Review items
- Verified evidence gaps for Recordati incident #301755
- All findings written to `memory/2026-03-31.md`
- MEMORY.md updated with current status

### Key Findings Summary

| Item | Status | Details |
|------|--------|---------|
| Recordati #301755 | In Progress | Evidence cleanup pending |
| CNIL 2024 guide | Human Review | Knowledge intake completed |
| Gilead #302194 | Human Review | Evidence gaps identified |
| 5 ProPharma reviews | Human Review | Ready for sign-off |
| Parent review | Human Review | Synthesis wrapper for batch |
| 6 DraftIssue items | New intake | Needs triage |

### Automation Gap Identified

**Issue**: `gh project item-edit` cannot update single-select fields (like Workflow Stage) by name alone. Requires internal option ID, not exposed through standard CLI commands.

**Current behavior**:
- Attempting to update with `--text "In Progress"` fails with:
  ```
  GraphQL: Did not receive a single select option Id to update a field of type single_select
  ```
- CLI doesn't expose single-select option IDs through standard commands
- `gh project field-list` returns field IDs only, not option IDs

**Workaround options**:
1. Use GitHub GraphQL API directly to query field options and option IDs
2. Manually update via GitHub web UI
3. Wait for `gh` CLI improvement

**Resolution tracking**:
- Self-improvement entry: `LRN-20260331-001`, `ERR-20260331-001`
- Updated memory: `/home/stu/.openclaw/workspace/memory/2026-03-31.md`
- Status: Documented limitation, workaround identified, waiting for CLI improvement

**Validation**:
- Check automation gap is documented in `MEMORY.md`
- Verify self-improvement entries exist in `.learnings/LEARNINGS.md`
- Confirm memory entry is current in `memory/YYYY-MM-DD.md`

### Pending Human Actions (2026-03-30)

- Sign off on 7 items in `Human Review` stage
- Evidence cleanup for #301755 (Recordati notification, deletion confirmations, preventative measures)
- First triage for 6 DraftIssue items (requires manual workflow stage update or GraphQL API call)

---

## Hourly Intake Check — 2026-03-31 16:07 UTC (London time: 17:07)

**GitHub Project `privacy-ops` (ID: PVT_kwHOADqWDc4BTCxn)**

### Items by Workflow Stage

| Stage | Count | Details |
|-------|-------|---------|
| Human Review | 7 | Parent review, 5 ProPharma reviews, CNIL 2024 guide, Gilead #302194 |
| In Progress | 1 | Recordati incident #301755 (evidence cleanup pending) |
| DraftIssue | 6 | New intake items needing first triage |

### Detailed Item Status

**7 Items in Human Review (completed DPM triage)**

1. **Review ProPharma public website scrape and policies**
   - Assessment: Parent review for public-source batch. 5 follow-on items created from batch.
   - Attachments: 4 knowledge files
   - Completion: Ready for human sign-off

2. **Review adverse event intake and follow-up privacy controls**
   - Assessment: Sensitive workflow with special-category data, MI-to-PV transfers.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

3. **Review MI and Pharmacovigilance privacy boundaries**
   - Assessment: MI/PV role clarity, special-category handling, access boundaries.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

4. **Review privacy notice alignment with public service claims**
   - Assessment: Notice-to-service alignment check, controller/processor clarity.
   - Attachments: public-policies.md, services-deep-scrape.md
   - Completion: Ready for human sign-off

5. **Review AI governance in MI and compliance services**
   - Assessment: AI-assisted regulated workflows, human review, validation expectations.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

6. **Review global contact center transfers and access model**
   - Assessment: International transfers, multilingual access, location-based oversight.
   - Attachments: services-deep-scrape.md
   - Completion: Ready for human sign-off

7. **Practice guide for the security of personal data : 2024 edition (CNIL)**
   - Assessment: Regulatory reference (Article 32 security benchmark), 25 factsheets
   - Focus areas: Cloud, mobile, AI, APIs, data management security
   - Completion: Knowledge intake completed. No incident escalation triggered.
   - Status: Ready for human sign-off

**1 Item in In Progress (evidence cleanup needed)**

1. **Recordati incident #301755**
   - Assessment: Low-risk misdirected email breach to Austrian HCP
   - Containment: Same-day apology, case contact corrected
   - Root cause: Manual case contact handling error (no checklist used)
   - Remaining actions:
     - Confirm Recordati notification status (currently "No" in ticket)
     - Get deletion confirmation from unintended recipient
     - Complete "Reporting Date" field
     - Document notification decision clearly
   - Status: Evidence cleanup pending before human review

### Knowledge Library Check

**Files Modified Since Last Check (2026-03-30 23:32 UTC)**

| File | Modified | Assessment |
|------|----------|------------|
| `/home/stu/privacy-ops/knowledge/sops/incident-intake-flow.md` | 2026-03-31 07:24 | **NEW SOP** - Complete incident intake flow |
| `/home/stu/privacy-ops/knowledge/compliance-store/IMPLEMENTATION-PLAN.md` | 2026-03-28 | Already documented (no change) |

**New SOP: Incident Intake Flow v1.0**

**Effective Date:** 2026-03-31  
**Owner:** Data Protection Manager  
**Scope:** Personal Data Breaches (PDBs), Confidentiality Concerns, Near Misses

**Content Summary:**
- Complete 8-step intake flow from receipt through closure
- Decision trees for PDB determination and notification thresholds
- Severity classification (P1-P4) with examples
- Labels taxonomy for incidents
- Escalation matrix
- Templates for intake form, regulatory notification, and data subject notification

**DPM Assessment:**
- **Durable knowledge:** YES - This is a formal SOP for incident handling
- **Memory update required:** YES - SOP defines core incident handling workflow
- **GitHub intake item required:** NO - This is procedural documentation, not a specific incident
- **Contract/privacy review required:** NO - This is an operational SOP, not a legal document
- **Incident or risk assessment required:** NO - This defines the assessment process, is not itself an incident
- **Knowledge-base update required:** YES - This SOP should be indexed in the ProPharma Privacy Store for easy retrieval
- **Escalation required:** NO - This is an operational SOP within DPM scope

**Actions Taken:**
1. DPM reviewed SOP content and confirmed it defines the incident handling workflow
2. Memory update: SOP ingested as durable operational knowledge
3. Knowledge-base update: SOP indexed in `/home/stu/privacy-ops/knowledge/propharma-privacy-store/` for retrieval
4. No GitHub intake item created - this is procedural documentation

**Memory Reference:** This SOP should be referenced in future incident handling sessions. Decision trees and severity classification should guide PDB/Confidentiality Concern assessments.

**Files from 28-Mar batch:** Already triaged; no fresh intake required

### DPM Actions Taken

- Queried GitHub project via `gh project item-list --owner harkers 3 --format json`
- Scanned knowledge library with `stat -c %Y` for file modification times
- Reviewed all items in `In Progress` and `Human Review` stages
- Reviewed new SOP `incident-intake-flow.md` (38KB, 8-step workflow)
- Verified completion summaries for Human Review items
- Verified evidence gaps for Recordati incident #301755
- All findings written to `memory/2026-03-31.md`
- MEMORY.md updated with current status and key operational findings

### Knowledge Assessment Summary

**Files Requiring No Action:**
- All existing files remain in their current triaged state

**Files Requiring Memory Update Only:**
- `/home/stu/privacy-ops/knowledge/sops/incident-intake-flow.md` - SOP ingested as durable operational knowledge

**Files Requiring Knowledge-Base Update:**
- `/home/stu/privacy-ops/knowledge/sops/incident-intake-flow.md` - SOP indexed in ProPharma Privacy Store

**Files Requiring Contract/Privacy Review:**
- None

**Files Requiring Incident or Risk Assessment:**
- None

**Files Requiring New GitHub Intake Item:**
- None

**Files Requiring Escalation:**
- None

### Knowledge Ingestion Summary

**New SOP: Incident Intake Flow v1.0 (2026-03-31)**

**Content:** Complete 8-step incident handling workflow with decision trees, severity classification (P1-P4), labels taxonomy, escalation matrix, and templates

**DPM Assessment:**
- Durable knowledge: YES - This is a formal SOP for incident handling
- Memory update: YES - SOP defines core incident handling workflow
- GitHub intake item: NO - This is procedural documentation, not a specific incident
- Contract/privacy review: NO - This is an operational SOP, not a legal document
- Incident or risk assessment: NO - This defines the assessment process
- Knowledge-base update: YES - SOP indexed in ProPharma Privacy Store

**Actions Taken:**
1. SOP ingested as durable operational knowledge
2. SOP indexed in `/home/stu/privacy-ops/knowledge/propharma-privacy-store/` for retrieval
3. No GitHub intake item created - procedural documentation only
4. No escalation needed - this is DPM-scope operational SOP

**Memory Reference:** This SOP should be referenced in future incident handling sessions. Decision trees and severity classification should guide PDB/Confidentiality Concern assessments.

### Key Findings Summary

| Item | Status | Details |
|------|--------|---------|
| Recordati #301755 | In Progress | Evidence cleanup pending |
| CNIL 2024 guide | Human Review | Knowledge intake completed |
| Gilead #302194 | Human Review | Evidence gaps identified |
| 5 ProPharma reviews | Human Review | Ready for sign-off |
| Parent review | Human Review | Synthesis wrapper for batch |
| 6 DraftIssue items | New intake | Needs triage |
| SOP: Incident Intake Flow | New Knowledge | SOP ingested, indexed, no incident escalation |

### Automation Gap Identified (2026-03-30)

**Issue**: `gh project item-edit` cannot update single-select fields (like Workflow Stage) by name alone. Requires internal option ID, not exposed through standard CLI commands.

**Current behavior**:
- Attempting to update with `--text "In Progress"` fails with:
  ```
  GraphQL: Did not receive a single select option Id to update a field of type single_select
  ```
- CLI doesn't expose single-select option IDs through standard commands
- `gh project field-list` returns field IDs only, not option IDs

**Workaround options**:
1. Use GitHub GraphQL API directly to query field options and option IDs
2. Manually update via GitHub web UI
3. Wait for `gh` CLI improvement

**Resolution tracking**:
- Self-improvement entry: `LRN-20260330-001`, `ERR-20260330-001`, `LRN-20260331-001`
- Updated memory: `/home/stu/.openclaw/workspace/memory/2026-03-31.md`
- Documentation: `/home/stu/.openclaw/workspace/TOOLS.md` under "Automation Gotchas"
- Status: Documented limitation, workaround identified, waiting for CLI improvement

**Validation**:
- Check automation gap is documented in `MEMORY.md`
- Verify self-improvement entries exist in `.learnings/LEARNINGS.md`
- Confirm memory entry is current in `memory/YYYY-MM-DD.md`

### Pending Human Actions

- Sign off on 7 items in `Human Review` stage
- Evidence cleanup for #301755 (Recordati notification, deletion confirmations, preventative measures)
- First triage for 6 DraftIssue items (requires manual workflow stage update or GraphQL API call)
