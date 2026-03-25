# Security Reviewer Examples

## Good finding
- REST write endpoint checks authentication but not capability.
- Risk: authenticated low-privilege users may gain write access.
- Severity: high.
- Recommendation: require explicit capability check in permission callback.

## Review focus
- auth/authz
- secret handling
- unsafe input
- trust boundaries
- production exposure
