# ForgeDeck — Implementation Backlog v1.0

## Purpose

This backlog turns ForgeDeck from a strong architecture idea into concrete build work.

It assumes the product direction is now clear:
ForgeDeck is the **premium presentation foundry** for the Forge ecosystem.

The backlog is structured around practical delivery, not theatrical ticket inflation.

---

## Delivery Tracks

### Track A — Core runtime and API
Covers service stability, MCP/tool layer, validation, and output handling.

### Track B — Template and design system
Covers layout quality, CSS tokens, visual consistency, and deck composition standards.

### Track C — Ecosystem integration
Covers how ForgeDeck is invoked by ForgeOrchestra, ForgeDiscord, ForgePipeline, and related tools.

### Track D — Product ergonomics
Covers preview, discovery, artifact handling, and operator usability.

---

## Priority Scale
- **P0** = essential
- **P1** = strongly recommended next
- **P2** = post-MVP / expansion

---

# Stage 1 — Core Runtime Hardening

## FG-001 Document and stabilise service runtime
**Priority:** P0

### Scope
- verify startup behavior
- verify health endpoint reliability
- document runtime assumptions
- ensure graceful shutdown for browser resources

### Deliverables
- runtime notes
- startup/shutdown checks
- reliability checklist

---

## FG-002 Improve request validation
**Priority:** P0

### Scope
- validate deck payload shape before render
- validate layout existence
- validate required fields for each layout
- return clear errors

### Deliverables
- validation layer
- better error messages
- malformed payload tests

---

## FG-003 Standardise output filename handling
**Priority:** P0

### Scope
- slug rules
- collision handling
- extension enforcement
- unsafe character cleanup

### Deliverables
- output naming policy
- tests for filename generation

---

## FG-004 Add deck manifest metadata output
**Priority:** P1

### Scope
- generate deck summary metadata
- capture layout usage
- include slide count and output details

### Deliverables
- deck manifest structure
- optional sidecar metadata file

---

## FG-005 Add structured logging
**Priority:** P1

### Scope
- request logging
- render timing
- error classification
- output generation logs

### Deliverables
- log format
- operational troubleshooting visibility

---

# Stage 2 — Template Contracts and Layout System

## FG-010 Define template contracts for all layouts
**Priority:** P0

### Scope
- required fields per layout
- optional fields per layout
- field semantics
- content examples

### Deliverables
- template schema docs
- machine-usable validation mapping

---

## FG-011 Formalize template library v1
**Priority:** P0

### Initial templates
- cover
- section
- framing
- two-column
- three-column
- four-column
- grid-6
- roadmap
- mechanisms
- statement
- metrics
- appendix

### Deliverables
- template inventory
- coverage matrix
- examples

---

## FG-012 Build base design token system
**Priority:** P0

### Scope
- spacing scale
- typography scale
- palette
- panel/card tokens
- depth/shadow/glow rules
- numbering and footer behavior

### Deliverables
- `base.css`
- token conventions
- visual rule set

---

## FG-013 Add local/custom font support in container
**Priority:** P0

### Scope
- install preferred font stack
- verify browser rendering uses intended fonts
- document fallback stack

### Deliverables
- font install path
- font QA notes

---

## FG-014 Create visual QA deck set
**Priority:** P1

### Scope
- sample deck per major template family
- screenshot/output review
- consistency check

### Deliverables
- regression sample deck set
- QA review checklist

---

# Stage 3 — Render Pipeline Quality

## FG-020 Improve Playwright rendering reliability
**Priority:** P0

### Scope
- asset resolution reliability
- browser reuse optimization
- timeout handling
- deterministic render settings

### Deliverables
- renderer hardening
- reliability notes

---

## FG-021 Add single-slide preview workflow improvements
**Priority:** P1

### Scope
- cleaner preview responses
- easier inspection of template output
- optional preview metadata

### Deliverables
- improved `render_slide` behavior
- preview response schema

---

## FG-022 Add render performance instrumentation
**Priority:** P1

### Scope
- per-slide render timings
- total deck timing
- render bottleneck visibility

### Deliverables
- timing metrics in logs or metadata

---

## FG-023 Add temporary render/cache lifecycle strategy
**Priority:** P2

### Scope
- temp files if introduced
- cleanup behavior
- optional image cache policy

---

# Stage 4 — PPTX Assembly Layer Refinement

## FG-030 Document assembly-layer constraints explicitly
**Priority:** P0

### Scope
- image-backed slide rule
- notes behavior
- metadata support
- tradeoffs vs native-editable presentations

### Deliverables
- assembly notes
- user-facing constraints doc

---

## FG-031 Expand metadata handling
**Priority:** P1

