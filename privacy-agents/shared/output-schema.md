# Standard Output Schema

All privacy agents should produce outputs using this structure where applicable.

## Output structure

- **task_type**
- **status**
- **confidence_level**
- **facts_identified**
- **assumptions**
- **missing_information**
- **key_risks**
- **regulatory_considerations**
- **analysis**
- **recommended_actions**
- **escalation_required**
- **draft_output**
- **audit_log_summary**

## Rules

- Separate confirmed facts from unconfirmed claims.
- State assumptions explicitly.
- If evidence is insufficient, say so plainly.
- Do not imply that a legal conclusion is final unless explicitly instructed and authorised.
- Where applicable, include deadlines, owners, dependencies, and approval gates.

## Confidence scale

- **High** — material facts are well supported; limited ambiguity
- **Medium** — some ambiguity or missing inputs; recommendation is still useful
- **Low** — significant uncertainty; further evidence required before relying on conclusions
