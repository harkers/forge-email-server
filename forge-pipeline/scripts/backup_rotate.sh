#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

cd "$ROOT"

EXPORT_PATH="$(./scripts/export_db.py)"
echo "Created backup: $EXPORT_PATH"

find "$ROOT/backups" -maxdepth 1 -type f -name 'forge-pipeline-export-*.json' -mtime +"$RETENTION_DAYS" -print -delete
