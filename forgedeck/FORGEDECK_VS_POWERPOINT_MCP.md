# ForgeDeck vs PowerPoint MCP

## Purpose

This document defines the boundary between **ForgeDeck** and **PowerPoint MCP** so the two tools are used deliberately rather than interchangeably.

They both produce or manipulate PowerPoint presentations, but they solve different problems.

If this boundary is not explicit, people will reach for the wrong tool, get mediocre results, and then blame the universe.

---

## Short Version

### Use **ForgeDeck** when:
- you want a **premium generated deck**
- the input is **structured content**
- visual quality and design consistency matter most
- you want **HTML/CSS-grade rendering**
- you are generating a new deck or repeatable deck type

### Use **PowerPoint MCP** when:
- you need to **open, edit, or modify** a `.pptx`
- you want to manipulate **native PowerPoint objects**
- you need to update tables, text boxes, charts, shapes, or layouts directly
- you are refining an existing deck rather than generating a presentation system output

In one line:

**ForgeDeck is the presentation foundry. PowerPoint MCP is the editing toolkit.**

---

## Core Difference

### ForgeDeck
ForgeDeck is a **design-first generation engine**.

Its architecture is:
**HTML/CSS → Playwright → PPTX**

This means:
- the visual system is web-rendered
- slides are effectively image-backed in the final deck
- notes and metadata remain usable in PowerPoint
- quality comes from templates, CSS, typography, and browser rendering

### PowerPoint MCP
PowerPoint MCP is a **native presentation editing interface**.

It works by manipulating PowerPoint objects directly:
- slides
- text boxes
- tables
- charts
- connectors
- images
- masters
- transitions
- formatting

This means:
- you can edit a real `.pptx` at object level
- outputs stay structurally editable as PowerPoint objects
- visual fidelity is bounded by PowerPoint / python-pptx style primitives and the MCP server feature set

---

## Mental Model

### ForgeDeck
- input = structured narrative/content payload
- output = polished visual artifact
- best for repeatable deck generation

### PowerPoint MCP
- input = existing or new presentation plus editing instructions
- output = modified PowerPoint file with editable native elements
- best for direct authoring/editing tasks

---

## Design Quality Tradeoff

### ForgeDeck strengths
- real typography
- gradients, glass, shadows, depth
- custom fonts
- modern CSS composition
- pixel-perfect repeatability
- premium design system fidelity

### ForgeDeck limitation
- final slides are image-backed, not fully native editable compositions

### PowerPoint MCP strengths
- native slide object manipulation
- editable text boxes, charts, tables, shapes
- useful for incremental changes to working decks

### PowerPoint MCP limitation
- visual design ceiling is lower for premium system-driven output
- it is not the ideal engine for high-fidelity generated design language

---

## Best-Fit Use Cases

## Use ForgeDeck for
- executive briefings generated from structured data
- strategy decks
- product overview decks
- architecture presentations
- operational review decks
- board/update packs
- stakeholder summaries where visual polish matters
- repeatable branded presentation generation

## Use PowerPoint MCP for
- opening an existing client deck and editing copy
- changing chart data in an existing deck
- adding or editing tables, bullets, or shapes
- adjusting slides manually after generation
- inserting speaker notes into a native-editable deck
- patching or extending a presentation someone already authored in PowerPoint terms

---

## Workflow Patterns

## Pattern A — ForgeDeck first, PowerPoint MCP later
Use this when you want a premium generated base deck and maybe some manual edits afterward.

1. Generate deck in ForgeDeck
2. Download `.pptx`
3. If necessary, open in PowerPoint MCP for targeted edits

Good for:
- high-quality generated base decks
- small manual patching after generation

---

## Pattern B — PowerPoint MCP only
Use this when the deck is primarily a native PowerPoint editing problem.

1. Open presentation in PowerPoint MCP
2. Modify slides directly
3. Save presentation

Good for:
- updating an existing deck
- object-level editing
- chart/table/text corrections

---

## Pattern C — ForgeDeck as the engine behind another Forge tool
Use this when another product needs deck output.

Example:
- ForgePipeline wants a status deck
- ForgeDiscord routes a `/deck build` request
- ForgeOrchestra generates an executive briefing

Flow:
1. orchestration layer creates structured payload
2. ForgeDeck builds visual deck
3. output link returned to requesting surface

---

## Product Boundary Table

| Dimension | ForgeDeck | PowerPoint MCP |
|---|---|---|
| Primary role | Premium deck generation | Native PPTX editing |
| Best input | Structured content JSON | Existing presentation or direct editing instructions |
| Visual engine | HTML/CSS + browser render | PowerPoint object model |
| Output type | Image-backed premium deck with notes/metadata | Native editable PowerPoint file |
| Strength | Design quality and repeatability | Editability and object-level control |
| Weakness | Lower native editability of final visuals | Lower design ceiling for premium generated output |
| Best for | New generated decks | Editing / patching / refining decks |

---

## Ecosystem Role

### ForgeDeck in the Forge ecosystem
ForgeDeck should be the default engine when Forge products need:
- generated presentation artifacts
- premium visual output
- repeatable template-based slide production

### PowerPoint MCP in the Forge ecosystem
PowerPoint MCP should be the default tool when Forge products or operators need:
- deck editing
- post-generation tweaks
- direct manipulation of existing presentation elements

---

## Decision Rules

When deciding which tool to use, ask:

### 1. Is this a generation problem or an editing problem?
- generation → ForgeDeck
- editing → PowerPoint MCP

### 2. Does visual polish matter more than native editability?
- visual polish → ForgeDeck
- editability → PowerPoint MCP

### 3. Is the input structured content or an existing deck?
- structured content → ForgeDeck
- existing deck → PowerPoint MCP

### 4. Is this part of a repeatable deck-production workflow?
- yes → ForgeDeck
- no / ad hoc editing → PowerPoint MCP

---

## Recommended Operating Rule

### Standard rule
- **ForgeDeck** = create premium generated decks
- **PowerPoint MCP** = edit or refine decks as PowerPoint documents

### Practical rule
If you are building a deck system, use ForgeDeck.
If you are fixing a slide, use PowerPoint MCP.

---

## Future Combined Strategy

The strongest combined model is not choosing one forever. It is using both in sequence when needed.

### Recommended stack
- ForgeDeck for first-pass generation and design quality
- PowerPoint MCP for downstream object-level edits where required

This gives:
- quality at generation time
- flexibility at editing time

---

## Risks of Confusing Them

### If you misuse ForgeDeck
You may expect native editability that the output is not optimized for.

### If you misuse PowerPoint MCP
You may spend too much effort trying to make python-pptx / native primitives imitate a design system they were never meant to carry elegantly.

### Net result
Wrong tool choice leads to:
- worse quality
- slower work
- confusion about product roles
- avoidable frustration

---

## Final Recommendation

Treat the boundary as fixed:

### ForgeDeck
**The premium presentation foundry**
- structured input
- repeatable layout system
- premium visual output
- ecosystem generation engine

### PowerPoint MCP
**The PowerPoint editing toolkit**
- native `.pptx` manipulation
- object-level updates
- refinement and patching layer

This is the cleanest model, and it keeps both tools useful instead of forcing either one to pretend to be the other.
