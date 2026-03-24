# Trilium ETAPI Skill

## Purpose

Provides tooling for interacting with Trilium Notes via the ETAPI (External Trilium API) interface. Use when you need to:

- Read/write notes programmatically
- Organize note structure (create branches, move notes)
- Export/import note content
- Search and query notes
- Automate Trilium workflows

## Configuration

Add to `TOOLS.md`:

```markdown
### Trilium ETAPI

- **Host**: `http://192.168.10.5:8080`
- **Auth**: Plain `Authorization: <token>` header (NOT Bearer)
- **Token**: `<your-token>`
- **Version**: v0.58.7
- **OpenAPI**: `/etapi/etapi.openapi.yaml`
```

## Auth Pattern

**Critical**: Trilium ETAPI uses plain Authorization header, NOT Bearer:

```bash
# ✅ Correct
curl -H "Authorization: <token>" ...

# ❌ Wrong (will fail)
curl -H "Authorization: Bearer <token>" ...
```

## Core Endpoints

### Notes

#### Create Note
```bash
POST /etapi/create-note
Content-Type: application/json

{
  "parentNoteId": "root",
  "title": "Note Title",
  "type": "text",
  "content": "<h1>HTML content</h1>"
}
```

#### Get Note Metadata
```bash
GET /etapi/notes/{noteId}
```

#### Get Note Content
```bash
GET /etapi/notes/{noteId}/content
Accept: text/html
```

#### Update Note Content
```bash
PUT /etapi/notes/{noteId}/content
Content-Type: text/plain  # Important: use text/plain, not text/html

<h1>HTML content</h1>
```

#### Update Note Metadata
```bash
PATCH /etapi/notes/{noteId}
Content-Type: application/json

{
  "title": "New Title"
}
```

#### Search Notes
```bash
GET /etapi/notes?search=<query>&fastSearch=false&includeArchivedNotes=false
```

### Branches

#### Create Branch (Link Note to Parent)
```bash
POST /etapi/branches
Content-Type: application/json

{
  "parentNoteId": "<parent-note-id>",
  "noteId": "<existing-note-id>",
  "prefix": "Optional prefix"
}
```

#### Delete Branch (Unlink, Not Delete Note)
```bash
DELETE /etapi/branches/{branchId}
```

### Export

#### Export Note Subtree
```bash
GET /etapi/notes/{noteId}/export?format=html
# or
GET /etapi/notes/{noteId}/export?format=markdown
```

## Common Patterns

### File a Note Under Calendar Date

```bash
# 1. Find/verify calendar structure
GET /etapi/notes?search=calendar

# 2. Navigate: Calendar → Year → Month → Day
# Note IDs: Calendar root, year, month, day

# 3. Add note to date
POST /etapi/branches
{
  "parentNoteId": "<day-note-id>",
  "noteId": "<your-note-id>",
  "prefix": "Daily Summary"
}

# 4. Remove from root (optional)
DELETE /etapi/branches/root_<note-id>
```

### Create Daily Summary Note

```bash
# Create under calendar date
POST /etapi/create-note
{
  "parentNoteId": "<today-note-id>",
  "title": "Daily Summary - YYYY-MM-DD",
  "type": "text",
  "content": "<h1>Summary</h1>..."
}
```

### Bulk Reorganisation

```bash
# For each note to move:
# 1. Create new branch under target parent
POST /etapi/branches
{"parentNoteId": "target", "noteId": "note", "prefix": ""}

# 2. Delete old branch
DELETE /etapi/branches/old_branch_id
```

## Known Issues (v0.58.7)

### Content Update Quirk

PUT /etapi/notes/{noteId}/content may not persist in v0.58.7:
- Returns 204 No Content (looks successful)
- But GET returns `[object Object]` or old content
- **Workaround**: Create new note with content in create-note call

### Recommended Pattern

```bash
# Instead of update, create new with content:
POST /etapi/create-note
{
  "parentNoteId": "...",
  "title": "...",
  "content": "<full-html-content>"
}
```

## OpenAPI Reference

Full spec available at:
- Running instance: `http://<host>/etapi/etapi.openapi.yaml`
- Saved locally: `skills/trilium-etapi/etapi.openapi.yaml`

Refresh spec:
```bash
curl -s <host>/etapi/etapi.openapi.yaml \
  -H "Authorization: <token>" \
  -o skills/trilium-etapi/etapi.openapi.yaml
```

## Tool Commands

### Read Note
```bash
curl -s <host>/etapi/notes/<id> \
  -H "Authorization: <token>"
```

### Read Content
```bash
curl -s <host>/etapi/notes/<id>/content \
  -H "Authorization: <token>" \
  -H "Accept: text/html"
```

### Create Note
```bash
curl -s -X POST <host>/etapi/create-note \
  -H "Authorization: <token>" \
  -H "Content-Type: application/json" \
  -d '{"parentNoteId":"root","title":"Test","type":"text","content":"<h1>Test</h1>"}'
```

### Update Content
```bash
curl -s -X PUT <host>/etapi/notes/<id>/content \
  -H "Authorization: <token>" \
  -H "Content-Type: text/plain" \
  --data-binary @content.html
```

### Create Branch
```bash
curl -s -X POST <host>/etapi/branches \
  -H "Authorization: <token>" \
  -H "Content-Type: application/json" \
  -d '{"parentNoteId":"parent","noteId":"child","prefix":""}'
```

### Delete Branch
```bash
curl -s -X DELETE <host>/etapi/branches/<branch-id> \
  -H "Authorization: <token>"
```

## Security Notes

- Token grants full ETAPI access — treat as credentials
- Read-only operations safe to automate
- Write/delete operations require explicit user approval
- Never exfiltrate note content to external systems

## Version Compatibility

Tested with:
- Trilium v0.58.7 (build a3149aecf41bac3c559ebbd1865e916264985ac3)
- ETAPI spec version: 1.0.0

API shape may differ in other versions — always fetch OpenAPI spec from target instance.
