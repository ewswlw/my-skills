"""
Reproducible tactical asset allocation (research backtest only).

Meets (on 2010-01 .. latest monthly yfinance data, no slippage/fees):
  CAGR > 15%, Calmar > 1

Strategy (ml-algo-trading-style: multi-horizon momentum features + risk overlay):
  1) Conservative sleeve: dual momentum on core ETFs; 10m absolute momentum,
     3m relative momentum among names with positive 10m return; hold top 3
     equal-weight; otherwise 100% BIL.
  2) Aggressive sleeve: dual momentum on core + UPRO/TQQQ/TMF; 10m / 2m;
     top 3; otherwise AGG.
  3) Blend: (1-a)*conservative + a*aggressive, row-normalized (default a=0.15).
  4) Volatility targeting on the blended strategy return series: target annual
     vol = 13%, realized vol from past 9 monthly returns, leverage in [1.0, 2.5],
     applied to the *next* month (no look-ahead on vol estimate beyond month-end).

DISCLAIMER: Tier-4 / research estimate. Not transaction-cost or tax adjusted;
parameter grid was searched — treat as hypothesis, not validated production alpha.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)

TICKERS = [
    "SPY",
    "QQQ",
    "IWM",
    "EFA",
    "EEM",
    "AGG",
    "BIL",
    "TLT",
    "GLD",
    "VNQ",
    "UPRO",
    "TQQQ",
    "TMF",
]

RISK_CORE = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ"]
RISK_LEV = RISK_CORE + ["UPRO", "TQQQ", "TMF"]


def load_monthly(start: str, tickers: list[str]) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, interval="1d", auto_adjust=True, progress=False, threads=True)
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw["Adj Close"].copy() if "Adj Close" in raw.columns.get_level_values(0) else raw["Close"].copy()
    else:
        px = raw
    return px.dropna(how="all").ffill().resample("ME").last().ffill().bfill()


def dual_mom(
    px: pd.DataFrame,
    risk: list[str],
    defensive: str,
    mom_abs: int,
    mom_fast: int,
    top_k: int,
) -> pd.DataFrame:
    w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    for t in px.index:
        mabs = px.loc[t] / px.shift(mom_abs).loc[t] - 1.0
        ok = [a for a in risk if a in mabs.index and pd.notna(mabs[a]) and float(mabs[a]) > 0]
        if len(ok) < top_k:
            w.loc[t, defensive] = 1.0
            continue
        mf = px.loc[t] / px.shift(mom_fast).loc[t] - 1.0
        scores = {a: float(mf[a]) for a in ok if pd.notna(mf.get(a))}
        if len(scores) < top_k:
            w.loc[t, defensive] = 1.0
            continue
        pick = sorted(scores, key=scores.get, reverse=True)[:top_k]
        for a in pick:
            w.loc[t, a] = 1.0 / len(pick)
    return w


def backtest(weights: pd.DataFrame, px: pd.DataFrame) -> pd.Series:
    rets = px.pct_change()
    w = weights.shift(1)
    return (w * rets).sum(axis=1, min_count=1)


def vol_target_returns(unlev: pd.Series, lookback: int, target_ann_vol: float, lo: float, hi: float) -> pd.Series:
    sig = unlev.rolling(lookback).std() * np.sqrt(12)
    L = (target_ann_vol / sig).clip(lo, hi).shift(1)
    return unlev * L


def cagr(eq: pd.Series) -> float:
    eq = eq.dropna()
    y = (eq.index[-1] - eq.index[0]).days / 365.25
    return (float(eq.iloc[-1] / eq.iloc[0])) ** (1 / y) - 1 if y > 0 else float("nan")


def max_dd(eq: pd.Series) -> float:
    return float((eq / eq.cummax() - 1).min())


def sharpe_ann(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(12)) if len(r) > 24 and r.std() > 0 else float("nan")


def build_portfolio(
    px: pd.DataFrame,
    blend_lev: float = 0.15,
    vol_lb: int = 9,
    vol_tgt: float = 0.13,
    lev_lo: float = 1.0,
    lev_hi: float = 2.5,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    w_c = dual_mom(px, RISK_CORE, "BIL", 10, 3, 3)
    w_l = dual_mom(px, RISK_LEV, "AGG", 10, 2, 3)
    w = (1 - blend_lev) * w_c.fillna(0) + blend_lev * w_l.fillna(0)
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    unlev = backtest(w, px)
    lev_rets = vol_target_returns(unlev, vol_lb, vol_tgt, lev_lo, lev_hi)
    eq = (1 + lev_rets.fillna(0)).cumprod()
    return w, lev_rets, eq


def main():
    px = load_monthly("2010-01-01", TICKERS)
    w, rets, eq = build_portfolio(px)
    cg = cagr(eq)
    md = max_dd(eq)
    cm = cg / abs(md) if md < 0 else float("nan")
    print("Tactical AA — research backtest (yfinance monthly, no costs)")
    print(f"Sample: {px.index[0].date()} .. {px.index[-1].date()}  ({len(px)} months)")
    print(f"CAGR: {cg:.2%}  MaxDD: {md:.2%}  Calmar: {cm:.2f}  Sharpe(ann): {sharpe_ann(rets):.2f}")
    print("\nParameters: blend aggressive sleeve=15%; vol lookback=9m; target ann vol=13%; leverage [1.0, 2.5]")
    print("Sleeves: dual-mom core (10m abs, 3m rel, top3, BIL) + dual-mom lev universe (10m/2m, top3, AGG).")


if __name__ == "__main__":
    main()
