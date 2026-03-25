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

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = DATABASE_URL.startswith("postgresql")

try:
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

# SQLAlchemy imports (for PostgreSQL)
if USE_POSTGRES:
    try:
        from sqlalchemy import create_engine, text
        SQLALCHEMY_AVAILABLE = True
    except ImportError:
        SQLALCHEMY_AVAILABLE = False
        USE_POSTGRES = False
else:
    SQLALCHEMY_AVAILABLE = False

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
WS_PORT = int(os.environ.get("FORGE_PIPELINE_WS_PORT", 4182))
WS_ENABLED = os.environ.get("FORGE_PIPELINE_WS_ENABLED", "true").lower() == "true"

# PostgreSQL engine (lazy)
_pg_engine = None
_pg_session = None

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


def get_postgres_engine():
    """Get or create PostgreSQL engine."""
    global _pg_engine
    if _pg_engine is None and SQLALCHEMY_AVAILABLE:
        _pg_engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
    return _pg_engine


def db():
    """Get database connection - SQLite or PostgreSQL."""
    if USE_POSTGRES and SQLALCHEMY_AVAILABLE:
        engine = get_postgres_engine()
        conn = engine.connect()
        # Wrap to provide dict-like row access
        return PostgresConnection(conn)
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn


class PostgresConnection:
    """Wrapper for SQLAlchemy connection to mimic sqlite3 interface."""
    
    def __init__(self, conn):
        self._conn = conn
        self._last_result = None
        self._closed = False
    
    def execute(self, sql, params=()):
        if self._closed:
            raise RuntimeError("Connection is closed")
        # Convert ? placeholders to :param0, :param1, etc. for SQLAlchemy
        if params:
            if isinstance(params, (list, tuple)):
                # Convert positional params to named params
                param_dict = {f'param{i}': p for i, p in enumerate(params)}
                new_sql = sql
                for i in range(len(params)):
                    new_sql = new_sql.replace('?', f':param{i}', 1)
                self._last_result = self._conn.execute(text(new_sql), param_dict)
            elif isinstance(params, dict):
                self._last_result = self._conn.execute(text(sql), params)
            else:
                self._last_result = self._conn.execute(text(sql))
        else:
            self._last_result = self._conn.execute(text(sql))
        return PostgresResult(self._last_result)
    
    def commit(self):
        if not self._closed:
            self._conn.commit()
    
    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            # Return connection to pool by calling close on the SQLAlchemy connection
            self._conn.close()
        except Exception:
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class PostgresResult:
    """Wrapper for SQLAlchemy Result to mimic sqlite3 cursor."""
    
    def __init__(self, result):
        self._result = result
        self._rows = None
    
    def fetchone(self):
        row = self._result.fetchone()
        if row is None:
            return None
        # Convert to Row-like object with dict access
        keys = list(self._result.keys()) if hasattr(self._result, 'keys') else []
        return PostgresRow(row, keys)
    
    def fetchall(self):
        rows = self._result.fetchall()
        keys = list(self._result.keys()) if hasattr(self._result, 'keys') else []
        return [PostgresRow(row, keys) for row in rows]


class PostgresRow:
    """Row object that supports both dict-style and attribute access."""
    
    def __init__(self, row, keys):
        self._row = row
        self._keys = keys
        self._dict = {k: v for k, v in zip(keys, row)} if keys else {}
    
    def __getitem__(self, key):
        return self._dict[key]
    
    def __contains__(self, key):
        return key in self._dict
    
    def keys(self):
        return self._keys
    
    def get(self, key, default=None):
        return self._dict.get(key, default)

ALLOWED_PROJECT_STATUS = {'on-track', 'at-risk', 'off-track', 'not-started', 'in-progress', 'blocked', 'completed', 'overdue', 'cancelled'}
ALLOWED_TASK_STATUS = {'todo', 'in-progress', 'blocked', 'done'}
ALLOWED_PRIORITY = {'low', 'medium', 'high', 'critical'}
ALLOWED_RISK_STATE = {'none', 'watch', 'at-risk', 'critical'}
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
            "status": "not-started",
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
            "status": "not-started",
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


