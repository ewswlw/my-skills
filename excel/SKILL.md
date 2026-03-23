---
name: excel
description: Excel and spreadsheet authoring on Windows with UV Python (.xlsx, .xlsm, .csv, .tsv)—formulas, finance-style formatting, openpyxl/pandas/xlwings, recalc in Excel, openpyxl charts (pitfalls, IB/deck-style line & bar styling, hidden staging sheets), xlwings PNG/PDF exports for multimodal visual QA. Use when the user invokes /excel, or asks for spreadsheet models, DCF/LBO/comps workbooks, or xlsx/csv as the primary deliverable. Does not apply when the primary output is Word, HTML, script-only pipelines, or Google Sheets API work.
---

# Excel

Invoke this skill with **`/excel`** or any request for spreadsheet / `.xlsx` work matching the triggers below.

## Environment (this workspace)

- **OS:** Windows. Treat **Microsoft Excel (desktop)** as the default engine to **recalculate** and sanity-check workbooks after `openpyxl` writes.
- **Python (UV):** Use **UV** only: `uv sync`, `uv add openpyxl` / `uv add pandas` / `uv add xlwings` as needed. Run scripts with `uv run python script.py`. Do not use bare `pip` or unqualified `python` unless the shell already has the intended `.venv` active.
- **Working directory:** When using the **Obsidian Vault** repo, **`pyproject.toml` is at the vault root** (`Documents\Obsidian Vault`). Run `uv run python ...` from that root, **or** pass the project explicitly, e.g. `uv run --directory "C:\Users\<user>\Documents\Obsidian Vault" python path\to\script.py`, when the shell cwd is a subfolder (e.g. `Coding Projects\...`) that does not contain `pyproject.toml`. For other projects, run from **that** project’s root where `pyproject.toml` lives.
- **Paths:** Use `pathlib.Path` for all file paths. Folder names may include **spaces**—in PowerShell, **quote** paths: `Start-Process "C:\Users\...\Obsidian Vault\model.xlsx"`.
- **Encoding:** Read/write text CSV/TSV with `encoding="utf-8"` and `errors="replace"` when opening files in Python (matches project standards).

### Recalculate after saving (Windows, priority order)

1. **Excel UI:** Open the `.xlsx`, allow full calculation, confirm no `#REF!` / `#DIV/0!` in the model area, save.
2. **`xlwings`** (if `uv add xlwings` and Excel installed): open workbook, `app.calculate()`, save, then **close the book and quit Excel if this was the only automation** so no invisible `EXCEL.EXE` stays running (e.g. `wb.close()`; `app.quit()` when appropriate—test so you do not kill a user’s other open workbooks without intent).
3. **LibreOffice** (if installed): headless binary is often `C:\Program Files\LibreOffice\program\soffice.exe` (varies by install). Optional `--headless` conversion/recalc—only if already used in the project.

**PowerShell — open a workbook in the default app (quick manual recalc):**

```powershell
Start-Process ".\path\to\model.xlsx"
# Paths with spaces: always quote
Start-Process "C:\Users\You\Documents\Obsidian Vault\file dump\model.xlsx"
```

Use `Resolve-Path` or full paths when the shell cwd is not the file’s folder.

### xlwings sketch (optional)

```python
import xlwings as xw
from pathlib import Path

p = Path(r"C:\absolute\path\to\model.xlsx")
app = xw.App(visible=False)
wb = None
try:
    wb = app.books.open(str(p))
    app.calculate()
    wb.save()
finally:
    if wb is not None:
        wb.close()
    app.quit()
```

Adjust visibility and `quit()` vs leaving Excel open to match whether the user has other sessions.

### Visual QA for AI (layout, charts, print)

**Constraint:** Assistants do **not** render `.xlsx` as Excel does. **Layout, colors, conditional formatting, and chart appearance** require pixels: **PNG**, **PDF pages**, or **screenshots**. `openpyxl` is for **structure and styles in XML**, not WYSIWYG proof.

