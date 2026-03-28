# Bloomberg Data Pipeline Validation (xbbg + data_validation)

<!-- Last verified: data_validation module + xbbg skill | March 2026 -->
<!-- Depends: `data_validation` package on PYTHONPATH (see ml-algo-trading references) -->

After **any** Bloomberg pull intended for quant modeling, backtests, or ML pipelines, normalize the DataFrame and run `data_validation.validate()` **before** downstream code. This reference maps **xbbg output shapes** to the validator’s expected layouts and gives copy-paste presets.

**Full module spec:** `../ml-algo-trading/references/data-validation.md` (ValidationConfig, ValidatedDataset, errors, skip mode).

---

## 1. xbbg Output → `validate()` Input Mapping

`data_validation` accepts:

| Layout | Column index | Index |
|--------|----------------|-------|
| **Long** | `date`, `ticker`, `field`, `value` (exact names) | — (`date` column) |
| **Wide (recommended for Bloomberg)** | String columns `"{TICKER}:{field}"` (field names lowercase) | `DatetimeIndex` (tz-naive or tz-aware; validator normalizes to UTC) |

**Always coerce** string `N/A` to NaN before validation: `df.replace("N/A", float("nan"))`.

### `bbg_to_validation_format()` — normalize `bdh` / flattened pulls

Use this so wide panels use **stable string column names** (matches `SchemaRegistry` and avoids MultiIndex surprises).

```python
from __future__ import annotations

import pandas as pd


def bbg_to_validation_format(
    df: pd.DataFrame,
    tickers: str | list[str] | None = None,
) -> pd.DataFrame:
    """Normalize xbbg history/reference output for data_validation.validate().

    - bdh multi-ticker: MultiIndex columns (ticker, field) -> 'TICKER:field'
    - bdh single-ticker: flat field columns -> 'TICKER:field' when `tickers` is one security
    - Already-wide string columns: returned as-is (still ensure DatetimeIndex)

    xbbg lowercases field names in output; this keeps lowercase field parts.
    """
    if df.empty:
        return df

    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("Expected DatetimeIndex on rows (bdh/bdib resampled to daily first).")

    out = df.copy()

    if isinstance(out.columns, pd.MultiIndex):
        new_cols = []
        for col in out.columns:
            t, f = col[0], col[1]
            new_cols.append(f"{t}:{str(f).lower()}")
        out.columns = new_cols
        return out

    if tickers is not None:
        if isinstance(tickers, str):
            tickers = [tickers]
        if len(tickers) == 1:
            t = tickers[0]
            out.columns = [f"{t}:{str(c).lower()}" for c in out.columns]
            return out

    return out
```

### v1.x long format (`Format.LONG`)

If you use `format=Format.LONG`, ensure columns are exactly **`date`, `ticker`, `field`, `value`** (rename if xbbg uses different labels), then pass directly to `validate()` — the pipeline will pivot to wide `{ticker}:{field}` internally.

### `bdp()` snapshots (cross-sectional)

`validate()` expects a **time index**. For a **single as-of snapshot**, build a one-row panel:

```python
import pandas as pd

def bdp_snapshot_to_validation_row(df_bdp: pd.DataFrame, asof: str) -> pd.DataFrame:
    """tickers × fields -> one row, columns 'TICKER:field', DatetimeIndex."""
    s = df_bdp.stack()
    cols = [f"{t}:{str(f).lower()}" for t, f in s.index]
    return pd.DataFrame([s.values.astype(float)], columns=cols, index=pd.DatetimeIndex([pd.Timestamp(asof)]))
```

### `bds()` / `beqs()` tabular outputs

Not time-series panels. **Do not** pass directly to `validate()`. Join to a date grid or merge with `bdh` history first, then normalize with `bbg_to_validation_format()`.

### `bdib()` intraday bars

The default `ValidationConfig` targets **daily EOD** (calendar `XNYS`, gap rules, quality gates). For intraday:

- Aggregate to daily OHLCV first, **or**
- Use `skip_validation=True` for exploratory work while keeping bias + calendar + provenance, **or**
- Supply a custom `ValidationConfig` (calendar, frequencies) aligned to your bar size — expect more WARN/FAIL from stationarity and gap logic.

---

## 2. Asset-Class `ValidationConfig` Presets

Defaults in the library already match **Bloomberg daily equity**; override per asset class:

```python
from data_validation import ValidationConfig

# US equities — daily OHLCV / factors (default-like, explicit)
EQUITY_CONFIG = ValidationConfig(
    calendar="XNYS",
    default_timezone="America/New_York",
    target_frequency="D",
    gap_thresholds={"equities": 3, "credit": 3, "fx_rates": 3, "macro": 65},
    source_name="bloomberg_equity",
)

# Credit / FI (yields, spreads — tighter yield tolerance when reconciling)
CREDIT_CONFIG = ValidationConfig(
    calendar="XNYS",
    target_frequency="D",
    gap_thresholds={"credit": 3, "equities": 3, "fx_rates": 3, "macro": 65},
    reconciliation_tolerances={"prices": 0.0001, "yields": 0.0005, "spreads": 0.0005},
    source_name="bloomberg_credit",
)

# Macro / slow series (FRED-style gaps tolerated)
MACRO_CONFIG = ValidationConfig(
    calendar="XNYS",
    target_frequency="D",
    gap_thresholds={"macro": 65, "equities": 3, "credit": 3, "fx_rates": 3},
    source_name="bloomberg_macro",
)

# FX spot / forwards (use FX-aware calendars if you switch from XNYS)
FX_CONFIG = ValidationConfig(
    calendar="XNYS",
    target_frequency="D",
    gap_thresholds={"fx_rates": 3, "equities": 3, "credit": 3, "macro": 65},
    source_name="bloomberg_fx",
)
```

