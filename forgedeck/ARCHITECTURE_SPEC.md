# ForgeDeck — Architecture Specification v1.0

## Status
Draft

## Purpose

This document defines the intended architecture for ForgeDeck as a premium deck-generation engine in the Forge ecosystem.

ForgeDeck exists to solve a specific problem:
**traditional `python-pptx`-first deck generation is not a credible design system.**
It is a file-format assembly layer, not a high-fidelity presentation design surface.

The architectural answer is:

**HTML/CSS → Playwright → PPTX**

That gives ForgeDeck pixel-perfect slide rendering, a real design system, modern composition primitives, and still delivers a practical `.pptx` output with notes and metadata.

---

## Architectural Thesis

### Core principle
Use web rendering as the visual system.
Use `python-pptx` only as the assembly/container layer.

### Why
Direct `python-pptx` authoring is limited by:
- manual coordinate placement
- weak typography control
- flat fills and simplistic shape styling
- limited compositional primitives
- poor support for premium visual systems

### Therefore
ForgeDeck should be architected so that:
- visual composition is done in HTML/CSS templates
- rendering is done by headless Chromium via Playwright
- `.pptx` packaging is handled after rendering
- notes and metadata remain editable in PowerPoint

---

## System Overview

### Pipeline
Structured content JSON  
→ layout selection + template data  
→ Jinja2 HTML templates  
→ design system CSS + assets  
→ Playwright render (high-res PNG)  
→ python-pptx assembly  
→ `.pptx` output + notes + metadata

### Result
A deck that:
- looks professionally designed
- is visually consistent with a design system
- is generated from structured content
- can still carry editable notes and core properties

---

## High-Level Components

## 4.1 API Layer
**Technology:** FastAPI

### Responsibilities
- expose service endpoints
- publish MCP-style tool surface
- validate requests
- return output metadata and download references

### Current/expected endpoints
- `GET /health`
- `GET /tools`
- `POST /call`
- `GET /download/{filename}`
- `GET /decks`

### Tool surface
- `build_deck`
- `render_slide`
- `list_layouts` / `list_templates`
- `list_decks`
- optional later: `delete_deck`, `inspect_template`, `validate_deck_payload`

---

## 4.2 Template Layer
**Technology:** Jinja2 HTML templates + CSS

### Responsibilities
- define slide structures
- enforce design system rules
- separate layout from content
- support multiple presentation patterns

### Expected template types
- cover
- section / divider
- two-column
- three-column
- grid-6
- roadmap
- statement / key message
- mechanisms / process
- comparison
- metrics / scoreboard

### Requirements
- reusable layouts
- clean content contracts
- predictable field schemas
- support for speaker notes in parallel content structures

---

## 4.3 Design System Layer
**Technology:** CSS + local assets/fonts

### Responsibilities
- visual consistency
- typography
- palette
- spacing
- card patterns
- depth/shadow/gradient treatment
- audience and brand modes

### Recommended baseline
ForgeDeck should align with ForgeOrchestra visual language where appropriate:
- obsidian/dark architectural base
- premium neutral typography
- restrained luminous accents
- clear hierarchy
- high-density capability without visual noise

### Requirements
- local font support
- reusable token system
- ability to switch theme/audience modes later

---

## 4.4 Render Engine
**Technology:** Playwright + headless Chromium

### Responsibilities
- render HTML templates to high-resolution slide images
- ensure fonts and CSS resolve correctly
- produce consistent screenshots for assembly

### Current model
- 1280×720 CSS viewport
- device scale factor 2
- output 2560×1440 PNG

### Requirements
- deterministic rendering
- stable local asset resolution
- browser reuse where possible for performance
- safe cleanup on shutdown

### Why Playwright
Playwright gives a real browser layout engine:
- proper typography
- proper CSS behavior
- gradients, blur, shadow, glass, overlays
- compositional control impossible in raw python-pptx

---

## 4.5 Assembly Layer
**Technology:** python-pptx

### Responsibilities
- create widescreen `.pptx`
- insert each rendered slide image full-bleed
- attach speaker notes
- set core properties/metadata
- save output file

### Principle
This layer should remain intentionally thin.

It is not the design engine.
It is the packaging and presentation-file output layer.

### Requirements
- full-slide image placement
- note insertion
- title metadata
- correct output path handling

---

## 4.6 Output Layer
**Technology:** filesystem + volume-backed deck store

### Responsibilities
- persist built `.pptx` files
- expose download paths
- list available decks
- allow downstream systems to retrieve artifacts

### Current model
- output directory: `/decks`
- Docker volume-backed persistence

### Requirements
- predictable filenames
- collision handling
- durable storage
- optional cleanup/retention policy later

---

## Data Model

## 5.1 Input model
The core input is structured JSON.

