# Deekshak SS — Complete Design System

**Status:** Canonical brand source of truth  
**Source site:** https://deekshak.site  
**Code:** `H:\portfolio\site\src\styles.css` + `src/components/portfolio/*`  
**Consumers:** Portfolio · Business OS (`app.deekshak.site`) · any future Deekshak product  

**Rule:** Replicate **only** these tokens and recipes. No ad-hoc hex, no new fonts, no freeform spacing.

---

## 0. Design philosophy

| Principle | What it means |
|---|---|
| Proof + sex appeal | Neon / glass motion for brand; content stays honest and dense |
| Dark glassmorphism | Semi-transparent surfaces over deep navy + low-chroma aurora |
| Dual type pairing | Inter for structure; Instrument Serif *italic* only for accent words |
| Discrete scales | USWDS-style limited palettes (8pt space, fixed radii, named colors) |
| Product vs marketing | Marketing = colorful hero/footer; product canvas = quiet mid navy |

---

## 1. Fonts

### Load (Google Fonts)

```
Inter:wght@300;400;500;600;700
Instrument+Serif:ital@0;1
JetBrains+Mono:wght@400;500
display=swap
```

Preconnect: `fonts.googleapis.com` + `fonts.gstatic.com` (anonymous).

### Families (CSS vars)

| Token | Stack | Role |
|---|---|---|
| `--font-sans` | `"Inter", ui-sans-serif, system-ui, sans-serif` | Body, UI, nav, **all structure headings** |
| `--font-display` / `--font-serif` | `"Instrument Serif", "Cormorant Garamond", ui-serif, Georgia, serif` | **Accent phrases only** |
| `--font-mono` | `"JetBrains Mono", ui-monospace, SFMono-Regular, monospace` | Eyebrows, chips, stage numbers, labels |

### Typography rules

| Element | Font | Weight | Tracking | Notes |
|---|---|---|---|---|
| `h1–h4` | Inter (`--font-sans`) | **600** | `-0.025em` | Never full heading in Instrument Serif |
| Body | Inter | 400 | normal | `font-feature-settings: "ss01", "cv11"` |
| Accent span | Instrument Serif | **400** | inherit | Classes: `font-display italic font-normal text-gradient` |
| Eyebrow / kicker | JetBrains Mono | 400–500 | `0.18em–0.22em` | Uppercase |
| Nav label | Inter | 500 | tight | `text-sm` |
| Button label | Inter | 500–600 | slight negative | Primary 600 |

### Type scale (from live components)

| Use | Size recipe |
|---|---|
| Hero H1 | `clamp(2.15rem, 7.5vw, 4.5rem)` · `leading-[1.05]` · `tracking-tight` |
| Section H2 | `clamp(1.65rem, 5.5vw, 3rem)` · `leading-[1.1]` · `font-semibold` |
| Card H3 | `text-xl` → `sm:text-2xl` → `md:text-3xl` · `font-semibold` · `tracking-tight` |
| Body | `15px` / `text-base` / `md:text-lg` · `leading-relaxed` · `text-muted-foreground` |
| Subhead (hero) | `text-base` → `sm:text-lg` → `md:text-xl` · `font-medium` · `text-foreground/90` |
| Eyebrow | `10px` → `11px` · mono · uppercase · `tracking-[0.18em]` → `0.22em` |
| Chip / mono tag | `10px–11px` mono |
| Button | `text-xs` (compact) / `text-sm` (default) · `font-semibold` on primary-lg |

### Text utilities

```css
.text-gradient {
  background-image: var(--gradient-text);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.text-balance { text-wrap: balance; }
.text-pretty  { text-wrap: pretty; }
.break-anywhere { overflow-wrap: anywhere; word-break: break-word; }
```

### Selection

```css
::selection {
  background: color-mix(in oklab, var(--neon) 45%, transparent);
  color: var(--foreground);
}
```

### Do NOT

- Use Space Grotesk or other display sans  
- Put Instrument Serif on entire titles  
- Use `font-weight: 700` on Instrument Serif (looks faux-bold)

---

## 2. Color tokens (exact)

All values from live `:root` in `styles.css`.

### Core surfaces

