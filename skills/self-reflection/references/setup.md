# Setup — Self-Reflection

## First-Time Setup

This skill works best as a companion to `self-improving`.
If `~/self-improving/` does not exist yet, install and set up `self-improving` first.

## 1. Add Reflection Steering to SOUL.md

Add this section to your `SOUL.md`:

```markdown
**Self-Reflection**
After meaningful work, briefly compare outcome vs intent.
Extract only specific, reusable lessons.
Do not log one-off observations or vague criticism.
Route reusable lessons to the correct scope before handing them to `self-improving`.
```

## 2. Add Reflection Trigger Guidance to AGENTS.md

Add this section to your `AGENTS.md` or workspace guidance:

```markdown
## Self-Reflection

Run a brief post-task review after multi-step work, bug fixes, user feedback, or any case where output required rework.
Use the reflection format:
- CONTEXT
- INTENT
- OUTCOME
- GAP
- LESSON
- ACTION

Only store lessons that are reusable, recurring, or materially improve future execution.
```

## 3. Keep a Reflection Template Nearby

Save a reusable template as `reflection-template.md` or keep the following block available:

```text
CONTEXT: [task type]
INTENT: [what success should have looked like]
OUTCOME: [what actually happened]
GAP: [difference between intent and outcome]
LESSON: [what to do differently next time]
ACTION: [none | log to corrections.md | log to domain/project file]
```

## 4. Add a Reflection Log (Optional)

If you want a dedicated review trail before lessons are handed to `self-improving`, create:

`~/self-improving/reflections.md`

Suggested starter structure:

```markdown
# Self-Reflections Log

Track meaningful post-task reflections before or alongside promotion into other self-improving files.
```

This log is optional. Durable lessons should still end up in the scoped self-improving files.

## 5. Recommended Operating Rule

Use this rule in workspace guidance:

```markdown
Reflect briefly after meaningful work.
Store only lessons that improve future execution.
Do not confuse hindsight with evidence.
Do not promote a lesson to persistent memory without repetition or confirmation.
```

## Verification

A correct setup should make the agent do all of the following:
- reflect after substantial work, not every tiny action
- compare outcome against original intent
- extract a concrete lesson
- decide whether the lesson is reusable
- route the lesson by scope
- hand off storage decisions to `self-improving`
