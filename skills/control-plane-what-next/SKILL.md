---
name: control-plane-what-next
description: "Determine the next priority work item after control-plane completes a task. Query Forge Pipeline for pending items, evaluate priority, and present auto-approve options. Use when control-plane finishes work and needs to know what to do next, or when user wants to set auto-approve windows."
---

# Control Plane: What Next

Determine the next priority work and manage auto-approve windows.

## Responsibilities
- Query Forge Pipeline for pending work items
- Evaluate priority based on urgency, dependencies, and impact
- Present next item with context (model, tokens, estimated effort)
- Manage auto-approve windows (time-based or job-count-based)
- Track token usage and model assignments per job

## Rules
- Always query Forge Pipeline before recommending work
- Respect auto-approve windows set by user
- Ask for approval outside auto-approve windows
- Track completed jobs against job-count windows
- Report token usage and model assignments after each job

## Auto-Approve Windows

Offer these options:
1. **Next 6 hours** — Auto-approve until timestamp
2. **Next 5 control-plane jobs** — Auto-approve next N jobs
3. **Next 12 hours** — Auto-approve until timestamp
4. **Next 24 hours** — Auto-approve until timestamp
5. **Next 72 hours** — Auto-approve until timestamp
6. **Until all jobs completed** — Auto-approve until pipeline empty

## Workflow

### After Control-Plane Completes Work

1. Query Forge Pipeline: `GET /api/tasks?status=pending`
2. Query Forge Pipeline: `GET /api/projects` for context
3. Evaluate priority using:
   - Project dependencies
   - Task urgency (due dates, blockers)
   - Impact (P0/P1/P2)
   - Resource availability (model, tokens)
4. Present next item with:
   - Work ID
   - Task type
   - Assigned model
   - Estimated tokens
   - Priority justification
5. Check auto-approve window:
   - If within window: proceed automatically
   - If outside window: ask for approval

### Setting Auto-Approve Window

Store in `~/.openclaw/workspace/.control-plane-auto-approve.json`:
```json
{
  "mode": "time" | "jobs" | "unlimited",
  "started": "2026-03-25T09:00:00Z",
  "expires": "2026-03-25T15:00:00Z" | null,
  "jobsRemaining": 5 | null,
  "completedJobs": []
}
```

### Checking Auto-Approve Status

1. Load auto-approve config
2. If `mode === "time"`: check if current time < expires
3. If `mode === "jobs"`: check if jobsRemaining > 0
4. If `mode === "unlimited"`: always approve until pipeline empty
5. If approved: proceed, decrement jobsRemaining if applicable

## Pipeline Integration

### Forge Pipeline Endpoints

```bash
# Get pending tasks
curl http://localhost:4174/api/tasks?status=pending

# Get all projects
curl http://localhost:4174/api/projects

# Get specific project
curl http://localhost:4174/api/projects/{id}

# Create task
curl -X POST http://localhost:4174/api/tasks -d '{"projectId": "...", "title": "..."}'

# Update task status
curl -X PATCH http://localhost:4174/api/tasks/{id} -d '{"status": "in_progress"}'
```

### Priority Evaluation

1. **P0 (Critical)** — Blocks other work, production down, security issue
2. **P1 (High)** — Important but not blocking, significant impact
3. **P2 (Medium)** — Should do soon, moderate impact
4. **P3 (Low)** — Nice to have, low impact

Evaluate based on:
- Dependencies (blocked by / blocking)
- Due dates
- Project health (red/yellow/green)
- Resource requirements (model, tokens, time)

## Output Format

### Next Item Report

```markdown
## What's Next

### Auto-Approve Status
- **Mode:** time | jobs | unlimited
- **Expires:** timestamp | "after N jobs" | "until pipeline empty"
- **Jobs remaining:** N | unlimited

### Next Priority Item

**Work ID:** {id}
**Task Type:** {type}
**Project:** {projectName}
**Priority:** P0/P1/P2/P3
**Model:** {model}
**Estimated tokens:** {tokens}

**Justification:**
- {reason 1}
- {reason 2}

**Scope:**
- {scope item 1}
- {scope item 2}

Proceed? [Auto-approved within window]
```

### After Job Completion

```markdown
## Job Complete

**Work ID:** {id}
**Task Type:** {type}
**Model:** {model}
**Tokens:** {in}k in / {out}k out
**Duration:** {duration}

**Result:**
- {outcome}

**Auto-approve remaining:** N jobs | time remaining
```

## References
- Read `references/priority-evaluation.md` for detailed priority rules
- Read `references/model-assignments.md` for model selection logic