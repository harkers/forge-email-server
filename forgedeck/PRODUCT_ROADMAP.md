# ForgeDeck — Product Roadmap v1.0

## Purpose

This roadmap defines how ForgeDeck should evolve from a technically sound deck-generation service into a real Forge ecosystem product.

ForgeDeck is not just a script that happens to output `.pptx` files.
It should become the **presentation foundry** for the Forge ecosystem: structured content in, premium decks out.

---

## Product Position

### Core product role
ForgeDeck is a **premium deck-generation engine** built for:
- executive updates
- strategy decks
- product briefs
- architecture presentations
- operational reviews
- investor-style and stakeholder-ready deck outputs

### Product promise
One structured input → one polished deck artifact.

### Key differentiator
ForgeDeck does not try to author decks using raw PowerPoint primitives as its main design surface.
Instead, it uses web-grade visual systems and assembles final delivery decks through a controlled pipeline.

---

## Strategic Goals

### Goal 1 — Make deck generation credible
Decks should look designed, not merely generated.

### Goal 2 — Standardise narrative output across Forge tools
ForgeOrchestra, ForgeDiscord, ForgePipeline, and related systems should be able to generate presentation artifacts through a consistent engine.

### Goal 3 — Separate content from presentation
Users and agents should work with structured content; ForgeDeck should handle layout and visual composition.

### Goal 4 — Create reusable presentation infrastructure
Decks should be built from repeatable templates, design tokens, and output modes rather than slide-by-slide improvisation.

---

## Product Stages

## Stage 1 — Technical Foundation
**Status:** partially present

### Outcome
ForgeDeck is operational as a working deck-generation service.

### Scope
- FastAPI service online
- MCP-style tool surface
- build_deck flow works
- render_slide preview works
- PPTX assembly works
- output storage works

### Current strengths
- correct architectural direction already chosen
- Playwright rendering in place
- python-pptx correctly relegated to assembly layer
- API and Docker deployment already present

### Remaining foundation work
- document template contracts
- improve font handling
- tighten output lifecycle/retention
- add payload validation by layout

---

## Stage 2 — Design System Maturity

### Goal
Turn ForgeDeck from a rendering service into a visually coherent deck engine.

### Scope
- create robust `base.css` / token system
- align with ForgeOrchestra parent visual language
- establish typography stack
- add premium slide patterns
- define audience modes

### Key features
- design tokens for spacing, type, color, depth
- consistent slide chrome, headers, footers, numbering
- executive / product / technical style variants
- reusable card systems and narrative layouts

### Deliverables
- style token file
- layout library v1
- visual QA standards
- sample deck gallery

---

## Stage 3 — Template System Expansion

### Goal
Expand ForgeDeck into a practical deck-production system.

### Scope
Build a usable set of layout families.

### Priority layouts
- cover
- section divider
- framing / key message
- two-column
- three-column
- four-column
- grid-6
- roadmap / timeline
- process / mechanisms
- comparison
- metrics / scoreboard
- quote / statement
- appendix / reference

### Deliverables
- layout schemas
- per-template required fields
- preview examples
- template documentation

---

## Stage 4 — Content Contract & Validation Layer

### Goal
Make inputs reliable and easier for agents and users to generate.

### Scope
- schema validation by layout
- better error messages
- template discovery
- structured deck manifest output

### Features
- reject malformed slide data cleanly
- explain missing required fields
- list templates with field requirements
- optionally emit deck manifest/summary alongside output

### Benefit
This makes ForgeDeck much easier to use programmatically from OpenClaw and other Forge tools.

---

## Stage 5 — Ecosystem Integration

### Goal
Make ForgeDeck a native service within the Forge ecosystem.

### Integrations
#### ForgeOrchestra
Use ForgeDeck for:
- strategy decks
- system briefings
- operating reviews
- roadmap presentations

#### ForgeDiscord
Use ForgeDeck as a routed output surface for:
- presentation requests
- summary decks
- stakeholder pack generation

#### ForgePipeline
Use ForgeDeck for:
- project status decks
- portfolio reviews
- board/update packs

### Deliverables
- documented invocation patterns
- shared output contracts
- standard deck request payloads for ecosystem tools

---

## Stage 6 — Product Surface Expansion

### Goal
Move beyond a raw API-only service.