**Preferred (Windows + Excel installed):** [xlwings `Range`](https://docs.xlwings.org/en/stable/api/range.html) methods that use **Excel’s engine** as the renderer:

| Method | Use |
|--------|-----|
| **`Range.to_png(path)`** | Export a range to PNG—best for **tight iteration** with multimodal review (dashboard block, main table, one chart area). |
| **`Range.to_pdf(path, ...)`** | Export a range to PDF—good for **print / page-break** checks; optional layout PDF (xlwings PRO) per docs. |
| **`Range.copy_picture(...)`** | Copy as picture (`appearance`: `screen` vs `printer`; `format`: `picture` vs `bitmap`)—clipboard pipeline if building custom tooling. |

**Workflow:**

1. **Recalculate** (`app.calculate()` or full calc) so values and CF match what you trust.
2. Export **named regions** or logical blocks (not always whole sheets)—e.g. `Dashboard!A1:M45`, one file per block—so review stays readable.
3. Use a **`qa/`** (or similar) folder and stable names: `SheetName__A1_M45.png`, optionally a small JSON manifest listing sheet, range, path.
4. **Manual** is fine: **Save As PDF**, **Print to PDF**, **Copy as Picture**, or **Win+Shift+S** on a region—attach images or paths for review.

**Pair with vault skill:** When the Obsidian vault is in play, apply **`.cursor/skills/excel-output-verification/SKILL.md`** for the **structural** pass + **IB-style visual checklist** (§1–§3); use **PNG/PDF exports** for the **visual** half the checklist assumes.

**Avoid:** Relying on **LibreOffice headless** PDF for final **Excel-faithful** layout—it can diverge from Excel; reserve for bulk/CI when Excel is unavailable.

### Macros and `.xlsm`

- **`openpyxl`** can load/save `.xlsm` and preserve **VBA** in many cases but does **not execute** macros. Do not promise macro execution, signing, or trusted-folder behavior from Python here.
- If the user needs **editing VBA**, treat that as a separate, explicit task (often manual in Excel or specialized tools).

## When to apply

- User invokes **`/excel`** or references/attaches `.xlsx`, `.xlsm`, `.csv`, or `.tsv` and wants creation, edits, or analysis.
- Tasks described as models, three-statement builds, DCF shells, LBO templates, comps, merger math, or “deliver an Excel.”
- Cleaning or restructuring messy tabular files into a proper spreadsheet.

## When not to apply

- Primary output is a Word doc, HTML report, or DB pipeline.
- User wants logic only in Python with no workbook deliverable.
- Integration work focused on Google Sheets APIs (different tool stack).

## Non-negotiables

1. **Zero formula errors** in the delivered workbook: no `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?` in the modeled range unless the user explicitly wants a flagged error.
2. **Use Excel formulas for model math**—totals, growth, ratios, lookups—so the file recalculates when inputs change. Do not compute those in Python and paste numeric results unless the user asks for values-only or static export.
3. **Preserve existing templates**: match fonts, colors, sheet names, and layout when editing an established file; template rules beat this document.

## All Excel outputs

### Typography

Use one consistent professional font (e.g. Arial or Times New Roman) unless the user or template specifies otherwise. **Chart-deck sheets** (tabs that only hold figure titles + charts) often use **Calibri** for the section header band while **data tables** stay Arial/Times—match the bank template if one exists.

### openpyxl and calculated values

`openpyxl` stores formulas as strings and does **not** evaluate them. After saving, cached values may be stale or missing until Excel (or another engine) recalculates—see **Recalculate after saving** above.

### openpyxl charts (LineChart / BarChart)

Use this when building **dashboards or report workbooks** whose charts are fed from Python-populated data ranges. The **“formulas in cells”** rule elsewhere in this skill still applies to **valuation / three-statement models**; **data+chart** deliverables are expected to store **values** (and sometimes chart-only sheets) written by Python.

| Pitfall | What to do |
|--------|------------|
| **`DateAxis()`** | Do **not** replace `line_chart.x_axis` with `openpyxl.chart.axis.DateAxis()`. That pattern often produces **invalid drawing OOXML**; Excel opens with a repair dialog and may **strip `/xl/drawings/drawing*.xml`** (charts vanish or break). Keep the default **category axis**; for dense daily dates set **`tickLblSkip`** / **`tickMarkSkip`** (e.g. `90`–`120` for multi-year daily—raise the number if the x-axis is still crowded). |
| **NaN / dtypes in chart ranges** | Cells referenced by `Reference()` must not contain **`float('nan')`** or ambiguous pandas NA—Excel chart XML is brittle. Map **`pd.isna` → leave cell empty / `None`**; use **`pd.Timestamp(...).to_pydatetime()`** for date categories when appending rows. |
| **Horizontal bar charts** | Set **`chart.barDir = "bar"`** (horizontal). In openpyxl, `type` is an alias of `barDir`; prefer **`barDir`** for clarity. |
| **Axis `majorTickMark` / `minorTickMark`** | Valid values are **`cross` \| `in` \| `out`** only. Do **not** set them to **`"none"`**—that is invalid and may be dropped or mis-serialized. Omit tick-mark styling unless you need a specific value. |
| **Many charts on one sheet** | Overlapping **`add_chart(..., anchor)`** placements (and oversized `height`/`width`) stack drawings and look bad; Excel may struggle. Prefer **several chart sheets** or a **single column** with **large vertical gaps** between anchors (rough guide: **≥ ~30 rows** between tops for ~9 cm tall charts; reduce cm size if needed). |
| **Staging data visible** | Raw ranges used only to feed charts (e.g. `Chart_Data`) can be **`ws.sheet_state = "hidden"`** so the deck shows **Dashboard + figure tabs** without losing chart references. |
| **Validate after `save`** | `load_workbook(path, read_only=True).close()` catches bad package/chart XML before the user opens the file. Same rule as **Libraries**: do **not** `save()` a workbook after loading with **`data_only=True`** if you must preserve formulas—here, use **`read_only=True`** only for a smoke test, not for editing. |

#### IB / deck-style polish (openpyxl, optional)

openpyxl will not match a hand-finished PowerPoint, but you can get **cleaner, institutional-looking** charts than the default Excel palette:

- **Line charts:** After `add_data` / `set_categories`, set **`chart.style`** to a restrained preset (e.g. **8**), **`series.smooth = True`**, per-series **`graphicalProperties.line`** with **`LineProperties`**, **`solidFill = ColorChoice(srgbClr="…")`** using **RRGGBB** hex strings without `#`, and **`width`** in **EMUs** (~**22_500** ≈ 1.7 pt). Use a **fixed palette** (navy, gold, steel blue, …) and cycle by series index.  
- **Plot frame:** `chart.plot_area.spPr` with light **`solidFill`**, thin **`ln`** border (`LineProperties` + `ColorChoice`) so the plot reads like a slide.  
- **Grid:** Assign **`majorGridlines = ChartLines()`** to the **numeric value axis** (usually **`y_axis`** on line charts and many horizontal bar charts); set the gridline **`spPr.ln`** to light gray (`ColorChoice`, e.g. `E5E7EB`).  
- **Legend:** `chart.legend.position = "b"` and **`overlay = False`** so the legend does not cover the plot.  
- **Bar charts:** Set **`chart.style`** (e.g. **10**), **`clustered`** grouping, **`gapWidth`** (~40–50), **`series.graphicalProperties.solidFill`** for **navy / slate** fills (`ColorChoice(srgbClr=...)`). Same **plot_area** frame as line charts if you want consistency.  
- **Imports (typical):** `from openpyxl.chart.axis import ChartLines`; `from openpyxl.chart.shapes import GraphicalProperties`; `from openpyxl.drawing.colors import ColorChoice`; `from openpyxl.drawing.line import LineProperties`.

**Verification (charts):** no `DateAxis` replacement; chart data ranges have no NaN; no invalid tick-mark strings; optional round-trip `read_only` load after save; open once in Excel desktop to confirm **no “Repaired drawing”** prompt.

**Final polish:** Open in Excel desktop—formatting chart titles and data labels in the UI still beats openpyxl for pixel-perfect **bank-style** output.

## Financial presentation (default unless template overrides)

### Color conventions (RGB)

| Role | Style |
|------|--------|
| Hard inputs; scenario drivers | Blue text `0,0,255` |
| Formulas and calculated cells | Black text `0,0,0` |
| Links to other sheets in the same workbook | Green text `0,128,0` |
| Links to other workbooks | Red text `255,0,0` |
| Key assumptions or cells to update | Yellow fill `255,255,0` |

### Number formats

- **Years / period labels:** Prefer text labels (e.g. `2024`) so they are not misread as thousands.
- **Currency:** Use accounting-style or thousands separators; **state units in headers** (e.g. `Revenue ($mm)`).
- **Zeros:** Often shown as `-` via number format (e.g. `0;0;-` for integers) depending on template.
- **Percentages:** Typically one decimal (`0.0%`) unless the user wants more precision.
- **Multiples:** e.g. `0.0x` for EV/EBITDA, P/E.
- **Negatives:** Parentheses `(123)` are common in finance tables when that is the house style.

### Formula construction

- Put **assumptions** (growth, margins, multiples, capex) in dedicated input cells; formulas reference those cells.
- Prefer `=B5*(1+$B$6)` over baking `1.05` into the formula.
- Check ranges for off-by-one errors; keep formulas **consistent across forecast columns**.
- Avoid accidental **circular references** unless the model explicitly uses iterative calculation.
- For **hardcoded inputs** that need audit trail, note source: system, document, date, and pointer (e.g. page, exhibit, ticker).
- **Locale:** Write formulas in **English function names** and comma-separated argument lists as stored in the file (`=SUM(A1:A10)`). If the user’s Excel UI uses different list separators, they still recalc correctly when opened; avoid hand-typing locale-specific separators inside string formulas unless matching an existing template.

## CRITICAL: formulas in cells, not Python constants

### Wrong

```python
# Bad: Python computes and writes a number
total = df["Sales"].sum()
ws["B10"] = total

# Bad: growth computed in Python then written as a number
growth = (df.iloc[-1]["Rev"] - df.iloc[0]["Rev"]) / df.iloc[0]["Rev"]
ws["C5"] = growth
```

### Right

```python
# Good: Excel evaluates the sum
ws["B10"] = "=SUM(B2:B9)"

# Good: growth stays in the sheet
ws["C5"] = "=(C4-C3)/C3"
```

Use Python to **place** formulas and formatting, not to replace the model’s calculation layer. Use **`ws`** (or a clearly named worksheet variable) consistently with `openpyxl`.

## Libraries

| Library | Use for |
|---------|---------|
| **pandas** | Read/write tables, analysis, bulk reshape, simple `to_excel` exports when no rich formatting is needed. |
| **openpyxl** | Fine-grained edits, formulas, styles, merges, sheets. |
| **xlwings** | Drive **Excel** for recalc/save; **`Range.to_png` / `to_pdf` / `copy_picture`** for **visual QA** artifacts; not a substitute for openpyxl when batch-authoring OOXML without Excel. |

**pandas:** For `.xlsx`, use engine **`openpyxl`** explicitly if needed: `pd.read_excel(path, engine="openpyxl")`. `sheet_name=None` loads all sheets as a dict. Set `dtype` where IDs must stay strings. Use `parse_dates` for date columns. Prefer `Path` objects where APIs allow.

**openpyxl:** Rows and columns are **1-based**. `load_workbook(path, data_only=True)` reads **cached** values only; if you save after loading with `data_only=True`, you can **destroy formulas**. Use `data_only=True` only for inspection, not for round-tripping a model.

For large files: `read_only=True` / `write_only=True` modes when appropriate.

### Minimal new workbook (openpyxl, pathlib)

```python
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font

out = Path("output.xlsx")
wb = Workbook()
ws = wb.active
ws["A1"] = "Label"
ws["B2"] = "=SUM(B3:B10)"
ws["A1"].font = Font(bold=True)
wb.save(out)
```

### Edit existing (openpyxl)

```python
from pathlib import Path
from openpyxl import load_workbook

src = Path("existing.xlsx")
wb = load_workbook(src)
ws = wb["Sheet1"]
ws["A1"] = "Updated"
wb.save(Path("modified.xlsx"))
```

## Code style for generated Python

- Keep scripts short and direct; avoid noisy prints unless debugging.
- Prefer clear variable names over clever one-liners.
- For Excel itself: use cell comments or small labels for non-obvious formulas or assumptions.
- Run with **`uv run python path\to\script.py`** from the **project root** (where `pyproject.toml` lives), or **`uv run --directory "<project root>"` python ...** when cwd is elsewhere.

## Verification checklist

**Before wide paste of formulas**

- [ ] Test 2–3 representative cells (cross-sheet refs, first/last forecast column).
- [ ] Map column letters for wide sheets (e.g. column 64 = `BL`).
- [ ] Remember Excel row 1 is often the header; DataFrame row 0 is not Excel row 1.

**Edge cases**

- [ ] Division: guard denominators or use `IF` patterns in Excel to avoid `#DIV/0!`.
- [ ] Lookups: confirm match type and sorted ranges for `VLOOKUP`/`MATCH`.
- [ ] Nulls: `NaN` from pandas must not become ambiguous text in cells.

**After save**

- [ ] Recalculate in **Excel** (preferred on this machine) or LibreOffice; scan for error tokens.
- [ ] If errors appear: `#REF!` → broken reference; `#NAME?` → typo in function name; `#VALUE!` → type mismatch.
- [ ] **Charts (openpyxl):** no `DateAxis` hack on line charts; chart `Reference` ranges free of NaN; axis tick marks only `cross`/`in`/`out` if set; optional `load_workbook(..., read_only=True).close()` after save; open in Excel and confirm no repair dialog for drawings; IB-style polish (if used) keeps palette + plot frame consistent.

**Visual / layout (for AI or deck review)**

- [ ] If the user needs **pixel-level** or **IB-style layout** feedback in chat: export **PNG or PDF** from Excel (**xlwings `to_png` / `to_pdf`**, or manual PDF/screenshot)—raw `.xlsx` alone is not enough for true visual inspection.
- [ ] Run **excel-output-verification** (vault) when polishing deliverables; supply **exported images** for the §2 visual checks.

## Best practices summary

- Prefer **openpyxl** when the deliverable is a **model** with formulas and formats; **pandas** when the task is **analysis** or a simple table export.
- Never ship a model full of Python-computed static numbers unless requested.
- Match the user’s or bank’s template over generic color rules when they conflict.
- For **visual** iteration with an assistant: **Excel-rendered** **PNG/PDF** (see **Visual QA for AI**); keep **openpyxl** for **structure** and formulas.