Map **columns → asset class** via `ValidationConfig.asset_class_map` when one panel mixes types (e.g. `{"USGG10YR Index:px_last": "macro"}`).

---

## 3. Corporate Actions and Bloomberg `adjust`

- For backtests, prefer `blp.bdh(..., adjust='all')` (or `adjust='all'` through the Section 16 `bbg()` dispatcher) so **splits and dividends** do not create spurious returns.
- The validator’s **corporate action** check flags extreme single-period returns (possible unadjusted data). If you **intentionally** use unadjusted prices, expect FAIL/WARN — document why or adjust inputs.
- Dividend **cross-field** checks use `ValidationConfig.dividend_tolerance` when price and return columns are both present.

---

## 4. Schema Presets (`SchemaRegistry` + `ColumnSpec`)

`validate()` records a **schema hash** and parses long/wide formats; **registered schemas are enforced only if you call** `SchemaRegistry().validate(df, source_name)` yourself **before** `validate()` (fail fast on wrong columns/dtypes).

```python
from data_validation import ColumnSpec, SchemaRegistry, ValidationConfig, validate

# Example: one equity ticker, OHLCV after bbg_to_validation_format
t = "AAPL US Equity"
SchemaRegistry().register(
    "bloomberg_equity_ohlcv",
    [
        ColumnSpec(f"{t}:px_open", "float64"),
        ColumnSpec(f"{t}:px_high", "float64"),
        ColumnSpec(f"{t}:px_low", "float64"),
        ColumnSpec(f"{t}:px_last", "float64"),
        ColumnSpec(f"{t}:volume", "float64"),
    ],
)

def run_validated(df_wide, source: str):
    SchemaRegistry().validate(df_wide, source)
    return validate(df_wide, ValidationConfig(source_name=source))
```

Register **after** you know final `TICKER:field` strings (including lowercase field names).

---

## 5. Validated `bbg()` Dispatcher

Use the **Section 16** `bbg()` helper as the single pull point, then normalize and validate:

```python
import pandas as pd
from data_validation import validate, ValidationConfig, ValidatedDataset

# bbg = the dispatcher defined in Section 16 of SKILL.md


def validated_bbg(
    tickers,
    flds,
    start_date=None,
    end_date=None,
    *,
    config: ValidationConfig | None = None,
    skip_validation: bool = False,
    **kwargs,
) -> ValidatedDataset:
    """Bloomberg pull + normalize + data_validation.validate() -> ValidatedDataset."""
    raw = bbg(tickers, flds, start_date=start_date, end_date=end_date, **kwargs)
    raw = raw.replace("N/A", float("nan"))
    panel = bbg_to_validation_format(raw, tickers=tickers)
    cfg = config or ValidationConfig()
    return validate(panel, cfg, skip_validation=skip_validation)
```

- **Returns** `ValidatedDataset` — use `.df`, `.report`, `.masks`, `.provenance_hash`, `.summary()` (see `data-validation.md`).
- **Cross-section only**: use `bdp_snapshot_to_validation_row` + `validate` with a one-row config or `skip_validation=True` if tests are inappropriate.

---

## 6. Anti-Patterns (Bloomberg-Specific)

| Trap | Why it hurts | Mitigation |
|------|----------------|------------|
| **MultiIndex vs flat `bdh`** | Switching one ticker ↔ many tickers changes column shape; schemas and feature code break silently | Always run through `bbg_to_validation_format()` or `bbg(..., flat=True)` then normalize |
| **`N/A` strings** | NaN logic and stats are wrong | `replace("N/A", nan)` before validation |
| **Empty `bdp`/`bdh`** | No exception — empty DataFrame | Guard with `.empty`; do not call `validate()` on empty frames |
| **Weekend / stale RT fields** | Wrong prices in “historical” pulls | Use `PX_LAST` for history, not `LAST_PRICE_RT` in `bdh` |
| **Mixed tz index** | `CalendarError` in validator | Normalize tz on ingest; avoid mixing tz-naive and tz-aware |
| **Unadjusted equity prices** | Fake momentum/mean reversion | `adjust='all'` for price history used in returns |
| **Macro + equity same panel** | Gap thresholds differ | `asset_class_map` + `MACRO_CONFIG`-style thresholds per column |
| **Secondary source reconciliation** | Bloomberg vs vendor drift | Set `ValidationConfig.secondary_source_df` and `reconciliation_tolerances` (always include `prices`, `yields`, `spreads` keys) |

---

## See Also

- `field-reference.md`, `ticker-formats.md`, `override-cheatsheet.md` — Bloomberg fields and tickers
- `../ml-algo-trading/references/data-validation.md` — validation domains, `ValidationError`, `skip_validation`
