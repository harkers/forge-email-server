#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
STORAGE_DIR = ROOT / "storage"
DATA_FILE = STORAGE_DIR / "forge-pipeline.json"
EVENTS_FILE = STORAGE_DIR / "events.json"
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


def ensure_store() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        data = DEFAULT_DATA
        touch_all(data)
        DATA_FILE.write_text(json.dumps(data, indent=2))
    if not EVENTS_FILE.exists():
        EVENTS_FILE.write_text(json.dumps({"events": []}, indent=2))


def touch_all(data: dict) -> None:
    stamp = now_iso()
    for project in data.get("projects", []):
        project.setdefault("status", "active")
        project.setdefault("tags", [])
        project["updatedAt"] = project.get("updatedAt") or stamp
        for task in project.get("tasks", []):
            task.setdefault("tags", [])
            task.setdefault("notes", "")
            task["updatedAt"] = task.get("updatedAt") or stamp


def load_data() -> dict:
    ensure_store()
    data = json.loads(DATA_FILE.read_text())
    touch_all(data)
    return data


def save_data(data: dict) -> None:
    touch_all(data)
    DATA_FILE.write_text(json.dumps(data, indent=2))


def load_events() -> dict:
    ensure_store()
    return json.loads(EVENTS_FILE.read_text())


def save_events(data: dict) -> None:
    EVENTS_FILE.write_text(json.dumps(data, indent=2))


def record_event(kind: str, payload: dict) -> dict:
    events = load_events()
    entry = {
        "id": new_id("event"),
        "kind": kind,
        "createdAt": now_iso(),
        "payload": payload,
    }
    events.setdefault("events", []).insert(0, entry)
    events["events"] = events["events"][:500]
    save_events(events)
    return entry


def new_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


def slugify(text: str) -> str:
    out = ''.join(ch.lower() if ch.isalnum() else '-' for ch in text).strip('-')
    while '--' in out:
        out = out.replace('--', '-')
    return out or new_id('project')


def find_project(data: dict, project_id: str):
    return next((p for p in data.get("projects", []) if p.get("id") == project_id), None)


def find_project_by_name(data: dict, name: str):
    name = name.strip().lower()
    return next((p for p in data.get("projects", []) if p.get("name", '').strip().lower() == name), None)


def find_task(project: dict, task_id: str):
    return next((t for t in project.get("tasks", []) if t.get("id") == task_id), None)


def find_task_by_title(project: dict, title: str):
    title = title.strip().lower()
    return next((t for t in project.get("tasks", []) if t.get("title", '').strip().lower() == title), None)


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


def upsert_project(data: dict, body: dict) -> tuple[dict, str]:
    project = None
    project_id = body.get('id')
    name = body.get('name')
    if project_id:
        project = find_project(data, project_id)
    if not project and name:
        project = find_project_by_name(data, name)

    if project:
        project.update({k: v for k, v in body.items() if k != 'tasks'})
        project['updatedAt'] = now_iso()
        action = 'updated'
    else:
        project = {
            'id': project_id or slugify(name or 'project'),
            'name': name or 'Untitled project',
            'description': body.get('description', ''),
            'notes': body.get('notes', ''),
            'status': body.get('status', 'active'),
            'tags': body.get('tags', []),
            'updatedAt': now_iso(),
            'tasks': body.get('tasks', []),
        }
        data.setdefault('projects', []).insert(0, project)
        action = 'created'
    return project, action


