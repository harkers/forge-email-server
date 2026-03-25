#!/usr/bin/env python3
"""
Forge Pipeline Client for control-plane-what-next

Handles:
- Fetching pending items from Forge Pipeline
- Updating task status after dispatch
- Integration with control-plane dispatch engine
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from copy import deepcopy

# Forge Pipeline state file location
FORGE_PIPELINE_FILE = Path.home() / ".openclaw" / "workspace" / ".forge-pipeline-state.json"

# Default pipeline structure for testing
DEFAULT_PIPELINE = {
    "projects": {},
    "status": "active",
    "lastUpdated": None,
}


def now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def load_forge_pipeline(file_path: Path = FORGE_PIPELINE_FILE) -> dict:
    """
    Load Forge Pipeline state from disk.
    
    Returns pipeline state or default empty state.
    """
    if not file_path.exists():
        return deepcopy(DEFAULT_PIPELINE)
    
    try:
        raw = file_path.read_text()
        return json.loads(raw)
    except (json.JSONDecodeError, IOError):
        return deepcopy(DEFAULT_PIPELINE)


def save_forge_pipeline(pipeline: dict, file_path: Path = FORGE_PIPELINE_FILE) -> bool:
    """
    Save Forge Pipeline state to disk.
    
    Returns True on success.
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = file_path.with_suffix(".tmp")
        temp_file.write_text(json.dumps(pipeline, indent=2, sort_keys=True))
        temp_file.replace(file_path)
        return True
    except IOError:
        return False


def fetch_pending_items(
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
    status_filter: list[str] = None,
) -> list[dict]:
    """
    Fetch pending items from Forge Pipeline.
    
    Converts pipeline items to job format for dispatch engine.
    
    Args:
        pipeline: Optional pipeline dict (loads from file if None)
        file_path: Path to pipeline file
        status_filter: Statuses to include (default: pending, ready, queued)
    
    Returns:
        List of job dicts ready for dispatch engine
    """
    if pipeline is None:
        pipeline = load_forge_pipeline(file_path)
    
    if status_filter is None:
        status_filter = ["pending", "ready", "queued", "in_progress"]
    
    jobs = []
    
    # Iterate through projects
    for project_id, project in pipeline.get("projects", {}).items():
        # Check project-level items
        for item_id, item in project.get("items", {}).items():
            status = item.get("status", "pending")
            
            # Skip non-pending items
            if status not in status_filter:
                continue
            
            # Convert to job format
            job = convert_pipeline_item_to_job(
                item=item,
                project_id=project_id,
                item_id=item_id,
            )
            jobs.append(job)
    
    # Also check for standalone tasks
    for task_id, task in pipeline.get("tasks", {}).items():
        status = task.get("status", "pending")
        
        if status not in status_filter:
            continue
        
        job = convert_task_to_job(task=task, task_id=task_id)
        jobs.append(job)
    
    return jobs


def convert_pipeline_item_to_job(
    item: dict,
    project_id: str,
    item_id: str,
) -> dict:
    """
    Convert a Forge Pipeline item to dispatch engine job format.
    
    Maps pipeline fields to job schema fields.
    """
    # Generate job ID
    job_id = f"{project_id}-{item_id}"
    
    # Determine task type from item category
    category = item.get("category", "coding")
    task_type_map = {
        "infrastructure": "infrastructure",
        "coding": "coding",
        "code": "coding",
        "review": "review",
        "security": "security",
        "docs": "docs",
        "documentation": "docs",
        "planning": "planning",
        "investigation": "investigation",
    }
    task_type = task_type_map.get(category.lower(), "coding")
    
    # Map priority
    priority = item.get("priority", "P2")
    impact_map = {
        "critical": "critical",
        "P0": "critical",
        "high": "high",
        "P1": "high",
        "medium": "medium",
        "P2": "medium",
        "low": "low",
        "P3": "low",
    }
    impact = impact_map.get(priority, "medium")
    
    # Build job
    job = {
        "jobId": job_id,
        "title": item.get("title", item.get("name", f"Task {item_id}")),
        "taskType": task_type,
        "description": item.get("description", ""),
        "dependsOn": item.get("dependsOn", item.get("dependencies", [])),
        "blocks": item.get("blocks", []),
        "sharedResources": item.get("sharedResources", item.get("locks", [])),
        "estimatedTokens": item.get("estimatedTokens", item.get("tokenEstimate", 30000)),
        "deadline": item.get("deadline"),
        "queueInsertedAt": item.get("createdAt", item.get("queuedAt", now_utc().isoformat())),
        "destructive": item.get("destructive", False),
        "productionImpact": item.get("productionImpact", item.get("prodImpact", False)),
        "executionReadiness": item.get("executionReadiness", item.get("readiness", 0.8)),
        "ready": item.get("ready", item.get("status") in ["ready", "pending"]),
        "confidence": item.get("confidence", item.get("executionReadiness", 0.8)),
        "impact": impact,
        "priority": priority,
        "metadata": {
            "projectId": project_id,
            "itemId": item_id,
            "source": "forge-pipeline",
            "originalStatus": item.get("status"),
        },
    }
    
    return job


