# ForgeDeck — Ecosystem Integration Specification v1.0

## Status
Draft

## Purpose

This specification defines how ForgeDeck should integrate with the rest of the Forge ecosystem.

ForgeDeck is not meant to sit in isolation as a clever rendering service. Its value increases when it becomes the standard presentation-generation engine for Forge products that need polished deck outputs.

This document defines that relationship.

---

## Integration Thesis

ForgeDeck should serve as the **presentation foundry** for Forge.

That means other Forge products should be able to:
- prepare structured content
- invoke ForgeDeck through a stable contract
- receive downloadable deck artifacts
- use those artifacts in workflows, reviews, updates, and outputs

In short:
- Forge products create the content and context
- ForgeDeck creates the presentation artifact

---

## Ecosystem Role

### ForgeDeck is responsible for
- deck template rendering
- visual system consistency
- deck assembly
- artifact production
- slide output quality

### Other Forge systems are responsible for
- deciding why a deck is needed
- generating structured content payloads
- choosing audience/use case
- routing requests
- handling approvals and user interaction where relevant

---

## Integration Model

### Standard pattern
Forge product  
→ structured deck payload  
→ ForgeDeck build request  
→ generated `.pptx` artifact  
→ requesting product receives URL/filename/result metadata

### Optional follow-on pattern
ForgeDeck output  
→ PowerPoint MCP for native edit pass if required

This preserves a clean division between generation and editing.

---

## Shared Contract Principles

Every integration should agree on:
- deck request payload structure
- output response shape
- artifact handling rules
- audience/theme signaling
- approval behavior where needed
- ownership of post-generation editing

---

## Canonical Deck Request Shape

### Proposed request shape
```json
{
  "title": "Quarterly Portfolio Review",
  "output_filename": "q2-portfolio-review",
  "audience_mode": "executive",
  "theme_mode": "forgeorchestra",
  "context": {
    "source_product": "forgepipeline",
    "workspace": "portfolio-review",
    "classification": "internal"
  },
  "slides": [
    {
      "layout": "cover",
      "data": {
        "title": "Quarterly Portfolio Review",
        "subtitle": "Q2 2026"
      },
      "notes": "Open with status and framing"
    }
  ]
}
```

### Required top-level fields
- `title`
- `slides`

### Recommended top-level fields
- `output_filename`
- `audience_mode`
- `theme_mode`
- `context`

---

## Canonical Response Shape

### Proposed response
```json
{
  "filename": "q2-portfolio-review.pptx",
  "download_url": "http://localhost:18103/download/q2-portfolio-review.pptx",
  "slide_count": 8,
  "message": "Built 8-slide deck: q2-portfolio-review.pptx"
}
```

### Optional future additions
- render duration
- warnings
- manifest URL
- template usage summary

---

## Integration by Forge Product

## 7.1 ForgeOrchestra Integration

### Role
ForgeOrchestra is the orchestration and command layer.
It should use ForgeDeck when deck output is part of a strategic, operational, or system-wide communication workflow.

### High-value use cases
- strategy decks
- roadmap decks
- architecture decks
- operating review decks
- executive update packs
- product family overview decks

### Integration pattern
1. ForgeOrchestra decides a deck is needed
2. It compiles structured content from the relevant workflow
3. It maps that content into ForgeDeck slide payloads
4. It calls ForgeDeck
5. It receives deck artifact details
6. It returns or distributes the result

### Requirements
- standard payload templates for recurring deck types
- theme alignment with ForgeOrchestra visual system
- support for executive and technical audience modes

---

## 7.2 ForgePipeline Integration

### Role
ForgePipeline is the portfolio and project visibility layer.
It should use ForgeDeck to turn structured project data into presentation artifacts.

### High-value use cases
- project status decks
- portfolio review decks
- board packs
- quarterly progress decks
- risk and roadmap presentations

### Integration pattern
1. ForgePipeline collects portfolio/project state
2. It transforms data into a deck payload
3. It chooses templates such as:
   - cover
   - metrics
   - grid-6
   - roadmap
   - risk/watchlist
   - summary / next actions
4. It calls ForgeDeck
5. It stores or surfaces the result for review/download

### Requirements
- canonical ForgePipeline-to-ForgeDeck payload schema
- repeatable board/update deck patterns
- optional future scheduled report generation

---

## 7.3 ForgeDiscord Integration