| Token | Value | Use |
|---|---|---|
| `--background` | `oklch(0.14 0.02 265)` | Page base (deep navy, not pure black) |
| `--foreground` | `oklch(0.98 0.005 250)` | Primary text |
| `--surface` | `oklch(0.17 0.024 265)` | Raised panels |
| `--surface-2` | `oklch(0.2 0.028 265)` | Hover / secondary surface |
| `--card` | `oklch(0.18 0.025 265)` | Cards |
| `--card-foreground` | `oklch(0.98 0.005 250)` | Card text |
| `--popover` | `oklch(0.18 0.025 265)` | Popovers |
| `--muted` | `oklch(0.22 0.025 265)` | Muted fills |
| `--muted-foreground` | `oklch(0.72 0.02 260)` | Secondary text |
| `--secondary` | `oklch(0.24 0.03 265)` | Secondary UI |
| `--secondary-foreground` | `oklch(0.98 0.005 250)` | |

### Brand / action

| Token | Value | Use |
|---|---|---|
| `--neon` | `oklch(0.78 0.18 210)` | Primary accent (cyan-electric) |
| `--neon-2` | `oklch(0.7 0.22 295)` | Violet brand pair |
| `--neon-3` | `oklch(0.82 0.17 165)` | Live / success mint |
| `--primary` | `oklch(0.72 0.19 235)` | Ring / legacy primary (electric blue) |
| `--primary-foreground` | `oklch(0.12 0.02 265)` | Text on neon gradient buttons |
| `--electric` | `oklch(0.72 0.19 235)` | Alias for electric blue (links optional) |
| `--teal` | `oklch(0.78 0.14 195)` | Support accent |
| `--emerald` | `oklch(0.76 0.15 165)` | Success (prefer neon-3 for status dots) |
| `--accent` | `oklch(0.68 0.22 300)` | Magenta-violet accent |
| `--destructive` | `oklch(0.65 0.22 25)` | Errors |

### Borders / form

| Token | Value |
|---|---|
| `--border` | `oklch(1 0 0 / 0.08)` |
| `--border-strong` | `oklch(1 0 0 / 0.14)` |
| `--input` | `oklch(1 0 0 / 0.12)` |
| `--ring` | `oklch(0.72 0.19 235)` |

### Gradients

```css
--gradient-hero:
  radial-gradient(ellipse at top, oklch(0.28 0.12 265 / 0.55), transparent 60%),
  radial-gradient(ellipse at bottom right, oklch(0.35 0.15 295 / 0.35), transparent 55%);

--gradient-brand: linear-gradient(135deg, var(--neon), var(--neon-2));
/* buttons also use: linear-gradient(to right, neon, neon-2) */

--gradient-text: linear-gradient(
  135deg,
  oklch(0.95 0.03 220),
  oklch(0.78 0.18 210) 45%,
  oklch(0.7 0.22 295)
);

--gradient-soft: radial-gradient(
  ellipse at top,
  color-mix(in oklab, var(--electric) 22%, transparent),
  transparent 60%
);
```

### Shadows

```css
--shadow-glow: 0 0 40px -8px oklch(0.72 0.19 235 / 0.55);

--shadow-glow-lg:
  0 0 80px -10px oklch(0.72 0.19 235 / 0.5),
  0 0 30px -5px oklch(0.7 0.22 295 / 0.35);

--shadow-card:
  0 10px 40px -12px oklch(0 0 0 / 0.6),
  inset 0 1px 0 oklch(1 0 0 / 0.06);
```

### Ambient mid-page (fixed, quiet)

Base:

```css
linear-gradient(180deg,
  oklch(0.145 0.022 265),
  oklch(0.12 0.018 268) 45%,
  oklch(0.13 0.02 265)
)
```

Dull multi-hue wash (`opacity: 0.70`):

```css
radial-gradient(ellipse 90% 50% at 50% -5%, oklch(0.28 0.08 265 / 0.35), transparent 55%),
radial-gradient(ellipse 60% 40% at 100% 40%, oklch(0.26 0.07 295 / 0.12), transparent 50%),
radial-gradient(ellipse 55% 35% at 0% 70%, oklch(0.24 0.06 220 / 0.1), transparent 50%)
```

