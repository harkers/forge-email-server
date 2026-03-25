# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## Session Startup

Before doing anything else:
1. Read `SOUL.md`
2. Read `USER.md`
3. Read `memory/YYYY-MM-DD.md` (today + yesterday)
4. If in main session, also read `MEMORY.md`

Don't ask permission. Just do it.

## Memory
- Daily notes: `memory/YYYY-MM-DD.md`
- Long-term: `MEMORY.md`

Write down what matters. Messaging systems drift if you don't document decisions.

## Red Lines
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm`
- When in doubt, ask.

## External vs Internal
**Safe freely:**
- Read files, inspect configs, organise docs, work in this workspace

**Ask first:**
- Sending live messages externally
- Changing production comms flows without confirmation
- Anything public-facing or irreversible

## Messaging Principle
ForgeDiscord exists to reduce noise and increase signal.
- Prefer summaries over spam
- Prefer stateful operator views over raw event floods
- Prefer acknowledgement without interruption when possible

## Make It Yours
Refine this as the system evolves.

## Forge Pipeline Sync

Forge Pipeline is the central portfolio/project layer. When significant changes happen in this workspace — new docs, architecture changes, roadmap updates, deployment changes, important decisions, or new implementation milestones — update the relevant Forge Pipeline project entry so portfolio visibility stays current.

## Self-Improvement

Use the `self-improvement` skill when commands fail unexpectedly, external tools break, the user corrects something important, a capability is missing, or a better recurring approach is discovered. Log the learning/error/request so it can improve future work instead of disappearing between sessions.

## Self-Reflection

Use the `self-reflection` skill after meaningful multi-step work, after rework, after user feedback, after fixing mistakes, or when the outcome was clearly weaker than intent. Keep reflections brief, evidence-based, and route reusable lessons into self-improvement rather than treating every task like a diary entry.

## Quarto / QMD Default

Quarto (`.qmd`) is available by default on this machine. Use Quarto for reports, specs, architecture docs, design docs, reviews, and other structured written outputs when publishing/export or richer document structure would help.

Important local note:
- Quarto CLI: `~/.local/bin/quarto`
- Use Quarto's bundled Deno, not the system Deno, when Quarto execution depends on it.
