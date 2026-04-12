# CLI Tool: CSV Folder → Excel Workbook

**File:** `cli_tool.py`  
**Date:** 2026-04-12  
**Python:** 3.12 | **Deps:** pandas, openpyxl

---

## Approach

### Architecture

The tool is structured as three layers:

1. **CLI layer** (`main` / `_build_parser`) — `argparse` with `--input`, `--output`, `--encoding`, `--verbose`. Input validation (directory exists, `.xlsx` extension) happens here before any work begins.

2. **Orchestrator** (`convert`) — scans the input folder, reads each CSV via `pandas.read_csv` (with `encoding_errors='replace'` for resilience), dispatches to sheet writers, and saves the workbook. Returns a count so the caller can exit non-zero on no output.

3. **Sheet writers** (`_write_data_sheet`, `_write_summary_sheet`) — pure openpyxl operations; no pandas dependency here, which keeps them testable in isolation.

### Key Design Decisions

| Decision | Rationale |
|---|---|
| `pandas` for CSV reading | Handles type inference, mixed encodings, and large files with `low_memory=False` |
| `dataframe_to_rows` for sheet population | Avoids iterating cell-by-cell in Python; fastest openpyxl path |
| Sheet names capped at 31 chars with illegal-char replacement | Excel hard limit; collision-resistant with numeric suffix (`_2`, `_3` …) |
| Summary sheet pinned to `index=0` | First visible tab is always the summary; data sheets follow alphabetically |
| `BarChart` anchored *below* the summary table | Chart row anchor is computed dynamically based on record count, so it never overlaps the table regardless of how many CSVs are processed |
| Alternating row fills + frozen headers | Standard IB/deck readability conventions |
| `--encoding` flag with `errors='replace'` fallback | Handles Latin-1 and other non-UTF-8 legacy exports without crashing |

### Error Handling

- Missing/non-directory `--input` → `sys.exit(1)` with clear message
- Per-file read errors → logged as `ERROR`, file skipped, processing continues
- Zero sheets written → `sys.exit(1)` (non-zero exit code for CI/scripting)

### Verified Output (3-file smoke test)

```
Sheets: ['Summary', 'employees', 'inventory', 'sales']
Summary table rows: 3 (one per CSV)
Charts in Summary: 1
Data sheets: correct row/column counts
```

### Usage

```bash
python cli_tool.py --input ./data --output report.xlsx
python cli_tool.py --input ./data --output report.xlsx --encoding latin-1
python cli_tool.py --input ./data --output report.xlsx --verbose
```

### Limitations / Future Work

- Non-recursive (does not descend into sub-folders); add `rglob` to extend
- No type coercion on export (dates stay as strings unless pandas infers them)
- Chart style is openpyxl built-in style 10; custom colour scheme would require direct XML manipulation
