# ForgeDiscord Implementation Notes

## MVP Intent
ForgeDiscord MVP is intentionally narrow:
- one dev server
- one bot
- three workflows
- thread-per-request
- intake + routing + status + approvals + audit

## Initial Workflows
- privacy incident intake
- vendor assessment intake
- general project intake

## Route Config Principle
Treat routing as configuration, not scattered conditionals.

## Job ID Pattern
Suggested:
- `INC-0001`
- `VEN-0001`
- `JOB-0001`

## Runtime Principle
Discord receives and coordinates.
OpenClaw executes.

## Suggested First Code Targets
- command registry
- modal schemas
- thread creation service
- route lookup service
- audit event writer
