---
name: ytm-branding
description: >
  Apply YTM Capital / Credit Investing visual and data-graphics foundations for
  any charts, plots, time series, dashboards, data visualizations, Marimo
  notebooks, Streamlit or Dash apps, HTML/React/CSS or Canvas-style UI, Excel
  and openpyxl-styled tables, PDF/slide/presentation exports, or web snippets —
  when the work is YTM, Credit Investing, fixed income, professional credit
  research, or "on-brand" deliverables, even if the user does not say "brand."
  Also use for Montserrat, deep navy + gold surfaces, vertical gold accent
  rules, KPI cards, branded dashboard headers with the YTM logo, and semantic
  color roles for comparability. Do NOT apply when the user clearly opts out
  with phrases like: off-brand, neutral style, not YTM, non-YTM, generic chart,
  default matplotlib, academic style, client template, use your own brand, or
  another client name. Apply more strongly (when ambiguous) if they ask for YTM
  brand, Credit Investing look, on-brand, match our marketing site, or use
  brand-identity. Also use for Jupyter, Voila, or notebook outputs when the
  deliverable is charts or branded UI for YTM / credit work.
---

# YTM / Credit Investing — brand identity (data + UI)

## What this skill does

When the task calls for **data graphics or branded UI** in the YTM / **Credit Investing** world, use this pack so outputs share **one** design system: fonts, **navy + gold surfaces**, **chart** roles, **page-level composition** (logo top-left, gold signature rule, vertical gold accent lines on KPI cards and section headers), accessibility rules, and copy-pastable **stack fragments** including full **dashboard scaffolds**. Long-form brand rules live in `references/DESIGN.md` — this file is the **operational** entry (when to use, how to route, what wins in conflicts). **Do not** duplicate every hex from `tokens.json` here; use **semantic names** in prose and code.

## Skill location (Windows / dual-host)

This skill is installed at:

```
C:\Users\Eddy\.claude\skills\ytm-branding\
├── SKILL.md
├── assets\                                 # YTM logos (R14 — only use what's here)
│   ├── ytm_logo_horizontal.png
│   ├── ytm_logo_horizontal_full.png
│   ├── ytm_icon_192.png
│   └── ytm_icon_full.png
└── references\
    ├── DESIGN.md                           # foundations + page-level composition (§6)
    ├── data-viz.md                         # chart semantics + contrast matrix
    ├── tokens.json                         # source of truth (schema_version)
    ├── chart_palette.py                    # get_chart_colors / get_brand_colors / get_logo_assets
    └── fragments\
        ├── matplotlib.mplstyle.txt         # chart-level style sheet
        ├── plotly_layout.json              # chart-level layout
        ├── web-tokens.css                  # :root tokens for HTML/React/CSS
        ├── matplotlib_dashboard_scaffold.py  # full dashboard: logo + header + KPI cards + charts
        └── web_dashboard_layout.html         # full dashboard: HTML/CSS counterpart
```

Both **Claude Code** and **Cursor** load this skill via the YAML `description` above. Tool naming differs across hosts but the operational steps are identical:

- **Read references with whatever read tool is available** (`Read`, `view`, `cat`-equivalent).
- **For Python imports** use the self-contained pattern in the "Quick pointers" section — never hardcode `/home/ubuntu/...` or any container path.

## Quick start (first action when this skill fires)

1. Identify the **artifact type** from the task (single chart, **full dashboard**, web component, spreadsheet, or slide/PDF) using the **Artifact router** table below. **Dashboards / KPI reports / branded layouts → row (1b) and the dashboard scaffolds, not row (1).**
2. Read `references/DESIGN.md` (especially **§6 page-level composition**) and `references/tokens.json` from this skill's directory.
3. Read the artifact-specific fragment from `references/fragments/` (see router table). For dashboards, **start from the scaffold fragment, do not build layout from scratch**.
4. Apply the semantic token names — **never raw hex** — in your output code or guidance.
5. **Branded deliverables (dashboards, reports, slides, PDFs) MUST include the YTM logo from `assets/`, top-left, ≥ `logo.min_height_px`** (see DESIGN.md §6.1 and the "Logos and assets" section below). Use `chart_palette.get_logo_assets()` to resolve the path.
6. Verify contrast against the matrix in `references/data-viz.md` before delivering.

