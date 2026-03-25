# OrderedHome Style Guide

## 1. Brand Positioning

OrderedHome is a modern household operations platform. It should feel calm, capable, trustworthy, and intelligently structured. The visual language should communicate order, clarity, reliability, and practical usefulness.

This is not a playful lifestyle app, and it is not a dry enterprise dashboard. It sits between the two:

- polished enough to feel premium
- warm enough to feel domestic
- structured enough to feel dependable
- modern enough to feel product-led

The experience should feel like:
- a well-designed control centre for everyday life
- clean, reassuring, and efficient
- premium but not cold
- practical without being dull

## 2. Brand Attributes

Core brand characteristics:
- organised
- dependable
- modern
- calm
- practical
- intelligent
- reassuring
- modular

Tone expressed visually:
- clean layouts
- generous spacing
- strong hierarchy
- restrained colour use
- rounded but not childish interface shapes
- subtle motion
- high legibility

## 3. Product Family Design Logic

OrderedHome is the parent platform.

Modules:
- ForgeHome
- ForgeCar
- ForgeGarden
- ForgeCover
- ForgeTravel
- ForgeHealth

The platform should have one core visual system, with module-level accents to create identity without fragmenting the experience.

Rule:
The platform always looks like one product family. Modules may have different accent colours, icons, and illustrations, but typography, spacing, interaction patterns, and layout structure stay consistent.

## 4. Design Principles

### 4.1 Clarity first
Every screen should answer:
- what this area is
- what needs attention
- what the user can do next

### 4.2 Calm over clutter
Avoid noisy interfaces, dense dashboards, and over-decoration. Use whitespace to create confidence.

### 4.3 Responsive by default
The system must work elegantly across:
- mobile
- tablet
- laptop
- desktop

Design mobile-first, then scale upward.

### 4.4 Familiar but elevated
Use established interaction patterns, but present them with cleaner hierarchy, better spacing, and stronger visual polish.

### 4.5 Information with warmth
This is a records-and-reminders product for people’s real lives. It should feel human and approachable, not bureaucratic.

## 5. Visual Direction

### 5.1 Overall look and feel
The interface should feel:
- light and spacious
- softly premium
- modular and card-based
- subtly layered
- legible in all lighting conditions

Suggested design references in spirit:
- modern fintech dashboards
- premium home management apps
- high-quality health and productivity products
- editorially clean consumer SaaS

Avoid:
- overly sharp enterprise styling
- skeuomorphic visuals
- cartoonish icons
- neon-heavy startup aesthetics
- excessive gradients
- cramped data tables as the default UI pattern

## 6. Colour System

### 6.1 Core palette
Primary ink:
- `#0F172A` — deep slate navy for primary text and strong UI anchors

Secondary ink:
- `#334155` — secondary text and medium emphasis

Muted text:
- `#64748B` — supporting text and metadata

Background base:
- `#F8FAFC` — app background

Surface:
- `#FFFFFF` — cards, panels, overlays

Surface alt:
- `#F1F5F9` — subtle section contrast

Border:
- `#E2E8F0` — low-contrast dividers and control outlines

Primary action:
- `#2563EB` — primary buttons, active states, selected items

Primary hover:
- `#1D4ED8`

Success:
- `#16A34A`

Warning:
- `#D97706`

Danger:
- `#DC2626`

Info:
- `#0891B2`

### 6.2 Module accent colours
ForgeHome:
- `#2563EB` — structured blue

ForgeCar:
- `#475569` — graphite slate

ForgeGarden:
- `#15803D` — grounded green

ForgeCover:
- `#7C3AED` — confident violet

ForgeTravel:
- `#0F766E` — teal for movement and planning

ForgeHealth:
- `#DB2777` — controlled rose tone

Rules:
- do not recolour the whole UI per module
- use accents as identifiers, not backgrounds for entire screens
- maintain the same neutrals throughout the product

### 6.3 Dark mode
Dark neutrals:
- app background: `#020617`
- surface: `#0F172A`
- surface alt: `#111827`
- primary text: `#E2E8F0`
- secondary text: `#94A3B8`
- borders: `#1E293B`