### Role
ForgeDiscord is the intake and coordination layer.
It should route presentation requests to ForgeDeck when a user or workflow needs a generated deck.

### High-value use cases
- build an executive summary deck from a request thread
- generate a stakeholder deck from structured intake
- create a progress pack from a workflow result
- produce a polished deck artifact for review/approval

### Integration pattern
1. User triggers a deck-related workflow in Discord
2. ForgeDiscord routes request to the correct workspace/workflow
3. Orchestrator or specialist workflow produces structured slide payload
4. ForgeDeck builds deck
5. ForgeDiscord posts status and final artifact link into thread/output channel

### Requirements
- request-to-deck workflow mapping
- clear approval behavior before distribution if sensitive
- concise Discord result summaries

### Important note
ForgeDiscord should not take over ForgeDeck’s job.
It coordinates the request; ForgeDeck renders the deck.

---

## 7.4 ForgeDeck + PowerPoint MCP Combined Workflow

### Role split
- ForgeDeck = generate premium first-pass deck
- PowerPoint MCP = native edit/refinement layer

### Use case
A Forge workflow may need a polished generated deck, followed by targeted manual/object-level edits.

### Combined flow
1. structured payload sent to ForgeDeck
2. deck generated
3. if native edits are required, deck passed to PowerPoint MCP
4. PowerPoint MCP applies table/chart/text/object changes
5. final deck delivered

### Good use cases
- generated board pack with later manual edits
- premium architecture deck with small last-mile changes
- executive deck requiring final direct object edits

---

## Context and Metadata Rules

Integrated requests should include context metadata where possible.

### Recommended context fields
- `source_product`
- `workspace`
- `request_id`
- `classification`
- `audience_mode`
- `theme_mode`
- `owner`

### Why
This helps:
- traceability
- artifact management
- auditability
- better downstream handling

---

## Approval and Governance Considerations

Not every deck needs approval, but some do.

### Approval-relevant scenarios
- client-facing deck generation
- executive or board pack generation
- sensitive incident or compliance summary deck
- external distribution workflows

### Recommended rule
The product requesting ForgeDeck owns approval policy.
ForgeDeck builds the artifact; the caller decides whether the artifact can be released.

Examples:
- ForgeDiscord may require approval before posting a final deck link
- ForgeOrchestra may require signoff for executive decks
- ForgePipeline may require internal review before board pack release

---

## Artifact Handling Rules

### Core rules
- ForgeDeck outputs are artifacts, not permanent records by default
- requesting products should decide whether to store links, manifests, or references
- retention and cleanup policies should be defined intentionally

### Recommended approach
- ForgeDeck provides artifact URL and metadata
- caller stores reference if needed
- artifact retention policy handled centrally later

---

## Error Handling in Integrated Flows

If ForgeDeck fails during an ecosystem workflow, the calling product should:
- surface that the build failed
- preserve source request context
- report reason if safe/useful
- offer retry or review path

### Example
- ForgeDiscord thread should show deck generation failure and next action
- ForgePipeline should record report build failure in audit/log context
- ForgeOrchestra should log the failed artifact generation step

---

## Future Integration Extensions

### Potential future additions
- scheduled deck builds from ForgePipeline data
- requestable deck generation via ForgeDiscord command surface
- design-mode variants per Forge product
- manifest sidecars stored for reporting and audit
- automated handoff into review workflows
- artifact gallery or registry for Forge outputs

---

## Non-Goals

This integration spec does not mean:
- every Forge tool should become deck-first
- ForgeDeck should own workflow routing
- ForgeDeck should become the approval engine
- ForgeDeck should become a document repository

It should remain the rendering/artifact engine.

---

## Recommended First Integrations

### Priority order
1. **ForgePipeline**
   - easiest structured-data-to-deck use case
   - natural fit for portfolio and status reporting

2. **ForgeOrchestra**
   - strategic and architecture deck generation
   - premium product/system briefings

3. **ForgeDiscord**
   - request routing and artifact delivery once request flows are stable

---

## Final Recommendation

ForgeDeck should be integrated as a shared Forge service with a stable deck-generation contract.

The clean model is:
- **ForgeOrchestra / ForgePipeline / ForgeDiscord create the request context**
- **ForgeDeck renders the presentation artifact**
- **PowerPoint MCP optionally refines the result if object-level editing is needed**

That keeps the ecosystem modular, sensible, and much less likely to become an overentangled mess.