def upsert_task(project: dict, body: dict) -> tuple[dict, str]:
    task = None
    task_id = body.get('id')
    title = body.get('title')
    if task_id:
        task = find_task(project, task_id)
    if not task and title:
        task = find_task_by_title(project, title)

    if task:
        task.update(body)
        task['updatedAt'] = now_iso()
        action = 'updated'
    else:
        task = {
            'id': task_id or new_id('task'),
            'title': title or 'Untitled task',
            'status': body.get('status', 'todo'),
            'priority': body.get('priority', 'medium'),
            'dueDate': body.get('dueDate', ''),
            'tags': body.get('tags', []),
            'notes': body.get('notes', ''),
            'updatedAt': now_iso(),
        }
        project.setdefault('tasks', []).insert(0, task)
        action = 'created'
    project['updatedAt'] = now_iso()
    return task, action


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
        data = load_data()

        if parsed.path == '/api/health':
            self.send_json(200, {
                'status': 'ok',
                'service': 'forge-pipeline-api',
                'authEnabled': bool(API_KEY),
            })
            return

        if parsed.path == '/api/summary':
            projects = data.get('projects', [])
            tasks = [t for p in projects for t in p.get('tasks', [])]
            self.send_json(200, {
                'projectCount': len(projects),
                'taskCount': len(tasks),
                'openTaskCount': len([t for t in tasks if t.get('status') != 'done']),
                'doneTaskCount': len([t for t in tasks if t.get('status') == 'done']),
                'blockedTaskCount': len([t for t in tasks if t.get('status') == 'blocked']),
                'updatedAt': now_iso(),
            })
            return

        if parsed.path == '/api/projects':
            projects = [p for p in data.get('projects', []) if project_matches(p, query, status)]
            self.send_json(200, {'projects': projects})
            return

        if parsed.path.startswith('/api/projects/') and '/tasks' not in parsed.path:
            project_id = parsed.path.split('/')[3]
            project = find_project(data, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            self.send_json(200, project)
            return

        if parsed.path == '/api/tasks':
            tasks = []
            for project in data.get('projects', []):
                for task in project.get('tasks', []):
                    if task_matches(task, query, status):
                        tasks.append({**task, 'projectId': project['id'], 'projectName': project['name']})
            self.send_json(200, {'tasks': tasks})
            return

        if parsed.path.startswith('/api/projects/') and parsed.path.endswith('/tasks'):
            parts = parsed.path.split('/')
            project_id = parts[3]
            project = find_project(data, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            tasks = [t for t in project.get('tasks', []) if task_matches(t, query, status)]
            self.send_json(200, {'tasks': tasks})
            return

        if parsed.path == '/api/events':
            events = load_events().get('events', [])
            limit = int(q.get('limit', ['50'])[0])
            self.send_json(200, {'events': events[:limit]})
            return

        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def do_POST(self):
        if not self.require_api_key():
            return
        parsed = urlparse(self.path)
        data = load_data()
        body = self.read_json()

        if parsed.path == '/api/projects':
            project = {
                'id': body.get('id') or new_id('project'),
                'name': body.get('name', 'Untitled project'),
                'description': body.get('description', ''),
                'notes': body.get('notes', ''),
                'status': body.get('status', 'active'),
                'tags': body.get('tags', []),
                'updatedAt': now_iso(),
                'tasks': body.get('tasks', []),
            }
            data.setdefault('projects', []).insert(0, project)
            save_data(data)
            record_event('project.created', {'projectId': project['id'], 'name': project['name']})
            self.send_json(201, project)
            return

        if parsed.path.startswith('/api/projects/') and parsed.path.endswith('/tasks'):
            project_id = parsed.path.split('/')[3]
            project = find_project(data, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            task = {
                'id': body.get('id') or new_id('task'),
                'title': body.get('title', 'New task'),
                'status': body.get('status', 'todo'),
                'priority': body.get('priority', 'medium'),
                'dueDate': body.get('dueDate', ''),
                'tags': body.get('tags', []),
                'notes': body.get('notes', ''),
                'updatedAt': now_iso(),
            }
            project.setdefault('tasks', []).insert(0, task)
            project['updatedAt'] = now_iso()
            save_data(data)
            record_event('task.created', {'projectId': project_id, 'taskId': task['id'], 'title': task['title']})
            self.send_json(201, task)
            return

        if parsed.path == '/api/bulk/import':
            projects = body.get('projects', [])
            if not isinstance(projects, list):
                self.send_json(400, {'error': 'projects_must_be_list'})
                return
            data['projects'] = projects
            save_data(data)
            record_event('bulk.import', {'projectCount': len(projects)})
            self.send_json(200, {'ok': True, 'projectCount': len(projects)})
            return

        if parsed.path == '/api/mcp/project-upsert':
            project, action = upsert_project(data, body)
            save_data(data)
            record_event('mcp.project-upsert', {'action': action, 'projectId': project['id'], 'name': project['name']})
            self.send_json(200, {'ok': True, 'action': action, 'project': project})
            return

        if parsed.path == '/api/mcp/task-upsert':
            project_id = body.get('projectId')
            project_name = body.get('projectName')
            project = find_project(data, project_id) if project_id else None
            if not project and project_name:
                project = find_project_by_name(data, project_name)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'projectId': project_id, 'projectName': project_name})
                return
            task, action = upsert_task(project, body)
            save_data(data)
            record_event('mcp.task-upsert', {'action': action, 'projectId': project['id'], 'taskId': task['id'], 'title': task['title']})
            self.send_json(200, {'ok': True, 'action': action, 'projectId': project['id'], 'task': task})
            return

        if parsed.path == '/api/mcp/project-update':
            project_id = body.get('projectId')
            project = find_project(data, project_id) if project_id else None
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'projectId': project_id})
                return
            summary = body.get('summary')
            note = body.get('note')
            status_value = body.get('status')
            tags = body.get('tags')
            if summary:
                project['description'] = summary
            if note:
                project['notes'] = (project.get('notes', '') + '\n\n' + note).strip()
            if status_value:
                project['status'] = status_value
            if isinstance(tags, list):
                merged = set(project.get('tags', [])) | set(tags)
                project['tags'] = sorted(merged)
            project['updatedAt'] = now_iso()
            save_data(data)
            record_event('mcp.project-update', {'projectId': project['id'], 'status': project.get('status')})
            self.send_json(200, {'ok': True, 'project': project})
            return

        if parsed.path == '/api/mcp/event':
            source = body.get('source', 'unknown')
            kind = body.get('kind', 'generic')
            payload = body.get('payload', {})
            entry = record_event(f'mcp.event.{kind}', {'source': source, 'payload': payload})
            self.send_json(201, {'ok': True, 'event': entry})
            return

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
        data = load_data()
        body = self.read_json()

        if parsed.path.startswith('/api/projects/') and '/tasks/' not in parsed.path and parsed.path.count('/') == 3:
            project_id = parsed.path.split('/')[3]
            project = find_project(data, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            if replace:
                project.clear()
                project.update({
                    'id': project_id,
                    'name': body.get('name', 'Untitled project'),
                    'description': body.get('description', ''),
                    'notes': body.get('notes', ''),
                    'status': body.get('status', 'active'),
                    'tags': body.get('tags', []),
                    'tasks': body.get('tasks', []),
                    'updatedAt': now_iso(),
                })
            else:
                project.update(body)
                project['updatedAt'] = now_iso()
            save_data(data)
            record_event('project.updated', {'projectId': project_id})
            self.send_json(200, project)
            return

        if '/tasks/' in parsed.path:
            parts = parsed.path.split('/')
            project_id = parts[3]
            task_id = parts[5]
            project = find_project(data, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            task = find_task(project, task_id)
            if not task:
                self.send_json(404, {'error': 'task_not_found', 'id': task_id})
                return
            if replace:
                task.clear()
                task.update({
                    'id': task_id,
                    'title': body.get('title', 'Untitled task'),
                    'status': body.get('status', 'todo'),
                    'priority': body.get('priority', 'medium'),
                    'dueDate': body.get('dueDate', ''),
                    'tags': body.get('tags', []),
                    'notes': body.get('notes', ''),
                    'updatedAt': now_iso(),
                })
            else:
                task.update(body)
                task['updatedAt'] = now_iso()
            project['updatedAt'] = now_iso()
            save_data(data)
            record_event('task.updated', {'projectId': project_id, 'taskId': task_id})
            self.send_json(200, task)
            return

        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def do_DELETE(self):
        if not self.require_api_key():
            return
        parsed = urlparse(self.path)
        data = load_data()

        if parsed.path.startswith('/api/projects/') and '/tasks/' not in parsed.path and parsed.path.count('/') == 3:
            project_id = parsed.path.split('/')[3]
            before = len(data.get('projects', []))
            data['projects'] = [p for p in data.get('projects', []) if p.get('id') != project_id]
            if len(data['projects']) == before:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            save_data(data)
            record_event('project.deleted', {'projectId': project_id})
            self.send_json(200, {'deleted': True, 'projectId': project_id})
            return

        if '/tasks/' in parsed.path:
            parts = parsed.path.split('/')
            project_id = parts[3]
            task_id = parts[5]
            project = find_project(data, project_id)
            if not project:
                self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                return
            before = len(project.get('tasks', []))
            project['tasks'] = [t for t in project.get('tasks', []) if t.get('id') != task_id]
            if len(project['tasks']) == before:
                self.send_json(404, {'error': 'task_not_found', 'id': task_id})
                return
            project['updatedAt'] = now_iso()
            save_data(data)
            record_event('task.deleted', {'projectId': project_id, 'taskId': task_id})
            self.send_json(200, {'deleted': True, 'projectId': project_id, 'taskId': task_id})
            return

        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    ensure_store()
    server = HTTPServer(('0.0.0.0', 4181), Handler)
    print('Forge Pipeline API listening on :4181')
    print(f'Auth enabled: {bool(API_KEY)}')
    server.serve_forever()
