# OpenClaw Environment Health Checklist

Run periodically (recommended: 2-4 times per day during heartbeats).

## Quick Checks (always run)

### Quarto
```bash
~/.local/bin/quarto --version
```
Expected: `1.4.557` or later

If broken, check:
- `~/.local/bin/quarto` should symlink to `~/.local/quarto/bin/quarto`
- bundled Deno at `~/.local/quarto/bin/tools/x86_64/deno` should exist

### Forge Pipeline API
```bash
curl -s http://127.0.0.1:18103/health | jq
```
Expected: `{"status": "ok"}` or similar healthy response

### OpenClaw Usage Dashboard
```bash
curl -s http://127.0.0.1:8899/api/health | jq
```
Expected: `{"ok": true, ...}` with session count

### Local Model Lanes
```bash
# Phi-4-mini
curl -s http://127.0.0.1:8091/v1/models | jq

# Coder-7B
curl -s http://127.0.0.1:8092/v1/models | jq

# Ollama
curl -s http://127.0.0.1:11434/api/tags | jq
```
Expected: each should return model lists without error

### Memory Search
```bash
# Quick test - should return results without error
openclaw memory search "test" --max-results 1
```
Expected: search completes without error

## Extended Checks (run less frequently)

### Stale Paired Devices
```bash
openclaw nodes status
```
Check for:
- devices that haven't checked in recently
- devices with stale location data
- devices with failed commands stuck in queue

### Forge Pipeline Sync
```bash
ls -la /data/appdata/forge-pipeline/
```
Check for:
- recent updates to project entries
- stale entries not updated in >7 days

### ZFS Pool Health
```bash
zpool status data
```
Expected: state `ONLINE`, no errors

### Docker Containers
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```
Check for:
- expected containers running
- no unhealthy status
- no unexpected containers

### Disk Space
```bash
df -h / /data
```
Check for:
- no filesystem >85% full
- /data pool has room

## Checklist Tracking

Store last check times in `memory/heartbeat-state.json`:

```json
{
  "lastChecks": {
    "quarto": 1703275200,
    "forge-pipeline": 1703275200,
    "usage-dashboard": 1703275200,
    "model-lanes": 1703275200,
    "memory-search": 1703275200,
    "paired-devices": 1703260800,
    "zfs-health": 1703246400,
    "docker": 1703246400,
    "disk-space": 1703246400
  }
}
```

## When to Alert

- Quick checks fail 2+ times in a row
- Extended checks show unhealthy state
- Disk space >85%
- ZFS pool degraded
- Model lanes unreachable
- Forge Pipeline or Usage Dashboard down

## Remediation Notes

### Quarto broken
- Check symlink: `ls -la ~/.local/bin/quarto`
- Verify bundle: `ls -la ~/.local/quarto/bin/quarto`
- Re-symlink if needed: `ln -sf ~/.local/quarto/bin/quarto ~/.local/bin/quarto`

### Forge Pipeline down
- Check MCP process: `ps aux | grep forge-pipeline`
- Restart if needed: see TOOLS.md for restart command

### Usage Dashboard down
- Restart: `cd /home/stu/.openclaw/workspace/projects/openclaw-usage-dashboard && python3 openclaw_usage_dashboard.py`

### Model lanes unreachable
- Check llama.cpp processes: `ps aux | grep llama`
- Verify ports: `ss -tlnup | grep -E "(8091|8092|11434)"`

### Memory search broken
- Check OpenClaw gateway: `openclaw gateway status`
- Check config for `memory` plugin