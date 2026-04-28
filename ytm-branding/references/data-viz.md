# Data visualization — YTM / Credit Investing

**Pairs with:** `tokens.json` (`chart` subtree), `references/fragments/*`, `chart_palette.py`.

**R12 (tertiary):** `color.text.tertiary` (`#0000ee`) is for **text links** on light-appropriate surfaces. **Do not** use it for small chart text, tick labels, or dense legend labels. Use `chart.tick` (resolved) instead.

**R13 (non-color):** **Should** use hatching, dash patterns, or marker shapes for at least one critical series when two series on `chart.panel` would otherwise be hard to distinguish by color alone, or when WCAG contrast limits hue choices.

---

## Semantic roles

| Name | Use |
|------|-----|
| `chart.panel` | Main plot background (screen default: **navy panel** `#1c2d42`; aligns with `color.surface.raised`). |
| `chart.panel_alt` | Alternative chart panel matching the page (`#162236`) — use when a chart should sit flush on the page background, with no surrounding card. |
| `chart.grid` | Grid lines; subtle vs panel (`#2a3a52`). |
| `chart.axis` | Axis spines and rules (color / weight in fragments). |
| `chart.tick` | Tick **labels**: typography = body / caption per stack; color = value in JSON (enough contrast on `chart.panel` for screen; see matrix). |
| `chart.legend` | Legend text and swatches. |
| `chart.series.1` … `chart.series.4` | **Ordered** series colors (primary to quaternary). Series 1 = brand blue (`#4a8ec2`), series 2 = gold (`#c9a84c`), series 3/4 = soft variants. Minimum four roles. |
| `chart.accent.rule` | **Gold rule** (`#c9a84c`) used for emphasis annotations, threshold lines (e.g. zero baseline highlight, target lines), and KPI underlines on chart panels. Stroke width ≥ 1.5 px so it reads at small sizes. |
| `chart.accent.kpi_bar` | Same gold token, alias used by KPI card scaffolds (see `DESIGN.md` §6.3). |
| `chart.derived.*` | Only if explicitly listed below with **must** verify contrast. |

---

## Screen vs print

- **Screen / dashboard on navy panel:** use `chart.panel` and series colors from `tokens.json`. Tick/legend text: use `chart.tick` color on `chart.panel` (contrast pre-verified; see matrix). Page background should be `color.surface.default` (`#162236`); chart panels can be `chart.panel` (`#1c2d42`) for slight elevation, or `chart.panel_alt` (`#162236`) for a flush look.
- **Print / PDF on light paper:** use `color.surface.strong` for figure background. Re-stroke axes and re-map tick text to **dark** (`color.text.inverse` = `#162236` or print-specific text color). **Re-verify 4.5:1** for all label text on the print background. Dark navy panel tokens **must not** be used for print body charts unless the print layout is explicitly dark.

---

## Contrast matrix (pre-verified pairs)

Tooling: re-check with WebAIM or similar when you change any hex.

| Text role | Background | Min ratio (normal text) | Notes |
|-----------|------------|-------------------------|--------|
| `chart.tick` (`#e6edf3`) | `chart.panel` (`#1c2d42`) | 4.5:1+ | **~12.4:1** — passes AA / AAA for normal text. **AE3** (tick on navy panel). |
| `chart.tick` (`#e6edf3`) | `chart.panel_alt` / `color.surface.default` (`#162236`) | 4.5:1+ | **~13.8:1** — passes AA / AAA. |
| `chart.legend` (`#c9d1d9`) | `chart.panel` (`#1c2d42`) | 4.5:1+ | **~9.5:1** — passes AA. |
| `color.text.muted` (`#6c7a8c`) | `color.surface.default` (`#162236`) | 3:1+ (large text only) | **~3.5:1** — large captions only; do **not** use for small body text on navy. |
| `color.brand.gold` (`#c9a84c`) | `color.surface.default` (`#162236`) | 4.5:1+ for text use | **~6.4:1** — safe for short headings / KPI numbers in gold; verify before using as small body text. Used primarily as a 2–3 px accent rule, not as text. |
| `color.brand.blue` (`#4a8ec2`) | `color.surface.default` (`#162236`) | 3:1+ (UI / large) | **~4.6:1** — passes AA for large text, borderline for small body — prefer for series strokes / icons, not body copy. |
| `chart.tick_print` (`#24292f`) | `color.surface.strong` / print (`#f6f8fa`) | 4.5:1+ | **~13.8:1** — print labels. |
| `color.text.tertiary` (`#0000ee`) | `color.surface.strong` (`#f6f8fa`) | 4.5:1+ | Re-verify if you change either side (WebAIM). **Not** for chart tick/label on dark panel. **R12**. |

**AE1:** Series colors are **not** Matplotlib Tab10 defaults; they map from `chart.series.1`–`4` via `chart_palette` / fragments. Series order is **brand blue → gold → soft blue → soft gold** so a default 1–2 series chart reads on-brand. Montserrat: set in `matplotlib.mplstyle.txt` and document fallback if font unavailable.

**Allowed derived colors:** If you add a new derived swatch, document it here, add a key under `chart.derived` in `tokens.json` if needed, and **bump** `schema_version`.

---

## Hatching / patterns (R13)

- **Matplotlib:** e.g. `hatch` on fills or alternating `linestyle` for line charts when comparing two series on `chart.panel`.
- **Plotly:** `line.dash` / marker symbols for the second of two series.
- **Should** apply when two series would collide perceptually (similar luminance on dark panel — e.g. soft blue vs soft gold at small sizes).

---

## Sync note

On any change to `chart.*` in `tokens.json`, bump `schema_version` and re-run a quick spot-check: one Matplotlib figure, one HTML snippet (see `SKILL.md`).
