#!/bin/bash
# Generate and post daily work summary to Trilium

set -e

DATE="${1:-$(date +%Y-%m-%d)}"
TRILIUM_HOST="http://192.168.10.5:8080"
TRILIUM_TOKEN="x2aVxHZNg6HO_2GItibwJswEbIqRJDPerRW3LIk1MTquibcjXpVgvdHQ="
WORKSPACE="/home/stu/.openclaw/workspace"

echo "📝 Generating daily summary for ${DATE}..."

# 1. Collect context
"${WORKSPACE}/skills/trilium-daily-summary/collect-daily.sh" "$DATE"

# 2. Read memory content
MEMORY_FILE="${WORKSPACE}/memory/${DATE}.md"
if [ -f "$MEMORY_FILE" ]; then
  MEMORY_CONTENT=$(cat "$MEMORY_FILE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
else
  MEMORY_CONTENT="No memory file for ${DATE}"
fi

# 3. Get git stats
cd "$WORKSPACE"
COMMIT_COUNT=$(git log --since="${DATE}T00:00:00" --until="${DATE}T23:59:59" --oneline 2>/dev/null | wc -l)
FILES_CREATED=$(git log --since="${DATE}T00:00:00" --until="${DATE}T23:59:59" --name-only --pretty=format: 2>/dev/null | sort -u | wc -l)

# 4. Count conversation sessions
SESSION_COUNT=$(ls -1 "${WORKSPACE}/memory/conversations/${DATE}"-session-*.qmd 2>/dev/null | wc -l)

# 5. Build HTML summary
cat > /tmp/trilium-daily-${DATE}.html << HTMLEOF
<h1>Daily Summary - ${DATE}</h1>

<h2>📊 Overview</h2>
<ul>
  <li><strong>Git commits:</strong> ${COMMIT_COUNT}</li>
  <li><strong>Files created/modified:</strong> ${FILES_CREATED}</li>
  <li><strong>Conversation sessions:</strong> ${SESSION_COUNT}</li>
  <li><strong>Memory file:</strong> $([ -f "$MEMORY_FILE" ] && echo "✅ Present" || echo "❌ Not found")</li>
</ul>

<h2>📝 Memory Note</h2>
<pre>${MEMORY_CONTENT}</pre>

<h2>💬 Conversation Sessions</h2>
<ul>
HTMLEOF

# Add session links
for session in "${WORKSPACE}/memory/conversations/${DATE}"-session-*.qmd; do
  if [ -f "$session" ]; then
    basename "$session" >> /tmp/trilium-daily-${DATE}.html
    echo "</ul>" >> /tmp/trilium-daily-${DATE}.html
  fi
done

# Add git commits
cat >> /tmp/trilium-daily-${DATE}.html << HTMLEOF

<h2>🔧 Git Commits Today</h2>
<ul>
HTMLEOF

git log --since="${DATE}T00:00:00" --until="${DATE}T23:59:59" --oneline 2>/dev/null | while read line; do
  echo "  <li><code>$line</code></li>" >> /tmp/trilium-daily-${DATE}.html
done

cat >> /tmp/trilium-daily-${DATE}.html << HTMLEOF
</ul>

<p><em>Generated automatically by Trilium Daily Summary skill</em></p>
<p><strong>Generated:</strong> $(date -Iseconds)</p>
HTMLEOF

echo "✓ HTML summary built: /tmp/trilium-daily-${DATE}.html"
wc -c /tmp/trilium-daily-${DATE}.html

# 6. Find calendar structure
echo "📅 Finding calendar structure..."

# Search for calendar root
CALENDAR_SEARCH=$(curl -s "${TRILIUM_HOST}/etapi/notes?search=calendar" \
  -H "Authorization: ${TRILIUM_TOKEN}")
CALENDAR_ID=$(echo "$CALENDAR_SEARCH" | jq -r '.results[0].noteId')

if [ -z "$CALENDAR_ID" ] || [ "$CALENDAR_ID" == "null" ]; then
  echo "❌ Calendar not found in Trilium"
  exit 1
fi

echo "✓ Calendar root: ${CALENDAR_ID}"

# Navigate to year
YEAR_SEARCH=$(curl -s "${TRILIUM_HOST}/etapi/notes/${CALENDAR_ID}" \
  -H "Authorization: ${TRILIUM_TOKEN}" | jq -r '.childNoteIds[]' | head -1)
YEAR_ID=$(curl -s "${TRILIUM_HOST}/etapi/notes?search=$(date +%Y)" \
  -H "Authorization: ${TRILIUM_TOKEN}" | jq -r '.results[0].noteId')

if [ -z "$YEAR_ID" ] || [ "$YEAR_ID" == "null" ]; then
  echo "⚠ Year $(date +%Y) not found, would need to create"
  YEAR_ID="root"  # Fallback
fi

# Navigate to month
MONTH_NUM=$(date -d "$DATE" +%m)
MONTH_NAME=$(date -d "$DATE" +%B)
MONTH_SEARCH=$(curl -s "${TRILIUM_HOST}/etapi/notes?search=${MONTH_NUM}%20-%20${MONTH_NAME}" \
  -H "Authorization: ${TRILIUM_TOKEN}")
MONTH_ID=$(echo "$MONTH_SEARCH" | jq -r '.results[0].noteId')

if [ -z "$MONTH_ID" ] || [ "$MONTH_ID" == "null" ]; then
  echo "⚠ Month ${MONTH_NUM} - ${MONTH_NAME} not found"
  MONTH_ID="$YEAR_ID"  # Fallback to year
fi

# Navigate to day
DAY_NUM=$(date -d "$DATE" +%d)
DAY_NAME=$(date -d "$DATE" +%A)
DAY_SEARCH=$(curl -s "${TRILIUM_HOST}/etapi/notes?search=${DAY_NUM}%20-%20${DAY_NAME}" \
  -H "Authorization: ${TRILIUM_TOKEN}")
DAY_ID=$(echo "$DAY_SEARCH" | jq -r '.results[0].noteId')

if [ -z "$DAY_ID" ] || [ "$DAY_ID" == "null" ]; then
  echo "⚠ Day ${DAY_NUM} - ${DAY_NAME} not found"
  DAY_ID="$MONTH_ID"  # Fallback to month
fi

echo "✓ Calendar path: Calendar → $(date +%Y) → ${MONTH_NUM}-${MONTH_NAME} → ${DAY_NUM}-${DAY_NAME}"
echo "✓ Target parent: ${DAY_ID}"

# 7. Create daily summary note
echo "📌 Creating summary note in Trilium..."

NOTE_TITLE="Daily Summary - ${DATE}"

CREATE_RESPONSE=$(curl -s -X POST "${TRILIUM_HOST}/etapi/create-note" \
  -H "Authorization: ${TRILIUM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"parentNoteId\": \"${DAY_ID}\",
    \"title\": \"${NOTE_TITLE}\",
    \"type\": \"text\",
    \"content\": \"$(cat /tmp/trilium-daily-${DATE}.html | sed 's/"/\\"/g' | tr '\n' ' ')\"
  }")

NOTE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.note.noteId')
BRANCH_ID=$(echo "$CREATE_RESPONSE" | jq -r '.branch.branchId')

if [ -z "$NOTE_ID" ] || [ "$NOTE_ID" == "null" ]; then
  echo "❌ Failed to create note in Trilium"
  echo "$CREATE_RESPONSE"
  exit 1
fi

echo "✅ Note created successfully!"
echo "   Note ID: ${NOTE_ID}"
echo "   Branch ID: ${BRANCH_ID}"
echo "   Title: ${NOTE_TITLE}"
echo "   Parent: ${DAY_ID} ($(date -d "$DATE" +%A))"
echo ""
echo "📍 View in Trilium: ${TRILIUM_HOST}/#/${NOTE_ID}"
