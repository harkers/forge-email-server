create extension if not exists pgcrypto;

create table if not exists cases (
    id uuid primary key default gen_random_uuid(),
    case_ref text not null unique,
    request_type text not null,
    title text not null,
    description text not null,
    submitted_by text not null,
    submitted_via text not null default 'web',
    urgency text not null default 'normal',
    business_area text,
    controller_name text,
    client_name text,
    deadline_at timestamptz,
    status text not null default 'submitted',
    confidentiality_level text not null default 'internal',
    contains_phi boolean not null default false,
    contains_special_category boolean not null default false,
    international_transfer boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    closed_at timestamptz
);

create index if not exists idx_cases_status on cases(status);
create index if not exists idx_cases_created_at on cases(created_at desc);
create index if not exists idx_cases_request_type on cases(request_type);

create table if not exists case_metadata (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references cases(id) on delete cascade,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_case_metadata_case_id on case_metadata(case_id);
create index if not exists idx_case_metadata_gin on case_metadata using gin (metadata);

create table if not exists tasks (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references cases(id) on delete cascade,
    parent_task_id uuid references tasks(id) on delete set null,
    task_type text not null,
    assigned_to text,
    workflow_name text not null,
    execution_target text not null,
    status text not null default 'queued',
    priority text not null default 'normal',
    queued_at timestamptz not null default now(),
    started_at timestamptz,
    finished_at timestamptz,
    due_at timestamptz,
    last_heartbeat_at timestamptz
);

create index if not exists idx_tasks_case_id on tasks(case_id);
create index if not exists idx_tasks_status on tasks(status);
create index if not exists idx_tasks_queued_at on tasks(queued_at desc);

create table if not exists task_events (
    id uuid primary key default gen_random_uuid(),
    task_id uuid references tasks(id) on delete cascade,
    case_id uuid not null references cases(id) on delete cascade,
    event_type text not null,
    event_at timestamptz not null default now(),
    actor_type text not null,
    actor_id text,
    summary text not null,
    commentary text,
    old_status text,
    new_status text,
    correlation_id text,
    payload_jsonb jsonb not null default '{}'::jsonb
);

create index if not exists idx_task_events_case_id on task_events(case_id);
create index if not exists idx_task_events_task_id on task_events(task_id);
create index if not exists idx_task_events_event_at on task_events(event_at desc);
create index if not exists idx_task_events_type on task_events(event_type);
create index if not exists idx_task_events_payload_gin on task_events using gin (payload_jsonb);

create table if not exists artefacts (
    id uuid primary key default gen_random_uuid(),
    case_id uuid not null references cases(id) on delete cascade,
    task_id uuid references tasks(id) on delete set null,
    artefact_type text not null,
    filename text not null,
    storage_path text not null,
    mime_type text not null,
    sha256 text not null,
    created_at timestamptz not null default now(),
    created_by text not null
);

create index if not exists idx_artefacts_case_id on artefacts(case_id);

create table if not exists access_audit (
    id uuid primary key default gen_random_uuid(),
    user_identity text not null,
    action text not null,
    object_type text not null,
    object_id text,
    event_at timestamptz not null default now(),
    source_ip inet,
    access_decision text not null,
    request_id text
);

create index if not exists idx_access_audit_event_at on access_audit(event_at desc);
create index if not exists idx_access_audit_identity on access_audit(user_identity);

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_cases_updated_at on cases;
create trigger trg_cases_updated_at
before update on cases
for each row execute function set_updated_at();
