# Validation

## Functional checks

1. Start the dashboard:
   ```bash
   cd /home/stu/.openclaw/workspace/projects/openclaw-usage-dashboard
   python3 openclaw_usage_dashboard.py
   ```
2. Confirm health endpoint responds:
   ```bash
   curl -s http://127.0.0.1:8899/api/health | jq
   ```
3. Confirm dashboard payload responds:
   ```bash
   curl -s http://127.0.0.1:8899/api/dashboard | jq '.stats, .summary.day[0], .recentSessions[0]'
   ```
4. Open `http://127.0.0.1:8899` locally and verify:
   - summary tables render
   - recent sessions render
   - rows with missing usage show `unknown`
   - no external binding is used unless explicitly configured

## Validation outcome for initial delivery

- script starts successfully
- `/api/health` returns session source stats
- `/api/dashboard` returns aggregated dashboard payload
- bind defaults to `127.0.0.1:8899`
