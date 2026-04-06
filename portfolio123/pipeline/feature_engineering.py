"""Factor screening (IC gate), fractional differentiation, feature matrix helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def screen_factors(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    threshold: float | None = None,
) -> dict[str, float | bool | int]:
    """
    Univariate IC screening gate: Pearson correlation t-stat vs forward returns.

    Aligns on index (date×ticker MultiIndex or same index).
    """
    thr = threshold if threshold is not None else config.SCREENING_T_THRESHOLD
    valid = factor_values.dropna()
    aligned = forward_returns.reindex(valid.index).dropna()
    common = valid.index.intersection(aligned.index)

    if len(common) < 30:
        return {
            "t_stat": 0.0,
            "ic": 0.0,
            "n": len(common),
            "passed": False,
        }

    v = valid.loc[common]
    a = aligned.loc[common]
    ic = float(v.corr(a))
    n = len(common)
    if abs(ic) >= 1.0:
        t_stat = 0.0
    else:
        t_stat = float(ic * np.sqrt(n - 2) / np.sqrt(1 - ic**2))

    return {
        "t_stat": round(t_stat, 4),
        "ic": round(ic, 6),
        "n": n,
        "passed": abs(t_stat) > thr,
    }


def screen_factors_panel(
    df: pd.DataFrame,
    factor_cols: list[str],
    forward_ret_col: str,
    min_names_per_date: int = 20,
    threshold: float | None = None,
) -> dict[str, dict[str, float | bool | int]]:
    """
    Cross-sectional IC per as-of date, then t-stat on the time series of mean IC.

    Expects columns: at least one of (date, asOfDt) and ticker/name, plus factor columns.
    """
    thr = threshold if threshold is not None else config.SCREENING_T_THRESHOLD
    date_col = "asOfDt" if "asOfDt" in df.columns else "date" if "date" in df.columns else None
    if date_col is None:
        raise ValueError("DataFrame needs 'asOfDt' or 'date' column")

    out: dict[str, dict[str, float | bool | int]] = {}
    for col in factor_cols:
        ics: list[float] = []
        for _, g in df.groupby(date_col, sort=False):
            g = g.dropna(subset=[col, forward_ret_col])
            if len(g) < min_names_per_date:
                continue
            ic = g[col].corr(g[forward_ret_col])
            if ic is not None and not np.isnan(ic):
                ics.append(float(ic))
        if len(ics) < 5:
            out[col] = {"t_stat": 0.0, "ic": 0.0, "n_periods": len(ics), "passed": False}
            continue
        arr = np.array(ics)
        mean_ic = float(np.mean(arr))
        std_ic = float(np.std(arr, ddof=1))
        n = len(ics)
        t_stat = float(mean_ic / (std_ic / np.sqrt(n))) if std_ic > 1e-12 else 0.0
        out[col] = {
            "t_stat": round(t_stat, 4),
            "ic": round(mean_ic, 6),
            "n_periods": n,
            "passed": abs(t_stat) > thr,
        }
    return out


def _weights_ffd(d: float, threshold: float) -> np.ndarray:
    """López de Prado fractional diff weights."""
    w = [1.0]
    k = 1
    while True:
        w_k = -w[-1] * (d - k + 1) / k
        if abs(w_k) < threshold:
            break
        w.append(w_k)
        k += 1
        if k > 10000:
            break
    return np.array(w[::-1])


def compute_ffd(series: pd.Series, d: float, threshold: float = 1e-5) -> pd.Series:
    """
    Fractional differentiation (FFD) for stationarity with memory preservation.

    Args:
        series: Time-ordered levels or prices
        d: Differentiation degree in (0, 1]
        threshold: Weight cutoff
    """
    w = _weights_ffd(d, threshold)
    width = len(w) - 1
    out = np.full(len(series), np.nan)
    x = series.values.astype(float)
    for i in range(width, len(series)):
        out[i] = float(np.dot(w, x[i - width : i + 1]))
    return pd.Series(out, index=series.index)


def compute_forward_returns(
    df: pd.DataFrame,
    price_col: str,
    horizon_bars: int,
    ticker_col: str = "ticker",
    date_col: str | None = None,
) -> pd.Series:
    """
    Point-in-time safe forward return over ``horizon_bars`` rows per ticker.

    Assumes df sorted by (ticker, date). Forward return = future / current - 1.
    """
    dcol = date_col or ("asOfDt" if "asOfDt" in df.columns else "date")
    work = df.sort_values([ticker_col, dcol]).copy()
    g = work.groupby(ticker_col, group_keys=False)
    fwd = g[price_col].transform(lambda s: s.shift(-horizon_bars) / s - 1.0)
    return fwd


def build_feature_matrix(
    raw: pd.DataFrame,
    feature_cols: list[str],
    cross_section_z: bool = True,
    date_col: str | None = None,
) -> pd.DataFrame:
    """
    Optional cross-sectional z-score per date for each feature column.
    """
    dcol = date_col or ("asOfDt" if "asOfDt" in raw.columns else "date")
    if dcol not in raw.columns:
        return raw[feature_cols].copy()
    out = raw[feature_cols].copy()
    if not cross_section_z:
        return out
    for col in feature_cols:
        out[col] = raw.groupby(dcol, sort=False)[col].transform(
            lambda x: (x - x.mean()) / x.std(ddof=0).replace(0, np.nan)
        )
    return out
