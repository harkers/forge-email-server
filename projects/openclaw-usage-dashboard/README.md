# OpenClaw Usage Dashboard

Internal-only lightweight dashboard for OpenClaw session/token/cost visibility on titan.

## Purpose

Provides a day/week/month dashboard by parsing OpenClaw session metadata and transcript JSONL files. It is designed to handle incomplete usage persistence from some local or OpenAI-compatible providers by showing `unknown` instead of fake precision.

## Run

```bash
cd /home/stu/.openclaw/workspace/projects/openclaw-usage-dashboard
python3 openclaw_usage_dashboard.py
```

Then open:

- `http://127.0.0.1:8899`

## Environment overrides

```bash
OPENCLAW_AGENT_ID=main
OPENCLAW_SESSIONS_DIR=/home/stu/.openclaw/agents/main/sessions
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8899
```

## Endpoints

- `/` - HTML dashboard
- `/api/dashboard` - JSON payload used by the dashboard
- `/api/health` - basic health and source stats

## Notes

- Source of truth for phase 1 is `sessions.json` plus transcript `*.jsonl`
- Token reporting and cost reporting are tracked separately
- Some local / OpenAI-compatible providers may record tokens while persisting `cost.total = 0` or omitting cost entirely; those rows now show **reported tokens** with **unknown cost** rather than fake zero spend
- Phase 2 should add diagnostics / OTel-backed metrics if authoritative provider metrics are needed
