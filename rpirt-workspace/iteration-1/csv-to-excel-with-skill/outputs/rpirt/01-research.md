# Phase 1 — Research

## Goal

Build a production-quality Python CLI tool (`cli_tool.py`) that reads all CSV files from a
user-specified input folder, converts each into a separate Excel worksheet (handling heterogeneous
schemas), generates a summary sheet with row counts and column names, and adds a bar chart to the
summary sheet visualising row counts per file. Output path is user-controlled via `--output`.
The tool must handle real-world edge cases (encoding, empty files, name collisions, oversized data)
gracefully and emit clear errors.

---

## Findings

### Environment (confirmed via live test)

| Item | Value |
|------|-------|
| Python in vault venv | 3.13.11 (user said 3.12 — both are fine; no breaking delta) |
| pandas | 2.3.0 |
| openpyxl | 3.1.5 |
| argparse | stdlib |
| pathlib | stdlib |

### openpyxl BarChart API (confirmed)

- `BarChart` lives in `openpyxl.chart`; set `chart.type = 'col'` for vertical (column) bars.
- Data reference: `Reference(ws, min_col, min_row, max_row)`.
- Categories: `chart.set_categories(Reference(...))`.
- Axis titles: `chart.y_axis.title`, `chart.x_axis.title` — both work.
- Anchoring: `ws.add_chart(chart, "B<row>")` — anchor below the summary table.
- Chart dimensions: `chart.width`, `chart.height` in cm-equivalent units.

### Sheet name constraints (confirmed)

- Maximum length: **31 characters** (Excel hard limit).
- Invalid characters: `[ ] : * ? / \` — must be stripped/replaced.
- openpyxl auto-deduplicates sheet names but produces unintuitive suffixes (Sheet1 → Sheet11).
  **Must implement deterministic deduplication** (append `_2`, `_3`, etc.) before passing to openpyxl.

### CSV edge cases (confirmed via test)

| Case | Behavior |
|------|----------|
| BOM-prefixed UTF-8 | `encoding='utf-8-sig'` strips BOM cleanly |
| Header-only CSV (0 data rows) | `pd.read_csv` returns 0-row DataFrame — valid, must show 0 in summary |
| Mixed-type columns | Default object dtype — no issue for Excel writing |
| Non-CSV files in folder | Must skip silently or with a logged warning |
| Completely empty file (0 bytes) | `pd.read_csv` raises `EmptyDataError` — must catch and report |
| Files with non-UTF-8 encoding | Need fallback: try `utf-8-sig`, then `latin-1` |

### Writing strategy: direct openpyxl vs pandas.to_excel

- `pandas.to_excel(ExcelWriter)` is convenient but offers limited control over cell formats,
  column widths, header styling, and chart placement.
- For production-grade output (auto-column widths, styled headers, charts on the summary sheet),
  **direct openpyxl writes** are necessary after using pandas to produce the DataFrame.
- Recommended pattern: `pd.read_csv()` → DataFrame → iterate rows → `ws.append(row)` with
  openpyxl, applying header style separately. This keeps pandas for parsing, openpyxl for rendering.

### Excel hard limits

- Max rows per sheet: **1,048,576** (including header = 1,048,575 data rows).
- Max columns per sheet: **16,384**.
- If a CSV exceeds these, the tool must warn and truncate rather than crash.

### CLI design patterns

- `argparse` positional `input_dir` + keyword `--output` is idiomatic and widely expected.
- Should validate: input dir exists, input dir is a directory, output path has `.xlsx` extension
  (or auto-append), output parent dir exists/can be created.
- Exit codes: 0 = success, 1 = user error (bad args), 2 = runtime error.

### Summary sheet design

- Row 1: bold column headers — `File`, `Rows`, `Columns`, `Column Names`.
- One row per CSV (sorted alphabetically for determinism).
- `Column Names` cell: comma-separated list; if very long, Excel will wrap (set wrap_text=True).
- Bar chart anchored below the data table.

### Logging

- Use stdlib `logging` with a console handler; default level INFO; `--verbose` for DEBUG.
- Errors that skip a file should log at WARNING level with filename and reason.

---

## Unknowns and Risks

| Risk | Severity | Note |
|------|----------|------|
| Very wide CSVs (>16,384 cols) | Low | Rare; warn + truncate to Excel limit |
| Extremely large CSVs (millions of rows) | Medium | pandas loads full file to RAM; no streaming. Acceptable for CLI scope but should warn if >500k rows. |
| Circular output path (output.xlsx inside input dir) | Low | Safe — openpyxl writes at end, pandas reads first; no conflict unless re-run mid-run |
| Non-standard line endings (CR, CRLF) | Low | pandas handles transparently |
| CSVs with duplicate column names | Low | pandas auto-renames (col, col.1, col.2); acceptable |
| openpyxl chart not rendering in older Excel versions | Low | BarChart is standard OOXML; should work Excel 2010+ |

---

## Key Constraints

- Python 3.12+ (confirmed 3.13 in venv — compatible).
- Only `pandas` and `openpyxl` as external dependencies (both confirmed available).
- Single output file: `cli_tool.py` — no package structure required.
- User-facing: entry point is `python cli_tool.py <input_dir> --output <path>`.
- Production-ready: must not crash on malformed inputs; must emit actionable error messages.
- No database, no network, no secrets — pure file I/O.
