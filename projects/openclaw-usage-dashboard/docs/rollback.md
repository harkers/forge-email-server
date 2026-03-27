# Rollback

1. Stop the dashboard process if running.
2. Remove or ignore the project directory:
   ```bash
   cd /home/stu/.openclaw/workspace
   # optional cleanup if you explicitly want removal later
   # trash projects/openclaw-usage-dashboard
   ```
3. Remove any future launcher, reverse proxy, cron, or service unit added for this dashboard.
4. Remove the corresponding TOOLS.md registry entry if the capability is being fully retired.
5. Re-validate that no listener remains on the dashboard port:
   ```bash
   ss -tlnp | grep 8899 || true
   ```

## Rollback impact

- no core OpenClaw services are changed by phase 1
- no gateway config is changed by phase 1
- no nginx/lighttpd/WordPress/MariaDB/Ollama bindings are modified by phase 1
