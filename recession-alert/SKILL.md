---
name: recession-alert
description: >
  Loads, validates, merges, and uses RecessionALERT macro and market-health data (CMHI, RFE, OPTIMUM, Trendex, SuperIndex, breadth, Gen-2, MF Prob) for any quantitative trading or asset allocation project, not only SPX. Covers vault Raw Data Excel ingestion, optional skill mirror checks, frequency alignment, feature engineering, statistical diagnostics, signal hierarchy, and test-driven development for clean pipelines. Use when the user mentions recession alert, RecessionALERT, CMHI, RFE-6, OPTIMUM, Trendex, SuperIndex, breadth timing, macro regime, or building strategies from Raw Data.
---

# RecessionALERT Quantitative Data Skill

Reference files live in this skill folder: `references/`. Read them when the task needs column-level detail, merge mechanics, features, signal rules, or tests.

## Quick start (paths)

**Primary in this vault:** The authoritative RecessionALERT workbooks live in the Obsidian vault export folder:

| Location | Purpose |
|----------|---------|
| `Coding Projects/Recession Alert/Raw Data/CMHI_DATA.xlsx` | CMHI export |
| `Coding Projects/Recession Alert/Raw Data/MonthlyData (4).xlsx` | Monthly / RFE export |
| `Coding Projects/Recession Alert/Raw Data/OPTIMUM_DATA.xlsx` | OPTIMUM export |
| `Coding Projects/Recession Alert/Raw Data/WeeklyData (2).xlsx` | Weekly breadth / Trendex / MF / Gen-2 export |

Validation and strategy loading should use this vault folder unless a project config explicitly overrides it. Do not silently prefer bundled skill workbooks over the vault source.

**Optional skill mirror:** This skill may also keep normalized copies under `<skill-root>/raw-data/` for portability:

| Location | Purpose |
|----------|---------|
| `<skill-root>/raw-data/cmhi_data.xlsx` | Mirror of `CMHI_DATA.xlsx` |
| `<skill-root>/raw-data/monthly_data_4.xlsx` | Mirror of `MonthlyData (4).xlsx` |
| `<skill-root>/raw-data/optimum_data.xlsx` | Mirror of `OPTIMUM_DATA.xlsx` |
| `<skill-root>/raw-data/weekly_data_2.xlsx` | Mirror of `WeeklyData (2).xlsx` |

`<skill-root>` is the folder containing this `SKILL.md` (e.g. `~/.claude/skills/recession-alert` on this machine). See `raw-data/README.md` for vendor filename mapping, hash checks, and refresh rules.

**Other vault paths:**

| Location | Purpose |
|----------|---------|
| `Coding Projects/Recession Alert/processed data/` | Regenerable parquet/CSV caches (e.g. Bloomberg) |
| `Coding Projects/Recession Alert/Guides/` | Full encyclopedias: economic meaning, methodology |

**Spec / constitution for this skill bundle:** `project-spec.md` and `project-constitution.md` next to this `SKILL.md` (not only under the vault Recession Alert folder).

**Primary implementation reference:** `spx_timing_strategy.py` (loaders `load_*`, `merge_all`, `engineer_features`, embedded tests). Treat it as one consumer of the panel—not the only possible strategy.

## Per-project config contract

Before writing pipeline code, define (or accept defaults for):

1. **Required series** — Which sheets/columns the project needs (drives max-overlap start).
2. **Start date rule** — User override, else **earliest date where all required columns are simultaneously non-null** on the aligned index (see `references/loaders-and-merge.md`).
3. **Benchmark** — Named per project (e.g. SPXT, RF, custom blend).
4. **Merge policy** — Default: business-day index + forward-fill slower series; document if you need point-in-time / as-of.
5. **Success metrics and validation** — Alpha vs benchmark, Sharpe, max DD, holdout / walk-forward / DSR, etc.

**Structural vs discretionary (must match constitution):**

- **Structural:** File path, sheet name, required column names → **fail fast** with a clear error. Never invent columns.
- **Discretionary:** Benchmark if user says “default,” thresholds, optional flags → **state best guess in writing**; user can override.

## Pipeline workflow (do not skip)

```
0. Install / sync -> 1. Config -> 2. Load raw -> 3. Validate schema
   -> 4. Merge panel -> 5. Engineer features -> 6. TESTS for 2-5
   -> 7. Strategy / model -> 8. Backtest + OOS gates -> 9. Document run
```

| Step | Action | Detail |
|------|--------|--------|
| 0 | Install / sync | From vault root: `uv sync` (see workspace `pyproject.toml`) |
| 1 | Write or adopt config | Required columns, start rule, benchmark |
| 2 | Validate raw source | Run the raw-data doctor/check path before research or backtests |
| 3 | Load | See `references/loaders-and-merge.md` |
| 4 | Merge | Daily index; reindex + `ffill` for slower frequencies |
| 5 | Features | See `references/features-and-transforms.md` |
| 6 | **Tests** | See `references/testing-patterns.md` — before trusting step 7 |
| 7 | Strategy | Rules / ML; signal layering: `references/signal-hierarchy.md` |
| 8 | Backtest | Holdout, DSR, walk-forward as appropriate |
| 9 | Reproducibility | Log Raw Data vintage, git hash, config snapshot |

## What this skill does not do

- Live order execution, brokerage APIs, or production tick infrastructure.
- Guaranteed out-of-sample alpha; all research is historical.
- Bloomberg fetching as primary documentation — use the **xbbg** skill for BDH/BDP patterns; this skill describes how merged code **uses** cached Bloomberg columns.

## Cross-skill integration

| Topic | Delegate to |
|-------|-------------|
| ML lifecycle (purged CV, triple barrier, meta-labeling, DSR) | `ml-algo-trading` |
| Bloomberg API details, field names | `xbbg` |
| Credit index / spread fetches | `credit-data` skill; **implementation note:** `spx_timing_strategy.py` may call a local `credit_return_index` module if present—see `references/loaders-and-merge.md` |
| `vectorbt` portfolio tearsheets | `vectorbt-tearsheet` |

## Reference map

| File | Contents |
|------|----------|
| [references/data-dictionary.md](references/data-dictionary.md) | Files, sheets, columns, ranges, pitfalls |
| [references/loaders-and-merge.md](references/loaders-and-merge.md) | Loaders, schema validation, merge order, Bloomberg, max overlap |
| [references/features-and-transforms.md](references/features-and-transforms.md) | Z-scores, momentum, passthroughs, fillna conventions |
| [references/signal-hierarchy.md](references/signal-hierarchy.md) | Six layers, ranked signals, pseudo-code, sizing |
| [references/testing-patterns.md](references/testing-patterns.md) | TDD categories, templates, validation gates |

## Triggers

Invoke for `/recession-alert`, RecessionALERT data, CMHI, RFE-6, OPTIMUM TRADE, Trendex, SuperIndex, merge Raw Data, asset allocation using recession indicators, or any task that reads the vault export folder or optional bundled `raw-data/` mirror.
