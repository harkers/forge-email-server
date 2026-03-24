# Product Family System

## Overview

ForgeOrchestra governs a product family where each product is visually a member of the same house.

### Shared Anatomy (All Products)

Every product inherits:

- ✅ Same logo construction rule
- ✅ Same card system
- ✅ Same nav system
- ✅ Same button language
- ✅ Same type hierarchy
- ✅ Same motion rules
- ✅ Same page shell
- ✅ Same background treatment
- ✅ Same icon grammar
- ✅ Same component anatomy

### Individual Identity Layer

Each child product gets:

- 🎨 One accent colour family
- 🌊 One ambient gradient signature
- 🔷 One iconic motif
- 🖼️ One signature hero illustration style

---

## Product Specifications

### ForgeOrchestra (Parent)

**Role:** Master environment, orchestration layer

**Accent:** Luminous Platinum Blue
- `#7AA6FF` (primary)
- `#9CC3FF` (secondary)
- `#C9D9FF` (tertiary)

**Motif:** Orbital grid, conductor-like motion, branching paths

**Visual Cues:**
- Central hub with controlled paths
- Layered arcs suggesting orchestration
- Balanced symmetry

**Use Cases:**
- System dashboard
- Workflow orchestration
- Cross-product navigation
- Command center

---

### ForgeCalendar

**Role:** Time, scheduling, cadence management

**Accent:** Ice Blue / Time Cyan
- `#7DD3E9` (primary)
- `#B8E8F5` (secondary)

**Motif:** Rings, time arcs, cadence lines

**Visual Cues:**
- Concentric circles
- Flowing time ribbons
- Pulsed rhythm markers
- Clean grid structures

**UI Patterns:**
- Timeline views with smooth arcs
- Event cards with subtle glow
- Calendar grid with hairline dividers
- Time indicators with soft pulse animation

**Motion:**
- Gentle sweeping transitions
- Time-based scroll easing
- Event creation with fluid expansion

---

### ForgePipeline

**Role:** Process orchestration, workflow automation, deployment

**Accent:** Emerald Teal / Process Green
- `#2DD4BF` (primary)
- `#34D399` (secondary)

**Motif:** Branching routes, staged nodes, directional grids

**Visual Cues:**
- Flow diagrams with smooth bezier curves
- Node-based structures
- Progress indicators along paths
- Status gates with clear states

**UI Patterns:**
- Pipeline cards with stage indicators
- Connection lines with animated flow
- Status badges (queued → running → complete)
- Branch/merge visualizations

**Motion:**
- Pulse animation along active paths
- Node activation with soft glow
- Progress fill with smooth easing

---

### ForgeDisplay

**Role:** Presentation layer, broadcast, dashboards

**Accent:** Warm Amber / Broadcast Gold
- `#F59E0B` (primary)
- `#FBBF24` (secondary)

**Motif:** Framed canvases, panels, timed loops

**Visual Cues:**
- Rectangular frames with soft radii
- Layered panel stacks
- Broadcast-style indicators
- Loop/sync symbols

**UI Patterns:**
- Canvas cards with elevated surfaces
- Panel tabs with smooth transitions
- Live indicators with subtle pulse
- Grid layouts with generous spacing

**Motion:**
- Panel slides with controlled ease
- Tab transitions with minimal overshoot
- Content fades with soft opacity shifts

---

### ForgeOpenClaw

**Role:** Agent orchestration, AI workflow, automation

**Accent:** Neural Violet / Deep Indigo
- `#8B5CF6` (primary)
- `#6366F1` (secondary)

**Motif:** Orchestration mesh, command lines, intelligent network

**Visual Cues:**
- Network graphs with weighted edges
- Command pathways
- Intelligence indicators
- Mesh/grid structures

**UI Patterns:**
- Agent cards with status rings
- Command palette with glass surfaces
- Session threads with connecting lines
- Intelligence/processing indicators

**Motion:**
- Network pulse with subtle propagation
- Agent state changes with smooth transitions
- Command execution with trail effects

---

## Product Naming Convention

