# RPIRT Run Summary

**Task:** Build a production-ready Python CLI tool to convert a folder of CSV files into a
single, well-formatted Excel workbook with one sheet per CSV, a Summary sheet, and a bar chart.

**Date:** 2026-04-12 13:15 ET  
**Complexity classification:** Complex (multi-component, production-ready requirement, explicit
methodology invocation)

---

## Phases Executed

### Phase 1 — Research
**Why:** Confirmed live environment (pandas 2.3.0, openpyxl 3.1.5, Python 3.13), tested the
openpyxl BarChart API interactively, validated CSV edge cases (BOM, empty, NaN, mixed types),
discovered Excel sheet name constraints (31-char limit, invalid chars), and identified the
`logging.basicConfig` idempotency pitfall. All findings written to `rpirt/01-research.md`.

### Phase 2 — Plan
**Why:** Translated research into 8 concrete, sequenced tasks (T1–T8) with explicit Definitions
of Done and risk mitigations. Established durable decisions (pandas for parsing, openpyxl for
rendering, single-file delivery, Summary at position 0). Written to `rpirt/02-plan.md`.

### Phase 3 — Implement
**Why:** Mechanical execution of the plan. Implemented all 8 tasks in `cli_tool.py` (560 lines):
CLI parsing, CSV discovery/loading with encoding fallback, sheet name sanitisation/deduplication,
data sheet writing with styled headers, Summary sheet, bar chart, and workbook save with
PermissionError handling. Deviations logged in `rpirt/03-progress.md`.

### Phase 4 — Review (2 rounds)
**Why:** Independent review as adversarial persona (power user at 2am). Generated an 8-criterion
domain-specific rubric. Round 1 found **4 issues**: (1) critical off-by-one bug in chart Reference
rows (`max_row=last_data_row + 1` should be `max_row=last_data_row`), (2) `logging.basicConfig`
without `force=True` silently no-ops if any library pre-configures logging, (3) missing type
annotations and plain dicts instead of TypedDict, (4) NaN values written as "nan" string instead
of blank cells. All 4 fixed; Round 2 scored all 8 criteria PASS. Written to `rpirt/04-review.md`.

### Phase 5 — Test
**Why:** Validated in production environment (real CSVs, real CLI invocations). Created 8 test
CSVs covering: normal data, heterogeneous schemas, NaN values, BOM encoding, 0-data-row files,
0-byte files, invalid sheet name chars, reserved name collision. Ran 19 test scenarios — all
PASS. Verified chart references point to exact rows (confirmed the off-by-one fix). Written to
`rpirt/05-test-results.md`.

---

## Deliverable

**File:** `outputs/cli_tool.py`

```
python cli_tool.py <input_dir> --output <output.xlsx> [--verbose]
```

**Features:**
- One sheet per CSV (alphabetical), styled headers, frozen pane, auto column widths
- Summary sheet always at position 0: File, Rows, Columns, Column Names
- Bar chart (vertical) on Summary showing row counts per file
- Handles: BOM files, NaN → blank cells, empty CSVs, 0-byte files, invalid sheet name chars,
  reserved name "summary", Excel row/column limits, PermissionError on save
- Exit codes: 0=success, 1=user error, 2=runtime error
- `--verbose` for DEBUG logging; all errors go to stderr

---

## Artifact Index

| File | Purpose |
|------|---------|
| `outputs/cli_tool.py` | Final deliverable |
| `outputs/rpirt/01-research.md` | Environment findings, API research, risks |
| `outputs/rpirt/02-plan.md` | Durable decisions, 8-task breakdown, DoD |
| `outputs/rpirt/03-progress.md` | Completion checklist + deviation log |
| `outputs/rpirt/04-review.md` | 8-criterion rubric, 2 review rounds, diagnosis |
| `outputs/rpirt/05-test-results.md` | 19 test scenarios, all PASS, remaining risks |
| `outputs/summary.md` | This file |
