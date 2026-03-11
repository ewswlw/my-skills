# Custom Metrics — Computation Logic

These metrics are NOT available natively in vectorbt's open-source `.stats()` methods. They must be manually computed from the portfolio's return series and equity curve.

Read this file when implementing Tables 8-12 of the tearsheet.

---

## Shared Helpers

These utility functions are used across multiple custom tables:

```python
import pandas as pd
import numpy as np

def compound_return(rets: pd.Series) -> float:
    """Compound a return series into a single return."""
    if len(rets) == 0:
        return 0.0
    return (1 + rets).prod() - 1

def annualized_return(rets: pd.Series, periods_per_year: int) -> float:
    """Annualize a compound return over the given window."""
    total = (1 + rets).prod()
    n_years = len(rets) / periods_per_year
    if n_years <= 0:
        return 0.0
    return total ** (1 / n_years) - 1

def get_periods_per_year(freq: str) -> int:
    """Map frequency string to periods per year."""
    freq_map = {"D": 252, "W": 52, "M": 12, "Q": 4, "Y": 1}
    # Normalize: take first char uppercase
    key = freq.upper().lstrip("0123456789")[0] if freq else "D"
    return freq_map.get(key, 252)
```

---

## Table 8 — Period Returns

Compute compound (or annualized) returns over specific lookback windows. Display `"N/A"` when data history is shorter than the window.

```python
def compute_period_returns(
    returns: pd.Series,
    periods_per_year: int,
) -> dict[str, float | str]:
    """
    Compute period returns for MTD, 3M, 6M, YTD, 1Y, 3Y, 5Y, 10Y, All-time.

    Args:
        returns: Return series with DatetimeIndex.
        periods_per_year: 252 for daily, 52 for weekly.

    Returns:
        Dict mapping period label to return value or "N/A".
    """
    if len(returns) == 0:
        return {k: "N/A" for k in [
            "MTD", "3M", "6M", "YTD", "1Y",
            "3Y (ann.)", "5Y (ann.)", "10Y (ann.)", "All-time (ann.)"
        ]}

    end = returns.index[-1]
    results = {}

    # MTD: first day of current month to end
    mtd_start = end.replace(day=1)
    mtd_rets = returns.loc[mtd_start:]
    results["MTD"] = compound_return(mtd_rets)

    # 3M
    start_3m = end - pd.DateOffset(months=3)
    if returns.index[0] <= start_3m:
        results["3M"] = compound_return(returns.loc[start_3m:])
    else:
        results["3M"] = "N/A"

    # 6M
    start_6m = end - pd.DateOffset(months=6)
    if returns.index[0] <= start_6m:
        results["6M"] = compound_return(returns.loc[start_6m:])
    else:
        results["6M"] = "N/A"

    # YTD: January 1 of current year to end
    ytd_start = end.replace(month=1, day=1)
    ytd_rets = returns.loc[ytd_start:]
    results["YTD"] = compound_return(ytd_rets)

    # 1Y
    start_1y = end - pd.DateOffset(years=1)
    if returns.index[0] <= start_1y:
        results["1Y"] = compound_return(returns.loc[start_1y:])
    else:
        results["1Y"] = "N/A"

    # 3Y (annualized)
    start_3y = end - pd.DateOffset(years=3)
    if returns.index[0] <= start_3y:
        results["3Y (ann.)"] = annualized_return(
            returns.loc[start_3y:], periods_per_year
        )
    else:
        results["3Y (ann.)"] = "N/A"

    # 5Y (annualized)
    start_5y = end - pd.DateOffset(years=5)
    if returns.index[0] <= start_5y:
        results["5Y (ann.)"] = annualized_return(
            returns.loc[start_5y:], periods_per_year
        )
    else:
        results["5Y (ann.)"] = "N/A"

    # 10Y (annualized)
    start_10y = end - pd.DateOffset(years=10)
    if returns.index[0] <= start_10y:
        results["10Y (ann.)"] = annualized_return(
            returns.loc[start_10y:], periods_per_year
        )
    else:
        results["10Y (ann.)"] = "N/A"

    # All-time (annualized)
    results["All-time (ann.)"] = annualized_return(returns, periods_per_year)

    return results
```

---

## Table 9 — Extremes

Best and worst returns at daily/weekly, monthly, and yearly granularity.

```python
def compute_extremes(returns: pd.Series, freq: str) -> dict[str, float]:
    """
    Compute best/worst returns at period, monthly, and yearly granularity.

    Args:
        returns: Return series with DatetimeIndex.
        freq: "D" for daily, "W" for weekly — determines the label.

    Returns:
        Dict mapping metric label to return value.
    """
    # Period-level (day or week)
    period_label = "Day" if freq.upper().startswith("D") else "Week"
    results = {
        f"Best {period_label}": returns.max(),
        f"Worst {period_label}": returns.min(),
    }

    # Monthly
    monthly_rets = (1 + returns).resample("ME").prod() - 1
    results["Best Month"] = monthly_rets.max()
    results["Worst Month"] = monthly_rets.min()

    # Yearly
    yearly_rets = (1 + returns).resample("YE").prod() - 1
    results["Best Year"] = yearly_rets.max()
    results["Worst Year"] = yearly_rets.min()

    return results
```