Grid: `bg-grid` at `opacity: 0.18`, mask  
`radial-gradient(ellipse at center, black 20%, transparent 70%)`.

### Hero / Contact colorful wash

- Layer: `bg-hero` (full `--gradient-hero`)  
- Grid: `bg-grid opacity-40` with mask `ellipse_at_center, black 30%, transparent 75%`  
- Orbs:  
  - `bg-neon/20 blur-[100px–120px] animate-glow-pulse` (large top center)  
  - `bg-neon-2/20 blur-[120px] animate-glow-pulse` delay `-1.5s` (desktop only right)  
- Contact also: `bg-hero opacity-90` + dual orbs  

### Theme color (meta)

`theme-color` / app chrome: deep navy near `#0a0f1c` / `oklch(0.14 0.02 265)`.

---

## 3. Spacing (8pt grid only)

| Token | rem | px |
|---|---|---|
| `--space-1` | 0.25 | 4 |
| `--space-2` | 0.5 | 8 |
| `--space-3` | 0.75 | 12 |
| `--space-4` | 1 | 16 |
| `--space-5` | 1.5 | 24 |
| `--space-6` | 2 | 32 |
| `--space-8` | 3 | 48 |
| `--space-10` | 4 | 64 |
| `--space-12` | 6 | 96 |
| `--space-16` | 8 | 128 |

### Layout recipes

| Element | Spec |
|---|---|
| Container | `max-w-6xl` (72rem) · `px-4 sm:px-6` |
| Section Y | `py-14 sm:py-20 md:py-28` |
| Scroll margin (fixed nav) | `scroll-mt-24 md:scroll-mt-28` |
| Header → content | `mt-8 sm:mt-10 md:mt-14` |
| Card padding | `p-4 sm:p-6 md:p-8` |
| Card / grid gap | `gap-3 sm:gap-4` (default) · `gap-6–10` for larger layouts |
| Nav outer | `px-3 sm:px-4` · `pt-[max(0.75rem,env(safe-area-inset-top))]` |
| Nav inner | `px-3 py-2.5 sm:px-5 sm:py-3` |
| Button pad | compact `px-3 py-2` · default `px-5 py-3` |
| Min touch target | `min-h-9` / `min-h-10` / `min-h-11` (44px-ish) |

---

## 4. Radius

| Token / class | Formula / value | Use |
|---|---|---|
| `--radius` | `0.85rem` (~13.6px) | Base |
| `sm` | `calc(var(--radius) - 6px)` | Small controls |
| `md` | `calc(var(--radius) - 2px)` | |
| `lg` | `var(--radius)` | |
| `xl` / `rounded-xl` | `calc(var(--radius) + 2px)` ≈ **0.975rem** | **Buttons**, inputs, brand badge, stage tiles |
| `2xl` / `rounded-2xl` | `calc(var(--radius) + 10px)` ≈ **1.475rem** | **Nav bar**, cards (mobile), drawers |
| `3xl` / `rounded-3xl` | `calc(var(--radius) + 18px)` ≈ **1.975rem** | **Large flagship cards** (sm+) |
| `full` | `9999px` | Eyebrow pills, filter chips, status dots |

---

## 5. Surfaces & utilities

### `glass`

```css
backdrop-filter: blur(14px) saturate(140%);
background: linear-gradient(oklch(1 0 0 / 0.04), oklch(1 0 0 / 0.015));
border: 1px solid oklch(1 0 0 / 0.08);
```

Use: nav pill, eyebrows, secondary chips, floating tags.

### `glass-strong`

```css
backdrop-filter: blur(20px) saturate(160%);
background: linear-gradient(oklch(1 0 0 / 0.07), oklch(1 0 0 / 0.02));
border: 1px solid oklch(1 0 0 / 0.1);
```

Use: feature cards, elevated content panels.

### Optional card sheen

Top hairline on flagship cards:

```html
<div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent" />
```

### Nested tiles (inside glass-strong)

```
rounded-xl border border-white/8 bg-white/5 px-3.5 py-3
hover: bg-white/[0.07]
```

### `bg-grid`

