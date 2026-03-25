# Agent Estate — Pull Instructions

## Download

From Mac or any OpenClaw instance:

```bash
# Download the estate bundle
scp user@titan:/home/stu/.openclaw/workspace/dist/agent-estate-v1-2026-03-25.tar.gz ~/.openclaw/

# Extract
cd ~/.openclaw
tar -xzf agent-estate-v1-2026-03-25.tar.gz

# Skills are now available
```

## Individual Skills

If you only need specific skills:

```bash
# Single skill
scp user@titan:/home/stu/.openclaw/workspace/dist/control-plane-agent.skill ~/.openclaw/skills/
scp user@titan:/home/stu/.openclaw/workspace/dist/manager-agent.skill ~/.openclaw/skills/

# Core specialists
scp user@titan:/home/stu/.openclaw/workspace/dist/{planner-agent,coding-worker-agent,reviewer-agent}.skill ~/.openclaw/skills/

# All skills at once
scp user@titan:/home/stu/.openclaw/workspace/dist/*.skill ~/.openclaw/skills/
```

## ClawHub (Future)

When ready for ClawHub publishing:

```bash
clawhub login
clawhub publish control-plane-agent
clawhub publish manager-agent
# ... etc
```

## Current Bundle

- **File:** `agent-estate-v1-2026-03-25.tar.gz`
- **Size:** 47K
- **Skills:** 19 total
- **Manifest:** `AGENT_ESTATE_MANIFEST.md`