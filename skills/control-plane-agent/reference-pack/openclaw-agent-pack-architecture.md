# Architecture Reference

## Objective

Provide a robust and comprehensible pattern for running multiple OpenClaw specialist agents in parallel, with Docker-based isolation, structured work handoff, and manager-controlled retrieval.

## High-level topology

```text
User / Intake
    |
    v
OpenClaw Gateway
    |
    +--> manager agent
             |
             +--> writes task packet to queue
             |
             +--> routes by workstream
                        |
                        +--> privacy-incident agent
                        +--> vendor-assessor agent
                        +--> research agent
                        +--> drafting agent

Shared orchestration storage
    - /queue/inbox
    - /queue/claimed
    - /queue/done
    - /queue/failed
    - /artifacts/<task-id>
    - /state/tasks
    - /state/reviews
```

## Control plane

The OpenClaw gateway is the control plane. It should not be duplicated per task. Native multi-agent support is preferred over launching multiple full gateway instances.

The manager agent is the orchestration authority. It decides:

- which specialist should receive work
- what the expected output shape is
- whether the returned work is accepted, revised, rejected, or re-routed
- whether external-facing output is ready

## Specialist agents

Each specialist agent should be tightly scoped.

### manager
Responsibilities:
- intake classification
- task packet creation
- routing
- review and merge
- audit log summary

### privacy-incident
Responsibilities:
- incident chronology drafting
- risk and impact summarisation
- containment/recovery wording
- notification decision support

### vendor-assessor
Responsibilities:
- vendor privacy/security posture review
- data residency and access-location extraction
- subprocessor/access analysis
- recommendation drafting

### research
Responsibilities:
- policy and regulatory lookup
- external source synthesis
- standards mapping
- evidence gathering

### drafting
Responsibilities:
- convert structured findings to polished outputs
- produce briefings, emails, reports, SOP sections
- preserve requested voice/tone and output format

## Workspace strategy

Each agent receives:

- private workspace
- private state directory (`agentDir`)
- private logs/temp area
- shared read/write queue access only where necessary

Example layout:

```text
/srv/openclaw/agents/manager/workspace
/srv/openclaw/agents/manager/state
/srv/openclaw/agents/privacy-incident/workspace
/srv/openclaw/agents/privacy-incident/state
/srv/openclaw/agents/vendor-assessor/workspace
/srv/openclaw/agents/vendor-assessor/state
```

## Handoff pattern

### Queue directories

```text
/srv/forgeorchestrate/queue/
  inbox/
  claimed/
  done/
  failed/
```

### Task lifecycle

1. Manager creates task packet in `inbox/`
2. Specialist claims task by moving it to `claimed/`
3. Specialist processes task in its own sandbox
4. Specialist writes outputs to `artifacts/<task-id>/`
5. Specialist writes `done/<task-id>.result.json`
6. Manager reviews and either:
   - accepts
   - reworks internally
   - sends to another specialist
   - fails and escalates

### Why file-based handoff first

- simple to debug
- observable without extra tooling
- easy to back up
- easy to audit
- low dependency footprint

## Task contract

A task packet should always define:

- task id
- assigned agent
- parent task id where relevant
- objective
- input paths and parameters
- constraints
- expected output type/path
- priority
- status

A result packet should always define:

- task id
- agent id
- completion status
- summary
- artifact paths
- review requirement
- confidence level
- known issues/open questions

## Docker model

There are two useful layers of Docker in this design.

### Layer 1: gateway/service containerisation
Optional. Run OpenClaw gateway itself in Docker only if it fits your operational model.

### Layer 2: per-agent sandboxing
Recommended. Each specialist executes tools in a sandbox profile appropriate to its function.

Examples:

- research agent: browser-enabled sandbox
- drafting agent: text-focused sandbox with limited network access
- vendor-assessor: browser + document parsing profile
- code agent, if later added: Python/dev toolchain profile

## Network and secrets posture

Default position:

- no new public ports
- restrict bind addresses to LAN / reverse proxy path as needed
- mount secrets read-only
- use separate credentials per agent where practical
- deny broad outbound access for agents that do not need it

## Review gate

The manager agent must validate specialist outputs before:

- external email is sent
- files are exported to clients
- records are written into source systems
- sensitive summaries are surfaced to end users

Without a review gate, multi-agent becomes multi-chaos.

## Scale path

### Phase 1
- queue files only
- manager + 2 specialists
- artifact folders
- manual review

### Phase 2
- Postgres task index
- retries/timeouts
- status dashboard
- metrics by workstream and agent

### Phase 3
- per-client isolated agent groups
- secret segmentation
- approval policies
- differentiated model/provider routing

