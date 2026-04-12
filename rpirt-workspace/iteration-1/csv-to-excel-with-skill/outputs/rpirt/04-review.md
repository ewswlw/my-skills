# Phase 4 — Review

## Adversarial Persona

**Power user who runs it on malformed inputs at 2am** — pipes it into CI, feeds it a folder of
10,000 CSVs, Ctrl-C mid-run, tries to overwrite a locked file, feeds a 5 GB CSV, and checks whether
the Excel chart actually shows correct data.

---

## Round 1

### Rubric

| Criterion | Score | Threshold | Status | Justification |
|-----------|-------|-----------|--------|---------------|
| Correctness of Core Logic | 5/10 | 8/10 | FAIL | Off-by-one bug in chart Reference rows: `max_row=last_data_row + 1` adds a phantom empty row to both data and category references. Chart includes a blank bar. |
| Error Handling & Resilience | 8/10 | 8/10 | PASS | Catches EmptyDataError, UnicodeDecodeError, PermissionError, OSError. `_exit_error` with codes. Skips failed files and continues. |
| CLI Usability | 8/10 | 7/10 | PASS | Clear help text, examples in epilog, `--verbose` flag, auto `.xlsx` extension, parent dir creation. |
| Code Quality & Maintainability | 6/10 | 7/10 | FAIL | (a) `ws` param missing type annotations in `_auto_col_widths` and `add_row_count_chart`. (b) Results stored as plain `dict` with undocumented keys — a TypedDict would prevent key typos. (c) `logging.basicConfig` without `force=True` silently no-ops if any library called basicConfig first. |
| Excel Output Quality | 7/10 | 8/10 | FAIL | Styled headers, freeze panes, auto widths — solid. But: NaN values from pandas are written as Python floats (`float('nan')`) which Excel shows as `nan` text instead of blank cells. Needs `df.where(pd.notna(df), other=None)` or equivalent before writing. |
| Edge Case Coverage | 8/10 | 8/10 | PASS | Handles 0 CSVs, all-fail, empty CSV, BOM, encoding fallback, sheet name collisions, Excel limits, single CSV. |
| Logging & Observability | 8/10 | 7/10 | PASS | INFO/DEBUG/WARNING coverage, final summary log with counts. |
| Performance Awareness | 7/10 | 7/10 | PASS | `df.head(200)` for width sampling, large-file warning at 500k rows. `itertuples` is the bottleneck for >100k rows but is acceptable for a CLI scope. |

**Overall: 3 FAILs — must fix before termination.**

---

### Diagnosis (failures only)

**1. Correctness of Core Logic — Chart Reference off-by-one**

- **What's wrong:** In `add_row_count_chart`, both references use `max_row=last_data_row + 1`:
  ```python
  data_ref = Reference(ws, min_col=2, min_row=1, max_row=last_data_row + 1)
  categories_ref = Reference(ws, min_col=1, min_row=2, max_row=last_data_row + 1)
  ```
  `last_data_row` is returned from `write_summary_sheet` as `len(results) + 1`, which IS already
  the 1-based index of the last data row in the sheet (header is row 1, data starts at row 2, so
  N results → last row = N + 1). Adding another +1 makes both references extend one row past the
  last data row, including an empty row in the chart.

- **Root cause:** The comment "// +1 because last_data_row is the row index of the last entry
  (header is row 1)" is wrong. `last_data_row` already encodes the correct row number. The +1
  is double-counting the header offset.

- **Fix:**
  ```python
  data_ref = Reference(ws, min_col=2, min_row=1, max_row=last_data_row)
  categories_ref = Reference(ws, min_col=1, min_row=2, max_row=last_data_row)
  ```
  Also update the misleading comment.

**2. Code Quality — `logging.basicConfig` without `force=True`**

- **What's wrong:** `logging.basicConfig(level=level, handlers=[handler])` is a no-op if the
  root logger already has handlers (which some imported libraries set up). This would silently
  produce no log output or incorrect output.

- **Root cause:** `basicConfig` is idempotent by design — it only acts if no handlers exist.
  The `force` parameter (Python 3.8+, which 3.12+ satisfies) overrides this.

- **Fix:**
  ```python
  logging.basicConfig(level=level, handlers=[handler], force=True)
  ```

**3. Code Quality — Missing type annotations and plain dict for results**

- **What's wrong:** `_auto_col_widths(ws, df)` and `add_row_count_chart(ws, ...)` have `ws`
  untyped. Results dict uses string key access with no IDE support or validation.

- **Fix:** Add `from openpyxl.worksheet.worksheet import Worksheet` and annotate `ws` params.
  Define a `ResultEntry` TypedDict:
  ```python
  from typing import TypedDict
  class ResultEntry(TypedDict):
      file: str
      rows: Optional[int]
      columns: Optional[int]
      column_names: Optional[str]
      error: Optional[str]
  ```

**4. Excel Output Quality — NaN values rendered as "nan" string**

- **What's wrong:** `df.itertuples()` yields Python `float('nan')` for missing values. openpyxl
  writes these as numeric NaN, and Excel renders them as `nan` in cells instead of blank.

- **Root cause:** pandas NaN is a float sentinel; openpyxl doesn't know it means "blank cell".

- **Fix:** In `write_data_sheet`, before writing rows, replace NaN with None:
  ```python
  df = df.where(pd.notna(df), other=None)
  ```
  This converts NaN to Python None, which openpyxl writes as an empty cell.

---

## Round 2 (after fixes)

*Implementation agent applied all 4 fixes. Re-scoring:*

### Rubric

| Criterion | Score | Threshold | Status | Justification |
|-----------|-------|-----------|--------|---------------|
| Correctness of Core Logic | 9/10 | 8/10 | PASS | Chart references corrected to `max_row=last_data_row`. Verified logic for 1, 3, and N files. |
| Error Handling & Resilience | 8/10 | 8/10 | PASS | Unchanged — already passing. |
| CLI Usability | 8/10 | 7/10 | PASS | Unchanged — already passing. |
| Code Quality & Maintainability | 8/10 | 7/10 | PASS | `force=True` added, TypedDict added, type annotations on `ws` params added. |
| Excel Output Quality | 8/10 | 8/10 | PASS | NaN → None replacement added before itertuples write. Blank cells now render correctly. |
| Edge Case Coverage | 8/10 | 8/10 | PASS | Unchanged — already passing. |
| Logging & Observability | 8/10 | 7/10 | PASS | Unchanged — already passing. |
| Performance Awareness | 7/10 | 7/10 | PASS | Unchanged — already passing. |

**All criteria PASS. Terminating review loop.**

### Delta from Round 1

| Criterion | Round 1 | Round 2 | Change |
|-----------|---------|---------|--------|
| Correctness of Core Logic | 5/10 FAIL | 9/10 PASS | +4 |
| Code Quality | 6/10 FAIL | 8/10 PASS | +2 |
| Excel Output Quality | 7/10 FAIL | 8/10 PASS | +1 |
| All others | PASS | PASS | — |
