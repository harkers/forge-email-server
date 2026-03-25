---
name: Self-Reflection
slug: self-reflection
version: 1.0.0
homepage: https://clawic.com/skills/self-reflection
description: "Post-task evaluation skill for comparing outcome vs intent, identifying quality gaps, and routing reusable lessons into self-improving memory. Use when (1) a multi-step task completes; (2) the user gives positive or negative feedback; (3) a bug or mistake is fixed; (4) the agent notices output could have been better; (5) the user explicitly installs or references the skill for the current task."
changelog: "Initial standalone release extracted from self-improving and expanded into a structured reflection workflow with scoped routing and storage decisions."
metadata: {"clawdbot":{"emoji":"🪞","requires":{"bins":[]},"os":["linux","darwin","win32"],"configPaths":["~/self-improving/"],"configPaths.optional":["./AGENTS.md","./SOUL.md"]}}
---

## When to Use

Use after meaningful work when there is an outcome worth evaluating. Reflection should be brief, evidence-based, and action-oriented.

Typical triggers:
- after completing a multi-step task
- after receiving user feedback
- after fixing a bug or mistake
- after reworking output before delivery
- when you notice the result could have been better

Do not use for trivial acknowledgements, one-line replies, or low-value routine actions with no meaningful outcome to compare.

## Architecture

This skill is the evaluation layer. It does not own long-term memory.

Flow:

```text
Task completes
→ reflect briefly
→ classify lesson
→ decide whether to store
→ hand reusable lesson to self-improving
```

Role split:
- `self-reflection` detects gaps and extracts lessons
- `self-improving` stores, tracks, promotes, or archives those lessons

## Quick Reference

| Topic | File |
|------|------|
| Setup guide | `setup.md` |
| Reflection examples | `examples.md` |
| Reflection template | `reflection-template.md` |
| Routing and storage rules | `routing.md` |
| Suggested self-improving integration | `integration.md` |

## Requirements

- No credentials required
- No extra binaries required
- Best used alongside the `self-improving` skill

## Core Reflection Loop

After significant work, pause and evaluate:

1. Did it meet expectations?
   Compare outcome vs original intent.

2. What could be better?
   Identify what was weak, inefficient, unclear, missing, overcomplicated, or avoidably risky.

3. Is this reusable?
   Decide whether the lesson should affect future behavior.

4. Where should it go?
   Route the lesson by scope:
   - one-off → no log
   - repeated general issue → `corrections.md`
   - domain-specific lesson → `domains/<domain>.md`
   - project-specific lesson → `projects/<project>.md`

## Reflection Output Format

Use this structure:

```text
CONTEXT: [task type]
INTENT: [what success should have looked like]
OUTCOME: [what actually happened]
GAP: [difference between intent and outcome]
LESSON: [what to do differently next time]
ACTION: [none | log to corrections.md | log to domain/project file]
```

This skill should prefer concise, specific entries over narrative self-commentary.

## Decision Rules

Log only when at least one of these is true:
- the lesson is likely to recur
- it would improve future execution
- it explains rework or repeated friction
- it identifies a systematic weakness
- it changes how similar tasks should be handled next time

Do not log:
- emotional reactions
- vague self-criticism
- one-time task details with no reuse value
- speculative lessons without evidence
- generic praise with no behavioral takeaway

## Trigger Rules

### Always reflect after
- completing a multi-step task
- a failed attempt followed by recovery
- fixing a bug or mistake
- explicit user feedback
- output that required rework before delivery

### Reflect when noticed internally
- response drifted from the user's intent
- answer was technically correct but poorly structured
- too much or too little detail was given
- assumptions had to be corrected mid-task
- a better path became obvious after completion

### Do not reflect after
- trivial one-shot replies
- simple confirmations
- low-value housekeeping
- mechanical work with no quality decision to evaluate

## Storage Handoff

When a reusable lesson is found:
- hand the concise lesson to `self-improving`
- let `self-improving` decide whether to append, track, promote, or archive

This skill should not directly promote lessons to HOT memory.
It nominates; `self-improving` remembers.

## Common Traps

| Trap | Why It Fails | Better Move |
|------|--------------|-------------|
| Reflecting on everything | Creates noise and slows execution | Reflect only on meaningful outcomes |
| Logging every thought | Pollutes memory | Store only reusable lessons |
| Vague hindsight | Produces weak rules | Tie lessons to intent, outcome, and gap |
| Promoting too early | Creates brittle memory | Let self-improving track repetition first |
| Writing abstract reflections | Hard to apply later | Convert every lesson into a concrete behavior |

## Scope

This skill ONLY:
- evaluates completed work
- identifies quality gaps
- extracts actionable lessons
- routes reusable lessons by scope
- hands candidate lessons to `self-improving`

This skill NEVER:
- replaces long-term memory
- stores credentials or sensitive data
- promotes lessons directly to HOT memory
- turns every task into a retrospective
- confuses introspection with evidence

## Quality Standard

Good reflection is:
- brief
- specific
- evidence-based
- reusable
- action-oriented

Bad reflection is:
- abstract
- repetitive
- self-congratulatory
- disconnected from real output quality
- too vague to change future behavior

## Related Skills
Install with `clawhub install <slug>` if user confirms:

- `self-improving` — stores and promotes validated lessons
- `memory` — long-term factual continuity
- `learning` — adaptive teaching and explanation
- `decide` — decision patterns and trade-off handling

## Feedback

- If useful: `clawhub star self-reflection`
- Pair with `self-improving` for durable learning
