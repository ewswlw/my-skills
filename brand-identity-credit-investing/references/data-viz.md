# Data visualization — YTM / Credit Investing

**Pairs with:** `tokens.json` (`chart` subtree), `references/fragments/*`, `chart_palette.py`.

**R12 (tertiary):** `color.text.tertiary` (`#0000ee`) is for **text links** on light-appropriate surfaces. **Do not** use it for small chart text, tick labels, or dense legend labels. Use `chart.tick` (resolved) instead.

**R13 (non-color):** **Should** use hatching, dash patterns, or marker shapes for at least one critical series when two series on `chart.panel` would otherwise be hard to distinguish by color alone, or when WCAG contrast limits hue choices.

---

## Semantic roles

| Name | Use |
|------|-----|
| `chart.panel` | Main plot background (screen default: dark; aligns with `color.surface.raised` / chart-specific value in JSON). |
| `chart.grid` | Grid lines; subtle vs panel. |
| `chart.axis` | Axis spines and rules (color / weight in fragments). |
| `chart.tick` | Tick **labels**: typography = body / caption per stack; color = value in JSON (enough contrast on `chart.panel` for screen; see matrix). |
| `chart.legend` | Legend text and swatches. |
| `chart.series.1` … `chart.series.4` | **Ordered** series colors (primary to quaternary). Minimum four roles. Optional future: `chart.series.5` or `chart.emphasis` if design extends. |
| `chart.derived.*` | Only if explicitly listed below with **must** verify contrast. |

---

## Screen vs print

- **Screen / deck on dark panel:** use `chart.panel` and series colors from `tokens.json`. Tick/legend text: use `chart.tick` color on `chart.panel` (contrast pre-verified; see matrix).  
- **Print / PDF on light paper:** use `color.surface.strong` (or print-specific path in `tokens.json` / fragments) for figure background. Re-stroke axes and re-map tick text to **dark** on light (`color.text.inverse` or print-specific text color). **Re-verify 4.5:1** for all label text on the print background. Dark panel tokens **must not** be used for print body charts unless the print layout is explicitly dark.

---

## Contrast matrix (pre-verified pairs)

Tooling: re-check with WebAIM or similar when you change any hex.

| Text role | Background | Min ratio (normal text) | Notes |
|-----------|------------|-------------------------|--------|
| `chart.tick` (`#e6edf3`) | `chart.panel` (`#0d1117`) | 4.5:1+ | **~16:1** — **AE3** (tick on dark panel). |
| `chart.tick` print (`#24292f`) | `color.surface.strong` / print (`#f6f8fa`) | 4.5:1+ | **~13.8:1** — print labels. |
| `color.text.tertiary` (`#0000ee`) | `color.surface.strong` (e.g. `#f6f8fa`, link / body) | 4.5:1+ | **Re-verify** if you change either side (WebAIM). **Not** for chart tick/label on dark `chart.panel`. **R12**. |

**AE1:** Series colors are **not** Matplotlib Tab10 defaults; they map from `chart.series.1`–`4` via `chart_palette` / fragments. Montserrat: set in `matplotlib.mplstyle.txt` and document fallback if font unavailable.

**Allowed derived colors:** If you add a new derived swatch, document it here, add a key under `chart.derived` in `tokens.json` if needed, and **bump** `schema_version`.

---

## Hatching / patterns (R13)

- **Matplotlib:** e.g. `hatch` on fills or alternating `linestyle` for line charts when comparing two series on `chart.panel`.  
- **Plotly:** `line.dash` / marker symbols for the second of two series.  
- **Should** apply when two series would collide perceptually (similar luminance on dark background).

---

## Sync note

On any change to `chart.*` in `tokens.json`, bump `schema_version` and re-run a quick spot-check: one Matplotlib figure, one HTML snippet (see `SKILL.md`).