## Files (read in this order for a typical chart or dashboard)

1. `references/DESIGN.md` — missions, must/should, foundations, **§6 page-level composition** (logo, header, vertical accents, KPI cards, negative space).
2. `references/tokens.json` — machine-readable values + `schema_version` (current: **2026.04.27.1** — navy + gold).
3. `references/data-viz.md` — `chart.*` semantics, **contrast matrix**, screen vs print, **R12/R13** (tertiary / hatching).
4. `references/chart_palette.py` — `get_chart_colors()`, `series_hex_list()`, `get_brand_colors()` (navy/gold/blue), `get_logo_assets()` (resolved logo paths + sizing). Import or copy in-notebook.
5. `references/fragments/` — chart-level (`matplotlib.mplstyle.txt`, `plotly_layout.json`, `web-tokens.css`) **and** page-level (`matplotlib_dashboard_scaffold.py`, `web_dashboard_layout.html`).

## Precedence (R9)

1. **A direct user opt-out** or a competing **non-YTM** brand / style instruction in the **current** prompt **wins** — do not apply this skill's YTM defaults for that request. If the same prompt **mixes** on-brand and opt-out language, **treat the opt-out as winning** for palette and surfaces.
2. Else, if the task matches the **description** (charts, viz, YTM, credit, dashboards, **Marimo**, **Streamlit**, web, Excel, etc.), **apply** this skill's defaults.
3. Optional project rules do **not** override (1). If both exist, user intent in the prompt still wins for opt-out.

## Opt-out vs force (phrase lists; user may edit `SKILL.md`)

| Intent | Example phrases (non-exhaustive) |
|--------|----------------------------------|
| **Opt-out (do not apply YTM defaults)** | off-brand, neutral style, not YTM, non-YTM, generic chart, default matplotlib, academic style, client template, use your own brand, another client's name |
| **Force (apply when ambiguous)** | YTM brand, Credit Investing look, on-brand, match our marketing site, use brand-identity, YTM Capital styling |

**AE2 / F2:** If an opt-out phrase is present, **do not** apply YTM navy surfaces, gold accents, or the YTM series palette for that request.

## "More colorful" or punchier (R11)

**Do not** add arbitrary new hues. **Do** adjust contrast, type weight, panel elevation (`color.surface.raised` → `color.surface.elevated`), spacing, and **series order** within the defined `chart.series.1`–`4` before introducing any new color. If still ambiguous, use **hatching or dash patterns** per `data-viz.md` (R13). The brand-blue + gold series order already gives a strong, on-brand 1–2 series comparison.

## Logos and assets (R14) — **mandatory for branded deliverables (R16)**

`assets/` ships with official YTM marks:

- `ytm_logo_horizontal.png` — primary horizontal lockup (default for dashboards, headers, slides)
- `ytm_logo_horizontal_full.png` — horizontal lockup, full-bleed variant
- `ytm_icon_192.png` — square app icon (192 px) — favicons, compact headers
- `ytm_icon_full.png` — square mark, full-bleed variant

**R16 — Logo is mandatory** for any dashboard, branded report, slide deck, or PDF export produced under this skill.

