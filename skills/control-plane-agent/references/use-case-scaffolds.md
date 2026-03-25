# Use-Case Scaffolds

Use these scaffolds to stand up agent sets for common workflow families.

## 1. Coding / product delivery scaffold

Recommended agents:
- manager
- planner
- coding-worker
- reviewer
- architecture-reviewer
- security-reviewer
- deployer
- documentation-writer

Routing pattern:
- manager -> planner -> coding-worker -> reviewer -> manager
- add architecture-reviewer when boundaries may drift
- add security-reviewer when auth, exposure, secrets, or untrusted input are involved
- add deployer only after acceptance
- add documentation-writer when implementation changes need docs/runbooks/spec updates

## 2. Investigation / debugging scaffold

Recommended agents:
- manager
- investigator
- coding-worker
- reviewer
- deployer

Routing pattern:
- manager -> investigator -> coding-worker -> reviewer -> manager
- use deployer only if fix must be released

## 3. Research / advisory scaffold

Recommended agents:
- manager
- researcher
- domain specialist if available
- drafting

Routing pattern:
- manager -> researcher -> domain specialist or drafting -> manager

## 4. Security / risk scaffold

Recommended agents:
- manager
- investigator
- security-reviewer
- drafting

Routing pattern:
- manager -> investigator -> security-reviewer -> drafting -> manager

## 5. Planning / architecture scaffold

Recommended agents:
- manager
- planner
- architecture-reviewer
- documentation-writer

Routing pattern:
- manager -> planner -> architecture-reviewer -> documentation-writer -> manager

## 6. Portfolio / governance scaffold

Recommended agents:
- manager
- planner
- documentation-writer
- forge-pipeline-sync specialist or equivalent project-tracking worker

Routing pattern:
- manager -> planner/documentation-writer -> portfolio sync -> manager

## 7. Privacy / compliance scaffold

Recommended agents:
- manager
- privacy-incident
- vendor-assessor
- researcher
- drafting

Routing pattern:
- manager -> privacy-incident or vendor-assessor -> researcher if external evidence needed -> drafting -> manager

## Minimal starter set

If starting small, use only:
- manager
- coding-worker
- reviewer
- investigator
- drafting

Add specialists only when repeated workload or risk justifies them.

## Expansion rule

Create a new specialist when all are true:
- the task family recurs
- the evaluation criteria are stable
- the scope boundary can be described clearly
- routing to the specialist reduces ambiguity or risk

Do not create specialists just because a topic sounds important.
