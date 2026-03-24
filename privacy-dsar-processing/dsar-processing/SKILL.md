---
name: dsar-processing
description: Manage data subject access request (DSAR) intake, scoping, search tracking, review, redaction planning, response drafting, and case closure. Use when handling privacy access requests, GDPR/UK GDPR subject access requests, or building a repeatable DSAR workflow in a workspace.
---

# DSAR Processing

Use this skill to run DSAR cases in a structured, auditable way.

## Workflow

1. Log the request receipt date and assign a case ID.
2. Confirm jurisdiction, legal basis, and response deadline.
3. Verify identity if needed before disclosure.
4. Clarify scope when the request is broad or ambiguous.
5. Identify systems, custodians, and repositories to search.
6. Record searches in a search log with dates, methods, and outcomes.
7. Preserve originals and separate raw source data from reviewed output.
8. Review collected material for third-party data, privilege, exemptions, and redactions.
9. Draft the response with a clear description of what was searched and what is being disclosed.
10. Record final disclosure decisions and closure notes.

## Working pattern

- Keep one folder per case under `requests/`.
- Treat `inbox/` as raw intake only.
- Treat `exports/` as reviewed output only.
- Write process decisions into notes rather than leaving them implicit.
- Prefer append-only audit notes over rewriting history.

## Minimum case files

For each case, maintain:

- `request.md`
- `identity-check.md`
- `scope.md`
- `search-log.md`
- `review-notes.md`
- `response.md`

## Script

Use `scripts/uk_gdpr_deadline.py <YYYY-MM-DD>` to calculate the standard one-month deadline and the outer extended deadline for UK GDPR cases.

## References

Read these when needed:

- `references/checklists.md` for the operational checklist
- `references/case-template.md` for the standard case file layout
- `references/uk-gdpr.md` for UK GDPR deadline tracking and response handling
