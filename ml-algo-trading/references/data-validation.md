# Data Validation for ML Algorithmic Trading

Run this validation **before any modeling step** (Step 1.5 in the pipeline). It guarantees every DataFrame entering the strategy lifecycle is free of alignment errors, bias contamination, fill artifacts, and statistical anomalies.

---

## Quick Start

```python
from data_validation import validate, ValidationConfig

# Zero-config: works for standard Bloomberg daily equity data
validated = validate(df)

# Access the validated DataFrame
clean_df = validated.df

# Check what happened
validated.summary()
```

---

## When to Use

Every time data enters the ml-algo-trading pipeline — after Step 1 (Hypothesis) and before Step 2 (Data + Predictability Gate). The pipeline diagram is:

```
0. Install -> 1. Hypothesis -> 1.5. DATA VALIDATION -> 2. Predictability Gate
                                         |
    3. Features -> 4. Labels -> 5. Model + Purged CV
                                         |
    8. Deploy/Reject <-- 7. PSR + DSR <-- 6. Walk-Forward
```

---

## Validation Domains (7)

### 1. Schema Enforcement
Validates column names, dtypes, and structure against a registered schema. Halts on unknown/missing columns or dtype mismatches.

### 2. Calendar & Timezone
Normalizes all timestamps to UTC, aligns to NYSE trading calendar (configurable), excludes non-trading days.

### 3. Temporal Alignment & Gap Handling
Harmonizes mixed frequencies (daily/weekly/monthly), detects gaps using asset-class-specific thresholds, forward-fills with `_stale_days` counter.

| Asset Class | Max Gap (biz days) |
|---|---|
| Equities | 3 |
| Credit | 3 |
| FX/Rates | 3 |
| Macro | 65 |

### 4. Bias Prevention (ALWAYS runs, never skippable)
- **Look-ahead**: Shift-and-correlate test (|r| > 0.5 at lags 1-5) + AST-based feature audit
- **Survivorship**: Point-in-time universe snapshot validation
- **Selection bias**: Universe rationale logging
- **Backfill bias**: Value-before-report-date detection
- **Corporate actions**: Single-day return > 50% flagging
- **As-of enforcement**: First-reported macro values only

### 5. Statistical Quality Gates
ADF stationarity, Jarque-Bera normality, dual outlier detection (z-score AND IQR), ACF/Ljung-Box autocorrelation, missing data rate, tiered minimum history (252/500/60).

### 6. Cross-Source Reconciliation
Multi-source diff (1bps prices, 5bps yields), single-source self-consistency (return continuity, cross-field dividends, revision detection).

**Instrument and proxy series:** Reconcile the economic claim to the data **actually** used. **ETF** prices can diverge from **spot/underlying** (tracking error, **roll yield** in commodity trackers, corporate actions, liquidity). **Rolled futures** embed **term-structure** and **roll** effects. If the research thesis refers to **spot** economics but the series is a **rolled** or **ETF** product, **document** the mismatch, **restate the thesis** to match the **tradable** instrument, or use a more appropriate data source. See `lead-lag-predictive-inclusion.md` (instrument hygiene).

### 7. Provenance Hash Chain
SHA-256 chain from raw input through every transformation to final output. Deterministic: same input + config = same hash.

---

## Custom Configuration

```python
from data_validation import validate, ValidationConfig

config = ValidationConfig(
    calendar="XLON",                    # London Stock Exchange
    target_frequency="W",               # Weekly
    gap_thresholds={"equities": 5},     # Looser gap tolerance
    look_ahead_target_column="RET_1W",  # Column to test for look-ahead
    min_history_standard=500,           # Stricter history requirement
    n_parallel=8,                       # More parallel workers
)

validated = validate(df, config)
```

---

## Schema Registration

```python
from data_validation import SchemaRegistry, ColumnSpec

SchemaRegistry().register("bloomberg_equity", [
    ColumnSpec("SPX:PX_LAST", "float64", nullable=False),
    ColumnSpec("SPX:PX_OPEN", "float64"),
    ColumnSpec("SPX:PX_HIGH", "float64"),
    ColumnSpec("SPX:PX_LOW", "float64"),
    ColumnSpec("SPX:VOLUME", "float64"),
])

validated = validate(df, ValidationConfig(source_name="bloomberg_equity"))
```

---

## Feature Registration (for AST Audit)

```python
from data_validation import register_feature

register_feature("mom_13w", "rolling", source_code="""
df['mom_13w'] = df['price'].pct_change(13)
""")

register_feature("z_score_expanding", "expanding", source_code="""
mu = df['spread'].expanding(min_periods=26).mean()
sigma = df['spread'].expanding(min_periods=26).std()
df['z_score'] = (df['spread'] - mu) / sigma
""")

register_feature("external_signal", "external")  # No AST audit, logged as unauditable
```

---

## Reading Results

```python
# Per-series report card
validated.summary()

# Programmatic access
report = validated.report
for series, checks in report["per_series"].items():
    if checks["status"] == "WARN":
        print(f"{series}: {checks}")

# Fill masks
stale = validated.masks["_stale_days"]
outliers = validated.masks["_is_outlier"]
filled = validated.masks["_is_filled"]

# Provenance
print(validated.provenance_hash)
for step in validated.provenance_log:
    print(f"  {step['step']}: {step['output_hash'][:16]}...")

# Serialize for reproducibility
validated.to_parquet("data/validated_panel.parquet")
```

---

## Error Handling

```python
from data_validation import (
    validate, ValidationError, SchemaError, BiasError, CalendarError
)

try:
    validated = validate(df, config)
except SchemaError as e:
    print(f"Schema violations: {e.violations}")
except BiasError as e:
    print(f"Bias detected ({e.bias_type}): {e.flagged_columns}")
except CalendarError as e:
    print(f"Calendar error: {e.calendar_name}, range={e.date_range}")
except ValidationError as e:
    print(f"{len(e.failures)} failures found:")
    for f in e.failures:
        print(f"  [{f.check_name}] {f.series}: {f.description}")
```

---

## Edge Cases Handled

| Input | Behavior |
|---|---|
| Empty DataFrame | Raises ValidationError immediately |
| Single-row DataFrame | Stat tests skipped with WARN; bias/schema still run |
| All-NaN column | missing_rate=100%, FAIL |
| Duplicate dates | FAIL (never auto-deduplicated) |
| Timezone-naive index | Auto-localized to default_timezone with WARNING |
| Leading NaN (new issuance) | _stale_days = -1 sentinel, _is_filled = False |
| Inf values | Classified as outliers, WARN |
| Data predates calendar | Truncated with WARNING |

---

## Skip Mode

For quick exploratory work, `skip_validation=True` bypasses quality gates, gap checks, and reconciliation — but **bias checks always run**:

```python
validated = validate(df, config, skip_validation=True)
# Schema, calendar, bias, and provenance still execute
# Quality, alignment, reconciliation skipped
```

---

## See Also

- `predictability-analysis.md` — Run on ValidatedDataset output (Step 2)
- `feature-engineering.md` — Feature registration contract for AST audit
- `eda-ml-practices.md` — Phase 1 checklist references this module
- `validation-backtesting.md` — Downstream validation (purged CV, DSR)
