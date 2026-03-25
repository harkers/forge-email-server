# Operations Runbook

## Start
```bash
docker compose up -d
```

## Stop
```bash
docker compose down
```

## Rebuild app
```bash
docker compose build app worker
docker compose up -d app worker
```

## View logs
```bash
docker compose logs -f app
docker compose logs -f worker
docker compose logs -f postgres
docker compose logs -f cloudflared
```

## Database shell
```bash
docker compose exec postgres psql -U privacy_app -d privacy_intake
```

## Check queued tasks
```bash
docker compose exec postgres psql -U privacy_app -d privacy_intake -c "select id, case_id, task_type, status, queued_at from tasks order by queued_at desc limit 20;"
```

## Check recent events
```bash
docker compose exec postgres psql -U privacy_app -d privacy_intake -c "select event_at, event_type, summary from task_events order by event_at desc limit 20;"
```

## Backup
```bash
bash ops/backup/backup-postgres.sh
```

## Restore sketch
Use `psql` or `pg_restore` depending on dump format. Test restores on a non-production copy before relying on this operationally.

## Upgrade notes
- review release notes
- back up first
- apply migrations explicitly
- restart app and worker after schema change