### Possible directions
- operator UI for previewing and generating decks
- template browser
- deck history page
- output management UI
- audience mode chooser
- deck diff/version compare

### Decision point
Determine whether ForgeDeck remains:
1. internal infrastructure only
2. developer/operator tool
3. full standalone Forge product

Most likely path:
- start as infrastructure/service
- grow into operator-facing tool
- later become a standalone Forge product if demand justifies it

---

## Stage 7 — Advanced Output Intelligence

### Goal
Make the system smarter about narrative structure and output quality.

### Potential features
- deck outline recommendation
- slide-type recommendation from content structure
- executive summary mode
- automatic appendix generation
- design linting / deck quality checks
- audience-aware phrasing presets
- layout balancing rules

### Important rule
ForgeDeck should help structure and polish outputs, but should not become a chaotic pseudo-designer inventing nonsense because a payload was vague.

---

## Product Tracks

## Track A — Platform / Engineering
Focus:
- runtime stability
- rendering reliability
- deployment
- storage
- performance
- API/tool surface

## Track B — Design System / Templates
Focus:
- template quality
- typography
- hierarchy
- visual coherence
- audience modes
- design tokens

## Track C — Ecosystem Integration
Focus:
- OpenClaw workflows
- ForgeOrchestra integration
- ForgeDiscord routing
- ForgePipeline reporting
- deck request contracts

## Track D — Product Surface
Focus:
- usability
- preview flow
- template discovery
- output management
- operator interface

---

## Roadmap by Version

## v0.1 — Working Engine
### Focus
Basic operational service.

### Includes
- API online
- core templates
- deck build flow
- deck download/listing

---

## v0.2 — Design Foundation
### Focus
Visual consistency and better templates.

### Includes
- base.css/design tokens
- improved type scale
- more premium layouts
- better template naming and schema docs

---

## v0.3 — Validation & Contract Layer
### Focus
Reliable structured input.

### Includes
- payload validation by layout
- clearer tool output
- template contract docs
- better error responses

---

## v0.4 — Forge Integration
### Focus
Native use inside Forge ecosystem.

### Includes
- documented use from ForgeOrchestra
- ForgeDiscord routing support
- ForgePipeline reporting patterns
- standard deck request payloads

---

## v0.5 — Operator Tooling
### Focus
Better human usability.

### Includes
- preview workflow improvements
- template browser/discovery
- operator docs
- artifact management improvements

---

## v1.0 — Premium Presentation Foundry
### Focus
ForgeDeck becomes the standard deck engine for Forge.

### Includes
- mature template library
- stable render pipeline
- strong visual system
- ecosystem-wide integration
- documented product role
- audience modes
- quality standards

---

## Risks

### Risk 1 — Beautiful pipeline, weak templates
If templates are mediocre, the architecture still produces mediocre decks.

### Risk 2 — Service remains too infra-only
If no operator surface or ecosystem contracts are defined, adoption will stay narrow.

### Risk 3 — Confusion with PowerPoint MCP
If the boundary is not clear, people will misuse one tool for the other.

### Risk 4 — Font/design inconsistency in container
Without proper font and asset handling, quality drops fast.

### Risk 5 — Overengineering before use cases solidify
Keep the roadmap grounded in actual presentation workflows.

---

## Success Criteria

ForgeDeck is succeeding when:
- generated decks look intentionally designed
- Forge tools can request decks through a stable contract
- the output is stakeholder-ready without ugly manual cleanup
- template coverage supports recurring real-world use cases
- operators understand when to use ForgeDeck vs PowerPoint MCP
- ForgeDeck becomes the obvious deck-generation path inside Forge

---

## Recommended Next Product Moves

1. define the boundary between ForgeDeck and PowerPoint MCP
2. create an implementation backlog
3. define template library v1
4. define design token system for deck rendering
5. define first ecosystem integrations (ForgeOrchestra / ForgePipeline / ForgeDiscord)

---

## Final Recommendation

ForgeDeck should be built and positioned as:

**the premium presentation foundry for the Forge ecosystem**

That means:
- design-first output
- structured content contracts
- repeatable layouts
- premium visual systems
- orchestration-friendly invocation
- clear ecosystem role

That is a real product direction, not just a clever rendering trick.
