# YTM Capital — Credit Investing design foundations

**Canonical reference:** This file is the long-form source for brand voice, token semantics, and quality gates. Keep it aligned with `tokens.json` (`schema_version`). If you also maintain a TypeUI or `TYPEUI_SH_MANAGED` block elsewhere, reconcile changes here and bump `schema_version` in `tokens.json` as the system of record (see `SKILL.md`).

**Last reconciled (implementation scaffold):** 2026-04-23 — replace or merge with your exported DESIGN if your live source is more current.

---

## 1. Mission and scope

YTM Capital’s Credit Investing work products should read as **rigorous, institutional, and clear**: confident without hype, data-forward, and accessible by default. Visual design supports **clarity and comparability** (charts, tables, small dashboards, printed decks, and web snippets), not decoration. **On-screen** charts may use a dark `chart.panel`; **light slide or print** bodies should follow `data-viz.md` (print) and `chart.tick_print`, not a dark panel dropped onto white paper.

**In scope of this system:** color roles, typography, spacing, motion, surfaces, and **semantic** use of those tokens in deliverables.  
**Out of scope (v1):** inventing logos, wordmarks, or marketing assets that are not supplied under `assets/` with explicit rules.

---

## 2. Brand principles

- **Clarity over noise:** Prefer a restrained palette, consistent scales, and legible type over extra colors.
- **One system:** Agents and implementers use **semantic token names** (see `tokens.json`); ad hoc hex is reserved for vetted **derived** colors documented in `references/data-viz.md` and verified for contrast.
- **Accessibility (WCAG 2.2 AA):** UI text and **chart labels / tick / legend** text on chosen backgrounds must meet **4.5:1** for normal text where applicable. **Do not** use `color.text.tertiary` (`#0000ee`) for small chart or dense label text; it is reserved for **text links** on appropriate surfaces.
- **“More colorful” / punchier requests:** **Must not** add arbitrary new hues. **Must** first vary **contrast, type weight, panel elevation** (`color.surface.raised`), **spacing**, and **allowed series order** (per `data-viz.md` and `SKILL.md`) while staying within WCAG constraints. Optional **non-color** encodings (pattern, shape, hatch) are **should**-level for critical comparisons when color alone is ambiguous (especially on dark panels).

---

## 3. Typography

- **Primary sans:** **Montserrat** (with sensible system fallbacks) for headings, body, and UI. Load via normal web or document font stack; bundling a WOFF2 in-repo is not required for v1.
- **Scales** are defined in `tokens.json` under `type.scale.*` (pixel/rem-style numeric steps). Use the scale for chart tick and legend text where matplotlib/plotly expose font size in points—map semantically to “caption” / “body” as in `data-viz.md`.
- **Numeric data** in reports and labels: tabular alignment as appropriate; no decorative type.

---

## 4. Color — foundations (marketing / UI)

Semantic roles (see `tokens.json` for exact hex unless noted as chart-only in `data-viz.md`):

| Token path | Role |
|------------|------|
| `color.text.primary` | Main body and primary labels on default surfaces. |
| `color.text.secondary` | Supporting text, de-emphasized UI copy. |
| `color.text.tertiary` | **Link blue** for text links on light-appropriate surfaces (`#0000ee`). **Not** for small chart or dense label text. |
| `color.text.inverse` | Primary text on light / inverse surfaces. |
| `color.surface.default` | Default app / slide background (screen, dark-leaning). |
| `color.surface.raised` | Elevated panels, cards, chart panels. |
| `color.surface.strong` | **Print and light** surfaces (e.g. paper, PDF body); re-verify any dark text. |

**Rule:** `SKILL.md` and task instructions use **names only** for component guidance; full hex for foundations lives in `tokens.json` and this document where needed for human readers.

---

## 5. Space, radii, motion

- **Space:** `space.*` in `tokens.json` — use consistent steps for padding, gap, and chart margins.
- **Radii:** `radius.*` for buttons, cards, and rounded figure elements when applicable.
- **Motion:** `motion.duration.*` for transitions; avoid unnecessary animation on data-dense or print-bound outputs.

---

## 6. Data visualization (normative pointer)

Chart- and export-specific roles (`chart.panel`, `chart.grid`, `chart.series.1`–`chart.series.4`, screen vs. print, contrast matrix) are **fully specified in `references/data-viz.md`**. The `chart` subtree in `tokens.json` holds the resolved values. Do not fork chart semantics in this file; extend `data-viz.md` and bump `schema_version` when chart tokens change.

---

## 7. Required output structure (for agent-produced artifacts)

1. **Identify surface:** Screen (dark) vs print/PDF (often light) per use case.  
2. **Apply font stack** and semantic colors from `tokens.json` / fragments.  
3. **Charts:** use **series roles in order** before inventing new colors; use `references/chart_palette.py` (or copy dict from JSON) for Matplotlib/Plotly/pandas.  
4. **Verify:** Contrast for tick/legend/label text against the active panel/background, per `data-viz.md` matrix.  
5. **Logos / identity marks:** do not add unless `assets/` and rules exist (future).

---

## 8. Quality gates (must / should)

- **Must:** Meet contrast requirements for text and **chart labels** on stated backgrounds.  
- **Must:** Honor user **opt-out** of YTM defaults when the prompt uses phrases listed in `SKILL.md` (takes precedence).  
- **Should:** Add pattern, hatch, or shape differentiation for at least one critical series when color-on-dark is ambiguous.  
- **Should:** Prefer copy-pastable `references/fragments/*` and `chart_palette` over re-typing hex.

---

## 9. Glossary (token roots in `tokens.json`)

- `schema_version` — String; bump when any key in `tokens.json` changes.  
- `font.*` — Family and weights.  
- `type.scale.*` — Type scale step names to numeric values.  
- `color.*` — Text and surface roles for UI and print.  
- `space.*`, `radius.*`, `motion.*` — Layout and animation.  
- `chart.*` — Panel, grid, axis, tick, legend, series roles (see `data-viz.md`).

---

## 10. Changelog (optional)

*When you sync from an external design source, add one line: date, what changed, and new `schema_version`.*

- 2026-04-23 — Initial package scaffold; chart roles and `schema_version` align with U2–U3 implementation pass.
