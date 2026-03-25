# Examples — Self-Reflection

## Example 1 — Writing Task

```text
CONTEXT: Drafting stakeholder email
INTENT: Clear update with low-friction ask and fast decision path
OUTCOME: Technically accurate, but too dense and back-loaded
GAP: Reader would need to work to find the decision needed
LESSON: Front-load decision and action request, then give background
ACTION: log to domains/communication.md
```

## Example 2 — UI Build

```text
CONTEXT: Building Flutter settings screen
INTENT: Clean, balanced UI ready for review
OUTCOME: Functional but spacing looked off and required rework
GAP: Layout quality was not checked before presentation
LESSON: Do one visual pass for spacing and alignment before showing user
ACTION: log to domains/flutter.md
```

## Example 3 — Incident Analysis

```text
CONTEXT: Privacy incident risk assessment
INTENT: Produce a defensible, regulator-aware assessment with clear next steps
OUTCOME: Analysis was accurate but missing a concise executive summary
GAP: Decision-makers had to read the full detail to get the conclusion
LESSON: Start incident assessments with a short conclusion block before the detailed analysis
ACTION: log to domains/privacy.md
```

## Example 4 — Research Task

```text
CONTEXT: Product recommendation research
INTENT: Identify the best options with current, verifiable evidence
OUTCOME: Good recommendations, but too much time spent on low-signal sources
GAP: Search path was broader than necessary
LESSON: Prioritize primary sources and only add secondary sources where they materially improve comparison
ACTION: log to corrections.md
```

## Example 5 — No Log Needed

```text
CONTEXT: One-line confirmation reply
INTENT: Acknowledge receipt
OUTCOME: Acknowledged clearly
GAP: None worth storing
LESSON: None
ACTION: none
```

## Example 6 — Bug Fix Recovery

```text
CONTEXT: Debugging API integration failure
INTENT: Restore working integration and explain root cause clearly
OUTCOME: Bug fixed, but root cause explanation came late in the response
GAP: User had the fix before the explanation, but not the decision context
LESSON: After a fix, state root cause in one sentence before the remediation steps
ACTION: log to domains/coding.md
```
