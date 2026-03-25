import os
import time
import uuid
from psycopg.types.json import Json
from .db import get_db

POLL_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "8"))

def fetch_one_queued_task(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, case_id, task_type, workflow_name, execution_target, status
            from tasks
            where status = 'queued'
            order by queued_at asc
            limit 1
            for update skip locked
            """
        )
        return cur.fetchone()

def append_event(conn, *, task_id, case_id, event_type, actor_type, actor_id, summary, commentary, old_status=None, new_status=None, payload=None, correlation_id=None):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into task_events (
                task_id, case_id, event_type, actor_type, actor_id, summary, commentary,
                old_status, new_status, correlation_id, payload_jsonb
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (task_id, case_id, event_type, actor_type, actor_id, summary, commentary, old_status, new_status, correlation_id, Json(payload or {})),
        )

def process_once():
    with get_db() as conn:
        task = fetch_one_queued_task(conn)
        if not task:
            conn.commit()
            return False

        correlation_id = str(uuid.uuid4())

        with conn.cursor() as cur:
            cur.execute("update tasks set status = 'running', started_at = now(), last_heartbeat_at = now() where id = %s", (task["id"],))

        append_event(
            conn,
            task_id=task["id"],
            case_id=task["case_id"],
            event_type="worker_started",
            actor_type="worker",
            actor_id="privacy-intake-worker",
            summary="Worker started triage task.",
            commentary="Background worker picked up the queued task and began automated triage commentary generation.",
            old_status="queued",
            new_status="running",
            correlation_id=correlation_id,
            payload={"workflow_name": task["workflow_name"], "execution_target": task["execution_target"]},
        )

        time.sleep(1)

        append_event(
            conn,
            task_id=task["id"],
            case_id=task["case_id"],
            event_type="commentary_added",
            actor_type="worker",
            actor_id="privacy-intake-worker",
            summary="Initial processing commentary recorded.",
            commentary="Case reviewed by the placeholder worker. In a live deployment this is where the handoff to your privacy skill or orchestration layer would be recorded in detail.",
            correlation_id=correlation_id,
            payload={"next_step": "handoff_to_privacy_skill"},
        )

        with conn.cursor() as cur:
            cur.execute("update tasks set status = 'succeeded', finished_at = now(), last_heartbeat_at = now() where id = %s", (task["id"],))
            cur.execute("update cases set status = 'triaged' where id = %s and status = 'submitted'", (task["case_id"],))

        append_event(
            conn,
            task_id=task["id"],
            case_id=task["case_id"],
            event_type="task_completed",
            actor_type="worker",
            actor_id="privacy-intake-worker",
            summary="Initial triage task completed.",
            commentary="Placeholder processing finished successfully. Replace this stub with actual routing into the privacy skill and append richer event payloads from the real workflow.",
            old_status="running",
            new_status="succeeded",
            correlation_id=correlation_id,
            payload={"result": "triage_complete"},
        )

        conn.commit()
        return True

def main():
    while True:
        did_work = process_once()
        if not did_work:
            time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
