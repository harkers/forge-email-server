#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
PORT = int(os.environ.get("DASHBOARD_PORT", "8899"))
AGENT_ID = os.environ.get("OPENCLAW_AGENT_ID", "main")
SESSIONS_DIR = Path(
    os.environ.get(
        "OPENCLAW_SESSIONS_DIR",
        f"/home/stu/.openclaw/agents/{AGENT_ID}/sessions",
    )
).expanduser()
SESSIONS_JSON = SESSIONS_DIR / "sessions.json"


def iso_to_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except Exception:
        return None


def ms_to_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc)
    except Exception:
        return None


def safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def week_key(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


@dataclass
class UsageRow:
    session_key: str
    session_id: str
    started_at: datetime | None
    ended_at: datetime | None
    updated_at: datetime | None
    provider: str
    model: str
    channel: str
    chat_type: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    cache_read: int | None
    cache_write: int | None
    cost_total: float | None
    runtime_ms: int | None
    status: str
    usage_state: str
    cost_state: str
    source: str

    def bucket_day(self) -> str:
        dt = self.started_at or self.updated_at or self.ended_at or datetime.now(timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")

    def bucket_week(self) -> str:
        dt = self.started_at or self.updated_at or self.ended_at or datetime.now(timezone.utc)
        return week_key(dt.astimezone(timezone.utc))

    def bucket_month(self) -> str:
        dt = self.started_at or self.updated_at or self.ended_at or datetime.now(timezone.utc)
        return month_key(dt.astimezone(timezone.utc))


def load_sessions_json() -> dict[str, Any]:
    if not SESSIONS_JSON.exists():
        return {}
    try:
        return json.loads(SESSIONS_JSON.read_text())
    except Exception:
        return {}


def transcript_usage(session_file: Path) -> dict[str, Any]:
    if not session_file.exists():
        return {}

    latest_usage: dict[str, Any] | None = None
    provider = None
    model = None
    seen_assistant_message = False
    had_zero_usage = False

    try:
        with session_file.open() as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except Exception:
                    continue
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message") or {}
                if msg.get("role") != "assistant":
                    continue
                seen_assistant_message = True
                provider = msg.get("provider") or provider
                model = msg.get("model") or model
                usage = msg.get("usage")
                if isinstance(usage, dict):
                    latest_usage = usage
                    total = safe_int(usage.get("totalTokens"))
                    if total == 0:
                        had_zero_usage = True
    except Exception:
        return {}

    result: dict[str, Any] = {
        "provider": provider,
        "model": model,
        "seenAssistantMessage": seen_assistant_message,
        "hadZeroUsage": had_zero_usage,
    }
    if latest_usage:
        result["usage"] = latest_usage
    return result


def classify_usage_state(provider: str, usage: dict[str, Any] | None, transcript: dict[str, Any]) -> str:
    if usage:
        total = safe_int(usage.get("totalTokens"))
        if total and total > 0:
            return "reported"
        if total == 0:
            return "unknown"
    if transcript.get("usage"):
        total = safe_int((transcript.get("usage") or {}).get("totalTokens"))
        if total and total > 0:
            return "reported"
        if total == 0:
            return "unknown"
    if transcript.get("seenAssistantMessage"):
        return "unknown"
    if provider:
        return "estimated"
    return "unknown"


def classify_cost_state(provider: str, usage_state: str, cost_total: float | None, transcript_usage_obj: dict[str, Any] | None) -> str:
    if usage_state != "reported":
        return "unknown"

    if cost_total is None:
        return "unknown"

    if cost_total > 0:
        return "reported"

    if cost_total == 0:
        if provider in {"ollama", "openai-compatible", "unknown"}:
            return "unknown"
        if transcript_usage_obj and isinstance(transcript_usage_obj.get("cost"), dict):
            cost_obj = transcript_usage_obj.get("cost") or {}
            non_total_fields = [
                safe_float(cost_obj.get("input")),
                safe_float(cost_obj.get("output")),
                safe_float(cost_obj.get("cacheRead")),
                safe_float(cost_obj.get("cacheWrite")),
            ]
            if any((value or 0) > 0 for value in non_total_fields):
                return "reported"
        return "reported"

    return "unknown"


def build_row(session_key: str, meta: dict[str, Any]) -> UsageRow:
    session_id = meta.get("sessionId") or ""
    session_file = Path(meta.get("sessionFile") or (SESSIONS_DIR / f"{session_id}.jsonl"))
    transcript = transcript_usage(session_file)

    provider = str(meta.get("modelProvider") or transcript.get("provider") or "unknown")
    model = str(meta.get("model") or transcript.get("model") or "unknown")
    channel = str(meta.get("lastChannel") or meta.get("channel") or ((meta.get("deliveryContext") or {}).get("channel")) or "unknown")
    chat_type = str(meta.get("chatType") or ((meta.get("origin") or {}).get("chatType")) or "unknown")

    input_tokens = safe_int(meta.get("inputTokens"))
    output_tokens = safe_int(meta.get("outputTokens"))
    total_tokens = safe_int(meta.get("totalTokens"))
    cache_read = safe_int(meta.get("cacheRead"))
    cache_write = safe_int(meta.get("cacheWrite"))
    runtime_ms = safe_int(meta.get("runtimeMs"))
    cost_total = None

    transcript_usage_obj = transcript.get("usage") if isinstance(transcript.get("usage"), dict) else None
    if input_tokens is None and transcript_usage_obj:
        input_tokens = safe_int(transcript_usage_obj.get("input"))
    if output_tokens is None and transcript_usage_obj:
        output_tokens = safe_int(transcript_usage_obj.get("output"))
    if total_tokens is None and transcript_usage_obj:
        total_tokens = safe_int(transcript_usage_obj.get("totalTokens"))
    if cache_read is None and transcript_usage_obj:
        cache_read = safe_int(transcript_usage_obj.get("cacheRead"))
    if cache_write is None and transcript_usage_obj:
        cache_write = safe_int(transcript_usage_obj.get("cacheWrite"))
    if transcript_usage_obj:
        cost_total = safe_float(((transcript_usage_obj.get("cost") or {}).get("total")))

    usage_state = classify_usage_state(provider, {
        "input": input_tokens,
        "output": output_tokens,
        "totalTokens": total_tokens,
    }, transcript)
    cost_state = classify_cost_state(provider, usage_state, cost_total, transcript_usage_obj)

    if usage_state == "unknown":
        input_tokens = None
        output_tokens = None
        total_tokens = None
        cost_total = None

    if cost_state == "unknown":
        cost_total = None

    started_at = ms_to_dt(meta.get("startedAt"))
    ended_at = ms_to_dt(meta.get("endedAt"))
    updated_at = ms_to_dt(meta.get("updatedAt"))

    return UsageRow(
        session_key=session_key,
        session_id=session_id,
        started_at=started_at,
        ended_at=ended_at,
        updated_at=updated_at,
        provider=provider,
        model=model,
        channel=channel,
        chat_type=chat_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cache_read=cache_read,
        cache_write=cache_write,
        cost_total=cost_total,
        runtime_ms=runtime_ms,
        status=str(meta.get("status") or "unknown"),
        usage_state=usage_state,
        cost_state=cost_state,
        source="sessions.json + transcript jsonl",
    )


def collect_usage_records() -> tuple[list[UsageRow], dict[str, Any]]:
    sessions = load_sessions_json()
    rows = [build_row(k, v) for k, v in sessions.items()]
    rows.sort(key=lambda r: (r.started_at or r.updated_at or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)

    stats = {
        "sessionsDir": str(SESSIONS_DIR),
        "sessionsJsonExists": SESSIONS_JSON.exists(),
        "sessionCount": len(rows),
        "usageStates": dict(Counter(r.usage_state for r in rows)),
        "costStates": dict(Counter(r.cost_state for r in rows)),
        "providers": dict(Counter(r.provider for r in rows)),
    }
    return rows, stats


def summarize(rows: list[UsageRow], bucket_name: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[UsageRow]] = defaultdict(list)
    for row in rows:
        key = getattr(row, bucket_name)()
        grouped[key].append(row)

    output = []
    for key in sorted(grouped.keys(), reverse=True):
        items = grouped[key]
        cost_known = [r.cost_total for r in items if r.cost_total is not None]
        output.append({
            "period": key,
            "sessions": len(items),
            "reportedSessions": sum(1 for r in items if r.usage_state == "reported"),
            "unknownSessions": sum(1 for r in items if r.usage_state == "unknown"),
            "estimatedSessions": sum(1 for r in items if r.usage_state == "estimated"),
            "reportedCostSessions": sum(1 for r in items if r.cost_state == "reported"),
            "unknownCostSessions": sum(1 for r in items if r.cost_state == "unknown"),
            "inputTokens": sum(r.input_tokens or 0 for r in items),
            "outputTokens": sum(r.output_tokens or 0 for r in items),
            "totalTokens": sum(r.total_tokens or 0 for r in items),
            "costTotal": round(sum(cost_known), 6) if cost_known else None,
        })
    return output


def breakdown(rows: list[UsageRow], attr: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[UsageRow]] = defaultdict(list)
    for row in rows:
        grouped[getattr(row, attr)].append(row)
    items = []
    for key, entries in grouped.items():
        cost_known = [r.cost_total for r in entries if r.cost_total is not None]
        items.append({
            "name": key,
            "sessions": len(entries),
            "reportedSessions": sum(1 for r in entries if r.usage_state == "reported"),
            "unknownSessions": sum(1 for r in entries if r.usage_state == "unknown"),
            "estimatedSessions": sum(1 for r in entries if r.usage_state == "estimated"),
            "reportedCostSessions": sum(1 for r in entries if r.cost_state == "reported"),
            "unknownCostSessions": sum(1 for r in entries if r.cost_state == "unknown"),
            "totalTokens": sum(r.total_tokens or 0 for r in entries),
            "costTotal": round(sum(cost_known), 6) if cost_known else None,
        })
    items.sort(key=lambda x: (x["totalTokens"], x["sessions"]), reverse=True)
    return items


def row_to_dict(row: UsageRow) -> dict[str, Any]:
    return {
        "sessionKey": row.session_key,
        "sessionId": row.session_id,
        "startedAt": row.started_at.isoformat() if row.started_at else None,
        "endedAt": row.ended_at.isoformat() if row.ended_at else None,
        "updatedAt": row.updated_at.isoformat() if row.updated_at else None,
        "provider": row.provider,
        "model": row.model,
        "channel": row.channel,
        "chatType": row.chat_type,
        "inputTokens": row.input_tokens,
        "outputTokens": row.output_tokens,
        "totalTokens": row.total_tokens,
        "cacheRead": row.cache_read,
        "cacheWrite": row.cache_write,
        "costTotal": row.cost_total,
        "runtimeMs": row.runtime_ms,
        "status": row.status,
        "usageState": row.usage_state,
        "costState": row.cost_state,
        "source": row.source,
    }


def dashboard_payload() -> dict[str, Any]:
    rows, stats = collect_usage_records()
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "summary": {
            "day": summarize(rows, "bucket_day"),
            "week": summarize(rows, "bucket_week"),
            "month": summarize(rows, "bucket_month"),
        },
        "breakdown": {
            "models": breakdown(rows, "model"),
            "providers": breakdown(rows, "provider"),
            "channels": breakdown(rows, "channel"),
        },
        "recentSessions": [row_to_dict(r) for r in rows[:200]],
    }


HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>OpenClaw Usage Dashboard</title>
  <style>
    body { font-family: Inter, system-ui, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
    .wrap { max-width: 1200px; margin: 0 auto; padding: 24px; }
    h1, h2 { margin: 0 0 12px; }
    .muted, .mini { color: #94a3b8; }
    .row { display: grid; gap: 16px; }
    .cards { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
    .card { background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }
    .tabs { display: flex; gap: 8px; margin: 20px 0; }
    .tab, button { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 10px; padding: 8px 12px; cursor: pointer; }
    .tab.active { background: #2563eb; border-color: #2563eb; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #1f2937; vertical-align: top; }
    .pill { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; }
    .reported { background: #14532d; color: #bbf7d0; }
    .unknown { background: #78350f; color: #fde68a; }
    .estimated { background: #1e3a8a; color: #bfdbfe; }
    code { color: #93c5fd; }
    a { color: #93c5fd; }
  </style>
</head>
<body>
<div class=\"wrap\">
  <h1>OpenClaw Usage Dashboard</h1>
  <p id=\"summaryLine\" class=\"muted\">Loading…</p>
  <div class=\"row cards\" id=\"topCards\"></div>
  <div class=\"tabs\">
    <button class=\"tab active\" data-period=\"day\">Day</button>
    <button class=\"tab\" data-period=\"week\">Week</button>
    <button class=\"tab\" data-period=\"month\">Month</button>
    <button id=\"refreshBtn\">Refresh</button>
  </div>
  <div class=\"card\">
    <h2>Summary</h2>
    <div id=\"summaryTable\"></div>
  </div>
  <div class=\"row cards\" style=\"margin-top:16px\">
    <div class=\"card\"><h2>By model</h2><div id=\"modelsTable\"></div></div>
    <div class=\"card\"><h2>By provider</h2><div id=\"providersTable\"></div></div>
    <div class=\"card\"><h2>By channel</h2><div id=\"channelsTable\"></div></div>
  </div>
  <div class=\"card\" style=\"margin-top:16px\">
    <h2>Recent sessions</h2>
    <div id=\"sessionsTable\"></div>
    <p class=\"mini\">Unknown rows are expected for some local / OpenAI-compatible providers when usage is not persisted.</p>
  </div>
</div>
<script>
let payload = null;
let period = 'day';
function num(v) { return (v ?? 0).toLocaleString(); }
function money(v) { return v == null ? 'unknown' : '$' + Number(v).toFixed(4); }
function pill(state) { return `<span class=\"pill ${state}\">${state}</span>`; }
function table(headers, rows) {
  return `<table><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
function renderTop() {
  const stats = payload.stats;
  document.getElementById('summaryLine').innerHTML = `Source: <code>${stats.sessionsDir}</code> · Sessions: ${num(stats.sessionCount)} · Generated: ${payload.generatedAt}`;
  const cards = [
    ['Reported tokens', num(stats.usageStates.reported || 0)],
    ['Unknown tokens', num(stats.usageStates.unknown || 0)],
    ['Reported cost', num(stats.costStates.reported || 0)],
    ['Unknown cost', num(stats.costStates.unknown || 0)],
    ['Providers', num(Object.keys(stats.providers || {}).length)],
  ];
  document.getElementById('topCards').innerHTML = cards.map(([k,v]) => `<div class=\"card\"><div class=\"muted\">${k}</div><div style=\"font-size:28px;font-weight:700\">${v}</div></div>`).join('');
}
function renderSummary() {
  const rows = (payload.summary[period] || []).slice(0, 20).map(r => [r.period, num(r.sessions), num(r.reportedSessions), num(r.unknownSessions), num(r.reportedCostSessions), num(r.unknownCostSessions), num(r.totalTokens), money(r.costTotal)]);
  document.getElementById('summaryTable').innerHTML = table(['Period','Sessions','Reported tokens','Unknown tokens','Reported cost','Unknown cost','Total tokens','Cost'], rows);
}
function renderBreakdown(id, rows) {
  document.getElementById(id).innerHTML = table(['Name','Sessions','Reported tokens','Unknown tokens','Reported cost','Unknown cost','Tokens','Cost'], rows.slice(0,20).map(r => [r.name, num(r.sessions), num(r.reportedSessions), num(r.unknownSessions), num(r.reportedCostSessions), num(r.unknownCostSessions), num(r.totalTokens), money(r.costTotal)]));
}
function renderSessions() {
  const rows = (payload.recentSessions || []).slice(0, 50).map(r => [r.startedAt || r.updatedAt || '', `${r.provider}<br><span class=\"mini\">${r.model}</span>`, r.channel, `${pill(r.usageState)} ${pill(r.costState)}`, r.totalTokens == null ? 'unknown' : num(r.totalTokens), money(r.costTotal), r.status]);
  document.getElementById('sessionsTable').innerHTML = table(['Started','Provider / model','Channel','Usage / cost','Tokens','Cost','Status'], rows);
}
function applyPeriod() { renderTop(); renderSummary(); renderBreakdown('modelsTable', payload.breakdown.models || []); renderBreakdown('providersTable', payload.breakdown.providers || []); renderBreakdown('channelsTable', payload.breakdown.channels || []); renderSessions(); }
async function load() { const res = await fetch('/api/dashboard'); payload = await res.json(); applyPeriod(); }
document.querySelectorAll('.tab[data-period]').forEach(btn => btn.addEventListener('click', () => { document.querySelectorAll('.tab[data-period]').forEach(b => b.classList.remove('active')); btn.classList.add('active'); period = btn.dataset.period; applyPeriod(); }));
document.getElementById('refreshBtn').addEventListener('click', load);
load().catch(err => { document.getElementById('summaryLine').textContent = `Failed to load dashboard data: ${err}`; });
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "OpenClawUsageDashboard/0.1"

    def _json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body: str, status: int = 200) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._html(HTML)
            return
        if parsed.path == "/api/dashboard":
            self._json(dashboard_payload())
            return
        if parsed.path == "/api/health":
            records, stats = collect_usage_records()
            self._json({"ok": True, "sessionsDir": str(SESSIONS_DIR), "recordCount": len(records), "stats": stats})
            return
        self._json({"error": "not found"}, status=404)


def main() -> None:
    print("OpenClaw Usage Dashboard")
    print(f"Sessions dir : {SESSIONS_DIR}")
    print(f"Serving      : http://{HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
