# Handoff Packet

Use this packet whenever a worker agent finishes a bounded unit of work.

## Required format

```text
WORK ID: <id>
TASK TYPE: <build|fix|review|investigate|deploy|document|migrate|plan>
OWNER: <agent or role>
STATUS: <proposed_done|blocked|failed|needs_review>

SUMMARY:
- what was attempted
- what changed

SCOPE TOUCHED:
- files
- services
- systems

ARTIFACTS:
- commits
- files
- URLs
- builds
- reports

VALIDATION EVIDENCE:
- commands run
- tests/build results
- health checks
- screenshots
- feature markers

OPEN RISKS:
- unresolved issues
- assumptions
- missing verification

NEXT RECOMMENDED ACTION:
- close | hand to <role> | retry | escalate
```

## Rules
- Do not say "done" without evidence.
- Distinguish verified evidence from expectation.
- Include missing validation explicitly.
- Keep scope specific.
- Name the next owner when recommending handoff.

## Minimal example

```text
WORK ID: fw-014
TASK TYPE: build
OWNER: wordpress-worker
STATUS: proposed_done

SUMMARY:
- Added admin submenu registration for Cache Forge under Form Forge top-level menu.
- Updated slug wiring to remove orphan parent slug.

SCOPE TOUCHED:
- plugins/cache-forge/cache-forge.php
- plugins/form-forge/form-forge.php

ARTIFACTS:
- commit: abc1234

VALIDATION EVIDENCE:
- php -l passed for both edited files
- grep confirms submenu parent slug now matches existing top-level slug

OPEN RISKS:
- not verified in a live WordPress instance

NEXT RECOMMENDED ACTION:
- hand to reviewer
```