### Scope
- title
- subject
- author
- keywords
- comments
- classification labels where useful

### Deliverables
- richer PPTX metadata mapping

---

## FG-032 Improve speaker notes contract
**Priority:** P1

### Scope
- note formatting rules
- optional default notes behavior
- consistent note insertion

### Deliverables
- note schema guidance
- tests for notes handling

---

# Stage 5 — API / MCP Surface Maturity

## FG-040 Add template introspection endpoint/tool
**Priority:** P1

### Scope
- list available templates
- return required fields
- return optional fields
- return example payloads

### Deliverables
- better discovery for agents/operators

---

## FG-041 Add `validate_deck_payload` tool
**Priority:** P1

### Scope
- validate without rendering
- catch missing fields early
- support orchestration systems before build step

### Deliverables
- validation tool contract

---

## FG-042 Add artifact listing improvements
**Priority:** P1

### Scope
- richer `/decks` output
- timestamps
- size
- optional manifest link

---

## FG-043 Add artifact retention / cleanup policy
**Priority:** P2

### Scope
- cleanup strategy
- retention windows
- archival rules

---

# Stage 6 — Forge Ecosystem Integration

## FG-050 Define ForgeOrchestra invocation contract
**Priority:** P1

### Scope
- standard payload shape for strategy/product decks
- output expectations
- audience modes

### Deliverables
- contract doc
- example payloads

---

## FG-051 Define ForgePipeline reporting deck contract
**Priority:** P1

### Scope
- portfolio review deck
- project update deck
- board/status pack

### Deliverables
- payload templates
- route examples

---

## FG-052 Define ForgeDiscord request flow for deck generation
**Priority:** P1

### Scope
- how Discord requests create deck jobs
- approval behavior if needed
- output delivery in-thread or via result channel

### Deliverables
- Discord invocation pattern
- routing expectations

---

## FG-053 Define ForgeDeck ↔ PowerPoint MCP handoff pattern
**Priority:** P1

### Scope
- when ForgeDeck generates first-pass output
- when PowerPoint MCP takes over for edits
- clear combined workflow guidance

### Deliverables
- handoff workflow note
- example operator patterns

---

# Stage 7 — Product Ergonomics

## FG-060 Add template browser/operator discovery surface
**Priority:** P2

### Scope
- view available templates
- see sample outputs
- compare layouts

---

## FG-061 Add deck history / artifact view
**Priority:** P2

### Scope
- recent decks
- metadata listing
- download/manage output artifacts

---

## FG-062 Add audience modes
**Priority:** P2

### Examples
- executive
- technical
- product
- investor

### Deliverables
- audience mode token changes
- template behavior variants

---

## FG-063 Add narrative linting / structure checks
**Priority:** P2

### Scope
- detect weak deck structure
- detect missing framing/summary patterns
- suggest improvements before build

---

# MVP Milestones

## Milestone M1 — Stable service foundation
Includes:
- FG-001
- FG-002
- FG-003
- FG-010
- FG-012
- FG-013

## Milestone M2 — Credible design engine
Includes:
- FG-011
- FG-014
- FG-020
- FG-021
- FG-030
- FG-032

## Milestone M3 — Ecosystem-ready service
Includes:
- FG-040
- FG-041
- FG-042
- FG-050
- FG-051
- FG-052
- FG-053

---

# Recommended First Build Order

1. FG-002 request validation
2. FG-010 template contracts
3. FG-012 base design token system
4. FG-013 local/custom font support
5. FG-011 template library v1
6. FG-020 Playwright render hardening
7. FG-030 assembly constraints doc
8. FG-040 template introspection
9. FG-041 validate_deck_payload tool
10. FG-050 / FG-051 / FG-052 ecosystem contracts

This gets ForgeDeck from “good idea with working code” to “credible product subsystem.”

---

# Suggested First Sprint

## Sprint 1
- FG-002
- FG-010
- FG-012
- FG-013

### Outcome
ForgeDeck gains proper input contracts and real visual-system foundations.

## Sprint 2
- FG-011
- FG-020
- FG-021
- FG-030

### Outcome
ForgeDeck becomes visually and operationally more trustworthy.

## Sprint 3
- FG-040
- FG-041
- FG-050
- FG-051
- FG-052

### Outcome
ForgeDeck becomes ecosystem-usable, not just technically interesting.

---

# Final Recommendation

Treat this backlog as the bridge between architecture and adoption.

The most important early work is not random feature accumulation. It is:
- template contracts
- token/design system maturity
- render reliability
- clear ecosystem invocation patterns

That is what turns ForgeDeck into the real presentation foundry for Forge.