- **Default placement:** top-left.
- **Default height:** `logo.default_dashboard_height_px` (40 px).
- **Minimum height:** `logo.min_height_px` (28 px) — never smaller.
- Do **not** invent, download, recolor, or stretch logos. Do **not** add wordmarks, taglines, or marketing art that is not in `assets/`. If a deliverable needs an additional mark, ask — don't fabricate.
- Resolve paths and sizing via `chart_palette.get_logo_assets()` so the absolute path stays correct on this machine; do not hardcode `assets\` paths in user code if you can pull them from the helper.

Copy from `assets/` into the working directory or reference the absolute path:
`C:\Users\Eddy\.claude\skills\ytm-branding\assets\<file>.png`.

## TypeUI / managed blocks (R15)

If `TYPEUI_SH_MANAGED` or similar lives elsewhere, treat **`tokens.json` `schema_version` + this pack's `references/DESIGN.md`** as the reconciliation anchor for the skill. Sync upstream design changes there, then bump `schema_version`.

---

## Artifact router (R8 / R17)

For each deliverable type: read the **references** in the pre-flight, then the **fragment** or **helper** column. Dashboards and KPI reports get their own row — **do not** treat them as "a chart" and then stack charts manually.

| Artifact | Read first | Pre-flight (short) | Fragment / helper |
|----------|------------|--------------------|------------------|
| **(1) Static chart** (single Matplotlib / seaborn / PNG figure) | `DESIGN.md`, `data-viz.md`, `tokens.json` | Montserrat or fallback; `chart.panel` + `chart.series.*`; 4.5:1 for tick/legend; no `color.text.tertiary` on small chart text (R12) | `fragments/matplotlib.mplstyle.txt` + `chart_palette.py` |
| **(1b) Full dashboard / KPI report (Python)** *(R17)* | `DESIGN.md` (incl. **§6**), `data-viz.md`, `tokens.json` | Navy page surface (`color.surface.default`); **logo top-left** via `add_logo()`; gold signature rule under title (`draw_signature_rule()`); KPI cards with vertical gold accent (`draw_kpi_card()`); brand-blue + gold series | **`fragments/matplotlib_dashboard_scaffold.py`** (start here, do not rebuild layout from scratch) + `chart_palette.py` (`get_brand_colors`, `get_logo_assets`) |
| **(2) Interactive dashboard** (Plotly, **Marimo**, **Streamlit**, Dash, etc.) | Same + a11y for controls | Font stack; **focus** visible for HTML widgets; navy `chart.panel`; brand-blue + gold series; **logo in app header** | `fragments/plotly_layout.json` and/or `web-tokens.css` + `chart_palette.py`. For full-page Marimo / Streamlit layouts mirror the structure in `web_dashboard_layout.html` |
| **(2b) Web dashboard / branded HTML page** *(R17)* | `DESIGN.md` (incl. **§6**), `tokens.json`, `data-viz.md` | Navy `--brand-navy` body; logo in `<header>` left cluster; gold signature rule under title; KPI cards using `.kpi-card::before` accent rule; chart panel = `var(--chart-panel)` | **`fragments/web_dashboard_layout.html`** + `fragments/web-tokens.css` |
| **(3) Web component** (HTML, React, CSS — single component, not a full page) | `DESIGN.md`, `tokens.json`, `data-viz.md` | **Focus** states; semantic CSS vars; chart contrast; reuse `--accent-line-primary` for any leading accent rule | `fragments/web-tokens.css` |
| **(4) Spreadsheet** (Excel, openpyxl) | `data-viz.md`, `tokens.json` | Use **hex from `tokens.json` / `get_chart_colors()` / `get_brand_colors()`** for `Font`, `PatternFill`, borders, cell fills; document mapping in a comment in code. KPI sheet headers can use brand gold sparingly as a leading column accent | `chart_palette.py` (or read JSON) — align with the **excel** skill in your stack if present |
| **(5) Slide or PDF export** | `data-viz.md` (print section), `DESIGN.md` §6 | Light surface (`color.surface.strong`); `chart.tick_print`; re-verify 4.5:1; no dark `chart.panel` for print body unless the layout is explicitly dark; **logo top-left of cover slide and recurring page header** | Same fragments as (1) / (1b) / (2) but apply **print** tick colors from `tokens.json`; for full slide layouts, port the structure from `matplotlib_dashboard_scaffold.py` to your slide template |

**F1 / AE1:** With no opt-out, map series through `chart_palette`, **not** default Tab10 as primary. **Deck disambiguation:** if "deck" means an **on-screen** figure (dark UI / screen capture), use row **(1)** or **(1b)** with `chart.panel`. If the chart is placed on a **light slide master or print/PDF** with a **light** figure area, do **not** use dark `chart.panel` as the final export — use row **(5)**, `color.surface.strong`, and `chart.tick_print` in `tokens.json` per `data-viz.md` (print section).

---

## Quick pointers

- **WCAG (AE3):** Tick labels on `chart.panel` use `chart.tick` color — not `color.text.tertiary` (R12).
- **Python — UV first.** This vault uses `uv` (`uv run python ...`) per workspace rules. Never invoke a bare `python`.
- **Python — importing `chart_palette`:** Prefer the host-agnostic pattern below. It works in Cursor, Claude Code, Marimo, Jupyter, Streamlit, plain scripts, and notebooks — without hardcoding any agent host's container path.

  ```python
  from pathlib import Path
  import sys

  SKILL_REF = Path(r"C:\Users\Eddy\.claude\skills\ytm-branding\references")
  if str(SKILL_REF) not in sys.path:
      sys.path.insert(0, str(SKILL_REF))

  import chart_palette
  CHART = chart_palette.get_chart_colors()
  BRAND = chart_palette.get_brand_colors()
  series = chart_palette.series_hex_list()
  logo = chart_palette.get_logo_assets()  # resolved Path objects + sizing rules
  ```

  If you copy `chart_palette.py` next to your script (e.g. inside a project folder), `chart_palette.py` already resolves `tokens.json` via `Path(__file__).with_name("tokens.json")`, so move the JSON with it. The logo helper assumes `../assets/` next to `references/`; copy or symlink the `assets/` folder if you relocate the script.

- **Apply the Matplotlib style fragment** in one line (chart-level only):

  ```python
  import matplotlib.pyplot as plt
  plt.style.use(r"C:\Users\Eddy\.claude\skills\ytm-branding\references\fragments\matplotlib.mplstyle.txt")
  ```

- **Build a full dashboard (Python):** **start from the scaffold**, don't rebuild layout from scratch.

  ```python
  # Either run as-is to verify the brand renders, then edit KPI_CARDS / build_charts:
  #     uv run python C:\Users\Eddy\.claude\skills\ytm-branding\references\fragments\matplotlib_dashboard_scaffold.py
  #
  # Or import the helpers directly:
  import sys
  from pathlib import Path
  sys.path.insert(0, r"C:\Users\Eddy\.claude\skills\ytm-branding\references\fragments")
  from matplotlib_dashboard_scaffold import (
      add_logo, draw_signature_rule, draw_kpi_card,
  )
  ```

- **Apply the Plotly layout fragment:**

  ```python
  import json, plotly.graph_objects as go
  from pathlib import Path

  layout_doc = json.loads(
      Path(r"C:\Users\Eddy\.claude\skills\ytm-branding\references\fragments\plotly_layout.json").read_text(encoding="utf-8")
  )
  fig = go.Figure(layout=layout_doc["layout"])
  fig.update_layout(colorway=layout_doc["colorway"])
  ```

- **Web/CSS:** import `references/fragments/web-tokens.css` (or paste its `:root` block) and reference variables (`var(--chart-panel)`, `var(--brand-gold)`, `var(--accent-line-primary)`, etc.) instead of hex. For full pages start from `web_dashboard_layout.html`.

- **Bumping versions:** When any token key changes, bump `schema_version` in `tokens.json` (see `DESIGN.md` operational notes). Current schema: **2026.04.27.1**.

## Appendix: requirement spot-check

| Rule | Where defined |
|------|--------------|
| R2 — YAML description is the primary trigger | This file's frontmatter |
| R3 — Montserrat typography | `references/DESIGN.md` §3 |
| R4 — Color semantic roles | `references/DESIGN.md` §4, `tokens.json` |
| R5 — Space / radii / motion | `references/DESIGN.md` §5, `tokens.json` |
| R6 — Chart roles and contrast matrix | `references/data-viz.md` |
| R7 — Copy-pastable fragments | `references/fragments/` |
| R8 — Five+ artifact types in router | Artifact router table above (now 7 rows incl. 1b / 2b) |
| R9 — Precedence | Precedence section above |
| R10 — Print vs screen | `references/data-viz.md` (screen vs print section) |
| R11 — "More colorful" handling | Section above |
| R12 — `color.text.tertiary` restriction | `references/data-viz.md` R12 note |
| R13 — Hatching / non-color encoding | `references/data-viz.md` R13 section |
| R14 — Logos and assets | Logos and assets section above |
| R15 — TypeUI managed blocks | TypeUI section above |
| **R16 — Mandatory logo placement** for branded deliverables | Logos and assets section above; `DESIGN.md` §6.1 |
| **R17 — Page-level composition** (header bar + gold signature rule + vertical gold accents on KPI cards / section headers + navy stack) | `DESIGN.md` §6; `fragments/matplotlib_dashboard_scaffold.py`; `fragments/web_dashboard_layout.html` |
