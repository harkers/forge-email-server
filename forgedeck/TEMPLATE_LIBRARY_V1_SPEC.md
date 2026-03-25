# ForgeDeck — Template Library v1 Specification

## Status
Draft

## Purpose

This specification defines the first serious layout library for ForgeDeck.

Template Library v1 is intended to give ForgeDeck enough coverage to generate premium decks for recurring Forge use cases without forcing every presentation back into ad hoc slide invention.

This is not a random bucket of layouts. It is a deliberately shaped presentation system.

---

## Design Goals

Template Library v1 should:
- cover the most common deck patterns used across Forge work
- support strong narrative flow, not just pretty isolated slides
- align with premium Forge visual language
- be easy to invoke from structured content
- be predictable for agents and orchestration systems
- separate content schema from visual implementation

---

## Core Principles

### 1. Narrative before novelty
Layouts should support communication clearly. Decorative weirdness is not a product strategy.

### 2. Structured contracts
Every template must have a defined content schema.

### 3. Reusable composition
A good template should work across multiple products and contexts, not only one oddly specific moment.

### 4. Premium but controlled
The system should feel polished, but should avoid becoming visually overcaffeinated.

### 5. Forge-family consistency
The library should be compatible with ForgeOrchestra-level visual direction and adaptable to other Forge products through accent/theme modes.

---

## Template Families

Template Library v1 is organised into families.

## Family A — Identity & Framing
Used to open decks, define sections, and establish key messages.

### T1 — Cover
**Purpose:** Open the deck with title, subtitle, classification, and audience framing.

**Use for:**
- deck start
- executive briefing cover
- strategy deck opening

**Required fields:**
- `title`
- `subtitle`

**Optional fields:**
- `tag`
- `descriptor`
- `audience`
- `classification`
- `date_label`

**Notes:**
Should feel authoritative and restrained.

---

### T2 — Section Divider
**Purpose:** Introduce a new section cleanly.

**Required fields:**
- `title`

**Optional fields:**
- `tag`
- `body`
- `accent`

**Use for:**
- transitions between major themes
- chapter markers

---

### T3 — Statement
**Purpose:** Present one bold key message or argument.

**Required fields:**
- `statement`

**Optional fields:**
- `tag`
- `body`
- `accent`

**Use for:**
- executive takeaway
- key thesis
- narrative pivot

---

## Family B — Structured Exposition
Used when explaining ideas, structures, tradeoffs, and grouped information.

### T4 — Two Column
**Purpose:** Show two parallel sets of information.

**Required fields:**
- `title`
- `left`
- `right`

**Expected nested structure:**
- `left.label`
- `left.items[]`
- `right.label`
- `right.items[]`

**Use for:**
- problems vs response
- current vs future
- option A vs option B

---

### T5 — Three Column
**Purpose:** Present three coordinated pillars or streams.

**Required fields:**
- `title`
- `columns`

**Requirements:**
- `columns` must contain exactly 3 items

**Use for:**
- strategic pillars
- delivery tracks
- operating model components

---

### T6 — Four Column
**Purpose:** Present a compact set of four options/cards.

**Required fields:**
- `title`
- `cards`

**Requirements:**
- `cards` must contain exactly 4 items

**Use for:**
- scenarios
- options
- categories
- control sets

---

### T7 — Grid 6
**Purpose:** Present six concise idea cards in a two-row grid.

**Required fields:**
- `title`
- `cards`

**Requirements:**
- `cards` must contain exactly 6 items

**Use for:**
- capabilities
- principles
- workstreams
- modules

---

## Family C — Process & Time
Used for showing flow, stages, mechanisms, and sequence.

### T8 — Roadmap
**Purpose:** Show a phased timeline or plan.

**Required fields:**
- `title`
- `phases`

**Requirements:**
- v1 default assumes 3 phases

**Phase shape:**
- `label`
- `title`
- `items[]`
- optional `color_class`

**Use for:**
- implementation phases
- product roadmap
- rollout plan

---

### T9 — Mechanisms
**Purpose:** Explain how a system works through structured mechanism cards.

**Required fields:**
- `title`
- `cards`

**Requirements:**
- v1 assumes 4 cards

**Use for:**
- system flows
- operating model explanation
- governance/control mechanisms

---

### T10 — Timeline / Sequence
**Purpose:** Show ordered progression with clearer temporal structure than a roadmap.

**Required fields:**
- `title`
- `steps`

**Use for:**
- incident sequence
- implementation steps
- lifecycle explanation

---

