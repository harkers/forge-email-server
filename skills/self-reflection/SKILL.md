---
name: self-reflection
description: Post-task evaluation skill for comparing outcome vs intent, identifying quality gaps, and routing reusable lessons into self-improvement memory. Use after meaningful multi-step work, after user feedback, after fixing a bug or mistake, after rework, or when the result could clearly have been better. Not for trivial acknowledgements or routine one-liners.
---

# Self-Reflection

Use this skill as the evaluation layer after meaningful work.

## Core role
This skill:
- reflects briefly on completed work
- compares outcome vs intent
- identifies gaps and lessons
- decides whether the lesson is reusable
- routes reusable lessons to the self-improvement process

This skill does **not** own long-term memory.
It nominates lessons; self-improvement stores and promotes them.

## Reflection loop
After significant work, evaluate:
1. Did the result meet the original intent?
2. What was weak, inefficient, unclear, missing, or avoidably risky?
3. Is the lesson reusable?
4. What is the narrowest useful scope for the lesson?

## Reflection output format
Use:

```text
CONTEXT: [task type]
INTENT: [what success should have looked like]
OUTCOME: [what actually happened]
GAP: [difference between intent and outcome]
LESSON: [what to do differently next time]
ACTION: [none | log to corrections/general learning | log to domain/project-specific learning]
```

Keep it concise, evidence-based, and action-oriented.

## Log only when
Log when at least one is true:
- the lesson is likely to recur
- it would improve future execution
- it explains rework or repeated friction
- it identifies a systematic weakness
- it changes how similar tasks should be handled next time

Do not log:
- emotional reactions
- vague self-criticism
- one-off details with no reuse value
- speculative lessons without evidence
- generic praise with no behavioral takeaway

## Default triggers
Always reflect after:
- completing a multi-step task
- a failed attempt followed by recovery
- fixing a bug or mistake
- explicit user feedback
- output that required meaningful rework before delivery

Reflect when noticed internally:
- response drifted from user intent
- answer was technically right but badly structured
- too much or too little detail was given
- assumptions had to be corrected mid-task
- a better path became obvious after completion

Do not reflect after:
- trivial confirmations
- simple acknowledgements
- low-value housekeeping
- purely mechanical actions with no quality decision involved

## Scope routing rule
Route the lesson to the narrowest useful scope.
- one-off / trivial → none
- repeated general issue → general correction / learning
- domain-specific lesson → domain-level learning
- project-specific lesson → project/workspace learning

Default to narrower scope when unsure.

## Integration rule
When a reusable lesson exists, hand it to the self-improvement workflow rather than promoting it directly into hot or global memory.

## References
Read these as needed:
- `references/setup.md` — original setup guidance
- `references/examples.md` — reflection examples
- `references/reflection-template.md` — template notes
- `references/routing.md` — scope routing rules
- `references/integration.md` — relationship to self-improvement
