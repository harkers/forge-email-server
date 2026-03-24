# Material Design Language

## Core Philosophy

**Architectural glass over engineered structure.**

Not "frosted blur gimmick" — premium digital material that feels machined, intentional, and calm.

---

## Material Stack

### Base Layers (Bottom → Top)

1. **Matte Dark Foundation**
   - Obsidian black base (`#07090D`)
   - Non-reflective, light-absorbing
   - Provides depth anchor

2. **Atmospheric Depth**
   - Slight vignette (radial gradient, 10-15% darkening at edges)
   - Faint radial illumination from center
   - Ultra-subtle grid or arc structure (1-2% opacity)

3. **Surface Panels**
   - Translucent glass (`rgba(22, 29, 46, 0.72)`)
   - Backdrop blur: 8-12px
   - Hairline border: `rgba(255, 255, 255, 0.08)`

4. **Active Elements**
   - Slightly elevated (z-index + shadow)
   - Inner highlight on active state
   - Subtle accent glow (product-specific)

5. **Interactive Overlays**
   - Higher opacity glass (`rgba(22, 29, 46, 0.80)`)
   - Increased blur: 16px
   - Clear focus indicators

---

## Surface Treatment

### Card Surfaces

```css
.card {
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.04) 0%,
    rgba(255, 255, 255, 0.01) 100%
  );
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.08),
    0 4px 12px rgba(0, 0, 0, 0.12);
}

.card:hover {
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.10),
    0 6px 16px rgba(0, 0, 0, 0.14);
}

.card.active {
  border-color: rgba(122, 166, 255, 0.24);
  box-shadow: 0 0 24px rgba(122, 166, 255, 0.12);
}
```

**Characteristics:**
- Layered, not flat
- Soft radiused edges (20-24px)
- Hairline translucent borders
- Internal glow subtle and cool-toned
- Gradients barely perceptible

---

### Panel Surfaces

```css
.panel {
  background: rgba(22, 29, 46, 0.72);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
}

.panel.elevated {
  background: rgba(22, 29, 46, 0.80);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.20);
}
```

**Usage:**
- Side navigation panels
- Status bars
- Tool palettes
- Modal surfaces

---

### Input Surfaces

```css
.input {
  background: rgba(11, 16, 32, 0.60);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px 16px;
  color: rgba(245, 247, 251, 0.72);
}

.input:focus {
  background: rgba(11, 16, 32, 0.72);
  border-color: rgba(122, 166, 255, 0.40);
  box-shadow: 0 0 16px rgba(122, 166, 255, 0.08);
  color: rgba(245, 247, 251, 1.0);
}

.input::placeholder {
  color: rgba(245, 247, 251, 0.48);
}
```

**Characteristics:**
- Soft dark wells
- Thin illuminated border on focus
- No thick ugly outlines
- Placeholder text calm and muted

---

### Button Surfaces

```css
.button-primary {
  background: linear-gradient(
    180deg,
    rgba(122, 166, 255, 0.24) 0%,
    rgba(122, 166, 255, 0.16) 100%
  );
  border: 1px solid rgba(122, 166, 255, 0.32);
  border-radius: 12px;
  padding: 10px 20px;
  color: #F5F7FB;
  font-weight: 500;
}

.button-primary:hover {
  background: linear-gradient(
    180deg,
    rgba(122, 166, 255, 0.32) 0%,
    rgba(122, 166, 255, 0.24) 100%
  );
  box-shadow: 0 0 20px rgba(122, 166, 255, 0.12);
}

.button-primary:active {
  background: rgba(122, 166, 255, 0.40);
  transform: scale(0.98);
}

.button-secondary {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 10px 20px;
  color: rgba(245, 247, 251, 0.88);
}

.button-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.12);
}
```

**Characteristics:**
- Low-height, refined
- Soft radius (12px)
- Glow on focus, not giant shadows
- Primary action feels lit from within
- Minimal height: 40px standard, 36px compact

---

## Edge Treatment

### Border System

```css
/* Standard edge */
border: 1px solid rgba(255, 255, 255, 0.08);

/* Active edge */
border: 1px solid rgba(255, 255, 255, 0.12);

/* Accent edge (product-specific) */
border: 1px solid rgba(122, 166, 255, 0.24);

/* Inner highlight for depth */
box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
```

**Rules:**
- Always 1px, never thicker
- Translucent, never solid white
- Inner highlight for active surfaces only
- Consistent across all products

---

## Shadow System

### Elevation Levels

