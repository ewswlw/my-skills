# YTM Capital — Credit Investing design foundations

**Canonical reference:** This file is the long-form source for brand voice, token semantics, page-level composition, and quality gates. Keep it aligned with `tokens.json` (`schema_version`). If you also maintain a TypeUI or `TYPEUI_SH_MANAGED` block elsewhere, reconcile changes here and bump `schema_version` in `tokens.json` as the system of record (see `SKILL.md`).

**Last reconciled:** 2026-04-27 — page-level brand system pass (navy surfaces, gold accents, logo, dashboard scaffolds). See changelog at the bottom.

---

## 1. Mission and scope

YTM Capital's Credit Investing work products should read as **rigorous, institutional, and clear**: confident without hype, data-forward, and accessible by default. Visual design supports **clarity and comparability** (charts, tables, dashboards, printed decks, and web snippets), not decoration.

The brand reads on screen as **deep navy + warm gold**: dark navy page surfaces, slightly lighter navy panels, and thin gold rules used as section dividers, KPI accents, and emphasis lines. **Pure black** (`#000000` or near-black `#0b0d10`) is **not** on-brand for surfaces — use the navy stack from `tokens.json`.

**On-screen** charts and dashboards use the navy `chart.panel`. **Light slide or print** bodies follow `data-viz.md` (print) and `chart.tick_print`, not a dark panel dropped onto white paper.

**In scope of this system:** color roles, typography, spacing, motion, surfaces, **page-level composition** (logo, header bars, KPI cards, accent rules), and **semantic** use of those tokens in deliverables.
**Out of scope (v1):** inventing logos, wordmarks, or marketing assets that are not supplied under `assets/`.

---

## 2. Brand principles

- **Clarity over noise:** Prefer a restrained palette, consistent scales, and legible type over extra colors.
- **One system:** Agents and implementers use **semantic token names** (see `tokens.json`); ad hoc hex is reserved for vetted **derived** colors documented in `references/data-viz.md` and verified for contrast.
- **Institutional restraint:** Generous negative space, narrow set of weights, gold used sparingly as an accent (not a fill). Avoid dense, cluttered "data-dump" layouts.
- **Accessibility (WCAG 2.2 AA):** UI text and **chart labels / tick / legend** text on chosen backgrounds must meet **4.5:1** for normal text where applicable. Do not use `color.text.tertiary` (`#0000ee`) for small chart or dense label text; it is reserved for **text links** on light surfaces.
- **"More colorful" / punchier requests:** Must not add arbitrary new hues. Must first vary contrast, type weight, panel elevation (`color.surface.raised` → `color.surface.elevated`), spacing, and allowed series order while staying within WCAG. Optional non-color encodings (pattern, dash, hatch) are should-level for critical comparisons.

---

## 3. Typography

- **Primary sans:** **Montserrat** (with sensible system fallbacks) for headings, body, and UI.
- **Numeric KPI values:** Montserrat 600/700 at `type.scale.2xl`–`3xl`. Pair with a Montserrat 500 caption at `type.scale.sm` directly beneath, separated only by leading.
- **Section headers:** Montserrat 600 at `type.scale.lg`–`xl`, often paired with a thin **3 px gold** vertical accent line on the leading edge (see §6).
- **Numeric data** in tables and labels: tabular alignment as appropriate; no decorative type.
- **Scales** are defined in `tokens.json` under `type.scale.*`.

---

## 4. Color — foundations (marketing / UI)

Semantic roles (see `tokens.json` for exact hex unless noted as chart-only in `data-viz.md`):

| Token path | Role |
|------------|------|
| `color.text.primary` | Main body and primary labels on default surfaces. |
| `color.text.secondary` | Supporting text, de-emphasized UI copy. |
| `color.text.tertiary` | **Link blue** for text links on light-appropriate surfaces (`#0000ee`). **Not** for small chart or dense label text. |
| `color.text.muted` | Captions, axis titles on dark navy. |
| `color.text.inverse` | Primary text on light / inverse surfaces (resolves to navy). |
| `color.text.accent` | **Gold** text accent — KPI values, callouts, brand wordmark colorization. Use sparingly. |
| `color.surface.default` | Default page background — **deep navy** (`#162236`). |
| `color.surface.raised` | Elevated panels and chart panels — **navy panel** (`#1c2d42`). |
| `color.surface.elevated` | Cards and overlays sitting above raised surfaces — **navy card** (`#1e3048`). |
| `color.surface.strong` | **Print and light** surfaces (paper, PDF body); re-verify any dark text. |
| `color.brand.navy` / `navy_deep` / `navy_panel` / `navy_card` | Authentic YTM website navy stack — use these via the `surface.*` aliases above; raw `brand.*` values are for the rare case you need to bypass surface semantics. |
| `color.brand.blue` | YTM logo blue (`#4a8ec2`) — also used as `chart.series.1`. |
| `color.brand.gold` / `gold_soft` | Warm gold accent (`#c9a84c` / `#d8bf78`) — section dividers, KPI rules, hover states. **Never** as a wide background fill. |
| `color.brand.divider` | Hairline divider on navy (`#2a3a52`). |
| `color.accent.line_primary` | Default vertical accent rule — **gold**. |
| `color.accent.line_secondary` | Alternative vertical accent rule — **brand blue**. |
| `color.accent.line_neutral` | Neutral vertical rule on navy — soft white. |

