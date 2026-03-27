# Deployment Plan

## Scope

Phase 1 internal-only local dashboard for OpenClaw usage visibility on titan.

## Design

- single Python file
- no database
- reads OpenClaw `sessions.json` and transcript `*.jsonl`
- aggregates by day, week, month
- breakdown by model, provider, channel
- shows `unknown` for incomplete persisted usage instead of treating missing values as real zeroes
- bind to `127.0.0.1:8899` by default

## Constraints

- preserve existing titan service architecture
- do not change nginx -> lighttpd -> php-fpm -> WordPress chain
- do not expose the dashboard externally in phase 1
- do not change gateway config in phase 1

## Next phases

- phase 2: diagnostics / OTel-backed authoritative metrics
- phase 3: pricing rules, alerts, and optional authenticated front-end exposure if explicitly requested
