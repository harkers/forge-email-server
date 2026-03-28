# DevForge: Project Foundry
## ForgeTraining Specification

Status: Planning  
Date: 2026-03-28

## What ForgeTraining Is

ForgeTraining is the dedicated training and enablement domain.

It converts approved sprint, review, and release truth into role-based training modules, user guides, enablement notes, and Product Readiness Packs.

## Input Engine

ForgeTraining is planned to parse approved technical truth from:
- user stories and acceptance criteria
- sprint demo transcripts
- pull request summaries
- UI screenshots or Figma links
- release notes
- review and validation outcomes

## Core Logic Layers

### Layer A — Impact Analyzer
Classifies whether a change is a minor tweak, workflow change, new core feature, or another meaningful change type.

### Layer B — Persona Tailor
Shapes the output for target audiences such as:
- sales
- support
- end user
- admin / operations
- governance / compliance where needed

### Layer C — Asset Factory
Generates enablement outputs such as:
- markdown guides
- Loom or demo scripts
- FAQs
- knowledge checks
- Product Readiness Packs
- visual asset request lists

## Planned Standard Output

### Product Readiness Pack
- TL;DR summary
- Click-Path walkthrough
- Gotchas / risk notes
- knowledge check
- visual asset list

## Principle

ForgeTraining should generate enablement from approved behaviour, not draft assumptions.
