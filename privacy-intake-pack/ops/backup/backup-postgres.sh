#!/usr/bin/env bash
set -euo pipefail

TS="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="/opt/privacy-intake/backups"
mkdir -p "$BACKUP_DIR"

docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-privacy_app}" "${POSTGRES_DB:-privacy_intake}" > "${BACKUP_DIR}/privacy_intake_${TS}.sql"

find "$BACKUP_DIR" -type f -name 'privacy_intake_*.sql' -mtime +14 -delete

echo "Backup written to ${BACKUP_DIR}/privacy_intake_${TS}.sql"
