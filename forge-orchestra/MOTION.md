# Motion Language

## Core Philosophy

**Everything should feel like it already knows where it is going.**

Motion conveys intelligence, control, and calm power — not gimmicks or dopamine spam.

---

## Motion Principles

### Feel

- ✅ Fluid
- ✅ Responsive
- ✅ Intelligent
- ✅ Restrained
- ✅ Slightly cinematic

### Avoid

- ❌ Bouncy
- ❌ Gimmicky
- ❌ Overshoot and elastic spam
- ❌ Excessive duration
- ❌ Unnecessary animation

---

## Timing & Easing

### Duration Scale

```css
--duration-instant: 50ms;    /* Micro-interactions */
--duration-fast: 150ms;      /* Simple state changes */
--duration-normal: 300ms;    /* Standard transitions */
--duration-slow: 500ms;      /* Complex movements */
--duration-very-slow: 800ms; /* Large surface transitions */
```

**Usage:**
- Instant: Toggle switches, icon state changes
- Fast: Button hover, small element fades
- Normal: Card transitions, panel slides
- Slow: Modal appearance, large surface reveals
- Very Slow: Full page transitions, major layout shifts

### Easing Curves

```css
/* Primary ease - smooth, controlled */
--ease-out-smooth: cubic-bezier(0.16, 1, 0.3, 1);

/* Secondary ease - balanced */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);

/* Spring ease - minimal bounce */
--ease-spring: cubic-bezier(0.25, 0.1, 0.25, 1.4);

/* Linear for opacity only */
--ease-linear: linear;
```

**Characteristics:**
- `ease-out-smooth`: Fast start, slow settle (most common)
- `ease-in-out`: Symmetric, for reversible animations
- `ease-spring`: Slight overshoot (10% max), use sparingly
- `ease-linear`: Opacity fades only, never position

---

## Transition Presets

### Standard Transitions

```css
/* Smooth transition (default) */
--transition-smooth: 300ms cubic-bezier(0.16, 1, 0.3, 1);

/* Fast transition */
--transition-fast: 150ms cubic-bezier(0.16, 1, 0.3, 1);

/* Spring transition (rare) */
--transition-spring: 300ms cubic-bezier(0.25, 0.1, 0.25, 1.4);

/* Opacity only */
--transition-fade: 200ms linear;
```

### Property-Specific

```css
/* Transform only (GPU-accelerated) */
transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1);

/* Opacity + transform together */
transition: 
  opacity 200ms linear,
  transform 300ms cubic-bezier(0.16, 1, 0.3, 1);

/* Full property set (use sparingly) */
transition: 
  opacity 200ms linear,
  transform 300ms cubic-bezier(0.16, 1, 0.3, 1),
  box-shadow 300ms cubic-bezier(0.16, 1, 0.3, 1);
```

---

## Motion Patterns

### Panel Slide

```css
.panel-slide-in {
  opacity: 0;
  transform: translateX(-20px);
  transition: 
    opacity 300ms linear,
    transform 400ms cubic-bezier(0.16, 1, 0.3, 1);
}

.panel-slide-in.active {
  opacity: 1;
  transform: translateX(0);
}
```

**Usage:** Side navigation, tool palettes, drawer panels

**Characteristics:**
- Starts 20px offset
- Opacity fades slightly faster than movement
- Smooth settle, no bounce

---

### Card Reveal

```css
.card-reveal {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
  transition: 
    opacity 250ms linear,
    transform 350ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 350ms cubic-bezier(0.16, 1, 0.3, 1);
}

.card-reveal.active {
  opacity: 1;
  transform: translateY(0) scale(1);
}
```

**Usage:** Card lists, grid items, content blocks

**Characteristics:**
- Starts 12px below, slightly scaled down
- Staggered reveal for lists (50ms delay per item)
- Shadow transitions with transform

---

### Modal Appearance

```css
.modal-backdrop {
  opacity: 0;
  transition: opacity 300ms linear;
}

.modal-surface {
  opacity: 0;
  transform: translateY(24px) scale(0.96);
  transition: 
    opacity 350ms linear,
    transform 450ms cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-backdrop.active {
  opacity: 1;
}

.modal-surface.active {
  opacity: 1;
  transform: translateY(0) scale(1);
}
```

**Usage:** Modals, dialogs, overlays

**Characteristics:**
- Backdrop fades first (300ms)
- Surface follows with delay (50ms)
- Starts 24px below, slightly scaled
- Slow, controlled settle

---

### Button Press

```css
.button {
  transition: 
    transform 100ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 150ms cubic-bezier(0.16, 1, 0.3, 1),
    background 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

.button:active {
  transform: scale(0.97);
}
```

**Usage:** All interactive buttons

**Characteristics:**
- Fast, crisp press (100ms)
- Minimal scale (3% reduction)
- Shadow and background follow

---

### Hover Lift

```css
.card {
  transition: 
    transform 250ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 300ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 200ms linear;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.10),
    0 6px 16px rgba(0, 0, 0, 0.14);
  border-color: rgba(255, 255, 255, 0.12);
}
```

**Usage:** Cards, list items, selectable surfaces

**Characteristics:**
- Subtle lift (2px)
- Shadow intensifies
- Border brightens slightly
- Smooth, not snappy

---

### Glow Pulse (Loading/Processing)

```css
@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 24px rgba(122, 166, 255, 0.12);
  }
  50% {
    box-shadow: 0 0 32px rgba(122, 166, 255, 0.20);
  }
}

.glow-pulse {
  animation: glow-pulse 2000ms cubic-bezier(0.65, 0, 0.35, 1) infinite;
}
```