```css
background-image:
  linear-gradient(oklch(1 0 0 / 0.045) 1px, transparent 1px),
  linear-gradient(90deg, oklch(1 0 0 / 0.045) 1px, transparent 1px);
background-size: 60px 60px;
```

### Buttons

**Primary** (`btn-primary`):

```css
background-image: linear-gradient(to right, var(--neon), var(--neon-2));
color: var(--primary-foreground);
box-shadow: var(--shadow-glow);
/* no border */
transition: filter 0.2s ease, transform 0.2s ease;
hover: filter: brightness(1.1);
```

**Primary large** (`btn-primary-lg`): same + `shadow-glow-lg`.

**Secondary:** `glass-strong` or `border border-border-strong` + `hover:bg-white/10` or `hover:bg-white/5`.

**Ghost / tertiary:** text only or light fill `hover:bg-white/5`.

Shape: **`rounded-xl` always for CTAs** (not full pill).

### Accent / status dots

| Kind | Spec |
|---|---|
| Eyebrow neon dot | `h-1 w-1 rounded-full bg-neon` |
| Brand accent-dot | `6px` circle, `bg-neon`, glow `0 0 10px neon 70%` |
| Live status | `bg-neon-3` + `animate-ping` ring optional |
| Brand badge | `h-9 w-9 rounded-xl bg-gradient-to-br from-neon to-neon-2 text-primary-foreground shadow-glow` · initials **DS** / **OS** |

### Links (in body)

```
text-foreground underline decoration-neon/40 underline-offset-4 hover:decoration-neon
```

---

## 6. Motion

| Name | Keyframes / timing | Where |
|---|---|---|
| `fade-up` | y 24→0, opacity 0→1, **0.7s** `cubic-bezier(0.22, 1, 0.36, 1)` | Section enters |
| `float` | y 0 ↔ −14px, **6s** ease-in-out infinite | Portrait tags |
| `glow-pulse` | opacity 0.55↔0.9, blur 40↔60px, **4s** ease-in-out infinite | Hero/contact orbs |
| `orbit` | rotate 360 with `translateX(var(--orbit-r,120px))`, **18s** linear | Hero rings |
| `pulse-soft` | opacity 0.55↔1, **3s** | Soft UI pulse |
| `grid-slide` | bg-position +60px, **40s** linear | Optional grid drift |
| Nav enter | y −16→0, opacity, **0.55s** same ease | Header |
| Scroll reveals | duration **0.45–0.65s**, stagger **0.04–0.07s** | Cards |
| Hover | `brightness(1.1)` · subtle translate optional | Buttons |

**Orbit radius:** default 120px · tablet 96px · mobile 72px.

**Reduced motion:** disable float, glow-pulse, orbit, grid animations.

---

## 7. Component recipes (pixel-level)

### 7.1 Nav (fixed)

- Wrapper: `fixed inset-x-0 top-0 z-50` · safe-area top  
- Bar: `glass max-w-6xl rounded-2xl` · flex between  
- Brand badge gradient + optional name (`text-sm font-medium tracking-tight`)  
- Links: `text-sm text-muted-foreground hover:bg-white/5 hover:text-foreground rounded-lg px-2.5–3 py-2`  
- CTA: `btn-primary rounded-xl` · “Demo” on xs / “Live demo” sm+  
- Mobile drawer: `glass rounded-2xl` · `min-h-11` rows · scroll lock body when open  

### 7.2 Section header

1. Glass pill: `inline-flex items-center gap-2 rounded-full glass px-3 py-1`  
2. Neon `h-1 w-1 rounded-full bg-neon`  
3. Mono uppercase eyebrow  
4. Inter semibold H2 (clamp above)  
5. Optional accent: `font-display text-gradient italic font-normal` on 1–3 words  
6. Description: muted, max-w-2xl / max-w-3xl  

### 7.3 Section shell

```
section: relative scroll-mt-24 py-14 sm:py-20 md:scroll-mt-28 md:py-28
inner:   relative mx-auto max-w-6xl px-4 sm:px-6
```

### 7.4 Cards

