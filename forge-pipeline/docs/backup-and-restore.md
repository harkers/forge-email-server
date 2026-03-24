# Forge Pipeline Backup / Export / Import

Forge Pipeline now includes practical backup/export/import tools.

## What is available

### API export endpoint

- `GET /api/export`

Returns a JSON snapshot containing:
- projects
- tasks
- events
- export timestamp

This is useful for:
- backup pulls
- migrations
- external archiving
- debugging state safely

### CLI export tool

```bash
./scripts/export_db.py
```

This creates a timestamped export JSON file in:
- `backups/`

Example output:
- `backups/forge-pipeline-export-20260324T104300Z.json`

### CLI import tool

```bash
./scripts/import_db.py backups/forge-pipeline-export-20260324T104300Z.json
```

This replaces current DB contents with the exported data.

## Recommended backup pattern

For practical operations:

1. schedule regular export snapshots
2. keep timestamped exports in `backups/`
3. optionally sync backup files elsewhere
4. test restore occasionally instead of trusting vibes

## Important note

The import script is destructive:
- it clears current projects/tasks/events before importing the provided export file

So treat it like a proper restore, not a merge.
