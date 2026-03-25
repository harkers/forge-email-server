#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

ROOT = Path(__file__).resolve().parent
STORAGE_DIR = ROOT / "storage"
DB_FILE = STORAGE_DIR / "forge-pipeline.db"
LEGACY_JSON_FILE = STORAGE_DIR / "forge-pipeline.json"
LEGACY_EVENTS_FILE = STORAGE_DIR / "events.json"
LOG_FILE = STORAGE_DIR / "access.log"
API_KEY = os.environ.get("FORGE_PIPELINE_API_KEY", "")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
LOG_REQUESTS = os.environ.get("FORGE_PIPELINE_LOG_REQUESTS", "false").lower() == "true"

# Initialize Redis connection (lazy, optional)
_redis = None

def get_redis() -> Redis | None:
    global _redis
    if not REDIS_AVAILABLE:
        return None
    if _redis is None:
        try:
            _redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
            _redis.ping()
        except Exception:
            _redis = None
    return _redis

ALLOWED_PROJECT_STATUS = {'on-track', 'at-risk', 'off-track', 'not-started', 'in-progress', 'blocked', 'completed', 'overdue', 'cancelled'}
ALLOWED_TASK_STATUS = {'todo', 'in-progress', 'blocked', 'done'}
ALLOWED_PRIORITY = {'low', 'medium', 'high'}
MAX_NAME = 200
MAX_TEXT = 5000
MAX_TAGS = 50
MAX_TAG_LENGTH = 64

DEFAULT_DATA = {
    "projects": [
        {
            "id": "privacy-dsar",
            "name": "Privacy / DSAR",
            "description": "Handle access requests and related compliance tasks.",
            "notes": "Track deadlines carefully and maintain a full audit trail.",
            "status": "active",
            "tags": ["source:privacy-dsar", "privacy", "compliance"],
            "updatedAt": None,
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Review intake template",
                    "status": "todo",
                    "priority": "high",
                    "dueDate": "2026-03-31",
                    "tags": ["source:privacy-dsar", "privacy", "template"],
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
            "tags": ["source:display-forge", "signage", "platform"],
            "updatedAt": None,
            "tasks": [
                {
                    "id": "task-2",
                    "title": "Add scheduling logic",
                    "status": "in-progress",
                    "priority": "high",
                    "dueDate": "2026-03-28",
                    "tags": ["source:display-forge", "api", "schedule"],
                    "notes": "Eligibility and expiry rules first.",
                    "updatedAt": None,
                }
            ],
        },
    ]
}


