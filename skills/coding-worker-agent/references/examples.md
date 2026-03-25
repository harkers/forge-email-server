# Coding Worker Examples

## Good completion

```text
SUMMARY:
- Added settings route and wired UI save action.

SCOPE TOUCHED:
- api/settings.py
- web/src/pages/settings.tsx

ARTIFACTS:
- commit: abc1234

VALIDATION EVIDENCE:
- pytest tests/api/test_settings.py passed
- npm run build passed

OPEN RISKS:
- no browser-level verification yet

NEXT RECOMMENDED ACTION:
- hand to reviewer
```

## Bad completion

```text
Done. I fixed it and committed the changes.
```

Reason it is bad:
- no evidence
- no scope list
- no validation truthfulness