**Rule:** `SKILL.md` and task instructions use **names only** for component guidance; full hex for foundations lives in `tokens.json` and this document where needed for human readers.

---

## 5. Space, radii, motion

- **Space:** `space.*` in `tokens.json`. Default dashboard rhythm is `space.5` (24 px) gap between cards, `space.6` (32 px) outer page padding. Use `space.7`–`space.8` between major sections to enforce institutional negative space.
- **Radii:** `radius.md` (8 px) for cards and chart panels; `radius.lg` (12 px) for hero KPI tiles. Avoid pill-style radii on data surfaces.
- **Motion:** `motion.duration.*` for transitions; avoid unnecessary animation on data-dense or print-bound outputs.

---

## 6. Page-level composition (brand motifs)

These motifs are what make a layout read as **YTM**, not generic dark mode. They are required for any "dashboard", "report", or "presentation-style" deliverable.

### 6.1 Logo placement (mandatory for branded deliverables)

- **Every** dashboard, KPI report, branded slide, and PDF export **must** include the official YTM logo from `assets/`.
- **Default placement:** **top-left** of the page or first slide. For Matplotlib figures, use `OffsetImage` anchored at the top-left of the figure (above the first axes row). For HTML/React, place inside the page header `<header>` left cluster.
- **Default size:** `logo.default_dashboard_height_px` (40 px). **Minimum** height is `logo.min_height_px` (28 px) — never render the logo smaller than this.
- **Asset preference:** `ytm_logo_horizontal.png` for wide layouts; `ytm_icon_192.png` for square or compact headers (favicons, small cards). Do **not** modify, recolor, or stretch the logo.
- **Clear space:** Maintain at least the logo's icon-height of clear space on all sides — do not crowd it with text or rules.

### 6.2 Header bar

- Sits across the full page width above the dashboard content area.
- Contents, left to right: **logo** (top-left), then page title (Montserrat 600, `type.scale.xl`), then optional subtitle/timestamp in `color.text.muted`.
- Background: `color.surface.default` (page navy), no border.
- Terminate the header with a **1 px** `color.brand.divider` hairline rule across the bottom of the header band; immediately under that, place a **2 px** `color.brand.gold` rule the width of the page title text only (not the full page) as the brand signature accent.

### 6.3 Vertical accent lines (KPI cards & section headers)

This is the single most distinctive YTM motif. Use it consistently:

- **KPI card:** `color.surface.elevated` background, `radius.md` corners, `space.4` inner padding. On the **leading edge** (left side), draw a **3 px** vertical rule (`--accent-line-width`) in `color.accent.line_primary` (gold) running the full height of the card. Inside the card: KPI value top (Montserrat 700, `type.scale.2xl`–`3xl`, `color.text.primary` or `color.text.accent` for emphasis), caption beneath in `color.text.muted` at `type.scale.sm`.
- **Section header (within a dashboard):** Place a 3 px gold vertical rule to the left of the section title text. Headers without this rule should be reserved for sub-sub-sections.
- **Alternative colors:** Use `color.accent.line_secondary` (brand blue) when the section is comparative/secondary; `color.accent.line_neutral` (soft white) for neutral grouping. Default is gold.

### 6.4 Cards and panels

- Card surface: `color.surface.elevated`. Chart panel inside a card: `color.surface.raised` (one step darker, so the chart visually recedes inside the card).
- **No drop shadows** on data surfaces — use surface tone differences for elevation, not blur.
- Card title: Montserrat 600 at `type.scale.md`–`lg`, in `color.text.primary`. Optional caption in `color.text.muted`.

### 6.5 Negative space

