# DevForge: Project Foundry
## Default Workspace Rules for Derived Projects

Status: Planning  
Date: 2026-03-28

## Purpose

Define the default rules and expectations that Project Foundry-derived workspaces should inherit unless explicitly overridden.

## Required Defaults

### 1. Forge Pipeline Sync

Derived projects should treat Forge Pipeline as the central portfolio and project visibility layer.

Meaningful changes should be reflected back into Forge Pipeline, including:
- new docs
- architecture changes
- roadmap changes
- major implementation milestones
- deployment changes
- key decisions
- project status updates

### 2. Self-Improvement

Derived projects should include a self-improvement rule.

Use self-improvement when:
- commands fail unexpectedly
- external tools or APIs fail
- the user corrects an important assumption
- a capability is missing
- a better recurring approach is discovered

The intent is to preserve reusable learnings instead of losing them between sessions.

### 3. Self-Reflection

Derived projects should include a self-reflection rule.

Use self-reflection after:
- meaningful multi-step work
- rework
- major user feedback
- fixing mistakes
- outcomes that were clearly weaker than intended

The goal is brief, evidence-based reflection with reusable lessons routed into self-improvement rather than vague self-commentary.

### 4. Quarto Availability

Derived projects should assume Quarto (`.qmd`) is available by default for:
- reports
- specs
- design docs
- architecture docs
- review packs
- structured long-form outputs

Use Quarto where publishing, export, or richer document structure would help.

## Rule

These defaults should be written into derived project guidance explicitly rather than assumed from memory.
