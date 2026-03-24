#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
STORAGE_DIR = ROOT / "storage"
DATA_FILE = STORAGE_DIR / "campaigns.json"

DEFAULT_DATA = {
    "screenId": "default",
    "campaigns": [
        {
            "id": "camp-001",
            "title": "Spring Promotion",
            "status": "active",
            "priority": 90,
            "durationSeconds": 12,
            "template": "full-screen-image",
            "body": "Fresh seasonal offer now running.",
            "activeFrom": None,
            "activeUntil": None,
            "media": {"type": "image", "url": "https://picsum.photos/1600/900?random=11"},
        },
        {
            "id": "camp-002",
            "title": "Community Events",
            "status": "active",
            "priority": 70,
            "durationSeconds": 10,
            "template": "rss-card",
            "body": "Upcoming local events and venue notices.",
            "activeFrom": None,
            "activeUntil": None,
            "media": {"type": "image", "url": "https://picsum.photos/1600/900?random=15"},
        },
        {
            "id": "camp-003",
            "title": "Brand Fallback",
            "status": "active",
            "priority": 20,
            "durationSeconds": 8,
            "template": "announcement",
            "body": "Display Forge keeps the screen alive even when everything else gets weird.",
            "activeFrom": None,
            "activeUntil": None,
            "media": {"type": "image", "url": "https://picsum.photos/1600/900?random=19"},
        },
    ],
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().replace(microsecond=0).isoformat()


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def ensure_data_file() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        payload = dict(DEFAULT_DATA)
        payload["generatedAt"] = now_iso()
        DATA_FILE.write_text(json.dumps(payload, indent=2))


def normalize_campaign(campaign: dict) -> dict:
    campaign.setdefault("activeFrom", None)
    campaign.setdefault("activeUntil", None)
    campaign.setdefault("media", {"type": "image", "url": "https://picsum.photos/1600/900?random=21"})
    campaign.setdefault("template", "announcement")
    campaign.setdefault("durationSeconds", 10)
    campaign.setdefault("priority", 50)
    campaign.setdefault("status", "draft")
    campaign.setdefault("body", "")
    return campaign


def load_data() -> dict:
    ensure_data_file()
    data = json.loads(DATA_FILE.read_text())
    data["campaigns"] = [normalize_campaign(c) for c in data.get("campaigns", [])]
    data["generatedAt"] = now_iso()
    return data


def save_data(data: dict) -> None:
    ensure_data_file()
    data["campaigns"] = [normalize_campaign(c) for c in data.get("campaigns", [])]
    data["generatedAt"] = now_iso()
    DATA_FILE.write_text(json.dumps(data, indent=2))


def next_id(campaigns: list[dict]) -> str:
    nums = []
    for c in campaigns:
        cid = c.get("id", "")
        if cid.startswith("camp-"):
            try:
                nums.append(int(cid.split("-")[1]))
            except Exception:
                pass
    return f"camp-{(max(nums) if nums else 0) + 1:03d}"


def campaign_is_active(campaign: dict, current: datetime | None = None) -> bool:
    if campaign.get("status") != "active":
        return False
    current = current or now_utc()
    active_from = parse_dt(campaign.get("activeFrom"))
    active_until = parse_dt(campaign.get("activeUntil"))
    if active_from and current < active_from:
        return False
    if active_until and current > active_until:
        return False
    return True


def eligibility_reason(campaign: dict, current: datetime | None = None) -> str:
    current = current or now_utc()
    if campaign.get("status") != "active":
        return "status_not_active"
    active_from = parse_dt(campaign.get("activeFrom"))
    active_until = parse_dt(campaign.get("activeUntil"))
    if active_from and current < active_from:
        return "scheduled_for_future"
    if active_until and current > active_until:
        return "expired"
    return "eligible"


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send(200, {"status": "ok", "service": "display-forge-api"})
            return

        if parsed.path == "/api/dashboard/summary":
            data = load_data()
            campaigns = data.get("campaigns", [])
            active = [c for c in campaigns if campaign_is_active(c)]
            scheduled = [c for c in campaigns if eligibility_reason(c) == "scheduled_for_future"]
            expired = [c for c in campaigns if eligibility_reason(c) == "expired"]
            self._send(200, {
                "campaignCount": len(campaigns),
                "activeCampaignCount": len(active),
                "scheduledCampaignCount": len(scheduled),
                "expiredCampaignCount": len(expired),
                "screenCount": 1,
                "feedErrorCount": 0,
            })
            return

        if parsed.path == "/api/campaigns":
            data = load_data()
            query = parse_qs(parsed.query)
            status = query.get("status", [None])[0]
            campaigns = data.get("campaigns", [])
            if status:
                campaigns = [c for c in campaigns if c.get("status") == status]
            payload = []
            for c in campaigns:
                item = dict(c)
                item["eligibility"] = eligibility_reason(c)
                payload.append(item)
            self._send(200, {"campaigns": payload})
            return

        if parsed.path == "/api/screens/default/playlist":
            data = load_data()
            campaigns = [c for c in data.get("campaigns", []) if campaign_is_active(c)]
            campaigns.sort(key=lambda c: c.get("priority", 0), reverse=True)
            self._send(200, {
                "screenId": data.get("screenId", "default"),
                "generatedAt": data.get("generatedAt"),
                "campaigns": campaigns,
            })
            return

        self._send(404, {"error": "not_found", "path": parsed.path})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/campaigns":
            data = load_data()
            campaigns = data.setdefault("campaigns", [])
            body = self._read_json()
            campaign = normalize_campaign({
                "id": next_id(campaigns),
                "title": body.get("title", "Untitled campaign"),
                "status": body.get("status", "draft"),
                "priority": int(body.get("priority", 50)),
                "durationSeconds": int(body.get("durationSeconds", 10)),
                "template": body.get("template", "announcement"),
                "body": body.get("body", ""),
                "activeFrom": body.get("activeFrom"),
                "activeUntil": body.get("activeUntil"),
                "media": body.get("media", {"type": "image", "url": "https://picsum.photos/1600/900?random=21"}),
            })
            campaigns.append(campaign)
            save_data(data)
            self._send(201, campaign)
            return

        self._send(404, {"error": "not_found", "path": parsed.path})

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/campaigns/"):
            campaign_id = parsed.path.rsplit("/", 1)[-1]
            data = load_data()
            body = self._read_json()
            for campaign in data.get("campaigns", []):
                if campaign.get("id") == campaign_id:
                    campaign.update(body)
                    normalize_campaign(campaign)
                    save_data(data)
                    self._send(200, campaign)
                    return
            self._send(404, {"error": "campaign_not_found", "id": campaign_id})
            return

        self._send(404, {"error": "not_found", "path": parsed.path})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/campaigns/"):
            campaign_id = parsed.path.rsplit("/", 1)[-1]
            data = load_data()
            campaigns = data.get("campaigns", [])
            new_campaigns = [c for c in campaigns if c.get("id") != campaign_id]
            if len(new_campaigns) == len(campaigns):
                self._send(404, {"error": "campaign_not_found", "id": campaign_id})
                return
            data["campaigns"] = new_campaigns
            save_data(data)
            self._send(200, {"deleted": True, "id": campaign_id})
            return

        self._send(404, {"error": "not_found", "path": parsed.path})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    ensure_data_file()
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Display Forge API listening on :8000")
    server.serve_forever()
