# Security Hardening Notes

## Keep this app separate
Do not merge it into the WordPress path.

## Network exposure
- No public host port for postgres
- Prefer no public host port for app
- Publish only via Cloudflare Tunnel
- Restrict local test bind to `127.0.0.1`

## Authentication
- Use Cloudflare Access as the first gate
- Allow only your identity for initial deployment
- Add service tokens only if machine-to-machine workflows need them

## Secrets
- Store secrets in `.env`
- Use file permissions `600` where practical
- Do not commit real secrets to git

## Database least privilege
- separate database
- separate application user
- no superuser for the app
- grant only required privileges

## Logging and audit
- application logs should omit secret values
- task event payloads should avoid raw secrets
- access audit should record read and admin actions

## Attachments
If enabled later:
- validate MIME type and extension
- virus scan where practical
- enforce size limits
- store outside the app image
- hash each upload

## Operational controls
- back up postgres
- test restore path
- use explicit migration files
- add health checks
- pin container image versions for stability
