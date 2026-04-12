# Phase 2 — Plan

## Durable Decisions

1. **Single-file delivery** (`cli_tool.py`) — no package, no setup.py. Runs as `python cli_tool.py`.
2. **pandas for parsing, openpyxl for rendering** — pandas handles CSV quirks; openpyxl gives full
   control over cell styles, column widths, and chart placement.
3. **Summary sheet is always Sheet 1** (index 0), named `"Summary"` — data sheets follow in
   alphabetical CSV order.
4. **Sheet names derived from CSV filename stem** — sanitised (invalid chars stripped, truncated to
   31 chars, deduplicated with `_2`/`_3` suffixes). `"Summary"` is reserved and triggers a rename
   if a CSV file is named `summary.csv`.
5. **Two-pass encoding fallback**: `utf-8-sig` first (handles BOM), then `latin-1`. Other encodings
   are not auto-detected — out of scope for CLI tool without chardet dependency.
6. **Exit codes**: 0 success, 1 bad arguments/no CSVs found, 2 runtime error.
7. **Logging to stderr** via stdlib `logging`; default INFO, `--verbose` enables DEBUG.
8. **Column widths auto-fitted** by scanning column data length (capped at 60 chars to avoid
   unreadable ultra-wide columns).
9. **Bar chart type**: vertical column chart (`BarChart.type = 'col'`) on the Summary sheet,
   anchored two rows below the last summary row.

---

## Task Breakdown

### T1 — CLI entry point and argument parsing
**Depends on:** none  
**Done when:**
- `argparse` parses `input_dir` (positional) and `--output` (required keyword).
- `--verbose` flag wired to logging level.
- `input_dir` validated: must exist and be a directory; exits with code 1 + message on failure.
- `--output` path: parent directory created if not exists; `.xlsx` extension auto-appended if absent.
- `main()` entry point wrapped in `if __name__ == "__main__"` block.

### T2 — CSV discovery and loading
**Depends on:** T1  
**Done when:**
- `discover_csvs(input_dir)` returns sorted list of `.csv` paths (case-insensitive glob).
- Returns empty list (not error) if folder has no CSVs; caller emits exit-1 message.
- `load_csv(path)` attempts `utf-8-sig` then `latin-1`; on `EmptyDataError` returns `(None, "empty file")` tuple; on any other exception returns `(None, str(e))`.
- Skips non-CSV files silently (they never enter the list).
- Logs WARNING for each file that fails to load; continues processing remaining files.

### T3 — Sheet name sanitisation and deduplication
**Depends on:** T2  
**Done when:**
- `sanitise_sheet_name(stem, used_names)` strips `[]:*?/\` characters, replaces with `_`.
- Truncates to 31 chars.
- If result is `"Summary"` (case-insensitive), renamed to `"Summary_data"`.
- Deduplicates against `used_names` set using `_2`, `_3` suffixes (re-truncating if needed).
- Returns sanitised name and updated `used_names`.

### T4 — Data sheet writing
**Depends on:** T2, T3  
**Done when:**
- For each successfully loaded DataFrame, a worksheet is created with the sanitised name.
- Row 1: bold header row with light blue fill, white font, frozen (freeze_panes).
- Rows 2+: DataFrame data written via `ws.append()`.
- Column widths auto-fitted (min 8, max 60) based on max character length in header+data sample.
- If DataFrame exceeds Excel row/column limits, truncate and log a WARNING with the original count.

### T5 — Summary sheet writing
**Depends on:** T4  
**Done when:**
- Sheet named `"Summary"` inserted at position 0.
- Headers: `File`, `Rows`, `Columns`, `Column Names` — styled identically to data sheet headers.
- One row per CSV (in alphabetical order, matching data sheets).
- Failed CSVs also appear in summary with `Rows = "ERROR"`, `Column Names = <error message>`.
- `Column Names` cell has `wrap_text=True` and row height set to accommodate wrapping.
- Column widths auto-fitted.

### T6 — Bar chart creation
**Depends on:** T5  
**Done when:**
- `BarChart` of type `'col'` created with title `"Row Counts per File"`.
- Y-axis title: `"Row Count"`, X-axis title: `"File"`.
- Data reference: `Rows` column (numeric rows only — ERROR rows excluded via a conditional check).
- Categories reference: `File` column.
- Chart anchored two rows below the last data row on the Summary sheet.
- Chart width ≈ 20, height ≈ 12 (openpyxl units).
- `chart.style = 10` for a cleaner default appearance.

### T7 — Workbook save and final reporting
**Depends on:** T6  
**Done when:**
- `wb.save(output_path)` called; any `PermissionError` (file open in Excel) caught and re-raised
  with actionable message: "Close the file in Excel and retry."
- Final INFO log: path written, N sheets created, N files skipped.
- Exit code 0.

### T8 — Robustness and edge cases
**Depends on:** T1–T7 (cross-cutting)  
**Done when:**
- Tool runs without crash when input folder contains 0 CSVs (exits 1 with message).
- Tool runs when all CSVs fail to load (exits 1 with message "No CSVs could be read.").
- Tool runs when a CSV has 0 data rows (shows 0 in summary, creates empty data sheet with headers).
- Tool handles a single CSV file correctly (chart still renders).
- `--output` points to a path where the parent does not yet exist: parent is auto-created.

---

## Risk Mitigations

| Risk (from Research) | Mitigation |
|----------------------|------------|
| Very wide CSVs (>16,384 cols) | Truncate columns to 16,383 in T4; emit WARNING with original count |
| Large CSVs (>500k rows) | Emit INFO warning if row count > 500,000 before writing; continue |
| Sheet name collision with "Summary" | Rename to "Summary_data" in T3 |
| openpyxl duplicate sheet names | Deterministic `_2`/`_3` deduplication in T3 before calling openpyxl |
| BOM / encoding issues | Two-pass fallback in T2 |
| Empty CSV (0 bytes) | Catch `EmptyDataError` in T2; mark as ERROR in summary |
| PermissionError on save | Catch in T7; emit actionable message |
| No CSVs in folder | Exit 1 with clear message after discovery in T2 |

---

## Definition of Done (overall)

- [ ] `python cli_tool.py <dir> --output out.xlsx` produces a valid `.xlsx`.
- [ ] One sheet per CSV + one `"Summary"` sheet (always first).
- [ ] Summary has correct row counts and column names for each CSV.
- [ ] Bar chart appears on Summary sheet with correct data.
- [ ] All error cases (empty file, unreadable file, bad args) exit with clear messages and non-zero codes.
- [ ] No crash on any single-file or edge-case input.
- [ ] Code passes `pylint` / `flake8` without errors (or warnings suppressed with justification).
- [ ] All functions have docstrings with Args/Returns.