```css
/* Level 1 - Subtle lift */
box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);

/* Level 2 - Card default */
box-shadow: 
  0 1px 2px rgba(0, 0, 0, 0.08),
  0 4px 12px rgba(0, 0, 0, 0.12);

/* Level 3 - Modal / overlay */
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.20);

/* Level 4 - Floating command palette */
box-shadow: 0 12px 48px rgba(0, 0, 0, 0.24);
```

**Characteristics:**
- Very soft, diffused
- Low opacity
- Layered, not cartoon drop shadows
- Multiple shadows for depth

---

## Glow Effects

### Accent Glow (Product-Specific)

```css
/* Parent brand - Platinum Blue */
glow-blue: 0 0 24px rgba(122, 166, 255, 0.15);

/* Calendar - Ice Cyan */
glow-cyan: 0 0 24px rgba(125, 211, 233, 0.15);

/* Pipeline - Emerald Teal */
glow-teal: 0 0 24px rgba(45, 212, 191, 0.15);

/* Display - Broadcast Amber */
glow-amber: 0 0 24px rgba(245, 158, 11, 0.15);

/* OpenClaw - Neural Violet */
glow-violet: 0 0 24px rgba(139, 92, 246, 0.15);
```

**Usage:**
- Active state indicators
- Focus states
- Processing/loading states
- Selected items

**Intensity:**
- Subtle: `0.08` opacity
- Standard: `0.15` opacity
- Strong: `0.24` opacity (rare, for critical states)

---

## Gradient System

### Ambient Gradients

```css
/* Parent brand ambient */
background: linear-gradient(
  180deg,
  rgba(122, 166, 255, 0.08) 0%,
  rgba(122, 166, 255, 0.02) 100%
);

/* Subtle surface gradient */
background: linear-gradient(
  180deg,
  rgba(255, 255, 255, 0.04) 0%,
  rgba(255, 255, 255, 0.01) 100%
);
```

**Rules:**
- Barely perceptible in static states
- Always vertical or 135deg diagonal
- Never competing with content
- Maximum 8% opacity at strongest point

---

## Background Atmosphere

### Base Background

```css
.background {
  background: 
    radial-gradient(
      ellipse at center,
      rgba(22, 29, 46, 0.40) 0%,
      rgba(7, 9, 13, 1.0) 100%
    ),
    #07090D;
}
```

### Atmospheric Layers

```css
.background-with-grid {
  background: 
    radial-gradient(
      ellipse at center,
      rgba(22, 29, 46, 0.40) 0%,
      rgba(7, 9, 13, 1.0) 100%
    ),
    linear-gradient(
      rgba(255, 255, 255, 0.02) 1px,
      transparent 1px
    ),
    linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.02) 1px,
      transparent 1px
    ),
    #07090D;
  background-size: 
    100% 100%,
    64px 64px,
    64px 64px;
}
```

**Elements:**
- Dark matte base
- Slight vignette (radial gradient)
- Faint radial illumination
- Ultra-subtle grid (1-2% opacity, 64px spacing)
- Product-specific ambient field (accent color, 2-4% opacity)

---

## Material Rules

### Do's

✅ Layered surfaces with clear hierarchy
✅ Translucent glass with backdrop blur
✅ Hairline borders (1px, translucent)
✅ Soft diffused shadows
✅ Subtle accent glows on active states
✅ Barely-perceptible gradients
✅ Consistent edge treatment

### Don'ts

❌ Flat, solid backgrounds
❌ Thick borders (>1px)
❌ Harsh drop shadows
❌ Heavy blur ("blur soup")
❌ Bright, competing gradients
❌ Inconsistent edge treatment
❌ Solid white on solid black

---

## Product Material Variations

All products share the same material stack, with accent variations:

| Product | Accent Glow | Ambient Tint |
|---------|-------------|--------------|
| ForgeOrchestra | Platinum Blue | Blue (4%) |
| ForgeCalendar | Ice Cyan | Cyan (4%) |
| ForgePipeline | Emerald Teal | Teal (4%) |
| ForgeDisplay | Broadcast Amber | Amber (4%) |
| ForgeOpenClaw | Neural Violet | Violet (4%) |

---

## Implementation Checklist

For any new surface:

- [ ] Uses correct background stack
- [ ] Has appropriate backdrop blur
- [ ] Uses 1px translucent border
- [ ] Has correct shadow elevation
- [ ] Uses product accent for active states
- [ ] Gradient is subtle (≤8% opacity)
- [ ] Radius matches surface type
- [ ] Hover state defined
- [ ] Focus state defined

---

**Material is the medium. Light is the signal. Structure is the foundation.**