class ValidationError(Exception):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.message = message
        self.field = field


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def cache_with_ttl(key: str, ttl_seconds: int = 60):
    """Decorator to cache function result in Redis with TTL."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis = get_redis()
            if redis:
                cached = redis.get(f'forge:cache:{key}')
                if cached:
                    return json.loads(cached)
            result = func(*args, **kwargs)
            if redis:
                try:
                    redis.setex(f'forge:cache:{key}', ttl_seconds, json.dumps(result))
                except Exception:
                    pass  # Cache best-effort
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str = '*'):
    """Invalidate cache keys matching pattern."""
    redis = get_redis()
    if redis:
        try:
            keys = redis.keys(f'forge:cache:{pattern}')
            if keys:
                redis.delete(*keys)
        except Exception:
            pass  # Cache best-effort


def log_request(method: str, path: str, status: int, duration_ms: float, user_agent: str = ''):
    """Log requests to access log file."""
    if not LOG_REQUESTS:
        return
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        log_line = f"{datetime.now(timezone.utc).isoformat()} {method} {path} {status} {duration_ms:.1f}ms {user_agent[:100]}\n"
        with open(LOG_FILE, 'a') as f:
            f.write(log_line)
    except Exception:
        pass  # Logging best-effort


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
            status TEXT NOT NULL DEFAULT 'not-started',
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


def require_object(body):
    if not isinstance(body, dict):
        raise ValidationError('request body must be a JSON object')


def clean_string(value, field, max_len=MAX_TEXT, allow_empty=True):
    if value is None:
        return '' if allow_empty else None
    if not isinstance(value, str):
        raise ValidationError('must be a string', field)
    value = value.strip()
    if not allow_empty and not value:
        raise ValidationError('must not be empty', field)
    if len(value) > max_len:
        raise ValidationError(f'must be <= {max_len} chars', field)
    return value


def clean_tags(value, field='tags'):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValidationError('must be a list of strings', field)
    out = []
    for item in value:
        if not isinstance(item, str):
            raise ValidationError('tags must be strings', field)
        item = item.strip()
        if not item:
            continue
        if len(item) > MAX_TAG_LENGTH:
            raise ValidationError(f'tag too long (>{MAX_TAG_LENGTH})', field)
        out.append(item)
    if len(out) > MAX_TAGS:
        raise ValidationError(f'too many tags (max {MAX_TAGS})', field)
    return out


def clean_project_status(value):
    value = clean_string(value or 'not-started', 'status', max_len=32, allow_empty=False)
    if value not in ALLOWED_PROJECT_STATUS:
        raise ValidationError(f'invalid project status: {value}', 'status')
    return value


def clean_task_status(value):
    value = clean_string(value or 'todo', 'status', max_len=32, allow_empty=False)
    if value not in ALLOWED_TASK_STATUS:
        raise ValidationError(f'invalid task status: {value}', 'status')
    return value


def clean_priority(value):
    value = clean_string(value or 'medium', 'priority', max_len=32, allow_empty=False)
    if value not in ALLOWED_PRIORITY:
        raise ValidationError(f'invalid priority: {value}', 'priority')
    return value


def clean_due_date(value):
    value = clean_string(value or '', 'dueDate', max_len=32, allow_empty=True)
    if value and len(value) != 10:
        raise ValidationError('dueDate must be YYYY-MM-DD', 'dueDate')
    return value


def ensure_source_tag(tags, source):
    tags = list(tags or [])
    source = (source or '').strip()
    if not source:
        return tags
    tag = source if source.startswith('source:') else f'source:{source}'
    if tag not in tags:
        tags.append(tag)
    return tags


def derive_source(body: dict) -> str:
    if isinstance(body.get('source'), str) and body.get('source').strip():
        return body['source'].strip()
    tags = body.get('tags', [])
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and tag.startswith('source:'):
                return tag.removeprefix('source:')
    return ''


def validate_project_payload(body, partial=False):
    require_object(body)
    out = {}
    if not partial or 'name' in body:
        out['name'] = clean_string(body.get('name', ''), 'name', max_len=MAX_NAME, allow_empty=partial)
        if not partial and not out['name']:
            raise ValidationError('name is required', 'name')
    if not partial or 'description' in body:
        out['description'] = clean_string(body.get('description', ''), 'description')
    if not partial or 'notes' in body:
        out['notes'] = clean_string(body.get('notes', ''), 'notes')
    if not partial or 'status' in body:
        out['status'] = clean_project_status(body.get('status', 'not-started'))
    if not partial or 'tags' in body:
        out['tags'] = clean_tags(body.get('tags', []))
    if 'id' in body and body['id'] is not None:
        out['id'] = clean_string(body['id'], 'id', max_len=MAX_NAME, allow_empty=False)
    return out


def validate_task_payload(body, partial=False):
    require_object(body)
    out = {}
    if not partial or 'title' in body:
        out['title'] = clean_string(body.get('title', ''), 'title', max_len=MAX_NAME, allow_empty=partial)
        if not partial and not out['title']:
            raise ValidationError('title is required', 'title')
    if not partial or 'status' in body:
        out['status'] = clean_task_status(body.get('status', 'todo'))
    if not partial or 'priority' in body:
        out['priority'] = clean_priority(body.get('priority', 'medium'))
    if not partial or 'dueDate' in body:
        out['dueDate'] = clean_due_date(body.get('dueDate', ''))
    if not partial or 'tags' in body:
        out['tags'] = clean_tags(body.get('tags', []))
    if not partial or 'notes' in body:
        out['notes'] = clean_string(body.get('notes', ''), 'notes')
    if 'id' in body and body['id'] is not None:
        out['id'] = clean_string(body['id'], 'id', max_len=MAX_NAME, allow_empty=False)
    return out


def validate_event_payload(body):
    require_object(body)
    source = clean_string(body.get('source', 'unknown'), 'source', max_len=MAX_NAME, allow_empty=False)
    kind = clean_string(body.get('kind', 'generic'), 'kind', max_len=MAX_NAME, allow_empty=False)
    payload = body.get('payload', {})
    if not isinstance(payload, dict):
        raise ValidationError('payload must be an object', 'payload')
    return {'source': source, 'kind': kind, 'payload': payload}


def project_count(conn: sqlite3.Connection) -> int:
    return conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0]


def event_count(conn: sqlite3.Connection) -> int:
    return conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]


def _get_summary_cached(conn: sqlite3.Connection) -> dict:
    """Get summary with Redis cache (60s TTL)."""
    redis = get_redis()
    if redis:
        cached = redis.get('forge:cache:summary')
        if cached:
            return json.loads(cached)
    
    # Compute summary
    projects = list_projects(conn)
    tasks = [t for p in projects for t in p.get('tasks', [])]
    summary = {
        'projectCount': len(projects),
        'taskCount': len(tasks),
        'openTaskCount': len([t for t in tasks if t.get('status') != 'done']),
        'doneTaskCount': len([t for t in tasks if t.get('status') == 'done']),
        'blockedTaskCount': len([t for t in tasks if t.get('status') == 'blocked']),
        'updatedAt': now_iso(),
    }
    
    # Cache it
    if redis:
        try:
            redis.setex('forge:cache:summary', 60, json.dumps(summary))
        except Exception:
            pass
    
    return summary


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
        project = validate_project_payload(project, partial=True) | {'name': project.get('name', 'Untitled project')}
        pid = project.get('id') or slugify(project.get('name', 'project'))
        conn.execute(
            'INSERT OR REPLACE INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (pid, project.get('name', 'Untitled project'), project.get('description', ''), project.get('notes', ''), project.get('status', 'not-started'), json.dumps(project.get('tags', [])), stamp),
        )
        for task_raw in next((p.get('tasks', []) for p in projects if p.get('id', pid) == project.get('id', pid) or p.get('name') == project.get('name')), []):
            task = validate_task_payload(task_raw, partial=True) | {'title': task_raw.get('title', 'Untitled task')}
            conn.execute(
                'INSERT OR REPLACE INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (task.get('id') or new_id('task'), pid, task.get('title', 'Untitled task'), task.get('status', 'todo'), task.get('priority', 'medium'), task.get('dueDate', ''), json.dumps(task.get('tags', [])), task.get('notes', ''), stamp),
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


def list_projects(conn: sqlite3.Connection, limit: int = 100, offset: int = 0) -> list[dict]:
    rows = conn.execute('SELECT * FROM projects ORDER BY updated_at DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    return [row_to_project(conn, row) for row in rows]


def count_projects(conn: sqlite3.Connection) -> int:
    return conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0]


def list_events(conn: sqlite3.Connection, limit: int = 50, offset: int = 0) -> list[dict]:
    rows = conn.execute('SELECT * FROM events ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
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
    clean = validate_project_payload(body, partial=True)
    source = derive_source(body)
    clean['tags'] = ensure_source_tag(clean.get('tags', []), source)
    project_id = clean.get('id')
    name = clean.get('name')
    project = get_project(conn, project_id) if project_id else None
    if not project and name:
        project = get_project_by_name(conn, name)

    if project:
        merged = {**project, **clean, 'updatedAt': now_iso()}
        conn.execute(
            'UPDATE projects SET name = ?, description = ?, notes = ?, status = ?, tags_json = ?, updated_at = ? WHERE id = ?',
            (merged['name'], merged.get('description', ''), merged.get('notes', ''), merged.get('status', 'not-started'), json.dumps(merged.get('tags', [])), merged['updatedAt'], merged['id']),
        )
        return get_project(conn, merged['id']), 'updated'

    pid = project_id or slugify(name or 'project')
    conn.execute(
        'INSERT INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (pid, name or 'Untitled project', clean.get('description', ''), clean.get('notes', ''), clean.get('status', 'not-started'), json.dumps(clean.get('tags', [])), now_iso()),
    )
    return get_project(conn, pid), 'created'


def upsert_task(conn: sqlite3.Connection, project_id: str, body: dict) -> tuple[dict, str]:
    clean = validate_task_payload(body, partial=True)
    source = derive_source(body)
    clean['tags'] = ensure_source_tag(clean.get('tags', []), source)
    task_id = clean.get('id')
    title = clean.get('title')
    task = get_task(conn, project_id, task_id) if task_id else None
    if not task and title:
        task = get_task_by_title(conn, project_id, title)

    if task:
        merged = {**task, **clean, 'updatedAt': now_iso()}
        conn.execute(
            'UPDATE tasks SET title = ?, status = ?, priority = ?, due_date = ?, tags_json = ?, notes = ?, updated_at = ? WHERE id = ? AND project_id = ?',
            (merged['title'], merged.get('status', 'todo'), merged.get('priority', 'medium'), merged.get('dueDate', ''), json.dumps(merged.get('tags', [])), merged.get('notes', ''), merged['updatedAt'], merged['id'], project_id),
        )
        conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
        return get_task(conn, project_id, merged['id']), 'updated'

    tid = task_id or new_id('task')
    conn.execute(
        'INSERT INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (tid, project_id, title or 'Untitled task', clean.get('status', 'todo'), clean.get('priority', 'medium'), clean.get('dueDate', ''), json.dumps(clean.get('tags', [])), clean.get('notes', ''), now_iso()),
    )
    conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
    return get_task(conn, project_id, tid), 'created'


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload):
        body = json.dumps(payload).encode('utf-8')
        duration_ms = (time.time() - getattr(self, '_start_time', time.time())) * 1000
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, X-Response-Time')
        self.send_header('X-Response-Time', f'{duration_ms:.1f}ms')
        self.end_headers()
        self.wfile.write(body)

    def send_validation_error(self, err: ValidationError):
        self.send_json(400, {'error': 'validation_error', 'message': err.message, 'field': err.field})

    def read_json(self):
        length = int(self.headers.get('Content-Length', '0'))
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode('utf-8'))
        except json.JSONDecodeError:
            raise ValidationError('invalid JSON body')

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
        self._start_time = time.time()
        parsed = urlparse(self.path)
        q = parse_qs(parsed.query)
        query = q.get('q', [None])[0]
        status = q.get('status', [None])[0]
        conn = db()

        if parsed.path == '/api/health':
            redis_status = 'unknown'
            redis = get_redis()
            if redis:
                try:
                    redis.ping()
                    redis_status = 'connected'
                except Exception:
                    redis_status = 'disconnected'
            else:
                redis_status = 'not_available'
            
            self.send_json(200, {
                'status': 'ok',
                'service': 'forge-pipeline-api',
                'authEnabled': bool(API_KEY),
                'storage': 'sqlite',
                'redis': redis_status,
                'redisAvailable': REDIS_AVAILABLE,
            })
            self.log_request_done(200)
            conn.close()
            return

        if parsed.path == '/api/summary':
            # Use cached summary (60s TTL)
            summary = _get_summary_cached(conn)
            self.send_json(200, summary)
            self.log_request_done(200)
            conn.close()
            return

        if parsed.path == '/api/projects':
            limit = int(q.get('limit', ['100'])[0])
            offset = int(q.get('offset', ['0'])[0])
            total = count_projects(conn)
            projects = [p for p in list_projects(conn, limit=limit, offset=offset) if project_matches(p, query, status)]
            has_more = offset + limit < total
            self.send_json(200, {'projects': projects, 'total': total, 'limit': limit, 'offset': offset, 'hasMore': has_more})
            self.log_request_done(200)
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
            limit = int(q.get('limit', ['100'])[0])
            offset = int(q.get('offset', ['0'])[0])
            all_tasks = []
            for project in list_projects(conn, limit=1000, offset=0):  # Get all projects for task count
                for task in project.get('tasks', []):
                    if task_matches(task, query, status):
                        all_tasks.append({**task, 'projectId': project['id'], 'projectName': project['name']})
            total = len(all_tasks)
            tasks = all_tasks[offset:offset + limit]
            has_more = offset + limit < total
            self.send_json(200, {'tasks': tasks, 'total': total, 'limit': limit, 'offset': offset, 'hasMore': has_more})
            self.log_request_done(200)
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
            offset = int(q.get('offset', ['0'])[0])
            total = event_count(conn)
            events = list_events(conn, limit=limit, offset=offset)
            has_more = offset + limit < total
            self.send_json(200, {'events': events, 'total': total, 'limit': limit, 'offset': offset, 'hasMore': has_more})
            self.log_request_done(200)
            conn.close()
            return

        if parsed.path == '/api/export':
            projects = list_projects(conn)
            events = list_events(conn, 500)
            self.send_json(200, {'exportedAt': now_iso(), 'projects': projects, 'events': events})
            conn.close()
            return

        conn.close()
        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def do_POST(self):
        if not self.require_api_key():
            return
        try:
            parsed = urlparse(self.path)
            body = self.read_json()
            conn = db()

            if parsed.path == '/api/projects':
                clean = validate_project_payload(body, partial=False)
                source = derive_source(body)
                clean['tags'] = ensure_source_tag(clean.get('tags', []), source)
                pid = clean.get('id') or new_id('project')
                conn.execute(
                    'INSERT INTO projects (id, name, description, notes, status, tags_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (pid, clean['name'], clean.get('description', ''), clean.get('notes', ''), clean.get('status', 'not-started'), json.dumps(clean.get('tags', [])), now_iso()),
                )
                conn.commit()
                project = get_project(conn, pid)
                conn.close()
                record_event('project.created', {'projectId': pid, 'name': project['name']})
                invalidate_cache('summary')
                self.send_json(201, project)
                return

            if parsed.path.startswith('/api/projects/') and parsed.path.endswith('/tasks'):
                project_id = parsed.path.split('/')[3]
                project = get_project(conn, project_id)
                if not project:
                    conn.close()
                    self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                    return
                clean = validate_task_payload(body, partial=False)
                source = derive_source(body)
                clean['tags'] = ensure_source_tag(clean.get('tags', []), source)
                tid = clean.get('id') or new_id('task')
                conn.execute(
                    'INSERT INTO tasks (id, project_id, title, status, priority, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (tid, project_id, clean['title'], clean.get('status', 'todo'), clean.get('priority', 'medium'), clean.get('dueDate', ''), json.dumps(clean.get('tags', [])), clean.get('notes', ''), now_iso()),
                )
                conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
                conn.commit()
                task = get_task(conn, project_id, tid)
                conn.close()
                record_event('task.created', {'projectId': project_id, 'taskId': tid, 'title': task['title']})
                invalidate_cache('summary')
                self.send_json(201, task)
                return

            if parsed.path == '/api/bulk/import':
                require_object(body)
                projects = body.get('projects', [])
                if not isinstance(projects, list):
                    conn.close()
                    raise ValidationError('projects must be a list', 'projects')
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
                require_object(body)
                project_id = clean_string(body.get('projectId') or '', 'projectId', max_len=MAX_NAME, allow_empty=True)
                project_name = clean_string(body.get('projectName') or '', 'projectName', max_len=MAX_NAME, allow_empty=True)
                project = get_project(conn, project_id) if project_id else None
                if not project and project_name:
                    project = get_project_by_name(conn, project_name)
                if not project:
                    conn.close()
                    self.send_json(404, {'error': 'project_not_found', 'projectId': project_id or None, 'projectName': project_name or None})
                    return
                task, action = upsert_task(conn, project['id'], body)
                conn.commit()
                conn.close()
                record_event('mcp.task-upsert', {'action': action, 'projectId': project['id'], 'taskId': task['id'], 'title': task['title']})
                self.send_json(200, {'ok': True, 'action': action, 'projectId': project['id'], 'task': task})
                return

            if parsed.path == '/api/mcp/project-update':
                require_object(body)
                project_id = clean_string(body.get('projectId') or '', 'projectId', max_len=MAX_NAME, allow_empty=False)
                project = get_project(conn, project_id)
                if not project:
                    conn.close()
                    self.send_json(404, {'error': 'project_not_found', 'projectId': project_id})
                    return
                description = clean_string(body.get('summary', project.get('description', '')), 'summary')
                notes = project.get('notes', '')
                if body.get('note'):
                    notes = (notes + '\n\n' + clean_string(body['note'], 'note')).strip()
                status_value = clean_project_status(body.get('status', project.get('status', 'not-started'))) if 'status' in body else project.get('status', 'not-started')
                source = derive_source(body)
                tags = sorted(set(project.get('tags', [])) | set(clean_tags(body.get('tags', [])))) if 'tags' in body else project.get('tags', [])
                tags = ensure_source_tag(tags, source)
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

            if parsed.path == '/api/webhook':
                require_object(body)
                action = clean_string(body.get('action', ''), 'action', max_len=100, allow_empty=False)
                source = derive_source(body) or clean_string(body.get('source', 'external'), 'source', max_len=100, allow_empty=False)

                if action == 'project_upsert':
                    webhook_payload = {**body, 'source': source}
                    project, act = upsert_project(conn, webhook_payload)
                    conn.commit()
                    conn.close()
                    record_event('webhook.project-upsert', {'action': act, 'projectId': project['id'], 'name': project['name'], 'source': source})
                    self.send_json(200, {'ok': True, 'action': act, 'project': project})
                    return

                if action == 'task_upsert':
                    project_id = clean_string(body.get('projectId') or '', 'projectId', max_len=MAX_NAME, allow_empty=True)
                    project_name = clean_string(body.get('projectName') or '', 'projectName', max_len=MAX_NAME, allow_empty=True)
                    project = get_project(conn, project_id) if project_id else None
                    if not project and project_name:
                        project = get_project_by_name(conn, project_name)
                    if not project:
                        conn.close()
                        self.send_json(404, {'error': 'project_not_found', 'projectId': project_id or None, 'projectName': project_name or None})
                        return
                    webhook_payload = {**body, 'source': source}
                    task, act = upsert_task(conn, project['id'], webhook_payload)
                    conn.commit()
                    conn.close()
                    record_event('webhook.task-upsert', {'action': act, 'projectId': project['id'], 'taskId': task['id'], 'title': task['title'], 'source': source})
                    self.send_json(200, {'ok': True, 'action': act, 'projectId': project['id'], 'task': task})
                    return

                if action == 'project_update':
                    project_id = clean_string(body.get('projectId') or '', 'projectId', max_len=MAX_NAME, allow_empty=False)
                    project = get_project(conn, project_id)
                    if not project:
                        conn.close()
                        self.send_json(404, {'error': 'project_not_found', 'projectId': project_id})
                        return
                    description = clean_string(body.get('summary', project.get('description', '')), 'summary')
                    notes = project.get('notes', '')
                    if body.get('note'):
                        notes = (notes + '\n\n' + clean_string(body['note'], 'note')).strip()
                    status_value = clean_project_status(body.get('status', project.get('status', 'not-started'))) if 'status' in body else project.get('status', 'not-started')
                    tags = sorted(set(project.get('tags', [])) | set(clean_tags(body.get('tags', [])))) if 'tags' in body else project.get('tags', [])
                    tags = ensure_source_tag(tags, source)
                    conn.execute(
                        'UPDATE projects SET description = ?, notes = ?, status = ?, tags_json = ?, updated_at = ? WHERE id = ?',
                        (description, notes, status_value, json.dumps(tags), now_iso(), project_id),
                    )
                    conn.commit()
                    updated = get_project(conn, project_id)
                    conn.close()
                    record_event('webhook.project-update', {'projectId': project_id, 'status': updated.get('status'), 'source': source})
                    self.send_json(200, {'ok': True, 'project': updated})
                    return

                if action == 'event':
                    event_body = validate_event_payload({'source': source, 'kind': body.get('kind', 'webhook'), 'payload': body.get('payload', {})})
                    conn.close()
                    entry = record_event(f'webhook.event.{event_body["kind"]}', {'source': event_body['source'], 'payload': event_body['payload']})
                    self.send_json(201, {'ok': True, 'event': entry})
                    return

                conn.close()
                raise ValidationError('unsupported webhook action', 'action')

            conn.close()
            self.send_json(404, {'error': 'not_found', 'path': parsed.path})
        except ValidationError as err:
            try:
                conn.close()
            except Exception:
                pass
            self.send_validation_error(err)

    def do_PUT(self):
        if not self.require_api_key():
            return
        self.handle_update(replace=True)

    def do_PATCH(self):
        if not self.require_api_key():
            return
        self.handle_update(replace=False)

    def handle_update(self, replace: bool):
        conn = None
        try:
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
                clean = validate_project_payload(body, partial=not replace)
                source = derive_source(body)
                if source:
                    base_tags = clean.get('tags', project.get('tags', [])) if not replace else clean.get('tags', [])
                    clean['tags'] = ensure_source_tag(base_tags, source)
                merged = ({
                    'id': project_id,
                    'name': clean.get('name', 'Untitled project'),
                    'description': clean.get('description', ''),
                    'notes': clean.get('notes', ''),
                    'status': clean.get('status', 'not-started'),
                    'tags': clean.get('tags', []),
                } if replace else {**project, **clean})
                conn.execute(
                    'UPDATE projects SET name = ?, description = ?, notes = ?, status = ?, tags_json = ?, updated_at = ? WHERE id = ?',
                    (merged['name'], merged.get('description', ''), merged.get('notes', ''), merged.get('status', 'not-started'), json.dumps(merged.get('tags', [])), now_iso(), project_id),
                )
                conn.commit()
                updated = get_project(conn, project_id)
                conn.close()
                record_event('project.updated', {'projectId': project_id})
                invalidate_cache('summary')
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
                clean = validate_task_payload(body, partial=not replace)
                source = derive_source(body)
                if source:
                    base_tags = clean.get('tags', task.get('tags', [])) if not replace else clean.get('tags', [])
                    clean['tags'] = ensure_source_tag(base_tags, source)
                merged = ({
                    'id': task_id,
                    'title': clean.get('title', 'Untitled task'),
                    'status': clean.get('status', 'todo'),
                    'priority': clean.get('priority', 'medium'),
                    'dueDate': clean.get('dueDate', ''),
                    'tags': clean.get('tags', []),
                    'notes': clean.get('notes', ''),
                } if replace else {**task, **clean})
                conn.execute(
                    'UPDATE tasks SET title = ?, status = ?, priority = ?, due_date = ?, tags_json = ?, notes = ?, updated_at = ? WHERE id = ? AND project_id = ?',
                    (merged['title'], merged.get('status', 'todo'), merged.get('priority', 'medium'), merged.get('dueDate', ''), json.dumps(merged.get('tags', [])), merged.get('notes', ''), now_iso(), task_id, project_id),
                )
                conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
                conn.commit()
                updated = get_task(conn, project_id, task_id)
                conn.close()
                record_event('task.updated', {'projectId': project_id, 'taskId': task_id})
                invalidate_cache('summary')
                self.send_json(200, updated)
                return

            conn.close()
            self.send_json(404, {'error': 'not_found', 'path': parsed.path})
        except ValidationError as err:
            if conn:
                conn.close()
            self.send_validation_error(err)

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
            invalidate_cache('summary')
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
            invalidate_cache('summary')
            self.send_json(200, {'deleted': True, 'projectId': project_id, 'taskId': task_id})
            return

        conn.close()
        self.send_json(404, {'error': 'not_found', 'path': parsed.path})

    def log_message(self, format, *args):
        return

    def log_request_done(self, status: int):
        duration_ms = (time.time() - getattr(self, '_start_time', time.time())) * 1000
        log_request(self.command, self.path, status, duration_ms, self.headers.get('User-Agent', ''))


if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', 4181), Handler)
    print('Forge Pipeline API listening on :4181')
    print(f'Auth enabled: {bool(API_KEY)}')
    print(f'Storage: sqlite ({DB_FILE})')
    print(f'Redis available: {REDIS_AVAILABLE} (host={REDIS_HOST}, port={REDIS_PORT})')
    if REDIS_AVAILABLE:
        redis = get_redis()
        if redis:
            print('Redis: connected')
        else:
            print('Redis: not connected (will retry on first cache operation)')
    server.serve_forever()
