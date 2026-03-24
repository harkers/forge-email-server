# Forge Pipeline

Project workspace for a project-based todo system with a fancy web display, extensive notes, and the usual scaffolding.

## Goals

- Track actions by project
- Maintain rich notes alongside tasks
- Provide a polished browser-based interface
- Keep data simple and portable during early development
- Become the central board for "where am I at and what do I do next?"

## Structure

- `app/` — web app source
- `app/data/` — starter project and task data
- `notes/` — product notes, planning, and decisions
- `docs/` — supporting documentation
- `scripts/` — helper scripts

## Current Features

- Project list with inline editing
- Add/delete projects
- Per-project task list
- Add/delete tasks
- Edit task title, status, priority, due date, and tags
- Rich project notes
- Search across projects/tasks/tags
- Filter tasks by status
- Local persistence using browser `localStorage`
- Sample seed data on first load

## Intended Direction

Forge Pipeline is meant to become the central project tracker so other projects can update it and give a quick answer to:

- what is in flight?
- what is blocked?
- what is next?
- what has already been finished?

## Running It

Use the existing helper script:

```bash
./scripts/serve.sh
```

Then open the local server in a browser.