---

## Table 10 — Drawdown Detail Metrics

Mix of native vectorbt calls and custom formulas.

```python
def compute_drawdown_details(pf, periods_per_year: int) -> dict[str, float]:
    """
    Compute drawdown detail metrics.

    Args:
        pf: vbt.Portfolio object.
        periods_per_year: 252 for daily, 52 for weekly.

    Returns:
        Dict with Avg Drawdown, Avg DD Days, Recovery Factor,
        Ulcer Index, Serenity Index.
    """
    results = {}

    # Native
    results["Avg. Drawdown"] = pf.drawdowns.drawdown.mean()
    results["Avg. Drawdown Days"] = pf.drawdowns.duration.mean()

    # Recovery Factor: total_return / abs(max_drawdown)
    total_ret = pf.total_return()
    max_dd = pf.drawdowns.max_drawdown()  # Negative value
    if max_dd != 0:
        results["Recovery Factor"] = total_ret / abs(max_dd)
    else:
        results["Recovery Factor"] = float("inf")

    # Ulcer Index: sqrt(mean(drawdown_pct^2))
    value = pf.value()
    rolling_max = value.expanding().max()
    drawdown_pct = (value - rolling_max) / rolling_max  # All <= 0
    ulcer_index = np.sqrt((drawdown_pct ** 2).mean())
    results["Ulcer Index"] = ulcer_index

    # Serenity Index: annualized_return / ulcer_index
    returns = pf.returns()
    ann_ret = annualized_return(returns, periods_per_year)
    if ulcer_index != 0:
        results["Serenity Index"] = ann_ret / ulcer_index
    else:
        results["Serenity Index"] = float("inf")

    return results
```

---

## Table 11 — Win Rate Breakdown

Resample returns to various periods and compute win percentages.

```python
def compute_win_rates(returns: pd.Series) -> dict[str, float]:
    """
    Compute win rate breakdown by period granularity.

    Args:
        returns: Return series with DatetimeIndex.

    Returns:
        Dict with Avg Up Month, Avg Down Month, Win Days/Month/Quarter/Year %.
    """
    results = {}

    # Monthly returns
    monthly_rets = (1 + returns).resample("ME").prod() - 1
    up_months = monthly_rets[monthly_rets > 0]
    down_months = monthly_rets[monthly_rets < 0]

    results["Avg. Up Month"] = up_months.mean() if len(up_months) > 0 else 0.0
    results["Avg. Down Month"] = down_months.mean() if len(down_months) > 0 else 0.0

    # Win percentages
    results["Win Days"] = (returns > 0).mean() * 100  # or "Win Weeks"
    results["Win Month"] = (monthly_rets > 0).mean() * 100

    # Quarterly
    quarterly_rets = (1 + returns).resample("QE").prod() - 1
    results["Win Quarter"] = (quarterly_rets > 0).mean() * 100

    # Yearly
    yearly_rets = (1 + returns).resample("YE").prod() - 1
    results["Win Year"] = (yearly_rets > 0).mean() * 100

    return results
```

---

## Table 12 — Monthly Returns Grid

Pivot table with rows = years, columns = Jan-Dec + YTD.

```python
def compute_monthly_grid(returns: pd.Series) -> pd.DataFrame:
    """
    Build a monthly returns grid (year x month pivot).

    Args:
        returns: Return series with DatetimeIndex.

    Returns:
        DataFrame with years as index, months (Jan-Dec) + YTD as columns.
        Values are returns as floats (format as % when rendering).
    """
    monthly_rets = (1 + returns).resample("ME").prod() - 1

    # Build pivot
    grid = monthly_rets.groupby(
        [monthly_rets.index.year, monthly_rets.index.month]
    ).first().unstack(level=1)

    # Flatten column MultiIndex if present
    if hasattr(grid.columns, "droplevel"):
        grid.columns = grid.columns.droplevel(0)

    # Rename columns to month abbreviations
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }
    grid = grid.rename(columns=month_names)

    # Add YTD column
    grid["YTD"] = grid.apply(
        lambda row: (1 + row.dropna()).prod() - 1, axis=1
    )

    return grid
```

### Rendering note

When rendering in Rich, color-code cells:
- **Green** for positive returns
- **Red** for negative returns
- Format all values as `f"{value:.2%}"`
- Empty cells (months with no data) display as `""` or `"-"`
