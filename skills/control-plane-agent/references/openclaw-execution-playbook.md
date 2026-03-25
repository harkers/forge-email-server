# OpenClaw Execution Playbook

Use this playbook when implementing the control plane inside OpenClaw.

## Purpose

Map the control-plane pattern onto native OpenClaw tools and behaviors.

Use OpenClaw-native coordination first:
- `sessions_spawn` for isolated worker execution
- `sessions_send` for directed follow-up
- `sessions_history` for reviewing worker output when needed
- `sessions_yield` to wait for background completion events
- `subagents` only for intervention or steering, not for tight polling loops

Do not simulate OpenClaw orchestration with ad hoc shell background processes when native session tools fit the job.

## Core mapping

### manager role
Typical OpenClaw actions:
- classify work in the main session
- create a work packet in files if the task is multi-step or needs auditability
- spawn bounded worker sessions
- review completion events and artifacts
- verify results with repo/file/tool checks
- reroute, accept, or escalate

### worker role
Typical OpenClaw actions:
- run in isolated subagent sessions for bounded tasks
- work only in inherited workspace scope unless otherwise specified
- return structured handoff content in the completion message
- stop when scope expands beyond contract

## Recommended execution modes

### Fast bounded work
Use a single spawned subagent run when:
- work is small to medium
- one specialist owns the whole scope
- no persistent thread is needed

Recommended pattern:
- `sessions_spawn(mode="run", runtime="subagent")`
- include a tight task contract
- wait for pushed completion rather than polling in a loop

### Persistent specialist thread
Use a persistent spawned session when:
- a specialist will be reused repeatedly
- the workflow spans several turns
- you want stable continuity for one role

Recommended pattern:
- `sessions_spawn(mode="session", runtime="subagent")`
- label the session by role or workstream
- use `sessions_send` for follow-up dispatches

### ACP harness case
If the user explicitly wants Codex/Claude Code/Gemini-style ACP work:
- use `sessions_spawn(runtime="acp")`
- set `agentId` explicitly unless a default exists
- on Discord, prefer `thread: true` and `mode: "session"`

Do not reroute ACP intent through local shell processes.

## Dispatch pattern

For each worker launch:
1. choose the role stub from `agent-prompt-stubs.md`
2. attach the task-specific contract
3. define allowed scope
4. define forbidden scope
5. define required outputs
6. define required validation evidence
7. specify completion format

Good `sessions_spawn` payload ingredients:
- one-sentence goal
- exact file/service scope
- explicit stop conditions
- evidence-first completion rules
- handoff packet format

## Verification pattern in OpenClaw

After a worker reports completion:
1. inspect artifacts or changed files directly
2. run narrow validation commands with `exec` when needed
3. inspect git state if repo-backed
4. compare claim vs evidence
5. decide accept / reject / reroute / escalate

Useful checks:
- `git status --short`
- `git log --oneline --max-count=<n>`
- targeted file reads
- build/test commands scoped to the affected area
- service health checks

Do not accept completion solely because:
- the subagent says it is done
- a commit exists
- a document was created

## Handoff storage pattern

Use file-backed work packets when:
- the task spans multiple worker steps
- auditability matters
- another session may need to resume later
- you want replayable routing state

Suggested paths:
- `state/tasks/<work-id>.md` or `.json`
- `artifacts/<work-id>/`
- optional queue-like folders if building a stronger orchestration layer:
  - `queue/inbox/`
  - `queue/claimed/`
  - `queue/done/`
  - `queue/failed/`

## On-demand oversight

Use these tools sparingly:

### `sessions_history`
Use when:
- the completion event is not enough
- you need exact prior worker reasoning or outputs
- you are auditing a questionable handoff

### `subagents(action="steer")`
Use when:
- the worker drifted
- you need to tighten scope
- you need to stop speculative work and refocus it

### `subagents(action="kill")`
Use when:
- the worker is clearly off-track
- the task became invalid
- a risky or destructive path is emerging

Do not repeatedly poll session lists or subagent lists for ordinary progress.

## Suggested manager workflow in OpenClaw

### Pattern A: build/fix
1. manager classifies request
2. manager writes or defines work packet
3. manager spawns coding-worker
4. coding-worker returns handoff
5. manager verifies with repo/file/build checks
6. manager optionally spawns reviewer
7. manager accepts or returns defects

### Pattern B: investigate -> fix
1. manager spawns investigator
2. investigator returns diagnosis + confidence
3. manager spawns coding-worker with bounded fix scope
4. manager verifies
5. manager routes to reviewer if needed

### Pattern C: research -> draft
1. manager spawns researcher
2. researcher returns cited findings
3. manager spawns drafting agent
4. manager verifies draft against source findings
5. manager approves or revises

## Prompting conventions for OpenClaw workers

Prefer this shape:

```text
ROLE STUB:
<insert role stub>

WORK CONTRACT:
- Goal:
- Allowed scope:
- Forbidden scope:
- Required outputs:
- Required validation evidence:
- Stop conditions:

COMPLETION FORMAT:
Return a handoff packet with summary, scope touched, artifacts, validation evidence, open risks, and next recommended action.
```

## Failure handling

If a worker result is weak:
- do one tightening pass with narrower scope and explicit proof requirements
- if still weak, reject and escalate or reroute

If a command or environment assumption fails unexpectedly:
- verify directly
- adjust the work packet
- avoid reporting success until evidence is restored

## Main rule

In OpenClaw, the manager should behave like an evidence-driven dispatcher and verifier, not like a narrator of worker optimism.
