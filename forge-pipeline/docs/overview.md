# Forge Pipeline Overview

Forge Pipeline is the central project and task hub for the workspace.

Its job is to answer, quickly and clearly:

- what is in flight?
- what is blocked?
- what needs doing next?
- what has already been completed?

It started as a visual project board and now includes a shared file-backed API so other tools and automations can write into the same source of truth.

## Core idea

Forge Pipeline is not just a todo app.
It is intended to be the shared operational layer where multiple projects can report progress, create next steps, and surface blockers.

## Current shape

- browser UI for human management
- file-backed HTTP API for automation and MCP integration
- JSON storage for portability and simplicity
- project/task model with notes, tags, and status tracking

## Current responsibilities

- maintain a project list
- maintain task lists under projects
- store notes and context close to work items
- provide summary rollups
- allow external systems to update the shared board

## Near-term direction

- richer automation endpoints
- auth/API protection
- activity log / audit trail
- event-style updates from other projects
