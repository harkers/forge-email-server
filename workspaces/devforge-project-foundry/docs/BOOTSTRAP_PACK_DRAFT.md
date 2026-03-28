# DevForge: Project Foundry
## Bootstrap Pack Draft

Status: Planning  
Date: 2026-03-28

## Purpose

Define the minimum bootstrap pack needed to create the future template repository cleanly once approvals land.

## Expected Bootstrap Contents

### Core repo files
- README.md
- LICENSE
- .gitignore
- .editorconfig
- .gitattributes
- CODEOWNERS
- CONTRIBUTING.md
- SECURITY.md
- CHANGELOG.md

### Core directories
- docs/
- templates/
- schemas/
- directives/
- agents/
- automation/
- examples/
- workspaces/

### Initial automation
- `init-project.sh`
- `validate-structure.sh`
- optional later helpers for comms, training, or risk generation

### Initial templates
- strategy brief
- requirements pack
- architecture decision record
- governance gate
- comms handoff pack
- training readiness pack
- risk register starter

### Initial schema candidates
- project metadata
- pipeline status
- control registry
- comms matrix
- training pack
- risk register

## Bootstrap Rule

Bootstrap should create the minimal durable foundation first. It should not attempt to automate every future idea on day one.