def init_db() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    if USE_POSTGRES and SQLALCHEMY_AVAILABLE:
        # PostgreSQL: create tables via SQLAlchemy
        engine = get_postgres_engine()
        with engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'not-started',
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL
                )
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'todo',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    risk_state TEXT NOT NULL DEFAULT 'none',
                    due_date TEXT NOT NULL DEFAULT '',
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    notes TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL
                )
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}'
                )
            '''))
            conn.commit()
        return
    
    # SQLite: existing logic
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
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
            risk_state TEXT NOT NULL DEFAULT 'none',
            due_date TEXT NOT NULL DEFAULT '',
            tags_json TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL,
            blocked_by TEXT NOT NULL DEFAULT '[]',
            blocking TEXT NOT NULL DEFAULT '[]'
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


def clean_risk_state(value):
    value = clean_string(value or 'none', 'risk_state', max_len=32, allow_empty=False)
    if value not in ALLOWED_RISK_STATE:
        raise ValidationError(f'invalid risk_state: {value}', 'risk_state')
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
    if not partial or 'riskState' in body:
        out['riskState'] = clean_risk_state(body.get('riskState', 'none'))
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


def project_count(conn) -> int:
    return conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0]


def event_count(conn) -> int:
    return conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]


def _get_summary_cached(conn) -> dict:
    """Get summary with Redis cache (60s TTL)."""
    redis = get_redis()
    if redis:
        cached = redis.get('forge:cache:summary')
        if cached:
            return json.loads(cached)
    
    # Compute summary
    projects = list_projects(conn)
    tasks = [t for p in projects for t in p.get('tasks', [])]
    
    # FP-010: Rename Open → Active, add At Risk
    # FP-011: Add KPI deltas (compare to previous snapshot)
    active_tasks = [t for t in tasks if t.get('status') != 'done']
    done_tasks = [t for t in tasks if t.get('status') == 'done']
    blocked_tasks = [t for t in tasks if t.get('status') == 'blocked']
    at_risk_tasks = [t for t in tasks if t.get('riskState', 'none') in ('at-risk', 'critical')]
    critical_tasks = [t for t in tasks if t.get('priority') == 'critical']
    
    summary = {
        'projectCount': len(projects),
        'taskCount': len(tasks),
        'activeTaskCount': len(active_tasks),
        'doneTaskCount': len(done_tasks),
        'blockedTaskCount': len(blocked_tasks),
        'atRiskTaskCount': len(at_risk_tasks),
        'criticalTaskCount': len(critical_tasks),
        'updatedAt': now_iso(),
    }
    
    # FP-011: Load previous snapshot and compute deltas
    prev_key = 'forge:snapshot:previous'
    prev_summary = None
    if redis:
        try:
            prev_data = redis.get(prev_key)
            if prev_data:
                prev_summary = json.loads(prev_data)
        except Exception:
            pass
    
    if prev_summary:
        summary['deltas'] = {
            'activeTaskCount': summary['activeTaskCount'] - prev_summary.get('activeTaskCount', 0),
            'doneTaskCount': summary['doneTaskCount'] - prev_summary.get('doneTaskCount', 0),
            'atRiskTaskCount': summary['atRiskTaskCount'] - prev_summary.get('atRiskTaskCount', 0),
            'blockedTaskCount': summary['blockedTaskCount'] - prev_summary.get('blockedTaskCount', 0),
        }
        # Include absolute previous values for trend calculation
        summary['previous'] = {
            'activeTaskCount': prev_summary.get('activeTaskCount', 0),
            'doneTaskCount': prev_summary.get('doneTaskCount', 0),
            'updatedAt': prev_summary.get('updatedAt'),
        }
    
    # Cache it and save snapshot
    if redis:
        try:
            redis.setex('forge:cache:summary', 60, json.dumps(summary))
            # Update snapshot every 5 minutes for delta comparison
            redis.setex(prev_key, 300, json.dumps({
                'activeTaskCount': summary['activeTaskCount'],
                'doneTaskCount': summary['doneTaskCount'],
                'atRiskTaskCount': summary['atRiskTaskCount'],
                'blockedTaskCount': summary['blockedTaskCount'],
                'updatedAt': summary['updatedAt'],
            }))
        except Exception:
            pass
    
    return summary


def migrate_if_needed() -> None:
    conn = db()
    try:
        # Add risk_state column to tasks if missing (v1.1.0)
        try:
            conn.execute('ALTER TABLE tasks ADD COLUMN risk_state TEXT NOT NULL DEFAULT "none"')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Add blocked_by and blocking columns for dependencies (v2.0.0)
        try:
            conn.execute('ALTER TABLE tasks ADD COLUMN blocked_by TEXT NOT NULL DEFAULT "[]"')
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute('ALTER TABLE tasks ADD COLUMN blocking TEXT NOT NULL DEFAULT "[]"')
        except sqlite3.OperationalError:
            pass

        # Add critical to priority if needed (v1.1.0)
        # Note: SQLite doesn't enforce CHECK constraints dynamically, so no migration needed

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
    finally:
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
                'INSERT OR REPLACE INTO tasks (id, project_id, title, status, priority, risk_state, due_date, tags_json, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (task.get('id') or new_id('task'), pid, task.get('title', 'Untitled task'), task.get('status', 'todo'), task.get('priority', 'medium'), task.get('riskState', 'none'), task.get('dueDate', ''), json.dumps(task.get('tags', [])), task.get('notes', ''), stamp),
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
        'riskState': row['risk_state'] if 'risk_state' in row.keys() else 'none',
        'dueDate': row['due_date'],
        'tags': json.loads(row['tags_json'] or '[]'),
        'notes': row['notes'],
        'updatedAt': row['updated_at'],
        'blockedBy': json.loads(row['blocked_by'] if 'blocked_by' in row.keys() else '[]'),
        'blocking': json.loads(row['blocking'] if 'blocking' in row.keys() else '[]'),
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
    try:
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
        
        # Publish to WebSocket clients via Redis pub/sub
        try:
            redis = get_redis()
            if redis:
                redis.publish('forge-pipeline:events', json.dumps({
                    'event': kind,
                    'payload': payload,
                }))
        except Exception:
            pass  # WebSocket publishing is optional
        
        return entry
    finally:
        conn.close()


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


def compute_workspace_rollup(conn: sqlite3.Connection) -> dict:
    """Compute aggregated metrics across all workspaces (by source tag)."""
    projects = list_projects(conn)
    workspaces = {}
    now = datetime.now(timezone.utc)
    
    for project in projects:
        # Find source tag for workspace
        source_tag = None
        for tag in project.get('tags', []):
            if tag.startswith('source:'):
                source_tag = tag.replace('source:', '')
                break
        
        if not source_tag:
            source_tag = 'default'
        
        if source_tag not in workspaces:
            workspaces[source_tag] = {
                'source': source_tag,
                'projects': 0,
                'tasks': 0,
                'completed': 0,
                'active': 0,
                'blocked': 0,
                'atRisk': 0,
                'critical': 0,
                'overdue': 0,
                'lastUpdated': None,
            }
        
        ws = workspaces[source_tag]
        ws['projects'] += 1
        
        for task in project.get('tasks', []):
            ws['tasks'] += 1
            status = task.get('status', 'todo')
            if status == 'done':
                ws['completed'] += 1
            elif status == 'in-progress':
                ws['active'] += 1
            elif status == 'blocked':
                ws['blocked'] += 1
            
            risk = task.get('riskState', 'none')
            if risk in ('at-risk', 'critical'):
                ws['atRisk'] += 1
            
            priority = task.get('priority', 'medium')
            if priority == 'critical':
                ws['critical'] += 1
            
            due = task.get('dueDate')
            if due and due != '':
                try:
                    due_date = datetime.fromisoformat(due.replace('Z', '+00:00'))
                    if due_date < now and status != 'done':
                        ws['overdue'] += 1
                except:
                    pass
        
        updated = project.get('updatedAt')
        if updated:
            if not ws['lastUpdated'] or updated > ws['lastUpdated']:
                ws['lastUpdated'] = updated
    
    # Sort by task count
    workspace_list = sorted(workspaces.values(), key=lambda w: -w['tasks'])
    
    return {
        'workspaces': workspace_list,
        'total': {
            'workspaces': len(workspace_list),
            'projects': sum(w['projects'] for w in workspace_list),
            'tasks': sum(w['tasks'] for w in workspace_list),
            'completed': sum(w['completed'] for w in workspace_list),
            'active': sum(w['active'] for w in workspace_list),
            'blocked': sum(w['blocked'] for w in workspace_list),
            'atRisk': sum(w['atRisk'] for w in workspace_list),
            'critical': sum(w['critical'] for w in workspace_list),
            'overdue': sum(w['overdue'] for w in workspace_list),
        }
    }


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
            'UPDATE tasks SET title = ?, status = ?, priority = ?, risk_state = ?, due_date = ?, tags_json = ?, notes = ?, blocked_by = ?, blocking = ?, updated_at = ? WHERE id = ? AND project_id = ?',
            (merged['title'], merged.get('status', 'todo'), merged.get('priority', 'medium'), merged.get('riskState', 'none'), merged.get('dueDate', ''), json.dumps(merged.get('tags', [])), merged.get('notes', ''), json.dumps(merged.get('blockedBy', [])), json.dumps(merged.get('blocking', [])), merged['updatedAt'], merged['id'], project_id),
        )
        conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
        return get_task(conn, project_id, merged['id']), 'updated'

    tid = task_id or new_id('task')
    conn.execute(
        'INSERT INTO tasks (id, project_id, title, status, priority, risk_state, due_date, tags_json, notes, blocked_by, blocking, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (tid, project_id, title or 'Untitled task', clean.get('status', 'todo'), clean.get('priority', 'medium'), clean.get('riskState', 'none'), clean.get('dueDate', ''), json.dumps(clean.get('tags', [])), clean.get('notes', ''), json.dumps(clean.get('blockedBy', [])), json.dumps(clean.get('blocking', [])), now_iso()),
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

        try:
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
                
                storage_type = 'postgresql' if USE_POSTGRES else 'sqlite'
                self.send_json(200, {
                    'status': 'ok',
                    'service': 'forge-pipeline-api',
                    'authEnabled': bool(API_KEY),
                    'storage': storage_type,
                    'redis': redis_status,
                    'redisAvailable': REDIS_AVAILABLE,
                })
                self.log_request_done(200)
                return

            if parsed.path == '/api/summary':
                # Use cached summary (60s TTL)
                summary = _get_summary_cached(conn)
                self.send_json(200, summary)
                self.log_request_done(200)
                return

            if parsed.path == '/api/projects':
                limit = int(q.get('limit', ['100'])[0])
                offset = int(q.get('offset', ['0'])[0])
                total = count_projects(conn)
                projects = [p for p in list_projects(conn, limit=limit, offset=offset) if project_matches(p, query, status)]
                has_more = offset + limit < total
                self.send_json(200, {'projects': projects, 'total': total, 'limit': limit, 'offset': offset, 'hasMore': has_more})
                self.log_request_done(200)
                return

            if parsed.path.startswith('/api/projects/') and '/tasks' not in parsed.path:
                project_id = parsed.path.split('/')[3]
                project = get_project(conn, project_id)
                if not project:
                    self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                    return
                self.send_json(200, project)
                return

            if parsed.path == '/api/tasks':
                limit = int(q.get('limit', ['100'])[0])
                offset = int(q.get('offset', ['0'])[0])
                status_filter = q.get('status', [None])[0]
                priority_filter = q.get('priority', [None])[0]
                query_text = q.get('q', [None])[0]
                
                all_tasks = []
                for project in list_projects(conn):
                    for task in project.get('tasks', []):
                        if status_filter and task.get('status') != status_filter:
                            continue
                        if priority_filter and task.get('priority') != priority_filter:
                            continue
                        if query_text and query_text.lower() not in task.get('title', '').lower():
                            continue
                        all_tasks.append({**task, 'projectId': project['id'], 'projectName': project['name']})
                
                self.send_json(200, {'tasks': all_tasks, 'total': len(all_tasks)})
                return

            if parsed.path == '/api/events':
                limit = int(q.get('limit', ['50'])[0])
                offset = int(q.get('offset', ['0'])[0])
                events = list_events(conn, limit=limit, offset=offset)
                self.send_json(200, {'events': events})
                return

            # FP-092: Workspace rollup endpoint
            if parsed.path == '/api/rollup':
                rollup = compute_workspace_rollup(conn)
                self.send_json(200, rollup)
                return

            self.send_json(404, {'error': 'not_found', 'path': parsed.path})
        finally:
            conn.close()

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

        # FP-091: Dependency graph endpoint
        if parsed.path == '/api/dependencies':
            # Build a dependency graph from all tasks
            graph = {'nodes': [], 'edges': []}
            task_map = {}  # Map task_id to task info
            
            for project in list_projects(conn, limit=1000, offset=0):
                for task in project.get('tasks', []):
                    task_id = f"{project['id']}:{task['id']}"
                    task_map[task_id] = {
                        'id': task_id,
                        'taskId': task['id'],
                        'projectId': project['id'],
                        'projectName': project['name'],
                        'title': task['title'],
                        'status': task.get('status', 'todo'),
                        'priority': task.get('priority', 'medium'),
                        'blockedBy': task.get('blockedBy', []),
                        'blocking': task.get('blocking', []),
                    }
                    graph['nodes'].append({
                        'id': task_id,
                        'label': task['title'],
                        'status': task.get('status', 'todo'),
                        'priority': task.get('priority', 'medium'),
                        'project': project['name'],
                    })
            
            # Build edges from blockedBy/blocking references
            for task_id, task_info in task_map.items():
                for blocked_id in task_info.get('blockedBy', []):
                    # Find the blocking task
                    for tid, t in task_map.items():
                        if t['taskId'] == blocked_id or tid == blocked_id:
                            graph['edges'].append({'source': tid, 'target': task_id, 'type': 'blocks'})
                for blocking_id in task_info.get('blocking', []):
                    for tid, t in task_map.items():
                        if t['taskId'] == blocking_id or tid == blocking_id:
                            graph['edges'].append({'source': task_id, 'target': tid, 'type': 'blocked-by'})
            
            self.send_json(200, graph)
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
        parsed = urlparse(self.path)
        body = self.read_json()
        conn = db()
        try:
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
                record_event('project.created', {'projectId': pid, 'name': project['name']})
                invalidate_cache('summary')
                self.send_json(201, project)
                return

            if parsed.path.startswith('/api/projects/') and parsed.path.endswith('/tasks'):
                project_id = parsed.path.split('/')[3]
                project = get_project(conn, project_id)
                if not project:
                    self.send_json(404, {'error': 'project_not_found', 'id': project_id})
                    return
                clean = validate_task_payload(body, partial=False)
                source = derive_source(body)
                clean['tags'] = ensure_source_tag(clean.get('tags', []), source)
                tid = clean.get('id') or new_id('task')
                conn.execute(
                    'INSERT INTO tasks (id, project_id, title, status, priority, risk_state, due_date, tags_json, notes, blocked_by, blocking, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (tid, project_id, clean['title'], clean.get('status', 'todo'), clean.get('priority', 'medium'), clean.get('riskState', 'none'), clean.get('dueDate', ''), json.dumps(clean.get('tags', [])), clean.get('notes', ''), json.dumps(clean.get('blockedBy', [])), json.dumps(clean.get('blocking', [])), now_iso()),
                )
                conn.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now_iso(), project_id))
                conn.commit()
                task = get_task(conn, project_id, tid)
                record_event('task.created', {'projectId': project_id, 'taskId': tid, 'title': task['title']})
                invalidate_cache('summary')
                self.send_json(201, task)
                return

            if parsed.path == '/api/bulk/import':
                require_object(body)
                projects = body.get('projects', [])
                if not isinstance(projects, list):
                    raise ValidationError('projects must be a list', 'projects')
                conn.execute('DELETE FROM tasks')
                conn.execute('DELETE FROM projects')
                import_projects(conn, projects)
                conn.commit()
                record_event('bulk.import', {'projectCount': len(projects)})
                self.send_json(200, {'ok': True, 'projectCount': len(projects)})
                return

            if parsed.path == '/api/mcp/project-upsert':
                project, action = upsert_project(conn, body)
                conn.commit()
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
                    'riskState': clean.get('riskState', 'none'),
                    'dueDate': clean.get('dueDate', ''),
                    'tags': clean.get('tags', []),
                    'notes': clean.get('notes', ''),
                    'blockedBy': clean.get('blockedBy', task.get('blockedBy', [])),
                    'blocking': clean.get('blocking', task.get('blocking', [])),
                } if replace else {**task, **clean})
                conn.execute(
                    'UPDATE tasks SET title = ?, status = ?, priority = ?, risk_state = ?, due_date = ?, tags_json = ?, notes = ?, blocked_by = ?, blocking = ?, updated_at = ? WHERE id = ? AND project_id = ?',
                    (merged['title'], merged.get('status', 'todo'), merged.get('priority', 'medium'), merged.get('riskState', 'none'), merged.get('dueDate', ''), json.dumps(merged.get('tags', [])), merged.get('notes', ''), json.dumps(merged.get('blockedBy', [])), json.dumps(merged.get('blocking', [])), now_iso(), task_id, project_id),
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
