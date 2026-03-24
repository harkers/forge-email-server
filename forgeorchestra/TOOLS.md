# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## ForgeOrchestra Infrastructure

### Design Tokens

**Radii:**
- Small elements: 12px
- Cards/containers: 20–24px
- Modal/shell surfaces: 28px

**Borders:**
- 1px translucent borders
- Occasional inner highlight line for active surfaces

**Shadows:**
- Very soft, diffused
- Low opacity
- Layered, not cartoon drop shadows

**Spacing:**
- 8pt grid base
- Premium spacing scale
- Never cram cards together

**Contrast:**
- High enough for clarity
- Softened by material layering
- Avoid harsh pure white against pure black everywhere

### Product Family

ForgeOrchestra governs a product family where each product is visually a member of the same house:

- **ForgeOrchestra** (parent) — Luminous Platinum Blue `#7AA6FF`
- **ForgeCalendar** — Ice Blue / Time Cyan
- **ForgePipeline** — Emerald Teal / Process Green
- **ForgeDisplay** — Warm Amber / Broadcast Gold
- **ForgeOpenClaw** — Violet / Deep Neural Indigo
