# Work State Template

Use this lightweight state model for multi-step orchestrated work.

## Markdown version

```markdown
# Work Item: <work_id>

- Goal: <goal>
- Type: <build|fix|review|investigate|deploy|document|migrate|plan>
- Status: <queued|running|needs_review|blocked|accepted|rejected|done>
- Current owner: <agent/role>
- Priority: <low|normal|high|critical>

## Scope
- Allowed:
- Forbidden:

## Dependencies
- <dependency>

## Artifacts
- <artifact>

## Last verification
- Result:
- Evidence:
- Gaps:

## Next action
- <next step>
```

## JSON version

```json
{
  "work_id": "example-001",
  "goal": "",
  "type": "build",
  "status": "queued",
  "current_owner": "",
  "priority": "normal",
  "scope": {
    "allowed": [],
    "forbidden": []
  },
  "dependencies": [],
  "artifacts": [],
  "last_verification": {
    "result": "not_run",
    "evidence": [],
    "gaps": []
  },
  "next_action": ""
}
```

## Notes
- Keep the state file small.
- Update it at ownership changes and verification gates.
- Prefer one work file per meaningful tracked unit.
