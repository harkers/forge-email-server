#!/bin/bash
# Collect daily work context for Trilium summary

set -e

DATE="${1:-$(date +%Y-%m-%d)}"
WORKSPACE="/home/stu/.openclaw/workspace"

echo "Collecting daily context for ${DATE}..."

# 1. Memory file
MEMORY_FILE="${WORKSPACE}/memory/${DATE}.md"
if [ -f "$MEMORY_FILE" ]; then
  echo "✓ Memory file found: ${MEMORY_FILE}"
  MEMORY_CONTENT=$(cat "$MEMORY_FILE")
else
  echo "⚠ Memory file not found: ${MEMORY_FILE}"
  MEMORY_CONTENT="No memory file for ${DATE}"
fi

# 2. Conversation sessions
SESSION_DIR="${WORKSPACE}/memory/conversations"
SESSIONS=$(ls -1 "${SESSION_DIR}/${DATE}"-session-*.qmd 2>/dev/null || true)
SESSION_COUNT=$(echo "$SESSIONS" | grep -c .qmd 2>/dev/null || echo "0")
echo "✓ Found ${SESSION_COUNT} conversation session(s)"

# 3. Git commits (today only)
cd "$WORKSPACE"
COMMITS=$(git log --since="${DATE}T00:00:00" --until="${DATE}T23:59:59" --oneline 2>/dev/null || true)
COMMIT_COUNT=$(echo "$COMMITS" | grep -c . 2>/dev/null || echo "0")
echo "✓ ${COMMIT_COUNT} git commit(s) today"

# 4. Files created/modified today
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | head -20 || true)

# 5. Build summary JSON
cat > /tmp/daily-context-${DATE}.json << EOF
{
  "date": "${DATE}",
  "memory_file": "${MEMORY_FILE}",
  "memory_present": $([ -f "$MEMORY_FILE" ] && echo "true" || echo "false"),
  "session_count": ${SESSION_COUNT:-0},
  "commit_count": ${COMMIT_COUNT:-0},
  "commits": $(echo "$COMMITS" | jq -R -s -c 'split("\n") | map(select(length > 0))'),
  "memory_content": $(echo "$MEMORY_CONTENT" | jq -R -s -c '.')
}
EOF

echo "✓ Context collected: /tmp/daily-context-${DATE}.json"
cat /tmp/daily-context-${DATE}.json | jq '. | del(.memory_content)'
