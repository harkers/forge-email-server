# Conversation Archive

This folder stores OpenClaw conversations as executable Quarto documents (`.qmd`).

## Structure

```
conversations/
├── YYYY-MM-DD-session-NNN.qmd  # Individual session documents
├── index.qmd                   # Master index (renders to HTML site)
└── render.sh                   # Batch render script
```

## Format

Each `.qmd` file includes:
- **YAML frontmatter**: date, session_id, topics, tags, model, duration
- **Conversation flow**: User messages, assistant responses, tool calls
- **Code blocks**: Commands, queries, API calls with results
- **Decisions**: Highlighted key decisions and outcomes
- **Memory links**: References to `memory/YYYY-MM-DD.md` entries

## Rendering

```bash
# Render single conversation
quarto render 2026-03-24-session-001.qmd --to html

# Render all conversations
./render.sh

# Output: conversations/_site/ with HTML archive
```

## Benefits

- **Executable**: Code chunks can be re-run
- **Searchable**: Structured metadata for filtering
- **Versioned**: Git-tracked conversation history
- **Multi-format**: HTML, PDF, or hosted site output

## First Session

Today's work (2026-03-24) is captured in:
- `2026-03-24-session-001.qmd` - Workspace bootstrap + Trilium + Forge Pipeline + Quarto install