## 7. Typography

Recommended:
- Inter
- Geist
- SF Pro Text / Display where native

Fallback:
- Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif

### 7.1 Type scale
- Display large: 48 / 56
- Display medium: 36 / 44
- Heading 1: 30 / 38 / 700
- Heading 2: 24 / 32 / 700
- Heading 3: 20 / 28 / 600
- Heading 4: 18 / 26 / 600
- Body large: 18 / 30 / 400
- Body: 16 / 26 / 400
- Body small: 14 / 22 / 400
- Caption: 12 / 18 / 500
- UI label: 14 / 20 / 600

### 7.2 Typography rules
- prioritize readability over compression
- avoid long stretches of low-contrast small text
- use weight and spacing before colour for hierarchy
- reserve large type for page titles and hero moments
- do not overuse all caps

## 8. Spacing and Layout

### 8.1 Spacing scale
Use a 4pt base grid.
Core values:
- 4
- 8
- 12
- 16
- 20
- 24
- 32
- 40
- 48
- 64

### 8.2 Radius scale
- small: 8px
- medium: 12px
- large: 16px
- extra large: 24px

Recommended:
- inputs/buttons: 12px
- cards: 16px
- modals/panels: 20–24px

### 8.3 Shadows
Use soft, restrained shadows.
Avoid hard or overly dark shadows.

## 9. Grid and Responsive Behaviour

### 9.1 Breakpoints
- small mobile: 0–479px
- mobile: 480–767px
- tablet: 768–1023px
- laptop: 1024–1279px
- desktop: 1280–1535px
- large desktop: 1536px+

### 9.2 Layout behaviour
Mobile:
- single-column layout by default
- bottom nav or compact top nav
- stacked cards
- collapsible filters
- sticky key actions where helpful

Tablet:
- 2-column card layouts where relevant
- side sheet patterns for detail views
- more persistent navigation

Desktop:
- 12-column grid
- left navigation rail/sidebar
- multi-panel layouts
- inline detail panels where useful
- denser info views only when clearly structured

### 9.3 Responsive content rules
- preserve hierarchy across sizes
- do not hide critical information without a clear access path
- cards should stretch elegantly
- tables must collapse into list/card views on smaller screens
- filters and actions should remain thumb-friendly on mobile

## 10. Navigation Patterns

### 10.1 Global navigation
Recommended top-level destinations:
- Dashboard
- ForgeHome
- ForgeCar
- ForgeGarden
- ForgeCover
- ForgeTravel
- ForgeHealth
- Documents
- Timeline
- Contacts

Desktop:
- left sidebar navigation
- workspace context shown clearly
- persistent quick-add action

Mobile:
- simplified nav
- primary modules in tab bar or menu
- quick capture always accessible

### 10.2 In-module navigation
Use sub-navigation for:
- overview
- active items
- calendar
- documents
- costs
- history
- settings

## 11. Component Style Direction

### 11.1 Cards
Cards are a primary UI pattern.
Use for reminders, jobs, policies, vehicles, plants, trips, appointments, and dashboard summaries.

### 11.2 Buttons
Primary button:
- strong fill using primary action colour
- white text
- medium weight
- comfortable padding
- 44px minimum height

Secondary button:
- soft neutral background or bordered style

Tertiary button:
- text button for lower-emphasis actions

Destructive button:
- reserved for deletion or irreversible actions

### 11.3 Inputs
Inputs should be:
- full-height and easy to tap
- clearly labeled above the field
- minimally decorative
- strongly legible
- consistent across all modules

### 11.4 Status indicators
Use coloured chips with icon support where useful.
Do not rely on colour alone.

### 11.5 Tables
Use tables only when the content truly benefits from tabular layout.
For most consumer-facing flows, prefer cards or grouped lists.

## 12. Iconography

Recommended:
- Lucide
- Phosphor
- Heroicons

Suggested module icons:
- ForgeHome: house / wrench
- ForgeCar: car / gauge
- ForgeGarden: leaf / sprout
- ForgeCover: shield / document-check
- ForgeTravel: suitcase / compass
- ForgeHealth: heart-pulse / cross

## 13. Data Visualisation

