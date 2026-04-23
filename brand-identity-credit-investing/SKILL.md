---
name: brand-identity-credit-investing
description: >
  Apply YTM Capital / Credit Investing visual and data-graphics foundations for
  any charts, plots, time series, dashboards, data visualizations, Marimo
  notebooks, Streamlit or Dash apps, HTML/React/CSS or Canvas-style UI, Excel
  and openpyxl-styled tables, PDF/slide/presentation exports, or web snippets —
  when the work is YTM, Credit Investing, fixed income, professional credit
  research, or “on-brand” deliverables, even if the user does not say “brand.”
  Also use for Montserrat, dark panels, and semantic color roles for
  comparability. Do NOT apply when the user clearly opts out with phrases like:
  off-brand, neutral style, not YTM, non-YTM, generic chart, default matplotlib,
  academic style, client template, use your own brand, or another client name.
  Apply more strongly (when ambiguous) if they ask for YTM brand, Credit
  Investing look, on-brand, match our marketing site, or use brand-identity.
  Also use for Jupyter, Voila, or notebook outputs when the deliverable is
  charts or branded UI for YTM / credit work.
---

# YTM / Credit Investing — brand identity (data + UI)

## What this skill does

When the task calls for **data graphics or branded UI** in the YTM / **Credit Investing** world, use this pack so outputs share **one** design system: fonts, surfaces, **chart** roles, accessibility rules, and copy-pastable **stack fragments**. Long-form brand rules live in `references/DESIGN.md` — this file is the **operational** entry (when to use, how to route, what wins in conflicts). **Do not** duplicate every hex from `tokens.json` here; use **semantic names** in prose and code.

## Files (read in this order for a typical chart)

1. `references/DESIGN.md` — missions, must/should, foundations.  
2. `references/tokens.json` — machine-readable values + `schema_version`.  
3. `references/data-viz.md` — `chart.*` semantics, **contrast matrix**, screen vs print, **R12/R13** (tertiary / hatching).  
4. `references/chart_palette.py` — `get_chart_colors()` or `CHART` dict, plus `series_hex_list()` for ordered series-1..4 colors (import or copy the dict in-notebook).  
5. `references/fragments/` — `matplotlib.mplstyle.txt`, `plotly_layout.json`, `web-tokens.css` for the target stack.

## Precedence (R9)

1. **A direct user opt-out** or a competing **non-YTM** brand / style instruction in the **current** prompt **wins** — do not apply this skill’s YTM defaults for that request. If the same prompt **mixes** on-brand and opt-out language, **treat the opt-out as winning** for palette and surfaces.  
2. Else, if the task matches the **description** (charts, viz, YTM, credit, dashboards, **Marimo**, **Streamlit**, web, Excel, etc.), **apply** this skill’s defaults.  
3. Optional project rules (e.g. a future Cursor rule) do **not** override (1). If both exist, user intent in the prompt still wins for opt-out.

## Opt-out vs force (phrase lists; user may edit `SKILL.md`)

| Intent | Example phrases (non-exhaustive) |
|--------|----------------------------------|
| **Opt-out (do not apply YTM defaults)** | off-brand, neutral style, not YTM, non-YTM, generic chart, default matplotlib, academic style, client template, use your own brand, another client’s name |
| **Force (apply when ambiguous)** | YTM brand, Credit Investing look, on-brand, match our marketing site, use brand-identity, YTM Capital styling |

**AE2 / F2:** If an opt-out phrase is present, **do not** apply YTM dark panels or the YTM series palette for that request.

## “More colorful” or punchier (R11)

**Do not** add arbitrary new hues. **Do** adjust contrast, type weight, panel elevation (`color.surface.raised`), spacing, and **series order** within the defined `chart.series.1`–`4` before introducing any new color. If still ambiguous, use **hatching or dash patterns** per `data-viz.md` (R13).

## Logos and assets (R14)

**Do not** invent, download, or place logos, wordmarks, or unapproved marketing art unless `assets/` and explicit rules are added in a follow-up.

## TypeUI / managed blocks (R15)

If `TYPEUI_SH_MANAGED` or similar lives elsewhere, treat **`tokens.json` `schema_version` + this pack’s `references/DESIGN.md`** as the reconciliation anchor for the skill. Sync upstream design changes there, then bump `schema_version`.

---

## Artifact router (R8)

For each deliverable type: read the **references** in the pre-flight, then the **fragment** or **helper** column.

| Artifact | Read first | Pre-flight (short) | Fragment / helper |
|----------|------------|--------------------|------------------|
| **(1) Static chart** (e.g. Matplotlib, PNG, seaborn) | `DESIGN.md`, `data-viz.md`, `tokens.json` | Montserrat or fallback; `chart.panel` + `chart.series.*`; 4.5:1 for tick/legend; no `color.text.tertiary` on small chart text (R12) | `fragments/matplotlib.mplstyle.txt` + `chart_palette.py` |
| **(2) Interactive dashboard** (Plotly, **Marimo**, **Streamlit**, Dash, etc.) | Same + a11y for controls | Font stack; **focus** visible for HTML widgets; color roles from `tokens.json`; contrast from matrix | `fragments/plotly_layout.json` and/or `web-tokens.css` + `chart_palette.py` |
| **(3) Web component** (HTML, React, CSS) | `DESIGN.md`, `tokens.json`, `data-viz.md` | **Focus** states; semantic CSS vars; chart contrast | `fragments/web-tokens.css` |
| **(4) Spreadsheet** (Excel, openpyxl) | `data-viz.md`, `tokens.json` | No fourth fragment in v1: use **hex from `tokens.json` / `get_chart_colors()`** for `Font`, `PatternFill`, borders, cell fills; document mapping in a comment in code | `chart_palette.py` (or read JSON) — align with the **excel** skill in your stack if present |
| **(5) Slide or PDF export** | `data-viz.md` (print section) | Light surface (`color.surface.strong`); `chart.tick_print`; re-verify 4.5:1; no dark `chart.panel` for print body unless the layout is explicitly dark | Same fragments as (1) or (2) but apply **print** tick colors from `tokens.json` |

**F1 / AE1:** With no opt-out, map series through `chart_palette`, **not** default Tab10 as primary. **Deck disambiguation:** if “deck” means an **on-screen** figure (dark UI / screen capture), use row **(1)** with `chart.panel`. If the chart is placed on a **light slide master or print/PDF** with a **light** figure area, do **not** use dark `chart.panel` as the final export — use row **(5)**, `color.surface.strong`, and `chart.tick_print` in `tokens.json` per `data-viz.md` (print section).

---

## Quick pointers

- **WCAG (AE3):** Tick labels on `chart.panel` use `chart.tick` color — not `color.text.tertiary` (R12).  
- **Python:** `import sys` then `sys.path.insert(0, r"<path-to-skill>/references")` (use forward slashes on macOS/Linux; backslashes on Windows) and `import chart_palette`; or read `tokens.json` in-place.  
- **Bumping versions:** When any token key changes, bump `schema_version` in `tokens.json` (see `DESIGN.md` operational notes).  

## Appendix: requirement spot-check (R2–R15)

- **R2:** This file’s **YAML description** is the primary trigger; it names Marimo, Streamlit, dashboards, Excel, etc.  
- **R3–R7, R10–R13:** See `DESIGN.md`, `data-viz.md`, `tokens.json`, `chart_palette.py`, `fragments/`.  
- **R8:** Five types in the router table.  
- **R9:** Precedence section.  
- **R14–R15:** Logos and TypeUI above.
