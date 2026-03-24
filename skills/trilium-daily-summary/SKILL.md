# Trilium Daily Summary Skill

## Purpose

Automated nightly job that creates comprehensive daily work summaries in Trilium under the calendar structure.

## When to Use

- Scheduled nightly via cron (recommended: 23:00 or 08:00)
- Manual trigger: "Update Trilium with today's work"
- End-of-day wrap-up sessions

## Workflow

### 1. Gather Daily Context

**Sources:**
- `memory/YYYY-MM-DD.md` - Daily memory note
- `memory/conversations/YYYY-MM-DD-session-*.qmd` - Session documents
- Git commits from workspace (today's date)
- Forge Pipeline board activity (if available)

**Collect:**
- Projects created/modified
- Technical specifications
- Decisions made
- Code/commands run
- Files created/updated
- Time spent per activity

### 2. Build Summary HTML

**Structure:**
```html
<h1>Daily Summary - YYYY-MM-DD</h1>
<h2>📊 Overview</h2>
<ul>
  <li>Duration: X hours</li>
  <li>Projects touched: N</li>
  <li>Files created: N</li>
  <li>Git commits: N</li>
</ul>

<h2>🚀 Major Work</h2>
<!-- Each major topic with technical specs -->

<h2>🔧 Technical Findings</h2>
<!-- Key discoveries, patterns, workarounds -->

<h2>📋 Next Steps</h2>
<!-- Pending items, TODOs -->
```

### 3. File Under Calendar

**Trilium Path:**
```
Calendar
└── YYYY
    └── MM - Month Name
        └── DD - Day Name
            └── Daily Summary - YYYY-MM-DD
```

**Steps:**
1. Find/create year note (e.g., "2026")
2. Find/create month note (e.g., "03 - March")
3. Find/create day note (e.g., "24 - Tuesday")
4. Create daily summary note under day
5. Populate with HTML content

### 4. ETAPI Calls

```bash
# 1. Find calendar structure
GET /etapi/notes?search=calendar

# 2. Navigate to today
GET /etapi/notes/{year-id}
GET /etapi/notes/{month-id}
GET /etapi/notes/{day-id}

# 3. Create summary note
POST /etapi/create-note
{
  "parentNoteId": "{day-id}",
  "title": "Daily Summary - YYYY-MM-DD",
  "type": "text",
  "content": "<full-html>"
}
```

## Automation Script

```bash
#!/bin/bash
# Daily Trilium summary generator

DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)
MONTH_NAME=$(date -d "$DATE" +%B)
DAY_NAME=$(date -d "$DATE" +%A)

# 1. Read memory file
MEMORY_FILE="/home/stu/.openclaw/workspace/memory/${DATE}.md"
if [ -f "$MEMORY_FILE" ]; then
  CONTENT=$(cat "$MEMORY_FILE")
else
  CONTENT="No memory file found for ${DATE}"
fi

# 2. Get git commits
COMMITS=$(cd /home/stu/.openclaw/workspace && git log --since="${DATE}T00:00:00" --until="${DATE}T23:59:59" --oneline 2>/dev/null | wc -l)

# 3. Count conversation sessions
SESSIONS=$(ls -1 /home/stu/.openclaw/workspace/memory/conversations/${DATE}-session-*.qmd 2>/dev/null | wc -l)

# 4. Build HTML
cat > /tmp/trilium-daily-${DATE}.html << EOF
<h1>Daily Summary - ${DATE}</h1>
<h2>📊 Stats</h2>
<ul>
  <li>Git commits: ${COMMITS}</li>
  <li>Conversation sessions: ${SESSIONS}</li>
  <li>Memory file: $([ -f "$MEMORY_FILE" ] && echo "Present" || echo "Not found")</li>
</ul>
<h2>📝 Memory Note</h2>
<pre>${CONTENT}</pre>
EOF

# 5. Post to Trilium (via skill or direct curl)
# ... ETAPI calls here
```

## Cron Configuration

```json
{
  "name": "Trilium Daily Summary",
  "schedule": {
    "kind": "cron",
    "expr": "0 23 * * *",
    "tz": "Europe/London"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Generate daily work summary and post to Trilium calendar under today's date. Gather from memory/YYYY-MM-DD.md, conversation files, and git commits. Include technical specs, decisions, and stats.",
    "thinking": "elevated",
    "timeoutSeconds": 300
  },
  "sessionTarget": "isolated",
  "enabled": true
}
```

## Content Sources

### Memory Files
- `/home/stu/.openclaw/workspace/memory/YYYY-MM-DD.md`
- Parse sections, extract key work items

### Conversation Archive
- `/home/stu/.openclaw/workspace/memory/conversations/YYYY-MM-DD-session-*.qmd`
- Extract YAML frontmatter (topics, outcomes, decisions)
- Include code blocks and technical findings

### Git Activity
- Commits from workspace (today's date)
- Files changed, lines added/removed

### Forge Pipeline (Optional)
- Projects created/updated today
- Board activity summary

## Output Format

**Note Title:** `Daily Summary - YYYY-MM-DD`

**Parent:** Calendar → YYYY → MM - Month → DD - Day

**Content:** Comprehensive HTML with:
- Overview stats
- Major work sections (by project/topic)
- Technical specifications
- Decisions and findings
- Code/command examples
- Next steps

## Error Handling

- **No memory file**: Create minimal summary with git stats
- **Trilium unreachable**: Log error, retry next run
- **Calendar structure missing**: Create year/month/day notes
- **Auth failure**: Surface to user, don't retry blindly

## Security

- Token stored in skill config or TOOLS.md
- Read-only operations safe
- Write operations require explicit setup
- Never exfiltrate content externally

## Testing

Manual test command:
```bash
# Trigger skill manually
"Generate today's Trilium daily summary"
```

Verify:
1. Note created under correct calendar date
2. Content matches memory file + conversations
3. HTML renders correctly in Trilium UI
4. Git stats accurate

## Version Notes

Tested with Trilium v0.58.7:
- Use `POST /etapi/create-note` (not separate content PUT)
- Plain `Authorization` header (not Bearer)
- Calendar structure may already exist (created by user)