Use charts for:
- spend over time
- fuel economy trends
- maintenance costs
- renewal calendar view
- garden yield trends
- appointment frequency

Rules:
- avoid cluttered chart chrome
- use module accent colours sparingly
- always pair charts with plain-language summaries
- never rely on charts alone for critical actions

## 14. Motion and Interaction

Motion should feel calm and purposeful.
Use for:
- panel transitions
- hover feedback
- expanding details
- save confirmations
- task completion feedback

Recommended timings:
- micro interactions: 120–180ms
- panel transitions: 180–240ms
- modal/sheet entrances: 220–280ms

## 15. Imagery and Illustration

Recommended:
- clean lifestyle photography with real homes, cars, gardens, travel, and health admin contexts
- quiet editorial illustration for empty states
- simple line illustrations for onboarding

Avoid:
- cheesy stock imagery
- exaggerated smiles
- over-illustrated dashboards

## 16. Accessibility

Requirements:
- WCAG AA contrast minimum
- keyboard navigability
- visible focus states
- semantic structure
- screen-reader-friendly controls
- large enough tap targets
- colour is never the only signifier

Minimums:
- interactive hit areas: 44x44px
- body text should rarely go below 14px
- strong visible focus ring on all interactive elements

## 17. Voice and UI Copy Style

The interface language should be:
- clear
- direct
- helpful
- calm
- practical

Examples:
- “Boiler service due in 12 days”
- “Your car insurance renews next month”
- “3 jobs need attention this week”
- “Passport expires in 5 months”

Avoid:
- jargon-heavy enterprise copy
- robotic system language
- over-cheerful fluff
- vague labels

## 18. Dashboard Design Pattern

The main dashboard should answer three things immediately:
- what needs attention
- what is coming up
- what has changed recently

Recommended dashboard blocks:
- due soon
- overdue items
- active reminders
- upcoming renewals
- recent documents added
- monthly spend summary
- quick capture actions
- module snapshots

## 19. Security and Trust Visual Language

The product should visually signal:
- security
- reliability
- privacy
- continuity

How:
- restrained UI
- stable layouts
- clear document ownership and timestamps
- visible audit/history patterns
- sensible empty and error states
- reassurance text where appropriate

## 20. Marketing Site Style Direction

The marketing site should feel:
- premium
- simple
- modern
- benefit-led

Suggested sections:
- hero statement
- product family overview
- module cards
- screenshots/mockups
- household benefits
- trust/security section
- pricing preview
- FAQ
- CTA

## 21. Design System Tokens Summary

### Colour tokens
- `color.text.primary`
- `color.text.secondary`
- `color.text.muted`
- `color.bg.canvas`
- `color.bg.surface`
- `color.bg.surfaceAlt`
- `color.border.default`
- `color.action.primary`
- `color.action.primaryHover`
- `color.status.success`
- `color.status.warning`
- `color.status.danger`
- `color.status.info`
- `color.module.home`
- `color.module.car`
- `color.module.garden`
- `color.module.cover`
- `color.module.travel`
- `color.module.health`

### Radius tokens
- `radius.sm = 8`
- `radius.md = 12`
- `radius.lg = 16`
- `radius.xl = 24`

### Spacing tokens
- `space.1 = 4`
- `space.2 = 8`
- `space.3 = 12`
- `space.4 = 16`
- `space.5 = 20`
- `space.6 = 24`
- `space.8 = 32`
- `space.10 = 40`
- `space.12 = 48`
- `space.16 = 64`

## 22. MVP Design Deliverables

Recommended first design deliverables:
- brand moodboard
- colour and token system
- type and spacing system
- responsive shell layout
- dashboard design
- module landing screen templates
- list/card patterns
- detail view pattern
- form pattern library
- reminder/alert pattern set
- document upload and view pattern

## 23. Final Design Intent

OrderedHome should feel like a premium household operating system.

It should be:
- modern but not trendy for the sake of it
- responsive without compromise
- information-rich without feeling heavy
- modular without feeling fragmented
- trustworthy without feeling corporate

The result should feel like a product that helps people keep life in order with less friction, less forgetting, and much better visibility.