## Family D — Evidence & Comparison
Used for comparing states, surfacing metrics, and showing analytical content.

### T11 — Comparison
**Purpose:** Compare two or more options clearly.

**Required fields:**
- `title`
- `items`

**Use for:**
- ForgeDeck vs PowerPoint MCP
- current state vs target state
- tool comparison

---

### T12 — Metrics / Scoreboard
**Purpose:** Present headline numbers and supporting labels.

**Required fields:**
- `title`
- `metrics`

**Use for:**
- KPI overview
- program status
- product performance snapshot

---

### T13 — Risk / Watchlist
**Purpose:** Show risks, blockers, watch items, or dependency concerns.

**Required fields:**
- `title`
- `items`

**Use for:**
- project risks
- decision blockers
- dependency warnings

---

## Family E — Closing & Support
Used to close the narrative or append supporting material.

### T14 — Summary / Next Actions
**Purpose:** End with concise recommendations and next steps.

**Required fields:**
- `title`
- `actions`

**Use for:**
- final slide
- decisions requested
- next-step summary

---

### T15 — Appendix / Reference
**Purpose:** Add lower-priority support content.

**Required fields:**
- `title`
- `items`

**Use for:**
- references
- supporting notes
- definitions

---

## Content Contract Pattern

Each template should support a consistent payload pattern.

### Standard top-level pattern
```json
{
  "layout": "template-name",
  "data": {
    "tag": "optional section tag",
    "title": "main title",
    "intro": "optional intro",
    "...": "template-specific fields"
  },
  "notes": "optional speaker notes"
}
```

### Rules
- `layout` selects the template
- `data` contains only template-relevant values
- `notes` stays separate from visual content
- template-specific schemas should be documented and validated

---

## Shared Visual Rules

Template Library v1 should inherit shared visual rules.

### Shared shell behavior
- consistent slide margins
- consistent title zone behavior
- consistent footer/slide number logic
- restrained use of accents
- premium dark-first surfaces by default

### Typography rules
- large clear display title
- restrained subtitle/body scale
- mono or semi-mono for technical/status elements where useful
- avoid walls of tiny text

### Density rules
- no template should encourage overstuffed slides
- if the content exceeds sensible density, split across slides

### Accent rules
- accents should communicate hierarchy, grouping, or emphasis
- accents should not become decorative noise

---

## Theme Compatibility

Template Library v1 should support a base ForgeDeck mode and future theme overlays.

### Base mode
- Obsidian Narrative
- premium dark architectural presentation system

### Future overlays
- ForgeOrchestra mode
- product-specific accent sets
- executive mode
- technical mode
- investor mode

V1 templates should be written so theme changes alter tokens rather than requiring fully separate templates.

---

## Required Documentation Per Template

Every template in v1 should eventually have:
- purpose
- best use cases
- required fields
- optional fields
- example payload
- layout preview
- anti-pattern guidance

Example anti-pattern guidance:
- don’t use Grid 6 for long paragraphs
- don’t use Statement for multi-argument exposition
- don’t force Metrics when no real metric hierarchy exists

---

## Suggested Initial V1 Priority Set

If implementing in strict order, start with:
1. Cover
2. Section Divider
3. Statement
4. Two Column
5. Three Column
6. Grid 6
7. Roadmap
8. Comparison
9. Metrics
10. Summary / Next Actions

That gives enough range to generate strong strategy, architecture, and update decks quickly.

---

## Example Deck Composition Patterns

### Strategy deck
- Cover
- Statement
- Three Column
- Roadmap
- Risk / Watchlist
- Summary / Next Actions

### Product architecture deck
- Cover
- Section Divider
- Mechanisms
- Two Column
- Comparison
- Summary / Next Actions

### Executive update deck
- Cover
- Metrics
- Grid 6
- Roadmap
- Summary / Next Actions

---

## Validation Requirements

V1 should validate:
- template exists
- required fields present
- item counts where fixed (3, 4, 6, etc.)
- field types correct
- no obviously malformed payloads

Validation errors should be clear enough that another agent or operator can fix the payload without guessing.

---

## Non-Goals for V1

V1 does not need:
- every imaginable niche template
- free-form visual chaos
- auto-layout magic for wildly malformed content
- dozens of near-duplicate slide styles

V1 should be small, strong, and reusable.

---

## Final Recommendation

Template Library v1 should be treated as:

**the foundational presentation vocabulary for ForgeDeck**

It should cover the core narrative patterns that Forge products actually need, while staying structured enough for reliable generation and polished enough to justify ForgeDeck existing at all.
