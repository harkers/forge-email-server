# ForgeDeck Review

## Source Location
`/home/stu/ForgeDeck`

## Project Ethos

### The fundamental problem
`python-pptx` is a file format library, not a design tool.

If you build directly in python-pptx, you are placing rectangles and text boxes by coordinate in inches. The ceiling is low. You can make it less bad, but it will always tend to look like it was assembled by code because the design primitives are too coarse.

### What is actually limiting direct python-pptx work
| Limitation | Root cause |
|---|---|
| No real typography | Cannot properly control tracking, leading, optical sizing, or font features |
| No gradients / glass / depth | Shape fills are fundamentally flat |
| No custom fonts by default | Container only has whatever system fonts exist |
| Layout is manual coordinates | No flexbox, grid, or compositional layout engine |
| Weak compositional design | Everything becomes a rectangle stacked on a rectangle |

## Correct Product Direction

### Proper architecture
**HTML/CSS → Playwright → PPTX**

Each slide is a Jinja2 HTML template rendered in a headless browser at high resolution (e.g. 2560×1440). Playwright screenshots it. `python-pptx` then assembles the images into a `.pptx` while preserving speaker notes, slide titles, and metadata.

### Pipeline
Content JSON  
→ Jinja2 HTML templates  
→ Forge design system CSS  
→ Playwright render  
→ high-resolution PNG per slide  
→ python-pptx assembler  
→ `.pptx`

### Why this is the right approach
This gives:
- full CSS design freedom
- real typography
- custom fonts
- gradients
- shadows
- glass/depth effects
- proper visual composition
- premium design system implementation

The PPTX becomes a delivery container for pixel-perfect slides plus editable notes and metadata.

## What ForgeDeck is now
ForgeDeck is already aligned with this architecture direction.

### Core shape
- FastAPI app exposing:
  - `GET /health`
  - `GET /tools`
  - `POST /call`
  - `GET /download/{filename}`
  - `GET /decks`
- Tool surface includes:
  - `build_deck`
  - `render_slide`
  - `list_layouts`
  - `list_decks`

### Render pipeline
1. Structured slide request enters via MCP-style `/call`
2. `builder.py` loops through slides
3. `renderer.py` uses Playwright to render HTML templates to PNG
4. `assembler.py` uses `python-pptx` to assemble widescreen PPTX
5. Deck saved to `/decks`

### Deployment
- Docker compose service: `forgedeck`
- Host network mode
- Port: `18103`
- Output volume: `forgedeck_decks`

### Dependencies
- fastapi
- uvicorn
- playwright
- python-pptx
- jinja2
- pydantic
- pillow
- aiofiles

## Product Framing
ForgeDeck should be treated as a deck-generation engine, not a direct slide-editing system.

### Strong product definition
A new service: **forge-deck on titan**

Suggested shape:
```text
services/forge-deck/
├── Dockerfile
├── app/
│   ├── main.py
│   ├── builder.py
│   ├── renderer.py
│   ├── assembler.py
│   └── templates/
│       ├── base.css
│       ├── cover.html
│       ├── section.html
│       ├── two-col.html
│       ├── three-col.html
│       ├── grid-6.html
│       ├── roadmap.html
│       └── ...
```

### MCP tool surface
- `build_deck` — takes structured JSON content, returns filename/output reference
- `render_slide` — preview a single slide
- `list_templates` / `list_layouts` — available layouts
- `download_deck` — retrieve generated file

## Initial Assessment
ForgeDeck looks like a legitimate presentation subsystem in the Forge ecosystem and the architecture direction is fundamentally sound.

Possible roles:
1. standalone Forge product
2. internal presentation engine used by ForgeOrchestra and related tools
3. backend deck-generation service behind a richer operator UI

## Recommended next questions
- Is ForgeDeck meant to be user-facing or internal infrastructure?
- Should it stay MCP-compatible only, or get a richer application shell?
- How should it relate to PowerPoint MCP and other deck/document systems?
- What deck templates and audience modes matter most?
- Should ForgeDeck become the standard presentation engine for Forge-family outputs?
