#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'api' / 'storage' / 'forge-pipeline.db'


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: import_db.py <export.json>', file=sys.stderr)
        return 2

    src = Path(sys.argv[1]).resolve()
    payload = json.loads(src.read_text())
    projects = payload.get('projects', [])
    events = payload.get('events', [])

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks')
    cur.execute('DELETE FROM projects')
    cur.execute('DELETE FROM events')

    for project in projects:
        cur.execute(
            'INSERT INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                project['id'], project.get('name', 'Untitled project'), project.get('description', ''), project.get('notes', ''),
                project.get('status', 'active'), json.dumps(project.get('tags', [])), project.get('updatedAt', ''),
            ),
        )
        for task in project.get('tasks', []):
            cur.execute(
                'INSERT INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    task['id'], project['id'], task.get('title', 'Untitled task'), task.get('status', 'todo'), task.get('priority', 'medium'),
                    task.get('dueDate', ''), json.dumps(task.get('tags', [])), task.get('notes', ''), task.get('updatedAt', ''),
                ),
            )

    for event in events:
        cur.execute(
            'INSERT INTO events (id, kind, created_at, payload_json) VALUES (?, ?, ?, ?)',
            (event['id'], event.get('kind', 'event'), event.get('createdAt', ''), json.dumps(event.get('payload', {}))),
        )

    conn.commit()
    conn.close()
    print(f'imported {len(projects)} projects and {len(events)} events from {src}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
