# Security Model

## Goal

Preserve clear trust boundaries while enabling parallel specialist work.

## Security principles

1. Least privilege
2. Explicit routing
3. Structured handoff
4. Review before release
5. No shared persistent state except intended queue/artifacts

## Boundary layers

### OpenClaw agent identity boundary
Each agent gets its own:
- workspace
- state directory
- optional auth profile
- tool access policy

### Docker sandbox boundary
Each agent gets a sandbox profile appropriate to its risk and function.

### Shared queue boundary
The queue is the only intended shared handoff path in MVP.

## Risks and controls

### Risk: agent state collision
Control:
- never reuse `agentDir`
- separate session stores and workspace paths

### Risk: uncontrolled cross-context leakage
Control:
- private workspaces
- manager-only merge/review
- do not let specialists browse other agent workspaces

### Risk: over-permissive network egress
Control:
- sandbox-specific network policy
- no broad outbound access by default
- only enable browser/network capability where required

### Risk: silent failure or dropped work
Control:
- explicit status files
- claimed/done/failed queue states
- timeout and retry policy once Postgres/monitoring is added

### Risk: unsafe automated publication
Control:
- manager approval gate
- outbound actions disabled or tightly constrained in MVP

## Logging and audit

Minimum recommended logs:
- task created timestamp
- task claimed timestamp
- assigned agent
- completion status
- artifact path
- review decision
- reviewer/manager note

Store summaries in `/srv/forgeorchestrate/state/reviews` initially.

## Secrets guidance

- use environment variables or mounted secret files
- mount read-only
- scope credentials to agent function
- avoid one shared super-token where possible

## Port and exposure guidance

- prefer reverse proxy path already in use
- avoid exposing extra ports externally
- bind locally or to LAN where appropriate
- keep sandbox execution plane off the public edge

