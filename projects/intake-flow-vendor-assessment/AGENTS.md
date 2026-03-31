# AGENTS.md — Intake Flow: Vendor Assessment

## Project Overview

**Project:** Intake Flow — Vendor Assessment  
**Owner:** [TBD]  
**Workspace:** `projects/intake-flow-vendor-assessment/`  
**Forge Pipeline:** `project-20260331151651096202`

## Forge Pipeline Sync

When significant changes happen in this workspace — new docs, architecture decisions, roadmap updates, deployment changes, or new implementation milestones — update the relevant Forge Pipeline project entry so portfolio visibility stays current.

## Self-Improvement

Use the `self-improvement` skill when commands fail unexpectedly, external tools break, the user corrects something important, a capability is missing, or a better recurring approach is discovered. Log the learning so it can improve future work.

## Self-Reflection

Use the `self-reflection` skill after meaningful multi-step work, after rework, after user feedback, after fixing mistakes, or when the outcome was clearly weaker than intent. Keep reflections brief and evidence-based; route reusable lessons into self-improvement.

## Local Model Lanes

This project may use the following local model lanes:
- **Phi-4-mini** (port 8091): Fast summaries, triage, drafting
- **Coder-7B** (port 8092): Code review, configs, debugging

Cloud models are the default for tool-calling workflows.

## Voice

Use the humanizer skill for any GitHub-facing or external-facing written communications.

## Red Lines

- No destructive operations without asking
- No external-facing communications without review
- Backup before migrations or schema changes
