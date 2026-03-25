# Forge Pipeline Design Tokens

Aligned with **ForgeOrchestra Design System v1.0 — Obsidian Intelligence**

---

## Brand Alignment

Forge Pipeline uses the ForgeOrchestra parent design system with a **Process Green** accent variant:

| Token | Value | Usage |
|-------|-------|-------|
| `--accent` | `#7AA6FF` | Primary actions, links |
| `--accent-2` | `#56e0c5` | Process indicators, success states |

---

## Color System

### Core Backgrounds

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-obsidian` | `#07090D` | Deep background |
| `--bg-carbon` | `#0B1020` | Primary background |
| `--bg-graphite` | `#111827` | Elevated surfaces |

### Secondary Surfaces

| Token | Value | Usage |
|-------|-------|-------|
| `--panel` | `rgba(255,255,255,0.08)` | Card backgrounds |
| `--panel-strong` | `rgba(255,255,255,0.12)` | Elevated panels |
| `--slate-glass` | `#161D2E` | Glass overlay |
| `--steel-mist` | `#1D2638` | Muted surface |

### Text

| Token | Value | Usage |
|-------|-------|-------|
| `--text` | `#F5F7FB` | Primary text |
| `--text-secondary` | `rgba(245,247,251,0.72)` | Secondary text |
| `--text-tertiary` | `rgba(245,247,251,0.48)` | Tertiary/muted |
| `--muted` | `#a8b1d1` | Labels, hints |

### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--danger` | `#ff7f98` | Error, critical, blocked |
| `--success` | `#56e0c5` | Success, on-track |
| `--warning` | `#ffbc58` | Warning, at-risk |
| `--info` | `#7AA6FF` | Info, neutral |

---

## Typography Scale

Modular scale (1.25 ratio) using Inter and SF Mono:

| Token | Size | Usage |
|-------|------|-------|
| `--text-xs` | `0.75rem (12px)` | Labels, badges |
| `--text-sm` | `0.875rem (14px)` | Body small, meta |
| `--text-base` | `1rem (16px)` | Body text |
| `--text-lg` | `1.125rem (18px)` | Emphasized body |
| `--text-xl` | `1.25rem (20px)` | Section headers |
| `--text-2xl` | `1.5rem (24px)` | Panel titles |
| `--text-3xl` | `2rem (32px)` | Page titles |
| `--text-4xl` | `2.5rem (40px)` | Hero |
| `--text-5xl` | `3.5rem (56px)` | Display |

Font families:
- `--font-sans`: Inter, SF Pro Display, -apple-system...
- `--font-mono`: SF Mono, Menlo, Monaco...

---

## Spacing Scale

8pt base grid:

| Token | Size | Usage |
|-------|------|-------|
| `--space-1` | `4px` | Tight gaps |
| `--space-2` | `8px` | Icon gaps |
| `--space-3` | `12px` | Small gaps |
| `--space-4` | `16px` | Standard gap |
| `--space-5` | `20px` | Card padding |
| `--space-6` | `24px` | Section gap |
| `--space-8` | `32px` | Layout padding |
| `--space-10` | `40px` | Large gap |
| `--space-12` | `48px` | Page padding |

---

## Border Radius

| Token | Size | Usage |
|-------|------|-------|
| `--radius-sm` | `12px` | Buttons, inputs, badges |
| `--radius-md` | `20px` | Cards, modals |
| `--radius-lg` | `24px` | Large containers |
| `--radius-xl` | `28px` | Full panels, shells |

---

## Motion Tokens

Fluid, responsive, intelligent transitions:

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| `--transition-fast` | `0.15s` | `ease` | Quick hover |
| `--transition-base` | `0.2s` | `ease` | Standard |
| `--transition-smooth` | `0.3s` | `cubic-bezier(0.4, 0, 0.2, 1)` | Panels |
| `--transition-slow` | `0.4s` | `cubic-bezier(0.4, 0, 0.2, 1)` | Large elements |
| `--transition-glide` | `0.5s` | `cubic-bezier(0.22, 1, 0.36, 1)` | Slides |

### Easing Curves

| Token | Curve | Feel |
|-------|-------|------|
| `--ease-out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Gentle exit |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | Balanced |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Subtle bounce |

---

## Shadow & Glow

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow` | `0 20px 60px rgba(0,0,0,0.35)` | Elevated cards |
| `--shadow-soft` | `0 8px 32px rgba(0,0,0,0.24)` | Subtle lift |
| `--glow` | `0 0 24px rgba(122,166,255,0.08)` | Active/active focus |

---

## Component Patterns

### Cards

```css
.project-card, .task-item {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--space-5);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}
.project-card:hover {
  border-color: var(--border-active);
  box-shadow: var(--shadow), var(--glow);
}
```

### Badges

```css
.badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: var(--text-xs);
  font-weight: 500;
}
```

### Buttons

```css
button {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  font-weight: 500;
  transition: all var(--transition-base);
}
button:hover {
  border-color: var(--border-active);
  box-shadow: var(--glow);
}
```

---

## Status Colors

### Task Priority

| Priority | Background | Color |
|----------|------------|-------|
| critical | `rgba(255,60,80,0.22)` | `#ffd5db` |
| high | `rgba(255,90,110,0.16)` | `#ffd5db` |
| medium | `rgba(255,188,88,0.16)` | `#ffe4b0` |
| low | `rgba(120,196,255,0.16)` | `#d3edff` |

### Project Status

| Status | Background | Color |
|--------|------------|-------|
| on-track | `rgba(86,224,197,0.18)` | `#caffee` |
| at-risk | `rgba(255,188,88,0.18)` | `#ffe4b0` |
| off-track | `rgba(255,90,110,0.18)` | `#ffd5db` |
| blocked | `rgba(255,127,152,0.18)` | `#ffd5df` |

### Risk State

| Risk | Background | Color |
|------|------------|-------|
| none | `rgba(120,196,255,0.12)` | `#d3edff` |
| watch | `rgba(255,188,88,0.18)` | `#ffe4b0` |
| at-risk | `rgba(255,127,152,0.18)` | `#ffd5df` |
| critical | `rgba(255,60,80,0.22)` | `#ffd5db` |

---

## Animation Classes

| Class | Animation |
|-------|-----------|
| `.animate-in` | Fade in |
| `.animate-slide-up` | Slide + fade up |
| `.animate-scale-in` | Scale + fade in |
| `.hover-lift` | Lift on hover |
| `.hover-glow` | Glow on hover |
| `.focus-ring` | Focus ring outline |
| `.skeleton` | Loading shimmer |

---

## Usage Guidelines

1. **Use CSS variables** — Never hardcode colors/sizes
2. **Prefer semantic tokens** — Use `--danger` not `#ff7f98`
3. **Motion is optional** — Reduced motion should be respected
4. **Consistent radii** — Match card depth to radius
5. **Premium spacing** — Generous margins, breathing room

---

*Last updated: 2026-03-25*
*Version: v1.6.0*