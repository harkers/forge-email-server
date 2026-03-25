#!/usr/bin/env python3
"""Migration script to export SQLite data and prepare for PostgreSQL."""

import json
import sqlite3
from pathlib import Path

STORAGE_DIR = Path(__file__).parent / "storage"
DB_FILE = STORAGE_DIR / "forge-pipeline.db"


def export_sqlite_data():
    """Export all data from SQLite to JSON for migration."""
    if not DB_FILE.exists():
        print("No SQLite database found, nothing to migrate.")
        return None
    
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    
    data = {
        "projects": [],
        "tasks": [],
        "events": []
    }
    
    # Export projects
    for row in conn.execute("SELECT * FROM projects"):
        data["projects"].append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"] or "",
            "notes": row["notes"] or "",
            "status": row["status"],
            "tags_json": row["tags_json"] or "[]",
            "updated_at": row["updated_at"]
        })
    
    # Export tasks
    for row in conn.execute("SELECT * FROM tasks"):
        data["tasks"].append({
            "id": row["id"],
            "project_id": row["project_id"],
            "title": row["title"],
            "status": row["status"],
            "priority": row["priority"],
            "risk_state": row["risk_state"] if "risk_state" in row.keys() else "none",
            "due_date": row["due_date"] or "",
            "tags_json": row["tags_json"] or "[]",
            "notes": row["notes"] or "",
            "updated_at": row["updated_at"]
        })
    
    # Export events
    for row in conn.execute("SELECT * FROM events"):
        data["events"].append({
            "id": row["id"],
            "kind": row["kind"],
            "created_at": row["created_at"],
            "payload_json": row["payload_json"] or "{}"
        })
    
    conn.close()
    
    # Save export
    export_file = STORAGE_DIR / "migration-export.json"
    with open(export_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Exported {len(data['projects'])} projects, {len(data['tasks'])} tasks, {len(data['events'])} events")
    print(f"Saved to {export_file}")
    return data


if __name__ == "__main__":
    export_sqlite_data()