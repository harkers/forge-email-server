#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
STORAGE_DIR = ROOT / "storage"
DB_FILE = STORAGE_DIR / "forge-pipeline.db"
LEGACY_JSON_FILE = STORAGE_DIR / "forge-pipeline.json"
LEGACY_EVENTS_FILE = STORAGE_DIR / "events.json"
API_KEY = os.environ.get("FORGE_PIPELINE_API_KEY", "")

DEFAULT_DATA = {
    "projects": [
        {
            "id": "privacy-dsar",
            "name": "Privacy / DSAR",
            "description": "Handle access requests and related compliance tasks.",
            "notes": "Track deadlines carefully and maintain a full audit trail.",
            "status": "active",
            "tags": ["privacy", "compliance"],
            "updatedAt": None,
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Review intake template",
                    "status": "todo",
                    "priority": "high",
                    "dueDate": "2026-03-31",
                    "tags": ["privacy", "template"],
                    "notes": "Check wording and deadline language.",
                    "updatedAt": None,
                }
            ],
        },
        {
            "id": "display-forge",
            "name": "Display Forge",
            "description": "Build the signage platform and playback stack.",
            "notes": "Focus on API, scheduling, playback resilience, and admin flow.",
            "status": "active",
            "tags": ["signage", "platform"],
            "updatedAt": None,
            "tasks": [
                {
                    "id": "task-2",
                    "title": "Add scheduling logic",
                    "status": "in-progress",
                    "priority": "high",
                    "dueDate": "2026-03-28",
                    "tags": ["api", "schedule"],
                    "notes": "Eligibility and expiry rules first.",
                    "updatedAt": None,
                }
            ],
        },
    ]
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    conn = db()
    cur = conn.cursor()
    cur.executescript(
        '''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'active',
            tags_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT NOT NULL DEFAULT '',
            tags_json TEXT NOT NULL DEFAULT '[]',
            notes TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}'
        );
        '''
    )
    conn.commit()
    conn.close()
    migrate_if_needed()


def project_count(conn: sqlite3.Connection) -> int:
    return conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0]


def event_count(conn: sqlite3.Connection) -> int:
    return conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]


def migrate_if_needed() -> None:
    conn = db()
    if project_count(conn) == 0:
        if LEGACY_JSON_FILE.exists():
            data = json.loads(LEGACY_JSON_FILE.read_text())
        else:
            data = DEFAULT_DATA
        import_projects(conn, data.get('projects', []))
    if event_count(conn) == 0 and LEGACY_EVENTS_FILE.exists():
        data = json.loads(LEGACY_EVENTS_FILE.read_text())
        for event in data.get('events', []):
            conn.execute(
                'INSERT OR REPLACE INTO events (id, kind, created_at, payload_json) VALUES (?, ?, ?, ?)',
                (event.get('id') or new_id('event'), event.get('kind', 'legacy.event'), event.get('createdAt', now_iso()), json.dumps(event.get('payload', {}))),
            )
    conn.commit()
    conn.close()


def import_projects(conn: sqlite3.Connection, projects: list[dict]) -> None:
    stamp = now_iso()
    for project in projects:
        conn.execute(
            'INSERT OR REPLACE INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                project.get('id') or slugify(project.get('name', 'project')),
                project.get('name', 'Untitled project'),
                project.get('description', ''),
                project.get('notes', ''),
                project.get('status', 'active'),
                json.dumps(project.get('tags', [])),
                project.get('updatedAt') or stamp,
            ),
        )
        for task in project.get('tasks', []):
            conn.execute(
                'INSERT OR REPLACE INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    task.get('id') or new_id('task'),
                    project.get('id') or slugify(project.get('name', 'project')),
                    task.get('title', 'Untitled task'),
                    task.get('status', 'todo'),
                    task.get('priority', 'medium'),
                    task.get('dueDate', ''),
                    json.dumps(task.get('tags', [])),
                    task.get('notes', ''),
                    task.get('updatedAt') or stamp,
                ),
            )


