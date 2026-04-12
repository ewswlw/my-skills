# Phase 3 — Progress

## Status

- [x] T1 — CLI entry point and argument parsing — **done**
- [x] T2 — CSV discovery and loading — **done**
- [x] T3 — Sheet name sanitisation and deduplication — **done**
- [x] T4 — Data sheet writing — **done**
- [x] T5 — Summary sheet writing — **done**
- [x] T6 — Bar chart creation — **done**
- [x] T7 — Workbook save and final reporting — **done**
- [x] T8 — Robustness and edge cases — **done** (handled inline in T1–T7)

## Deviations

- **T6 (chart row reference):** Plan said `last_data_row` was the last data row index. Implemented
  `add_row_count_chart` with `last_data_row + 1` as the `max_row` for the data Reference because
  openpyxl Reference uses 1-based row numbers and the header occupies row 1 — so `last_data_row + 1`
  is the actual final row in the sheet (results start at row 2). Anchor is set to
  `last_data_row + 3` for a visible gap below the table.

- **T4 (`_auto_col_widths`):** Used `df.head(200)` instead of the full DataFrame for column width
  sampling. Scanning all rows of a 500k-row CSV to find the widest cell would be too slow.
  A 200-row sample is representative and fast.

- **T8 (empty DataFrame edge case):** An "empty" CSV (header row only, 0 data rows) is considered
  *successful* (no error), appears in the summary with `Rows = 0`, and gets a data sheet with
  just the header row. This is more useful than treating it as an error.

- **Logging setup:** Used `logging.basicConfig` with explicit handlers list rather than calling
  `addHandler` manually — cleaner and avoids double-log in edge cases where basicConfig was
  already called.
