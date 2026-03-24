# Forge Pipeline Scheduled Backup Automation

Forge Pipeline now includes a simple backup rotation script:

- `scripts/backup_rotate.sh`

## What it does

1. runs the export tool
2. writes a timestamped JSON snapshot into `backups/`
3. deletes old snapshots beyond the configured retention period

## Default retention

By default:
- `RETENTION_DAYS=14`

Override it like this:

```bash
RETENTION_DAYS=30 ./scripts/backup_rotate.sh
```

## Manual run

```bash
./scripts/backup_rotate.sh
```

## Cron example

Run every night at 02:15:

```cron
15 2 * * * cd /path/to/forge-pipeline && ./scripts/backup_rotate.sh >> /var/log/forge-pipeline-backup.log 2>&1
```

## Docker / container note

If Forge Pipeline runs in Docker, you have two practical options:

### Option 1 — host-side scheduler

Run the backup script on the host against the mounted project directory.

This is the simplest option.

### Option 2 — separate scheduled container/task

Run the export command in a scheduled container or host cron job that has access to:
- the project directory
- the SQLite DB volume

## Recommended practice

- keep backups on persistent storage
- rotate them automatically
- occasionally copy snapshots off-box
- test restore once in a while instead of trusting optimism
