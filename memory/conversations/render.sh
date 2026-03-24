#!/bin/bash
# Render all conversation .qmd files to HTML archive

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📚 Rendering conversation archive..."

# Create output directory
mkdir -p _site

# Render each .qmd file
for qmd in *.qmd; do
  if [ -f "$qmd" ] && [ "$qmd" != "index.qmd" ]; then
    echo "  Rendering: $qmd"
    quarto render "$qmd" --to html --output-dir _site --quiet
  fi
done

# Render index last (may reference other files)
if [ -f "index.qmd" ]; then
  echo "  Rendering: index.qmd"
  quarto render index.qmd --to html --output-dir _site --quiet
fi

echo "✅ Archive ready in: _site/"
echo ""
echo "Open with: firefox _site/index.html || open _site/index.html"
