# Dispatch Template

Use this template when assigning a bounded unit of work to a worker agent.

```text
You own one bounded work unit.

WORK ID: <id>
GOAL: <one-sentence goal>
TASK TYPE: <build|fix|review|investigate|deploy|document|migrate|plan>

ALLOWED SCOPE:
- <paths/systems>

FORBIDDEN:
- <paths/systems/actions>

REQUIRED OUTPUTS:
- <artifact>
- <artifact>

REQUIRED VALIDATION EVIDENCE:
- <command/check>
- <command/check>

STOP CONDITIONS:
- stop if scope needs to expand
- stop if required dependency is missing
- stop if action becomes destructive or external

COMPLETION FORMAT:
Return a handoff packet with:
- summary
- scope touched
- artifacts
- validation evidence
- open risks
- next recommended action

Do not report success without evidence.
If blocked or uncertain, say so clearly.
```

## Tightening pass

If a worker returns an ambiguous result, re-dispatch with:
- narrower scope
- explicit file or service targets
- explicit proof requirements
- a ban on speculative success language
