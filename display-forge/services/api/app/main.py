#!/usr/bin/env python3
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "sample-playlist.json"


def load_data():
    return json.loads(DATA_FILE.read_text())


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            self._send(200, {"status": "ok", "service": "display-forge-api"})
            return
        if self.path in {"/api/dashboard/summary", "/api/screens/default/playlist"}:
            data = load_data()
            if self.path == "/api/dashboard/summary":
                campaigns = data.get("campaigns", [])
                active = [c for c in campaigns if c.get("status") == "active"]
                self._send(200, {
                    "campaignCount": len(campaigns),
                    "activeCampaignCount": len(active),
                    "screenCount": 1,
                    "feedErrorCount": 0,
                })
            else:
                self._send(200, data)
            return

        self._send(404, {"error": "not_found", "path": self.path})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Display Forge API listening on :8000")
    server.serve_forever()
