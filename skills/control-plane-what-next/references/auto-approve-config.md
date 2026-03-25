# Auto-Approve Configuration

## Storage Location

```
~/.openclaw/workspace/.control-plane-auto-approve.json
```

## Schema

```json
{
  "mode": "time" | "jobs" | "unlimited",
  "started": "ISO-8601 timestamp",
  "expires": "ISO-8601 timestamp | null",
  "jobsRemaining": number | null,
  "completedJobs": [
    {
      "workId": "CP-001",
      "taskType": "coding",
      "model": "qwen3:14b",
      "tokensIn": 50000,
      "tokensOut": 5000,
      "completedAt": "ISO-8601 timestamp"
    }
  ]
}
```

## Modes

### Time-Based

```json
{
  "mode": "time",
  "started": "2026-03-25T09:00:00Z",
  "expires": "2026-03-25T15:00:00Z",
  "completedJobs": []
}
```

Check: `current_time < expires`

### Job-Count-Based

```json
{
  "mode": "jobs",
  "started": "2026-03-25T09:00:00Z",
  "jobsRemaining": 5,
  "completedJobs": []
}
```

Check: `jobsRemaining > 0`
After each job: `jobsRemaining--`

### Unlimited (Until Pipeline Empty)

```json
{
  "mode": "unlimited",
  "started": "2026-03-25T09:00:00Z",
  "completedJobs": []
}
```

Check: pipeline has pending tasks

## Setting Auto-Approve

### Via Command
User says: "auto approve for 6 hours"

Create config:
```json
{
  "mode": "time",
  "started": "2026-03-25T09:00:00Z",
  "expires": "2026-03-25T15:00:00Z",
  "completedJobs": []
}
```

### Via Menu
Present options:
1. Next 6 hours
2. Next 5 control-plane jobs
3. Next 12 hours
4. Next 24 hours
5. Next 72 hours
6. Until all jobs completed

User selects, create appropriate config.

## Expiration

### Time-Based
On next invocation, check current time against expires.
If expired, clear config and ask for new approval.

### Job-Based
After each job, decrement jobsRemaining.
When jobsRemaining === 0, clear config and ask for new approval.

### Unlimited
Check if pipeline has pending tasks.
If pipeline empty, clear config and report completion.

## Reporting

After each job completion:
```
Auto-approve remaining: 3 jobs | 4h 23m remaining
```

On expiration:
```
Auto-approve window expired. Set new window? [Options...]
```