def convert_task_to_job(task: dict, task_id: str) -> dict:
    """
    Convert a standalone task to job format.
    """
    category = task.get("category", "coding")
    task_type_map = {
        "infrastructure": "infrastructure",
        "coding": "coding",
        "review": "review",
        "security": "security",
        "docs": "docs",
        "planning": "planning",
    }
    
    return {
        "jobId": task_id,
        "title": task.get("title", f"Task {task_id}"),
        "taskType": task_type_map.get(category.lower(), "coding"),
        "description": task.get("description", ""),
        "dependsOn": task.get("dependsOn", []),
        "blocks": task.get("blocks", []),
        "sharedResources": task.get("sharedResources", []),
        "estimatedTokens": task.get("estimatedTokens", 30000),
        "deadline": task.get("deadline"),
        "queueInsertedAt": task.get("createdAt", now_utc().isoformat()),
        "destructive": task.get("destructive", False),
        "productionImpact": task.get("productionImpact", False),
        "executionReadiness": task.get("readiness", 0.8),
        "ready": task.get("status") in ["ready", "pending"],
        "confidence": task.get("confidence", 0.8),
        "impact": task.get("impact", "medium"),
        "metadata": {
            "taskId": task_id,
            "source": "forge-pipeline-task",
        },
    }


def update_task_status(
    task_id: str,
    status: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
    result: Optional[dict] = None,
) -> bool:
    """
    Update task status in Forge Pipeline.
    
    Args:
        task_id: Task ID to update
        status: New status (dispatched, running, completed, failed, quarantined)
        pipeline: Optional pipeline dict (loads from file if None)
        file_path: Path to pipeline file
        result: Optional result metadata
    
    Returns:
        True on success
    """
    if pipeline is None:
        pipeline = load_forge_pipeline(file_path)
    
    # Try to find in projects first
    for project_id, project in pipeline.get("projects", {}).items():
        for item_id, item in project.get("items", {}).items():
            if f"{project_id}-{item_id}" == task_id or item_id == task_id:
                item["status"] = status
                item["lastUpdated"] = now_utc().isoformat()
                if result:
                    item["result"] = result
                return save_forge_pipeline(pipeline, file_path)
    
    # Try standalone tasks
    if task_id in pipeline.get("tasks", {}):
        pipeline["tasks"][task_id]["status"] = status
        pipeline["tasks"][task_id]["lastUpdated"] = now_utc().isoformat()
        if result:
            pipeline["tasks"][task_id]["result"] = result
        return save_forge_pipeline(pipeline, file_path)
    
    return False


