#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'api' / 'storage' / 'forge-pipeline.db'
OUT_DIR = ROOT / 'backups'


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = OUT_DIR / f'forge-pipeline-export-{stamp}.json'

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    projects_rows = conn.execute('SELECT * FROM projects ORDER BY updated_at DESC').fetchall()
    tasks_rows = conn.execute('SELECT * FROM tasks ORDER BY updated_at DESC').fetchall()
    events_rows = conn.execute('SELECT * FROM events ORDER BY created_at DESC').fetchall()

    tasks_by_project = {}
    for row in tasks_rows:
        tasks_by_project.setdefault(row['project_id'], []).append({
            'id': row['id'],
            'title': row['title'],
            'status': row['status'],
            'priority': row['priority'],
            'dueDate': row['due_date'],
            'tags': json.loads(row['tags_json'] or '[]'),
            'notes': row['notes'],
            'updatedAt': row['updated_at'],
        })

    projects = []
    for row in projects_rows:
        projects.append({
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'notes': row['notes'],
            'status': row['status'],
            'tags': json.loads(row['tags_json'] or '[]'),
            'updatedAt': row['updated_at'],
            'tasks': tasks_by_project.get(row['id'], []),
        })

    events = [{
        'id': row['id'],
        'kind': row['kind'],
        'createdAt': row['created_at'],
        'payload': json.loads(row['payload_json'] or '{}'),
    } for row in events_rows]

    payload = {
        'exportedAt': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'projects': projects,
        'events': events,
    }

    out.write_text(json.dumps(payload, indent=2))
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
