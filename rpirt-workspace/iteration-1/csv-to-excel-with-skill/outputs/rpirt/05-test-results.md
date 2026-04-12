# Phase 5 — Test Results

## Environment

- Python 3.13.11 (vault venv)
- pandas 2.3.0, openpyxl 3.1.5
- Windows 11, PowerShell 5.1
- Tool path: `outputs/cli_tool.py`

## What Was Tested

**Test data folder:** 8 CSV files covering all major cases:
- Normal CSVs with mixed types (employees.csv, products.csv)
- CSV with NaN/null values (with_nulls.csv)
- Header-only CSV with 0 data rows (empty_data.csv)
- BOM-encoded UTF-8 CSV (bom_file.csv)
- CSV with invalid sheet name chars in filename (data[2024].csv)
- CSV whose stem is the reserved name "summary" (summary.csv)
- 0-byte empty file (empty_file.csv)

**CLI surfaces tested:**
- Normal run with `--verbose`
- `--help`
- Non-existent input directory
- Missing `--output` argument
- Empty folder (no CSVs)
- Folder with only non-CSV files
- Single CSV file (chart edge case)
- Output path without `.xlsx` extension (auto-append)

---

## Results

| Test | Scenario | Result | Evidence |
|------|----------|--------|----------|
| T1 | Normal run: 8 CSVs, `--verbose` | PASS | Exit 0; 7 sheets written, 1 skipped |
| T2 | Summary sheet is always first | PASS | `wb.sheetnames[0] == 'Summary'` |
| T3 | Summary has correct row counts and column names | PASS | All 8 files present; row counts match source data |
| T4 | 0-data-row CSV shows 0 rows, not error | PASS | `empty_data.csv` → row 0, columns 3 in Summary |
| T5 | Completely empty file shows ERROR | PASS | `empty_file.csv` → ERROR in Summary, WARNING logged |
| T6 | BOM-encoded CSV handled correctly | PASS | `bom_file.csv` loaded, no BOM in column names |
| T7 | Invalid sheet name chars stripped | PASS | `data[2024].csv` → sheet `data_2024_` |
| T8 | Reserved name `summary.csv` renamed | PASS | Sheet named `Summary_data`, not `Summary` |
| T9 | NaN values written as blank cells (not "nan") | PASS | `with_nulls` sheet: row 2 has `(None, None)` |
| T10 | Bar chart: type col, title correct | PASS | `chart.type == 'col'`, title contains "Row Counts per File" |
| T11 | Chart references rows 2–9 (no phantom row) | PASS | Ref: `$B$2:$B$9`, max_row=9, row 10 is empty |
| T12 | Non-existent input dir → exit 1 + message | PASS | "Input directory does not exist", exit code 1 |
| T13 | Missing `--output` → argparse error | PASS | argparse error message, exit code 2 |
| T14 | Empty folder (no CSVs) → exit 1 | PASS | "No CSV files found", exit code 1 |
| T15 | Folder with only .txt files → exit 1 | PASS | "No CSV files found", exit code 1 |
| T16 | Single CSV → runs cleanly | PASS | 1 sheet + Summary; exit 0 |
| T17 | Output without .xlsx → auto-appended | PASS | `no_ext.xlsx` created successfully |
| T18 | `--help` → clear usage output | PASS | Shows args, description, examples |
| T19 | Exit codes are correct | PASS | 0=success, 1=user error, 2=runtime (argparse) |

**All 19 tests PASS.**

---

## Remaining Risks

| Risk | Severity | Note |
|------|----------|------|
| Very large CSVs (500k+ rows) | Medium | `itertuples` + `ws.append` is single-threaded and slow for large files. No streaming. Acceptable for CLI scope; documented in `--verbose` warning. |
| CSV with >16,383 columns | Low | Truncation logic present; untested at scale. |
| latin-1 files with genuinely ambiguous encoding | Low | Will load but may display garbled characters. chardet not in scope. |
| Excel chart rendering in LibreOffice/Google Sheets | Low | Standard OOXML chart; should render but not tested in non-Excel viewers. |
| Concurrent runs writing to same output path | Low | Last writer wins. No file locking. Acceptable for CLI. |

---

## Final Scorecard

| Phase | Summary |
|-------|---------|
| Review Round 1 | 3 FAILs: chart off-by-one, logging.basicConfig no force, NaN handling, missing types |
| Review Round 2 | All 8 criteria PASS — 2 rounds total |
| Test | 19/19 PASS |
| Remaining risks | 5 low/medium — all documented, none blocking |