### Example shape
```json
{
  "title": "Board Update",
  "slides": [
    {
      "layout": "cover",
      "data": {
        "title": "ForgeOrchestra",
        "subtitle": "Q2 Strategy Update"
      },
      "notes": "Open by framing the audience and context."
    }
  ],
  "output_filename": "board-update-q2"
}
```

### Core concepts
- deck title
- ordered slide list
- layout identifier
- layout-specific content payload
- optional speaker notes
- optional explicit output filename

---

## 5.2 Internal processing model
For each slide:
- resolve layout template
- merge with content payload
- render HTML
- inline/apply CSS
- render via Playwright
- capture PNG bytes
- pass image + notes to assembler

---

## 5.3 Output model
Outputs should include:
- filename
- download URL
- slide count
- status/message

Optional later fields:
- render duration
- template usage summary
- warnings/validation notes

---

## Deployment Architecture

## 6.1 Runtime model
ForgeDeck runs as a containerized service on titan.

### Current shape
- Docker container
- host network mode
- FastAPI app served by uvicorn
- port `18103`

### Compose service
- service name: `forgedeck`
- output volume: `forgedeck_decks`

---

## 6.2 Container requirements
The container must provide:
- Python runtime
- Chromium/browser dependencies
- Playwright
- Jinja2
- python-pptx
- local font support if premium typography is expected

### Important requirement
Custom/local font installation is part of the design system story.
If the container uses random fallback fonts, the entire point of the architecture is weakened.

---

## 6.3 Storage model
### Required stores
- rendered final decks (`/decks`)
- optional later temp render cache
- optional later template asset directory

### Suggested future additions
- retention policy
- cleanup utility
- artifact metadata index

---

## MCP / Tool Surface Role

ForgeDeck should act as a specialized deck-generation service that can be invoked by agents or orchestration layers.

### Best use
- agent produces structured deck payload
- ForgeDeck builds visual output
- output is returned as downloadable deck artifact

### This means
ForgeDeck is a **service in the ecosystem**, not merely a one-off script.

---

## Relationship to Forge Ecosystem

## 8.1 ForgeOrchestra relationship
ForgeOrchestra can use ForgeDeck as its presentation generation engine.

Possible use cases:
- strategy updates
- project briefs
- operating reviews
- executive summaries
- product architecture decks

## 8.2 ForgeDiscord relationship
ForgeDiscord can route requests that need slide/report output into ForgeDeck.

Example:
- `/job create` or future `/deck build`
- route to ForgeDeck workflow
- return download link and summary

## 8.3 PowerPoint MCP relationship
ForgeDeck and PowerPoint MCP are related but not identical.

### ForgeDeck
- focused on premium generated slide outputs
- design-first, template-driven
- image-backed slide rendering approach

### PowerPoint MCP
- focused on direct presentation editing/authoring through tool calls
- best when shape-level manipulation of an existing deck is needed

### Recommendation
Treat ForgeDeck as the premium deck foundry.
Treat PowerPoint MCP as the editing/manipulation tool when direct object-level editing matters.

---

## Technical Constraints

### Constraint 1 — image-backed slides
Generated slides are image-backed, not native editable PowerPoint objects.

### Consequence
- visuals are high-fidelity
- editable speaker notes remain available
- full slide editability is reduced compared with native PowerPoint construction

This is the tradeoff for design quality.

### Constraint 2 — browser runtime complexity
Playwright/Chromium introduces more runtime weight than a simple python-pptx script.

### Consequence
- larger image
- more dependencies
- browser stability considerations

### Constraint 3 — template quality determines deck quality
A weak template system produces weak decks no matter how good the transport layer is.

---

## Non-Goals

ForgeDeck is not intended to be:
- a generic WYSIWYG presentation editor
- a direct replacement for PowerPoint desktop editing
- a loose script pile for ad hoc screenshots
- a shape-by-shape design engine built on python-pptx primitives

---

## MVP Architecture Requirements

To be considered properly formed, ForgeDeck MVP should provide:
- stable FastAPI service
- working MCP-style tool interface
- at least 5–8 strong layout templates
- reusable CSS design system
- reliable Playwright rendering
- full-deck assembly into PPTX
- speaker notes support
- predictable deck download/listing
- operational deployment on titan

---

## Recommended Next Architecture Steps

1. formalize template contracts per layout
2. add dedicated design token file / base.css system
3. add local fonts into container
4. define audience modes (executive, product, technical, investor)
5. add validation for slide payloads by layout
6. add deck manifest/metadata sidecar
7. decide retention and artifact lifecycle
8. document ForgeDeck vs PowerPoint MCP boundary clearly

---

## Final Recommendation

ForgeDeck should be positioned as:

**A premium deck-generation engine for the Forge ecosystem, using HTML/CSS and browser rendering for visual quality, with python-pptx used as a packaging layer for deck delivery.**

That is the right architecture.
It solves the real problem instead of pretending raw python-pptx can become a proper design system if you just squint harder.