- Page outer padding: `space.6` (32 px) minimum.
- Card-to-card gap: `space.5` (24 px) minimum.
- Major section separation: `space.7`–`space.8` (48–64 px) above the next section header.
- Resist the urge to fill empty regions with extra widgets; an institutional layout breathes.

### 6.6 Don'ts

- No black backgrounds (`#000` / GitHub-dark `#0d1117`) for page surfaces — always navy.
- No neon/saturated accent palettes (purple, magenta, lime). Keep within the navy + gold + brand-blue family.
- No drop shadows, no glassmorphism, no rounded-pill chart legends.
- No logo recoloring, rotation, or watermarking. No fabricated wordmarks.

---

## 7. Data visualization (normative pointer)

Chart- and export-specific roles (`chart.panel`, `chart.grid`, `chart.series.1`–`chart.series.4`, screen vs print, contrast matrix) are **fully specified in `references/data-viz.md`**. The `chart` subtree in `tokens.json` holds the resolved values. Do not fork chart semantics in this file; extend `data-viz.md` and bump `schema_version` when chart tokens change.

Note the series order leads with **brand blue** (`chart.series.1`) and **gold** (`chart.series.2`) so a typical 1–2 series comparison reads on-brand by default.

---

## 8. Required output structure (for agent-produced artifacts)

1. **Identify surface:** Screen (dark navy) vs print/PDF (often light) per use case.
2. **Apply font stack** and semantic colors from `tokens.json` / fragments.
3. **For dashboards / branded reports:** Place the **logo top-left**, build a header bar with the gold signature rule (§6.2), and use **vertical gold accent lines** on KPI cards and section headers (§6.3).
4. **Charts:** Use **series roles in order** before inventing new colors; use `references/chart_palette.py` (or copy dict from JSON) for Matplotlib/Plotly/pandas.
5. **Verify:** Contrast for tick/legend/label text against the active panel/background, per `data-viz.md` matrix.
6. **Logos / identity marks:** Use **only** files from `assets/`. Never invent or recolor.

---

## 9. Quality gates (must / should)

- **Must:** Page surface is navy from `color.surface.*`, never pure black or GitHub dark.
- **Must:** Branded dashboards / reports include the YTM logo from `assets/`, top-left, ≥ `logo.min_height_px`.
- **Must:** Meet contrast requirements for text and **chart labels** on stated backgrounds.
- **Must:** Honor user **opt-out** of YTM defaults when the prompt uses phrases listed in `SKILL.md` (takes precedence).
- **Should:** Use vertical gold accent rules on KPI cards and section headers (the YTM signature motif).
- **Should:** Add pattern, hatch, or shape differentiation for at least one critical series when color-on-dark is ambiguous.
- **Should:** Prefer copy-pastable `references/fragments/*` and `chart_palette` over re-typing hex.

---

## 10. Glossary (token roots in `tokens.json`)

- `schema_version` — String; bump when any key in `tokens.json` changes.
- `font.*` — Family and weights.
- `type.scale.*` — Type scale step names to numeric values.
- `color.text.*` / `color.surface.*` — Text and surface roles for UI and print.
- `color.brand.*` — Authentic YTM website palette (navy stack, blue, gold, divider).
- `color.accent.*` — Vertical accent rule colors (KPI cards, section headers).
- `space.*`, `radius.*`, `motion.*` — Layout and animation.
- `chart.*` — Panel, grid, axis, tick, legend, series, accent rule (see `data-viz.md`).
- `logo.*` — Logo asset preferences and sizing rules.

---

## 11. Changelog

- **2026-04-27 — `schema_version` 2026.04.27.1** (page-level brand system pass).
  - Replaced GitHub-dark surfaces with the authentic YTM navy stack (`color.surface.default` → `#162236`, `raised` → `#1c2d42`, `elevated` → `#1e3048`).
  - Added `color.brand.*` (navy variants, blue `#4a8ec2`, gold `#c9a84c`, divider) and `color.accent.line_*` for vertical accent rules.
  - Re-ordered `chart.series.*` to lead with brand blue then gold; updated `chart.panel`, `chart.grid` to navy values.
  - Added `logo.*` token block (placement, sizing, asset preferences).
  - Added §6 "Page-level composition" covering logo placement, header bar with gold signature rule, vertical accent lines, cards, and negative space.
  - Closes the gap identified in `Forensic Audit_ _ytm-branding Skill vs. Actual Website Aesthetics.md`: chart-level dark theme → page-level brand system.
- 2026-04-23 — Initial package scaffold; chart roles and `schema_version` align with U2–U3 implementation pass.
