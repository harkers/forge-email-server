# Reviewer Agent Examples

## Good review finding

```text
Severity: medium
File: web/src/pages/settings.tsx
Finding: Save button now calls the new endpoint, but error handling does not surface failed responses to the user.
Evidence: catch block logs to console only.
Recommendation: show a visible error state or notice on non-2xx responses.
```

## Weak review finding

```text
This code feels a bit fragile.
```

Reason it is weak:
- no file
- no evidence
- no actionable fix
