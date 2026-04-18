"""
Month-end price levels from ~2000 with documented proxy stitching for late ETFs.

Stitching rule (DeepLogic / reproducibility): for each asset, extend history backward
using a proxy series scaled to match the primary in the *overlap* window (median price
ratio). If no overlap yet, use proxy levels directly until primary starts.
"""
from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)

LOGICAL_COLUMNS = [
    "SPY",
    "QQQ",
    "IWM",
    "EFA",
    "EEM",
    "TLT",
    "GLD",
    "VNQ",
    "AGG",
    "CASH",
    "UPRO",
    "TQQQ",
    "TMF",
]

DOWNLOAD_SYMBOLS = sorted(
    {
        "SPY",
        "QQQ",
        "IWM",
        "EFA",
        "EEM",
        "TLT",
        "GLD",
        "VNQ",
        "AGG",
        "BIL",
        "SHY",
        "IEF",
        "IYR",
        "GC=F",
        "UPRO",
        "TQQQ",
        "TMF",
        "SSO",
        "QLD",
        "UBT",
        "^IRX",
    }
)


def _adj_close(raw: pd.DataFrame) -> pd.DataFrame:
    if isinstance(raw.columns, pd.MultiIndex):
        if "Adj Close" in raw.columns.get_level_values(0):
            return raw["Adj Close"].copy()
        return raw["Close"].copy()
    if "Adj Close" in raw.columns:
        return raw[["Adj Close"]].copy()
    return raw.copy()


