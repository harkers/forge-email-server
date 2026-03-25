import uuid
from psycopg.types.json import Json
from .db import get_db

def next_case_ref(conn):
    with conn.cursor() as cur:
        cur.execute("select count(*)::int as count from cases;")
        count = cur.fetchone()["count"]
        return f"PI-{count + 1:04d}"

def create_case(payload: dict):
    with get_db() as conn:
        case_ref = next_case_ref(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into cases (
                    case_ref, request_type, title, description, submitted_by, urgency,
                    business_area, controller_name, client_name, deadline_at,
                    confidentiality_level, contains_phi, contains_special_category, international_transfer
                )
                values (
                    %(case_ref)s, %(request_type)s, %(title)s, %(description)s, %(submitted_by)s, %(urgency)s,
                    %(business_area)s, %(controller_name)s, %(client_name)s, %(deadline_at)s,
                    %(confidentiality_level)s, %(contains_phi)s, %(contains_special_category)s, %(international_transfer)s
                )
                returning id, case_ref;
                """,
                {**payload, "case_ref": case_ref},
            )
            case_row = cur.fetchone()

            cur.execute(
                "insert into case_metadata (case_id, metadata) values (%s, %s)",
                (case_row["id"], Json(payload.get("metadata", {}))),
            )

            cur.execute(
                """
                insert into tasks (case_id, task_type, workflow_name, execution_target, status, priority)
                values (%s, %s, %s, %s, %s, %s)
                returning id;
                """,
                (
                    case_row["id"],
                    "triage",
                    "privacy-intake-default",
                    "privacy-skill",
                    "queued",
                    payload["urgency"],
                ),
            )
            task_row = cur.fetchone()

            correlation_id = str(uuid.uuid4())

            cur.execute(
                """
                insert into task_events (
                    task_id, case_id, event_type, actor_type, actor_id,
                    summary, commentary, new_status, correlation_id, payload_jsonb
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    task_row["id"],
                    case_row["id"],
                    "case_created",
                    "system",
                    "web-intake",
                    "Case created from authenticated web intake.",
                    "Submission validated at application boundary and persisted to PostgreSQL. Initial triage task created.",
                    "queued",
                    correlation_id,
                    Json({"request_type": payload["request_type"], "submitted_by": payload["submitted_by"]}),
                ),
            )

            conn.commit()
            return {"id": case_row["id"], "case_ref": case_row["case_ref"], "task_id": task_row["id"]}

def list_cases():
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select id, case_ref, request_type, title, status, urgency, created_at
            from cases
            order by created_at desc
            limit 100
            """
        )
        return cur.fetchall()

def get_case(case_id: str):
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("select * from cases where id = %s", (case_id,))
        case_row = cur.fetchone()
        cur.execute("select metadata from case_metadata where case_id = %s order by created_at asc limit 1", (case_id,))
        meta_row = cur.fetchone()
        cur.execute(
            """
            select id, task_type, workflow_name, execution_target, status, priority, queued_at, started_at, finished_at
            from tasks where case_id = %s order by queued_at asc
            """,
            (case_id,),
        )
        tasks = cur.fetchall()
        cur.execute(
            """
            select event_at, event_type, actor_type, actor_id, summary, commentary, old_status, new_status, correlation_id, payload_jsonb
            from task_events
            where case_id = %s
            order by event_at asc
            """,
            (case_id,),
        )
        events = cur.fetchall()
        return {"case": case_row, "metadata": meta_row["metadata"] if meta_row else {}, "tasks": tasks, "events": events}
