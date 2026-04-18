"""
Macro series for tactical overlays — FRED when `FRED_API_KEY` is set, else Yahoo proxies.

Yahoo proxies (no key): ^VIX, ^TNX (10Y yield %), ^IRX (13-week discount %).
All resampled to month-end and **shifted** so row t uses only information through t.
"""
from __future__ import annotations

import os
import warnings
from io import StringIO

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)

# FRED series used when API key present (monthly or daily — we aggregate to ME)
FRED_SERIES = {
    "VIX": "VIXCLS",  # daily
    "T10Y2Y": "T10Y2Y",  # daily term spread
    "NFCI": "NFCI",  # weekly Chicago Fed NFCI (NaNs on non-update days)
    "UNRATE": "UNRATE",  # monthly
}


def _yf_macro_monthly(start: str) -> pd.DataFrame:
    tickers = ["^VIX", "^TNX", "^IRX"]
    raw = yf.download(tickers, start=start, interval="1d", auto_adjust=True, progress=False, threads=True)
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw["Close"].copy() if "Adj Close" not in raw.columns.get_level_values(0) else raw["Adj Close"].copy()
    else:
        px = raw
    px = px.dropna(how="all").ffill()
    m = px.resample("ME").last()
    m = m.rename(columns={"^VIX": "VIX", "^TNX": "TNX10Y", "^IRX": "IRX3M"})
    m["TERM_SPREAD_YF"] = m["TNX10Y"] - m["IRX3M"]
    return m


def _fred_csv(series_id: str, api_key: str, start: str) -> pd.DataFrame:
    import urllib.parse
    import urllib.request

    q = urllib.parse.urlencode(
        {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "csv",
            "observation_start": start,
        }
    )
    url = f"https://api.stlouisfed.org/fred/series/observations?{q}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        text = resp.read().decode("utf-8")
    df = pd.read_csv(StringIO(text), parse_dates=["observation_date"])
    df = df.rename(columns={"observation_date": "date", "value": series_id})
    df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
    df = df.set_index("date").sort_index()
    return df[[series_id]]


def load_macro_monthly(start: str = "2005-01-01") -> pd.DataFrame:
    key = os.environ.get("FRED_API_KEY", "").strip()
    yf_m = _yf_macro_monthly(start)
    if not key:
        out = yf_m.copy()
        out["T10Y2Y"] = out["TERM_SPREAD_YF"]
        return out

    # Merge FRED where available
    fred_parts = []
    for name, sid in FRED_SERIES.items():
        try:
            fred_parts.append(_fred_csv(sid, key, start))
        except Exception:
            continue
    if not fred_parts:
        out = yf_m.copy()
        out["T10Y2Y"] = out["TERM_SPREAD_YF"]
        return out

    fred = pd.concat(fred_parts, axis=1).sort_index()
    fred_m = fred.resample("ME").last().ffill()
    out = yf_m.join(fred_m, how="outer").sort_index().ffill()
    if "T10Y2Y" not in out.columns or out["T10Y2Y"].isna().all():
        out["T10Y2Y"] = out["TERM_SPREAD_YF"]
    return out


def macro_features(macro: pd.DataFrame) -> pd.DataFrame:
    """Point-in-time month-end features (no future rows)."""
    x = macro.copy()
    v = x["VIX"].astype(float)
    x["vix_z_12"] = (v - v.rolling(12).mean()) / v.rolling(12).std()
    x["vix_chg_3m"] = v / v.shift(3) - 1.0
    ts = x["T10Y2Y"].astype(float)
    x["ts_z_12"] = (ts - ts.rolling(12).mean()) / ts.rolling(12).std()
    if "NFCI" in x.columns:
        nf = x["NFCI"].astype(float)
        x["nfci_z_12"] = (nf - nf.rolling(12).mean()) / nf.rolling(12).std()
    else:
        x["nfci_z_12"] = 0.0
    return x
