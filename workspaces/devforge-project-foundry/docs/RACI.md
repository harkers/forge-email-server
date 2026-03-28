# DevForge: Project Foundry
## Human Governance RACI

Status: Planning  
Date: 2026-03-28

Legend:
- **R** Responsible
- **A** Accountable
- **C** Consulted
- **I** Informed

This RACI covers the human governance layer only.
It does not try to model all AI operating roles as if they were human staff.

| Activity | Executive Sponsor / Human Authority | Product Decision Owner | Governance Approval Owner | Privacy Approval Owner | Security Approval Owner | Release Approval Owner |
|---|---|---|---|---|---|---|
| Approve project concept | A | R | C | I | I | I |
| Approve charter and scope | A | R | C | I | I | I |
| Approve governance gate model | I | C | A/R | C | C | I |
| Approve privacy position where needed | I | C | C | A/R | C | I |
| Approve security-sensitive position where needed | I | C | C | C | A/R | I |
| Approve MVP roadmap | A | R | C | C | C | I |
| Approve repo bootstrap start | A | R | C | C | C | I |
| Approve release or equivalent gated transition | I | C | C | C | C | A/R |
| Escalation decision on major ambiguity or risk | A | R | C | C | C | C |

## Note

Detailed AI operating role routing belongs in `AGENT_DIRECTORY.md`, `SKILL_ROLE_MAPPING.md`, and `V1_ROLE_STACK.md`.
