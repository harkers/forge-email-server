# Agent Catalog

Use this catalog to scaffold specialist agents under the control plane.

Each agent definition should answer:
- what it owns
- what it must not own
- typical inputs
- expected outputs
- required verification
- common downstream handoff

## Core control-plane roles

### manager
Owns:
- intake classification
- decomposition
- routing
- handoff contract creation
- verification and review decisions
- final merge status

Must not own:
- broad specialist implementation when a bounded specialist exists
- silent publication without review

Typical outputs:
- task packets
- routing decisions
- review notes
- accepted/rejected status

### reviewer
Owns:
- read-only inspection
- correctness/risk feedback
- defect lists
- acceptance recommendation

Must not own:
- primary implementation in the same pass

Typical outputs:
- review packet
- findings with severity and evidence

## Delivery / engineering roles

### planner
Use for:
- plans
- decomposition
- milestone shaping within a task/workstream
- scope slicing

Owns:
- work breakdown
- sequencing
- dependency notes

Outputs:
- phased plan
- work graph
- acceptance criteria

Handoff to:
- manager or implementation worker

### coding-worker
Use for:
- bounded implementation work
- fixes
- refactors
- code wiring

Owns:
- one write scope at a time
- implementation evidence

Must not own:
- final acceptance
- broad architectural arbitration

Outputs:
- code changes
- commit references
- build/test evidence
- open risk notes

Handoff to:
- reviewer or manager

### architecture-reviewer
Use for:
- boundary checks
- coupling review
- ownership review
- systems design critique

Outputs:
- architecture findings
- change recommendations
- risk notes

Handoff to:
- manager or coding-worker

### security-reviewer
Use for:
- authz/authn review
- input validation review
- secret handling
- exposure/risk review

Outputs:
- security findings
- severity ranking
- remediation guidance

Handoff to:
- manager or coding-worker

### deployer
Use for:
- packaging
- deployment execution
- post-deploy verification
- carrying out an already-diagnosed deployment fix

Must not own:
- product decision-making
- hidden config changes outside assigned target

Outputs:
- artifact/tag reference
- deploy status
- endpoint/health evidence
- rollback note

Handoff to:
- manager

## Analysis / knowledge roles

### investigator
Use for:
- diagnosis
- root-cause analysis
- reproduction attempts
- narrowing unknowns

Outputs:
- findings
- repro steps
- confidence level
- next diagnostic step

Handoff to:
- manager or coding-worker

### researcher
Use for:
- source gathering
- policy lookup
- standards mapping
- evidence extraction from external/public material

Outputs:
- notes
- citations
- evidence summary
- unresolved questions

Handoff to:
- drafting, manager, or domain specialist

### documentation-writer
Use for:
- architecture packs
- specs
- runbooks
- review docs
- polished summaries

Outputs:
- document files
- concise summary
- assumptions/open questions

Handoff to:
- reviewer or manager

## Domain-specialist examples

### privacy-incident
Use for:
- incident chronology
- risk/impact wording
- containment/recovery summaries
- notification support
- evidence-backed incident drafting support

### vendor-assessor
Use for:
- vendor privacy/security review
- data residency extraction
- subprocessor/access analysis
- recommendation drafting
- evidence-gap identification

### drafting
Use for:
- converting structured findings into polished deliverables
- emails
- reports
- briefings
- SOP sections

## Workflow patterns by use case

### Build / feature delivery
1. manager
2. planner (optional)
3. coding-worker
4. reviewer
5. security-reviewer or architecture-reviewer if needed
6. manager acceptance

Use `portfolio-planning-agent` instead of `planner` when the work is cross-project/roadmap-level rather than task-level.

### Bug / incident fix
1. manager
2. investigator
3. coding-worker
4. reviewer
5. deployer if release required
6. manager acceptance

### Deployment
1. manager
2. deployment-diagnosis-agent when the problem is unknown, otherwise deployer
3. reviewer or manager verification
4. manager acceptance

### Research / advisory
1. manager
2. researcher or domain specialist
3. drafting
4. manager review

### Spec / architecture pack
1. manager
2. planner or architecture-reviewer
3. documentation-writer
4. reviewer
5. manager acceptance

Use `forge-wordpress-suite-agent` when suite/plugin-boundary governance is the dominant concern.

### Portfolio / governance
1. manager
2. portfolio-planning-agent
3. workspace-governor-agent when local rules/process need changing
4. documentation-writer when structured docs are needed
5. forge-pipeline-operator-agent or equivalent project-tracking worker
6. manager acceptance

### Privacy incident response
1. manager
2. privacy-incident-agent
3. researcher-agent if external evidence needed
4. drafting-agent for polished deliverable
5. manager review before external release
6. manager acceptance

### Vendor assessment
1. manager
2. vendor-assessor-agent
3. researcher-agent if external evidence needed
4. drafting-agent for polished deliverable
5. manager review before external release
6. manager acceptance

### Deployment diagnosis (runtime failure)
1. manager
2. deployment-diagnosis-agent
3. coding-worker-agent or deployer-agent depending on fix scope
4. reviewer if config changes are involved
5. manager acceptance with runtime verification

## Selection rules

Choose specialists by dominant risk:
- uncertainty -> investigator
- implementation -> coding-worker
- boundary/coupling -> architecture-reviewer
- trust/exposure -> security-reviewer
- release/runtime -> deployer
- external-source synthesis -> researcher
- final prose -> documentation-writer or drafting

When two risks are present, route sequentially rather than giving both ownership of the same write scope.
