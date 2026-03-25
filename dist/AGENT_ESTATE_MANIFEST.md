# Agent Estate Manifest

**Packaged:** 2026-03-25
**Version:** 1.0.0

## Contents

### Core Orchestration
- `control-plane-agent.skill` — Orchestration governor, handoff schema owner, verification model

### Core Specialists
- `manager-agent.skill` — Concrete orchestration authority
- `planner-agent.skill` — Task-level decomposition and sequencing
- `coding-worker-agent.skill` — Bounded implementation scope
- `reviewer-agent.skill` — Read-only correctness review
- `investigator-agent.skill` — Diagnosis and uncertainty reduction
- `documentation-writer-agent.skill` — Specs, runbooks, structured docs
- `architecture-reviewer-agent.skill` — Boundary and coupling review
- `security-reviewer-agent.skill` — Trust-boundary and exposure review
- `deployer-agent.skill` — Deployment execution and verification
- `researcher-agent.skill` — Source-backed external evidence
- `drafting-agent.skill` — Polished final writing

### Domain Specialists
- `privacy-incident-agent.skill` — Incident chronology and risk framing
- `vendor-assessor-agent.skill` — Vendor privacy/security review
- `forge-pipeline-operator-agent.skill` — Forge Pipeline state reflection
- `workspace-governor-agent.skill` — Workspace-local governance
- `forge-wordpress-suite-agent.skill` — ForgeWordPress suite governance
- `deployment-diagnosis-agent.skill` — Deployment/runtime failure diagnosis
- `portfolio-planning-agent.skill` — Portfolio-level planning and structuring

## Model Routing

Default model assignments (see `control-plane-agent/references/model-routing-matrix.md` for full details):

| Role | Default Model | Escalate To |
|------|---------------|-------------|
| control-plane-agent | gpt-oss:20b | Codex |
| manager-agent | qwen3.5:397b-cloud | Codex |
| security-reviewer-agent | Codex | — |
| coding-worker-agent | qwen3-coder-next:cloud | Codex |
| investigator-agent | gemma3:12b | qwen3.5 |
| deployment-diagnosis-agent | gemma3:12b | qwen3.5 |

**Note:** Avoid thinking models (deepseek-r1, phi4-reasoning) for subagents — output format issues.

## Installation

```bash
# Copy skill files to OpenClaw skills directory
cp *.skill ~/.openclaw/skills/

# Or extract individual skills
tar -xzf agent-estate-v1.tar.gz -C ~/.openclaw/skills/
```

## Usage

Each skill includes a SKILL.md with:
- Trigger description
- Responsibilities
- Rules
- Output format
- References

## License

Part of the OpenClaw agent estate. Use according to your OpenClaw license.