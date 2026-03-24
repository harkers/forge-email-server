# Design Tokens

## Color Palette

### Base Colors (Dark Mode First)

```css
/* Core Backgrounds */
--obsidian-black: #07090D;
--carbon-ink: #0B1020;
--deep-graphite: #111827;

/* Secondary Surfaces */
--slate-glass: #161D2E;
--steel-mist: #1D2638;
--graphite-border: rgba(255, 255, 255, 0.08);

/* Text Colors */
--text-primary: #F5F7FB;
--text-secondary: rgba(245, 247, 251, 0.72);
--text-tertiary: rgba(245, 247, 251, 0.48);
```

### Brand Accents

```css
/* ForgeOrchestra Parent - Luminous Platinum Blue */
--accent-blue-primary: #7AA6FF;
--accent-blue-secondary: #9CC3FF;
--accent-blue-tertiary: #C9D9FF;

/* Support Accent - Soft Electric Violet */
--accent-violet-primary: #7C72FF;
--accent-violet-secondary: #A495FF;
```

### Product Accents

```css
/* ForgeCalendar - Ice Blue / Time Cyan */
--calendar-cyan: #7DD3E9;
--calendar-ice: #B8E8F5;

/* ForgePipeline - Emerald Teal / Process Green */
--pipeline-teal: #2DD4BF;
--pipeline-emerald: #34D399;

/* ForgeDisplay - Warm Amber / Broadcast Gold */
--display-amber: #F59E0B;
--display-gold: #FBBF24;

/* ForgeOpenClaw - Neural Violet / Deep Indigo */
--openclaw-violet: #8B5CF6;
--openclaw-indigo: #6366F1;
```

---

## Typography

### Font Stack

```css
/* Primary Sans - Neutral Grotesk */
--font-primary: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;

/* Mono for Data States */
--font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
```

### Type Scale

```css
/* Hero Titles */
--text-hero: 48px / 600 weight / -0.02em letter-spacing;

/* Section Headers */
--text-section: 20px / 500 weight / -0.01em letter-spacing;

/* Body Text */
--text-body: 15px / 400 weight / 1.5 line-height;

/* Labels */
--text-label: 13px / 500 weight / 0.05em letter-spacing / uppercase;

/* Data States (Mono) */
--text-data: 13px / 400 weight / mono;
```

### Tracking & Leading

```css
--tracking-tight: -0.02em;
--tracking-normal: 0;
--tracking-wide: 0.05em;

--leading-tight: 1.2;
--leading-normal: 1.5;
--leading-loose: 1.7;
```

---

## Spacing

### 8pt Grid Base

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-7: 32px;
--space-8: 40px;
--space-9: 48px;
--space-10: 64px;
--space-11: 80px;
--space-12: 96px;
```

### Layout Margins

```css
--margin-page: 64px;
--margin-section: 48px;
--margin-block: 32px;
--margin-inline: 24px;
```

### Component Spacing

```css
--card-padding: 24px;
--button-padding-x: 20px;
--button-padding-y: 10px;
--input-padding: 12px;
```

---

## Radii

```css
/* Small Elements */
--radius-sm: 12px;

/* Cards / Containers */
--radius-md: 20px;
--radius-lg: 24px;

/* Modal / Shell Surfaces */
--radius-xl: 28px;

/* Full Circle */
--radius-full: 9999px;
```

---

## Borders

```css
/* Standard Border */
--border-thin: 1px solid rgba(255, 255, 255, 0.08);

/* Active Surface Inner Highlight */
--border-highlight: 1px solid rgba(255, 255, 255, 0.12);

/* Divider */
--border-divider: 1px solid rgba(255, 255, 255, 0.04);
```

---

## Shadows

```css
/* Soft Diffused Shadow */
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.12);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.16);
--shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.20);

/* Layered Elevation */
--shadow-card: 
  0 1px 2px rgba(0, 0, 0, 0.08),
  0 4px 12px rgba(0, 0, 0, 0.12);

/* Glow Effect */
--glow-subtle: 0 0 24px rgba(122, 166, 255, 0.15);
```

---

## Blur

```css
/* Restrained Backdrop Blur */
--blur-sm: 4px;
--blur-md: 8px;
--blur-lg: 16px;

/* Usage Rule: Only where it improves depth */
```

---

## Opacity & Transparency

```css
/* Glass Surfaces */
--opacity-glass: 0.72;
--opacity-glass-hover: 0.80;

/* Border Transparency */
--opacity-border: 0.08;
--opacity-border-active: 0.12;

/* Text Hierarchy */
--opacity-text-primary: 1.0;
--opacity-text-secondary: 0.72;
--opacity-text-tertiary: 0.48;
```

---

## Gradients

```css
/* Subtle Ambient Gradient */
--gradient-ambient: linear-gradient(
  180deg,
  rgba(122, 166, 255, 0.08) 0%,
  rgba(122, 166, 255, 0.02) 100%
);

/* Card Surface Gradient */
--gradient-card: linear-gradient(
  180deg,
  rgba(255, 255, 255, 0.04) 0%,
  rgba(255, 255, 255, 0.01) 100%
);

/* Product-Specific Gradients */
--gradient-calendar: linear-gradient(135deg, rgba(125, 211, 233, 0.1) 0%, rgba(125, 211, 233, 0.02) 100%);
--gradient-pipeline: linear-gradient(135deg, rgba(45, 212, 191, 0.1) 0%, rgba(45, 212, 191, 0.02) 100%);
--gradient-display: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.02) 100%);
--gradient-openclaw: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.02) 100%);
```

---

## Motion & Timing

```css
/* Duration */
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;

/* Easing */
--ease-out-smooth: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring: cubic-bezier(0.25, 0.1, 0.25, 1.4);

/* Transition Presets */
--transition-smooth: var(--duration-normal) var(--ease-out-smooth);
--transition-spring: var(--duration-fast) var(--ease-spring);
```

---

## Z-Index Scale

```css
--z-base: 0;
--z-surface: 10;
--z-overlay: 20;
--z-modal: 30;
--z-tooltip: 40;
--z-max: 50;
```

---

## Breakpoints

```css
/* Responsive */
--bp-sm: 640px;
--bp-md: 768px;
--bp-lg: 1024px;
--bp-xl: 1280px;
--bp-2xl: 1536px;
```

---

## Usage Notes

1. **Dark mode is the flagship** — design for dark first, light mode secondary
2. **Accent colors are signals, not takeovers** — use sparingly
3. **Spacing breathes** — never cram, always use generous margins
4. **Motion is predictive** — everything knows where it's going
5. **Contrast is high but softened** — avoid harsh #000 vs #FFF