| Variant | Classes |
|---|---|
| Strong panel | `glass-strong rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 shadow-card` |
| Tool / why tile | `glass-strong rounded-2xl p-4 sm:p-6` · equal height |
| Nested tile | `rounded-xl border-white/8 bg-white/5` |
| Stat cell | `glass rounded-xl sm:rounded-2xl p-3 sm:p-4 text-center` |

### 7.5 Filters / chips

- Active: `bg-gradient-to-r from-neon to-neon-2 text-primary-foreground shadow-glow rounded-full`  
- Idle: `glass text-muted-foreground`  
- Mobile: horizontal scroll, `scrollbar-none`  

### 7.6 Timeline / rail (portfolio)

- Left rail: 1px border + scroll-progress gradient electric→teal  
- Node: `h-3 w-3 rounded-full` electric fill + glow ring  

### 7.7 Workflow / process nodes

- `rounded-xl border` · active = electric border + glow  
- Connector pulse: electric gradient traveling along line  

### 7.8 Contact / footer

- Colorful zone (hero wash)  
- Channel rows: `glass-strong rounded-2xl` · mono label + value  
- Footer: border-t `white/8` · brand badge + explore/connect columns  

### 7.9 Product app mapping (Business OS)

| Portfolio element | App element |
|---|---|
| Nav glass bar | Sidebar glass + mobile topbar glass |
| Brand badge DS | Brand badge **OS** |
| btn-primary | New chat, primary actions, approve |
| glass-strong cards | Plan panel, empty cards, agent tiles, composer |
| Section eyebrow | `.page-kicker` mono pill + neon dot |
| text-gradient italic | Page title accents (*strategist*, *plan*, …) |
| Ambient mid | Body + main-glow dull wash + soft grid |
| Hero orbs | **Do not** put full hero orbs on product chrome (keep canvas quiet) |

---

## 8. Motion easing constants

```
ease-out-expo-ish: cubic-bezier(0.22, 1, 0.36, 1)
```

Used for: nav enter, section titles, card whileInView.

---

## 9. Accessibility & mobile

| Rule | Spec |
|---|---|
| Overflow | `html, body { overflow-x: clip }` |
| Safe areas | top/bottom env() on fixed chrome |
| Touch | min 36–44px targets · tap-highlight transparent |
| Images | `max-width: 100%; height: auto` |
| Reduced motion | disable ambient animations |
| Focus | neon outline 2px offset 2px on interactive |

---

## 10. Z-index map

| Layer | z |
|---|---|
| Ambient | −10 / fixed |
| Content | 0–1 |
| Mobile topbar | 30 |
| Scrim | 40 |
| Sidebar drawer | 50 |
| Portfolio fixed nav | 50 |

---

## 11. Implementation checklist (replication)

Copy in this order:

1. [ ] Fonts link (Inter + Instrument Serif + JetBrains Mono)  
2. [ ] All `:root` color + space + radius tokens (exact oklch)  
3. [ ] Gradients + shadows  
4. [ ] Base body (Inter, selection, h1–h4 rules)  
5. [ ] Utilities: glass, glass-strong, text-gradient, bg-grid, bg-hero, btn-primary(‑lg), accent-dot  
6. [ ] Motion keyframes + reduced-motion  
7. [ ] Ambient mid background  
8. [ ] Component recipes (nav / cards / buttons / kickers)  
9. [ ] No pure `#000` full-bleed mid; no Space Grotesk  

---

## 12. File map

| Path | Role |
|---|---|
| `H:\portfolio\site\DESIGN-SYSTEM.md` | **This file — canonical** |
| `H:\portfolio\site\src\styles.css` | Live CSS implementation |
| `H:\portfolio\site\src\components\portfolio/*` | Component recipes |
| `H:\business-os\docs\DESIGN-SYSTEM.md` | Copy for app monorepo |
| `H:\business-os\apps\web\src\styles.css` | App skin (must match tokens) |

---

## 13. Decision log

| Date | Decision |
|---|---|
| 2026-07 | Brand: Inter + Instrument Serif italic accents + JetBrains Mono |
| 2026-07 | Palette: friend neon tokens (oklch) on deep navy |
| 2026-07 | Mid quiet / hero+footer colorful |
| 2026-07 | 8pt spacing, discrete radii |
| 2026-07 | Exhaustive DS extracted from live portfolio for exact replication |