**Usage:** Processing states, active agents, loading indicators

**Characteristics:**
- Slow, calm pulse (2s cycle)
- Smooth ease in/out
- Intensity variation: 12% → 20% → 12%
- Never distracting

---

### Route Animation (Pipeline Flow)

```css
@keyframes flow-travel {
  0% {
    stroke-dashoffset: 100;
    opacity: 0.4;
  }
  50% {
    opacity: 1.0;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0.4;
  }
}

.route-flow {
  stroke-dasharray: 10 5;
  animation: flow-travel 3000ms cubic-bezier(0.65, 0, 0.35, 1) infinite;
}
```

**Usage:** Pipeline diagrams, connection lines, data flow

**Characteristics:**
- Dashed line with moving pattern
- 3s cycle, continuous
- Opacity breathes with movement
- Product accent color

---

### Staggered List Reveal

```css
.list-item {
  opacity: 0;
  transform: translateY(8px);
  transition: 
    opacity 250ms linear,
    transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
}

.list-item:nth-child(1) { transition-delay: 0ms; }
.list-item:nth-child(2) { transition-delay: 50ms; }
.list-item:nth-child(3) { transition-delay: 100ms; }
.list-item:nth-child(4) { transition-delay: 150ms; }
.list-item:nth-child(5) { transition-delay: 200ms; }

.list-item.active {
  opacity: 1;
  transform: translateY(0);
}
```

**Usage:** List items, grid cards, sequential content

**Characteristics:**
- 50ms stagger per item
- Subtle vertical movement (8px)
- Creates flowing reveal effect
- Maximum 5 items staggered (reset after)

---

## Motion Behaviors by Product

### ForgeOrchestra (Parent)

**Primary Motions:**
- Orbital rotation (slow, 10s cycles)
- Hub activation pulses
- Branch path illumination

**Tone:** Controlled, systemic, orchestral

---

### ForgeCalendar

**Primary Motions:**
- Time-based scroll easing
- Event creation fluid expansion
- Gentle sweeping transitions
- Pulse rhythm markers (subtle)

**Tone:** Flowing, rhythmic, calm

---

### ForgePipeline

**Primary Motions:**
- Pulse animation along active paths
- Node activation with soft glow
- Progress fill with smooth easing
- Flow travel on connection lines

**Tone:** Directed, purposeful, flowing

---

### ForgeDisplay

**Primary Motions:**
- Panel slides with controlled ease
- Tab transitions with minimal overshoot
- Content fades with soft opacity
- Loop indicators with gentle rotation

**Tone:** Stable, broadcast, clean

---

### ForgeOpenClaw

**Primary Motions:**
- Network pulse with subtle propagation
- Agent state changes with smooth transitions
- Command execution with trail effects
- Intelligence indicators with breath

**Tone:** Intelligent, responsive, neural

---

## Loading States

### Skeleton Loading

```css
@keyframes skeleton-shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: 200px 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.04) 0%,
    rgba(255, 255, 255, 0.08) 50%,
    rgba(255, 255, 255, 0.04) 100%
  );
  background-size: 400px 100%;
  animation: skeleton-shimmer 2000ms cubic-bezier(0.65, 0, 0.35, 1) infinite;
}
```

**Characteristics:**
- Slow shimmer (2s cycle)
- Subtle brightness variation
- Never distracting from content

---

### Processing Indicator

```css
@keyframes orbit-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.orbit-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(122, 166, 255, 0.12);
  border-top-color: rgba(122, 166, 255, 0.60);
  border-radius: 50%;
  animation: orbit-spin 1200ms cubic-bezier(0.65, 0, 0.35, 1) infinite;
}
```

**Characteristics:**
- Slow rotation (1.2s per revolution)
- Product accent color
- Thin stroke (2px)
- Smooth easing, not linear

---

## Motion Rules

### Do's

✅ Animate transform + opacity (GPU-accelerated)
✅ Use smooth easing curves
✅ Keep duration under 500ms for most interactions
✅ Stagger sequential reveals (50ms intervals)
✅ Match motion to product personality
✅ Provide reduced-motion support

### Don'ts

❌ Animate width/height (use transform instead)
❌ Use linear easing for position changes
❌ Exceed 800ms for standard interactions
❌ Bounce or elastic overshoot (>10%)
❌ Animate everything at once
❌ Ignore reduced-motion preferences

---

## Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Rule:** Always respect user preferences. Motion is enhancement, not requirement.

---

## Performance Guidelines

### GPU-Accelerated Properties

**Animate these (cheap):**
- `transform`
- `opacity`
- `filter` (use sparingly)

**Avoid these (expensive):**
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `font-size`

### Layer Promotion

```css
.will-animate {
  will-change: transform, opacity;
}

/* Remove after animation completes */
.will-animate.done {
  will-change: auto;
}
```

**Usage:** Promote layers before animating, clean up after

---

## Motion Checklist

Before shipping any animation:

- [ ] Duration is appropriate (≤500ms standard)
- [ ] Easing curve matches intent
- [ ] Uses GPU-accelerated properties
- [ ] Staggered if sequential (50ms intervals)
- [ ] Respects reduced-motion preferences
- [ ] Matches product personality
- [ ] Doesn't compete with content
- [ ] Has defined hover/active states
- [ ] Performance-tested (60fps)

---

**Motion is the breath of the system. It should feel alive, not agitated.**
