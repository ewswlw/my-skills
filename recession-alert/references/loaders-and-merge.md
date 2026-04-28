# Loaders, Schema Validation, and Merge

Patterns are taken from `spx_timing_strategy.py` in the Recession Alert project. **Source of truth:** inside the Obsidian vault, validate and load from `Coding Projects/Recession Alert/Raw Data/` using vendor filenames (`CMHI_DATA.xlsx`, `MonthlyData (4).xlsx`, `OPTIMUM_DATA.xlsx`, `WeeklyData (2).xlsx`). Skill `raw-data/` files are optional mirrors (`cmhi_data.xlsx`, `monthly_data_4.xlsx`, `optimum_data.xlsx`, `weekly_data_2.xlsx`) and should only be used outside the vault or after an explicit mirror-divergence check.

---

## Loader inventory

| Function | File | Sheet | Required columns (strict) | Returns |
|----------|------|-------|----------------------------|---------|
| `load_cmhi` | `CMHI_DATA.xlsx` | DAILY | DATE, SP500, DIFF, CMHI | Index DATE; cols SP500, DIFF, CMHI |
| `load_recession` | `MonthlyData (4).xlsx` | DATA | MONTH header + RFE-6 header | Dict: `rfe` (monthly RFE-6), `weekly` (SUPERINDEX[, WLIr]) |
| `load_recession` legacy check | `MonthlyData (4).xlsx` | RFE VARIANTS | Unnamed: 0, RFE-6 | Cross-check only; not primary live RFE source |
| `load_recession` | `WeeklyData (2).xlsx` | WEEKLY LEI's | DATE, SUPER | SUPER -> SUPERINDEX |
| `load_recession` (optional) | `MonthlyData (4).xlsx` | WEEKLY DATA | WEEK, WLIr if present | Joins WLIr onto weekly (may be stale) |
| `load_breadth` | `WeeklyData (2).xlsx` | SP500 BREADTH DATA | DATE, MTLV2 | MTLV2, SIGS (SIGS optional -> NaN) |
| `load_breadth_extended` | Same | Same | DATE, MTLV2 | MTLV2, SIGS, DCOM, VIX, %>50DMA (if present) |
| `load_trendex` | `WeeklyData (2).xlsx` | TRENDEX PROB MODELS | DATE, TDIFF, NET P, TOP, BOT | Those columns |
| `load_gen2` | `WeeklyData (2).xlsx` | GEN-2 PROB MODELS | DATE + any P(TOP)/P(BOT) | All P(TOP)/P(BOT) columns |
| `load_mf_prob` | `WeeklyData (2).xlsx` | SP500 MF PROB MODEL | DATE, NET AVG, NET TOP3, BIGBOT, BIGTOP, NET DIFF | Those columns |
| `load_optimum` | `OPTIMUM_DATA.xlsx` | OPTIMUM | DATE, TRADE, DIFFN, OPT-CMHI, STM | Those columns; empty DF if file missing |
| `load_bloomberg` | N/A | Cache/API | N/A | DataFrame: SPXT_Index, optional us_hy_credit_return_index |

**Date handling:** Parse with `pd.to_datetime(..., errors="coerce")`, drop NaT rows, sort index, dedupe weekly with `keep="last"` where applicable.

---

## Schema validation (`_validate_excel_schema`)

1. If strict mode is off, skip (project may use `EXCEL_SCHEMA_STRICT`).
2. Assert file exists → else `FileNotFoundError`.
3. Open `pd.ExcelFile(..., engine="openpyxl")`; assert sheet name in `sheet_names` → else `ValueError` listing available sheets.
4. Read `nrows=0` to get headers; assert every required column string (stripped) is in actual columns → else `ValueError` listing missing.
5. Optional `required_cols_any`: at least one column must match substring patterns (used for Gen-2 P(TOP)/P(BOT)).

This is **structural** validation—never substitute guessed column names.

---

## Merge order (`merge_all` pattern)

1. Build **business-day** `date_range` from `start_date` through today (`freq="B"`).
2. **CMHI daily** — `join` on index; `ffill` CMHI, DIFF.
3. **RFE-6** — monthly series `reindex(idx).ffill()` → daily `RFE_6`.
4. **Weekly SUPERINDEX / WLIr** — `reindex(idx).ffill()`.
5. **Breadth extended** — join + `ffill` per column; SIGS may `fillna(0)` if sparse pre-2015.
6. **Trendex, Gen-2, MF prob** — join + `ffill`.
7. **OPTIMUM** — join + `ffill` if present.
8. **Bloomberg** — see below. When SPXT has enough rows, code uses **`inner` join** on the SPXT column: the panel **shortens** to the intersection of RecessionALERT dates and SPXT dates (expected for aligned backtests). If SPXT is sparse, implementation may skip inner join and use SP500 from CMHI instead.

**Forward-fill semantics:** Each value is the **last observed** level as of that calendar day. It does not read future Excel rows early; it propagates the last known slow-frequency print onto subsequent days until the next observation. Document that this is not point-in-time publication lag unless you model it explicitly.

---

## Bloomberg integration

- **Cache:** `processed data/bloomberg_cache.parquet` — read first; refresh if stale (configurable max age).
- **SPXT:** `blp.bdh("SPXT Index", "PX_LAST", start, end)` → benchmark total return.
- **US HY:** Prefer `credit_return_index` helper when the project has `credit_return_index` / credit-return-index on `sys.path` (as in reference `spx_timing_strategy.py`); otherwise fallback `LF98TRUU Index` via xbbg. For field semantics, also use **`credit-data`** skill.
- **Join:** If SPXT column has fewer than `SPXT_MIN_DAYS_FOR_JOIN` valid rows, **warn** and fall back to SP500 from CMHI for price.
- **Normalize:** Flatten MultiIndex columns, strip timezone from index, replace spaces in column names.

Delegate field-level Bloomberg details to the **xbbg** skill.

---

## Maximum overlap start date

After `merge_all` (and optional column subset for **required** features):

```python
req = ["CMHI", "RFE_6", "SP500"]  # example — use project-specific list
sub = out[req].dropna(how="any")
first_valid = sub.index.min()
```

If the user passes `start_date`, take `max(first_valid, pd.Timestamp(start_date))` unless the spec says otherwise (consumer project’s `project-spec.md`, or requirements agreed in chat).

---

## Common pitfalls

| Issue | Mitigation |
|-------|------------|
| `MonthlyData (4).xlsx` WEEKLY DATA ends ~2015 | Use `WeeklyData (2).xlsx` WEEKLY LEI's `SUPER` for current SUPERINDEX |
| `RFE VARIANTS` ends in 2019 in current exports | Use `MonthlyData (4).xlsx` DATA sheet RFE-6 as primary; keep `RFE VARIANTS` as a legacy overlap check |
| RFE VARIANTS date column named `Unnamed: 0` | Rename to DATE for legacy cross-checks |
| SIGS missing or sparse early history | `fillna(0)` only where methodology allows |
| OPTIMUM file missing | Return empty DataFrame; strategy must handle |
| Inner join on SPXT drops early history | Expect shorter panel when Bloomberg inner-joins; document |
| Duplicate weekly dates | `~index.duplicated(keep="last")` on weekly frames |

---

## Idempotency

Deleting outputs under `processed data/` and re-running merge + fetch reproduces the panel from Raw Data + API (subject to API availability). Raw Data Excel files are never overwritten by this pipeline.