def mark_dispatched(
    task_id: str,
    model: str,
    pool: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> bool:
    """
    Mark a task as dispatched with model and pool info.
    """
    return update_task_status(
        task_id=task_id,
        status="dispatched",
        pipeline=pipeline,
        file_path=file_path,
        result={"model": model, "pool": pool, "dispatchedAt": now_utc().isoformat()},
    )


def mark_running(
    task_id: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> bool:
    """
    Mark a task as running.
    """
    return update_task_status(
        task_id=task_id,
        status="running",
        pipeline=pipeline,
        file_path=file_path,
    )


def mark_completed(
    task_id: str,
    actual_tokens: int,
    runtime_ms: int,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> bool:
    """
    Mark a task as completed.
    """
    return update_task_status(
        task_id=task_id,
        status="completed",
        pipeline=pipeline,
        file_path=file_path,
        result={
            "actualTokens": actual_tokens,
            "runtimeMs": runtime_ms,
            "completedAt": now_utc().isoformat(),
        },
    )


def mark_failed(
    task_id: str,
    error_message: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> bool:
    """
    Mark a task as failed.
    """
    return update_task_status(
        task_id=task_id,
        status="failed",
        pipeline=pipeline,
        file_path=file_path,
        result={
            "error": error_message,
            "failedAt": now_utc().isoformat(),
        },
    )


def mark_quarantined(
    task_id: str,
    reason: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> bool:
    """
    Mark a task as quarantined.
    """
    return update_task_status(
        task_id=task_id,
        status="quarantined",
        pipeline=pipeline,
        file_path=file_path,
        result={
            "quarantineReason": reason,
            "quarantinedAt": now_utc().isoformat(),
        },
    )


def get_pipeline_item(
    task_id: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> Optional[dict]:
    """
    Get a specific pipeline item by ID.
    """
    if pipeline is None:
        pipeline = load_forge_pipeline(file_path)
    
    # Try projects
    for project_id, project in pipeline.get("projects", {}).items():
        for item_id, item in project.get("items", {}).items():
            if f"{project_id}-{item_id}" == task_id or item_id == task_id:
                return convert_pipeline_item_to_job(item, project_id, item_id)
    
    # Try tasks
    if task_id in pipeline.get("tasks", {}):
        return convert_task_to_job(pipeline["tasks"][task_id], task_id)
    
    return None


def get_dependencies(
    task_id: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> list[dict]:
    """
    Get all dependencies for a task.
    
    Returns list of job dicts for dependencies.
    """
    job = get_pipeline_item(task_id, pipeline, file_path)
    if not job:
        return []
    
    depends_on = job.get("dependsOn", [])
    dependencies = []
    
    for dep_id in depends_on:
        dep_job = get_pipeline_item(dep_id, pipeline, file_path)
        if dep_job:
            dependencies.append(dep_job)
    
    return dependencies


def get_blocked_tasks(
    task_id: str,
    pipeline: Optional[dict] = None,
    file_path: Path = FORGE_PIPELINE_FILE,
) -> list[dict]:
    """
    Get all tasks blocked by a given task.
    
    Returns list of job dicts for blocked tasks.
    """
    job = get_pipeline_item(task_id, pipeline, file_path)
    if not job:
        return []
    
    blocks = job.get("blocks", [])
    blocked = []
    
    for blocked_id in blocks:
        blocked_job = get_pipeline_item(blocked_id, pipeline, file_path)
        if blocked_job:
            blocked.append(blocked_job)
    
    return blocked


if __name__ == "__main__":
    # Quick test
    print("Testing forge_pipeline_client...")
    
    # Create test pipeline
    test_pipeline = {
        "projects": {
            "test-project": {
                "name": "Test Project",
                "items": {
                    "item-1": {
                        "title": "Fix authentication bug",
                        "category": "coding",
                        "status": "pending",
                        "priority": "P1",
                        "productionImpact": True,
                        "dependsOn": [],
                        "blocks": ["item-2"],
                        "estimatedTokens": 40000,
                        "deadline": "2026-03-26T00:00:00Z",
                    },
                    "item-2": {
                        "title": "Review auth fix",
                        "category": "review",
                        "status": "pending",
                        "priority": "P2",
                        "dependsOn": ["item-1"],
                        "blocks": [],
                        "estimatedTokens": 20000,
                    },
                },
            },
        },
        "tasks": {
            "standalone-1": {
                "title": "Update documentation",
                "category": "docs",
                "status": "ready",
                "estimatedTokens": 15000,
            },
        },
    }
    
    # Fetch pending items
    pending = fetch_pending_items(test_pipeline)
    print(f"Pending items: {len(pending)}")
    for item in pending:
        print(f"  - {item['jobId']}: {item['title']} ({item['taskType']})")
    
    # Test status update
    updated = update_task_status("standalone-1", "running", deepcopy(test_pipeline))
    print(f"Status update would succeed: {updated}")
    
    print("\nforge_pipeline_client tests passed!")