def row_to_project(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    return {
        'id': row['id'],
        'name': row['name'],
        'description': row['description'],
        'notes': row['notes'],
        'status': row['status'],
        'tags': json.loads(row['tags_json'] or '[]'),
        'updatedAt': row['updated_at'],
        'tasks': get_tasks_for_project(conn, row['id']),
    }


def row_to_task(row: sqlite3.Row) -> dict:
    return {
        'id': row['id'],
        'title': row['title'],
        'status': row['status'],
        'priority': row['priority'],
        'dueDate': row['due_date'],
        'tags': json.loads(row['tags_json'] or '[]'),
        'notes': row['notes'],
        'updatedAt': row['updated_at'],
    }


def get_project(conn: sqlite3.Connection, project_id: str):
    row = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    return row_to_project(conn, row) if row else None


def get_project_by_name(conn: sqlite3.Connection, name: str):
    row = conn.execute('SELECT * FROM projects WHERE lower(name) = lower(?)', (name.strip(),)).fetchone()
    return row_to_project(conn, row) if row else None


def get_tasks_for_project(conn: sqlite3.Connection, project_id: str) -> list[dict]:
    rows = conn.execute('SELECT * FROM tasks WHERE project_id = ? ORDER BY updated_at DESC', (project_id,)).fetchall()
    return [row_to_task(row) for row in rows]


def get_task(conn: sqlite3.Connection, project_id: str, task_id: str):
    row = conn.execute('SELECT * FROM tasks WHERE project_id = ? AND id = ?', (project_id, task_id)).fetchone()
    return row_to_task(row) if row else None


def get_task_by_title(conn: sqlite3.Connection, project_id: str, title: str):
    row = conn.execute('SELECT * FROM tasks WHERE project_id = ? AND lower(title) = lower(?)', (project_id, title.strip())).fetchone()
    return row_to_task(row) if row else None


def list_projects(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute('SELECT * FROM projects ORDER BY updated_at DESC').fetchall()
    return [row_to_project(conn, row) for row in rows]


def list_events(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    rows = conn.execute('SELECT * FROM events ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    return [
        {'id': row['id'], 'kind': row['kind'], 'createdAt': row['created_at'], 'payload': json.loads(row['payload_json'] or '{}')}
        for row in rows
    ]


def record_event(kind: str, payload: dict) -> dict:
    conn = db()
    entry = {
        'id': new_id('event'),
        'kind': kind,
        'createdAt': now_iso(),
        'payload': payload,
    }
    conn.execute(
        'INSERT INTO events (id, kind, created_at, payload_json) VALUES (?, ?, ?, ?)',
        (entry['id'], entry['kind'], entry['createdAt'], json.dumps(entry['payload'])),
    )
    conn.execute(
        "DELETE FROM events WHERE id NOT IN (SELECT id FROM events ORDER BY created_at DESC LIMIT 500)"
    )
    conn.commit()
    conn.close()
    return entry


def new_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def slugify(text: str) -> str:
    out = ''.join(ch.lower() if ch.isalnum() else '-' for ch in text).strip('-')
    while '--' in out:
        out = out.replace('--', '-')
    return out or new_id('project')


def project_matches(project: dict, query: str | None, status: str | None) -> bool:
    blob = ' '.join([
        project.get('name', ''),
        project.get('description', ''),
        project.get('notes', ''),
        ' '.join(project.get('tags', [])),
    ]).lower()
    if query and query.lower() not in blob:
        task_hit = any(task_matches(t, query, None) for t in project.get('tasks', []))
        if not task_hit:
            return False
    if status and project.get('status') != status:
        return False
    return True


def task_matches(task: dict, query: str | None, status: str | None) -> bool:
    blob = ' '.join([
        task.get('title', ''),
        task.get('notes', ''),
        task.get('priority', ''),
        task.get('status', ''),
        task.get('dueDate', '') or '',
        ' '.join(task.get('tags', [])),
    ]).lower()
    if query and query.lower() not in blob:
        return False
    if status and task.get('status') != status:
        return False
    return True


def upsert_project(conn: sqlite3.Connection, body: dict) -> tuple[dict, str]:
    project_id = body.get('id')
    name = body.get('name')
    project = get_project(conn, project_id) if project_id else None
    if not project and name:
        project = get_project_by_name(conn, name)

    if project:
        merged = {
            **project,
            **{k: v for k, v in body.items() if k != 'tasks'},
            'updatedAt': now_iso(),
        }
        conn.execute(
            'UPDATE projects SET name = ?, description = ?, notes = ?, status = ?, tags_json = ?, updated_at = ? WHERE id = ?',
            (merged['name'], merged.get('description', ''), merged.get('notes', ''), merged.get('status', 'active'), json.dumps(merged.get('tags', [])), merged['updatedAt'], merged['id']),
        )
        return get_project(conn, merged['id']), 'updated'

    pid = project_id or slugify(name or 'project')
    conn.execute(
        'INSERT INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (pid, name or 'Untitled project', body.get('description', ''), body.get('notes', ''), body.get('status', 'active'), json.dumps(body.get('tags', [])), now_iso()),
    )
    return get_project(conn, pid), 'created'


def upsert_task(conn: sqlite3.Connection, project_id: str, body: dict) -> tuple[dict, str]:
    task_id = body.get('id')
    title = body.get('title')
    task = get_task(conn, project_id, task_id) if task_id else None
    if not task and title:
        task = get_task_by_title(conn, project_id, title)

    if task:
        merged = {
            **task,
            **body,
            'updatedAt': now_iso(),
        }
        conn.execute(
            'UPDATE tasks SET title = ?, status = ?, priority = ?, due_date = ?, tags_json = ?, notes = ?, updated_at = ? WHERE id = ? AND project_id = ?',
            (merged['title'], merged.get('status', 'todo'), merged.get('priority', 'medium'), merged.get('dueDate', ''), json.dumps(merged.get('tags', [])), merged.get('notes', ''), merged['updatedAt'], merged['id'], project_id),
        )
        conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
        return get_task(conn, project_id, merged['id']), 'updated'

    tid = task_id or new_id('task')
    conn.execute(
        'INSERT INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (tid, project_id, title or 'Untitled task', body.get('status', 'todo'), body.get('priority', 'medium'), body.get('dueDate', ''), json.dumps(body.get('tags', [])), body.get('notes', ''), now_iso()),
    )
    conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
    return get_task(conn, project_id, tid), 'created'


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get('Content-Length', '0'))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def api_key_ok(self) -> bool:
        if not API_KEY:
            return True
        provided = self.headers.get('X-API-Key', '')
        return provided == API_KEY

    def require_api_key(self) -> bool:
        if self.api_key_ok():
            return True
        self.send_json(401, {'error': 'unauthorized', 'message': 'valid X-API-Key required'})
        return False

    def do_OPTIONS(self):
        self.send_json(204, {})

    def do_GET(self):
        parsed = urlparse(self.path)
        q = parse_qs(parsed.query)
        query = q.get('q', [None])[0]
        status = q.get('status', [None])[0]
        conn = db()

        if parsed.path == '/api/health':
            self.send_json(200, {
                'status': 'ok',
                'service': 'forge-pipeline-api',
                'authEnabled': bool(API_KEY),
                'storage': 'sqlite',
            })
            conn.close()
            return

        if parsed.path == '/api/summary':
            projects = list_projects(conn)
            tasks = [t for p in projects for t in p.get('tasks', [])]
            self.send_json(200, {
                'projectCount': len(projects),
                'taskCount': len(tasks),
                'openTaskCount': len([t for t in tasks if t.get('status') != 'done']),
                'doneTaskCount': len([t for t in tasks if t.get('status') == 'done']),
                'blockedTaskCount': len([t for t in tasks if t.get('status') == 'blocked']),
                'updatedAt': now_iso(),
            })
            conn.close()
            return

        if parsed.path == '/api/projects':
            projects = [p for p in list_projects(conn) if project_matches(p, query, status)]
            self.send_json(200, {'projects': projects})
            conn.close()
            return

        if parsed.path.startswith('/api/projects/') and '/tasks' not in parsed.path:
            project_id = parsed.path.split('/')[3]
            project = get_project(conn, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                conn.close()
                return
            self.send_json(200, project)
            conn.close()
            return

        if parsed.path == '/api/tasks':
            tasks = []
            for project in list_projects(conn):
                for task in project.get('tasks', []):
                    if task_matches(task, query, status):
                        tasks.append({**task, 'projectId': project['id'], 'projectName': project['name']})
            self.send_json(200, {'tasks': tasks})
            conn.close()
            return

        if parsed.path.startswith('/api/projects/') and parsed.path.endswith('/tasks'):
            project_id = parsed.path.split('/')[3]
            project = get_project(conn, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                conn.close()
                return
            tasks = [t for t in project.get('tasks', []) if task_matches(t, query, status)]
            self.send_json(200, {'tasks': tasks})
            conn.close()
            return

        if parsed.path == '/api/events':
            limit = int(q.get('limit', ['50'])[0])
            self.send_json(200, {'events': list_events(conn, limit)})
            conn.close()
            return

        conn.close()
        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def do_POST(self):
        if not self.require_api_key():
            return
        parsed = urlparse(self.path)
        body = self.read_json()
        conn = db()

        if parsed.path == '/api/projects':
            pid = body.get('id') or new_id('project')
            conn.execute(
                'INSERT INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (pid, body.get('name', 'Untitled project'), body.get('description', ''), body.get('notes', ''), body.get('status', 'active'), json.dumps(body.get('tags', [])), now_iso()),
            )
            conn.commit()
            project = get_project(conn, pid)
            conn.close()
            record_event('project.created', {'projectId': pid, 'name': project['name']})
            self.send_json(201, project)
            return

        if parsed.path.startswith('/api/projects/') and parsed.path.endswith('/tasks'):
            project_id = parsed.path.split('/')[3]
            project = get_project(conn, project_id)
            if not project:
                conn.close()
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            tid = body.get('id') or new_id('task')
            conn.execute(
                'INSERT INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (tid, project_id, body.get('title', 'New task'), body.get('status', 'todo'), body.get('priority', 'medium'), body.get('dueDate', ''), json.dumps(body.get('tags', [])), body.get('notes', ''), now_iso()),
            )
            conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
            conn.commit()
            task = get_task(conn, project_id, tid)
            conn.close()
            record_event('task.created', {'projectId': project_id, 'taskId': tid, 'title': task['title']})
            self.send_json(201, task)
            return

        if parsed.path == '/api/bulk/import':
            projects = body.get('projects', [])
            if not isinstance(projects, list):
                conn.close()
                self.send_json(400, {'error': 'projects_must_be_list'})
                return
            conn.execute('DELETE FROM tasks')
            conn.execute('DELETE FROM projects')
            import_projects(conn, projects)
            conn.commit()
            conn.close()
            record_event('bulk.import', {'projectCount': len(projects)})
            self.send_json(200, {'ok': True, 'projectCount': len(projects)})
            return

        if parsed.path == '/api/mcp/project-upsert':
            project, action = upsert_project(conn, body)
            conn.commit()
            conn.close()
            record_event('mcp.project-upsert', {'action': action, 'projectId': project['id'], 'name': project['name']})
            self.send_json(200, {'ok': True, 'action': action, 'project': project})
            return

        if parsed.path == '/api/mcp/task-upsert':
            project_id = body.get('projectId')
            project_name = body.get('projectName')
            project = get_project(conn, project_id) if project_id else None
            if not project and project_name:
                project = get_project_by_name(conn, project_name)
            if not project:
                conn.close()
                self.send_json(404, {'error': 'project_not_found', 'projectId': project_id, 'projectName': project_name})
                return
            task, action = upsert_task(conn, project['id'], body)
            conn.commit()
            conn.close()
            record_event('mcp.task-upsert', {'action': action, 'projectId': project['id'], 'taskId': task['id'], 'title': task['title']})
            self.send_json(200, {'ok': True, 'action': action, 'projectId': project['id'], 'task': task})
            return

        if parsed.path == '/api/mcp/project-update':
            project_id = body.get('projectId')
            project = get_project(conn, project_id) if project_id else None
            if not project:
                conn.close()
                self.send_json(404, {'error': 'project_not_found', 'projectId': project_id})
                return
            description = body.get('summary', project.get('description', ''))
            notes = project.get('notes', '')
            if body.get('note'):
                notes = (notes + '\n\n' + body['note']).strip()
            status_value = body.get('status', project.get('status', 'active'))
            tags = sorted(set(project.get('tags', [])) | set(body.get('tags', []))) if isinstance(body.get('tags'), list) else project.get('tags', [])
            conn.execute(
                'UPDATE projects SET description = ?, notes = ?, status = ?, tags_json = ?, updated_at = ? WHERE id = ?',
                (description, notes, status_value, json.dumps(tags), now_iso(), project_id),
            )
            conn.commit()
            updated = get_project(conn, project_id)
            conn.close()
            record_event('mcp.project-update', {'projectId': project_id, 'status': updated.get('status')})
            self.send_json(200, {'ok': True, 'project': updated})
            return

        if parsed.path == '/api/mcp/event':
            conn.close()
            source = body.get('source', 'unknown')
            kind = body.get('kind', 'generic')
            payload = body.get('payload', {})
            entry = record_event(f'mcp.event.{kind}', {'source': source, 'payload': payload})
            self.send_json(201, {'ok': True, 'event': entry})
            return

        conn.close()
        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def do_PUT(self):
        if not self.require_api_key():
            return
        self.handle_update(replace=True)

    def do_PATCH(self):
        if not self.require_api_key():
            return
        self.handle_update(replace=False)

    def handle_update(self, replace: bool):
        parsed = urlparse(self.path)
        body = self.read_json()
        conn = db()

        if parsed.path.startswith('/api/projects/') and '/tasks/' not in parsed.path and parsed.path.count('/') == 3:
            project_id = parsed.path.split('/')[3]
            project = get_project(conn, project_id)
            if not project:
                conn.close()
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            merged = ({
                'id': project_id,
                'name': body.get('name', 'Untitled project'),
                'description': body.get('description', ''),
                'notes': body.get('notes', ''),
                'status': body.get('status', 'active'),
                'tags': body.get('tags', []),
            } if replace else {**project, **body})
            conn.execute(
                'UPDATE projects SET name = ?, description = ?, notes = ?, status = ?, tags_json = ?, updated_at = ? WHERE id = ?',
                (merged['name'], merged.get('description', ''), merged.get('notes', ''), merged.get('status', 'active'), json.dumps(merged.get('tags', [])), now_iso(), project_id),
            )
            conn.commit()
            updated = get_project(conn, project_id)
            conn.close()
            record_event('project.updated', {'projectId': project_id})
            self.send_json(200, updated)
            return

        if '/tasks/' in parsed.path:
            parts = parsed.path.split('/')
            project_id = parts[3]
            task_id = parts[5]
            task = get_task(conn, project_id, task_id)
            if not task:
                conn.close()
                self.send_json(404, {'error': 'task_not_found', 'id': task_id})
                return
            merged = ({
                'id': task_id,
                'title': body.get('title', 'Untitled task'),
                'status': body.get('status', 'todo'),
                'priority': body.get('priority', 'medium'),
                'dueDate': body.get('dueDate', ''),
                'tags': body.get('tags', []),
                'notes': body.get('notes', ''),
            } if replace else {**task, **body})
            conn.execute(
                'UPDATE tasks SET title = ?, status = ?, priority = ?, due_date = ?, tags_json = ?, notes = ?, updated_at = ? WHERE id = ? AND project_id = ?',
                (merged['title'], merged.get('status', 'todo'), merged.get('priority', 'medium'), merged.get('dueDate', ''), json.dumps(merged.get('tags', [])), merged.get('notes', ''), now_iso(), task_id, project_id),
            )
            conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
            conn.commit()
            updated = get_task(conn, project_id, task_id)
            conn.close()
            record_event('task.updated', {'projectId': project_id, 'taskId': task_id})
            self.send_json(200, updated)
            return

        conn.close()
        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def do_DELETE(self):
        if not self.require_api_key():
            return
        parsed = urlparse(self.path)
        conn = db()

        if parsed.path.startswith('/api/projects/') and '/tasks/' not in parsed.path and parsed.path.count('/') == 3:
            project_id = parsed.path.split('/')[3]
            deleted = conn.execute('DELETE FROM projects WHERE id = ?', (project_id,)).rowcount
            conn.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
            conn.commit()
            conn.close()
            if not deleted:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            record_event('project.deleted', {'projectId': project_id})
            self.send_json(200, {'deleted': True, 'projectId': project_id})
            return

        if '/tasks/' in parsed.path:
            parts = parsed.path.split('/')
            project_id = parts[3]
            task_id = parts[5]
            deleted = conn.execute('DELETE FROM tasks WHERE project_id = ? AND id = ?', (project_id, task_id)).rowcount
            conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
            conn.commit()
            conn.close()
            if not deleted:
                self.send_json(404, {'error': 'task_not_found', 'id': task_id})
                return
            record_event('task.deleted', {'projectId': project_id, 'taskId': task_id})
            self.send_json(200, {'deleted': True, 'projectId': project_id, 'taskId': task_id})
            return

        conn.close()
        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', 4181), Handler)
    print('Forge Pipeline API listening on :4181')
    print(f'Auth enabled: {bool(API_KEY)}')
    print(f'Storage: sqlite ({DB_FILE})')
    server.serve_forever()