def _download_monthly(symbols: set[str], start: str) -> pd.DataFrame:
    raw = yf.download(
        list(symbols),
        start=start,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    px = _adj_close(raw)
    if isinstance(px, pd.Series):
        px = px.to_frame()
    px = px.dropna(how="all").ffill()
    return px.resample("ME").last()


def _stitch_primary_proxy(primary: pd.Series, proxy: pd.Series) -> pd.Series:
    """Primary when available; before that, proxy * median(primary/proxy) in overlap."""
    p = primary.astype(float)
    u = proxy.astype(float)
    idx = p.index.union(u.index).sort_values()
    p = p.reindex(idx)
    u = u.reindex(idx)
    overlap = p.dropna().index.intersection(u.dropna().index)
    if len(overlap) >= 3:
        ratio = float((p.loc[overlap] / u.loc[overlap]).median())
        scaled_u = u * ratio
        out = p.copy()
        first_p = p.first_valid_index()
        if first_p is not None:
            mask = out.index < first_p
            out.loc[mask] = scaled_u.loc[mask]
        out = out.combine_first(p)
        return out
    return p.combine_first(u)


def _synth_3x_level(base_level: pd.Series) -> pd.Series:
    """
    Synthetic 3x long *level* from 1x level (no daily path dependency; known limitation).
    r_3x ≈ 3 * r_1x on simple monthly compounding (ignores leveraged ETF volatility drag).
    """
    r = base_level.pct_change()
    r3 = 3.0 * r
    lev = (1 + r3.fillna(0)).cumprod()
    if lev.notna().any():
        lev = lev / lev.dropna().iloc[0] * float(base_level.dropna().iloc[0])
    return lev


def _cash_level_from_irx(irx: pd.Series) -> pd.Series:
    """TBill-like level from ^IRX (yield in %). Approx monthly: y/12/100."""
    y = irx.astype(float).reindex(irx.index).ffill() / 100.0
    rm = y / 12.0
    return (1 + rm.fillna(0)).cumprod()


def build_panel(start: str = "1999-01-01") -> pd.DataFrame:
    px = _download_monthly(DOWNLOAD_SYMBOLS, start=start)
    out = pd.DataFrame(index=px.index)

    out["SPY"] = px["SPY"]
    out["QQQ"] = px["QQQ"]
    out["IWM"] = px["IWM"]
    out["EFA"] = px["EFA"]
    out["EEM"] = px["EEM"]
    out["TLT"] = px["TLT"]

    # Gold: GLD <- gold futures
    out["GLD"] = _stitch_primary_proxy(px["GLD"], px["GC=F"])

    # REITs: VNQ <- IYR
    out["VNQ"] = _stitch_primary_proxy(px["VNQ"], px["IYR"])

    # Aggregate bonds: AGG <- IEF (duration mismatch; documented proxy)
    out["AGG"] = _stitch_primary_proxy(px["AGG"], px["IEF"])

    # Cash: BIL <- SHY <- T-bill yield index
    cash_yield = _cash_level_from_irx(px["^IRX"])
    cash = _stitch_primary_proxy(px["BIL"], px["SHY"])
    cash = _stitch_primary_proxy(cash, cash_yield)
    out["CASH"] = cash

    # 3x equity: UPRO <- scaled SSO <- synthetic 3x SPY (pre-2009)
    k_sso = 1.45
    ov = px["UPRO"].dropna().index.intersection(px["SSO"].dropna().index)
    if len(ov) >= 6:
        k_sso = float(np.clip((px["UPRO"].loc[ov] / px["SSO"].loc[ov]).median(), 1.35, 1.75))
    upro_chain = _stitch_primary_proxy(px["UPRO"], px["SSO"] * k_sso)
    out["UPRO"] = _stitch_primary_proxy(upro_chain, _synth_3x_level(px["SPY"]))

    # TQQQ <- scaled QLD <- synthetic 3x QQQ
    k_qld = 1.45
    ov = px["TQQQ"].dropna().index.intersection(px["QLD"].dropna().index)
    if len(ov) >= 6:
        k_qld = float(np.clip((px["TQQQ"].loc[ov] / px["QLD"].loc[ov]).median(), 1.35, 1.75))
    tqqq_chain = _stitch_primary_proxy(px["TQQQ"], px["QLD"] * k_qld)
    out["TQQQ"] = _stitch_primary_proxy(tqqq_chain, _synth_3x_level(out["QQQ"]))

    # TMF <- scaled UBT <- synthetic 3x TLT
    k_ubt = 1.45
    ov = px["TMF"].dropna().index.intersection(px["UBT"].dropna().index)
    if len(ov) >= 6:
        k_ubt = float(np.clip((px["TMF"].loc[ov] / px["UBT"].loc[ov]).median(), 1.35, 1.75))
    tmf_chain = _stitch_primary_proxy(px["TMF"], px["UBT"] * k_ubt)
    out["TMF"] = _stitch_primary_proxy(tmf_chain, _synth_3x_level(px["TLT"]))

    out = out[LOGICAL_COLUMNS].astype(float)
    # Early-list gaps (e.g. EEM first months): propagate first valid
    return out.ffill().bfill()


def trim_from(panel: pd.DataFrame, first_date: str = "2003-01-01") -> pd.DataFrame:
    d = pd.Timestamp(first_date)
    return panel.loc[panel.index >= d].copy()


# --- Native ETF panel (no proxy stitching) ---

NATIVE_STRATEGY_TICKERS = [
    "SPY",
    "QQQ",
    "IWM",
    "EFA",
    "EEM",
    "TLT",
    "GLD",
    "VNQ",
    "AGG",
    "BIL",
    "UPRO",
    "TQQQ",
    "TMF",
]


def build_native_monthly(start: str = "2005-01-01") -> pd.DataFrame:
    """
    Month-end adjusted closes for strategy tickers only. NaNs remain before each
    fund's inception (no back-filled proxies).
    """
    raw = yf.download(
        list(NATIVE_STRATEGY_TICKERS),
        start=start,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    px = _adj_close(raw)
    if isinstance(px, pd.Series):
        px = px.to_frame()
    px = px.dropna(how="all").ffill()
    m = px.resample("ME").last()
    return m[NATIVE_STRATEGY_TICKERS].astype(float)


def first_month_all_native(panel: pd.DataFrame) -> pd.Timestamp:
    """First month-end row where every ticker has a non-null price."""
    valid = panel.dropna(how="any")
    if valid.empty:
        raise ValueError("No overlapping month with all native tickers — check downloads.")
    return valid.index[0]


def native_panel_from_common_start(start_download: str = "2005-01-01") -> tuple[pd.DataFrame, pd.Timestamp]:
    """
    Returns (panel trimmed to first full-coverage month, that first timestamp).
    Column order matches `engine` expectations (subset of LOGICAL_COLUMNS).
    """
    raw = build_native_monthly(start_download)
    first = first_month_all_native(raw)
    out = raw.loc[raw.index >= first].copy()
    return out, first