All products follow the `Forge[Name]` pattern:

```
ForgeOrchestra     (parent)
ForgeCalendar      (time & scheduling)
ForgePipeline      (workflow & automation)
ForgeDisplay       (presentation & dashboards)
ForgeOpenClaw      (agent orchestration)
```

**Future Products:**
- ForgeMemory (knowledge & context)
- ForgeConnect (integration & APIs)
- ForgeAudit (security & compliance)
- ForgeDeploy (infrastructure & releases)

---

## Cross-Product Navigation

### Shared Navigation System

All products use:

- **Side Navigation:** Integrated, not bolted on
  - Width: 280px collapsed, 320px expanded
  - Glass surface with subtle border
  - Product accent glow on active state

- **Top Bar:** Command-aware status
  - Height: 64px
  - Glass surface
  - Breadcrumb + actions

- **Product Switcher:** Unified launcher
  - Grid of product cards
  - Each card shows product accent
  - Smooth transition on switch

### Visual Continuity

When switching between products:

1. **Background stays consistent** (obsidian base)
2. **Accent color transitions** smoothly
3. **Typography unchanged**
4. **Motion language consistent**
5. **Only motif/artwork changes**

---

## Product Artwork System

Each product has signature hero illustrations:

### Style Guidelines

- **Abstract-systemic** (not stock photos)
- **3D-leaning renders** or high-end 2.5D
- **Glass/metallic materials**
- **Luminous accents**
- **Structured forms**

### ForgeCalendar Artwork
- Time rings in ice cyan
- Flowing arcs
- Cadence waveforms
- Clean geometric loops

### ForgePipeline Artwork
- Emerald branching paths
- Staged node clusters
- Directional flow arrows
- Process grid structures

### ForgeDisplay Artwork
- Amber framed panels
- Layered canvas stacks
- Broadcast-style indicators
- Warm luminous planes

### ForgeOpenClaw Artwork
- Violet network meshes
- Command line structures
- Intelligence node clusters
- Neural pathway visualizations

---

## Implementation Notes

### CSS Variables per Product

```css
/* Product-specific accent overrides */
[data-product="calendar"] {
  --accent-primary: var(--calendar-cyan);
  --accent-gradient: var(--gradient-calendar);
}

[data-product="pipeline"] {
  --accent-primary: var(--pipeline-teal);
  --accent-gradient: var(--gradient-pipeline);
}

[data-product="display"] {
  --accent-primary: var(--display-amber);
  --accent-gradient: var(--gradient-display);
}

[data-product="openclaw"] {
  --accent-primary: var(--openclaw-violet);
  --accent-gradient: var(--gradient-openclaw);
}
```

### Icon Motifs per Product

| Product | Primary Icons |
|---------|---------------|
| Calendar | rings, arcs, clock, schedule, pulse |
| Pipeline | branch, route, node, flow, stage |
| Display | frame, panel, canvas, broadcast, loop |
| OpenClaw | mesh, network, command, neural, sync |

---

## Brand Coherence Checklist

Before shipping any product:

- [ ] Uses ForgeOrchestra type system
- [ ] Uses shared spacing scale
- [ ] Uses shared radii system
- [ ] Uses shared motion tokens
- [ ] Uses shared material surfaces
- [ ] Uses shared icon grammar
- [ ] Has unique accent color applied
- [ ] Has unique motif/artwork
- [ ] Feels like part of the family

---

## Visual Differentiation Matrix

| Attribute | Parent | Calendar | Pipeline | Display | OpenClaw |
|-----------|--------|----------|----------|---------|----------|
| Accent | Platinum Blue | Ice Cyan | Emerald Teal | Broadcast Amber | Neural Violet |
| Motif | Orbital grid | Time rings | Branch paths | Framed panels | Network mesh |
| Gradient | Blue ambient | Cyan sweep | Teal flow | Amber glow | Violet pulse |
| Hero Art | Conductor arcs | Cadence loops | Node clusters | Canvas stacks | Neural mesh |

---

**The system is one. The instruments are many. The visual language is unified.**
