"""
TAA v3: blend conservative dual-momentum (Calmar>1) with return sleeves;
optional equity drawdown throttle on aggregate exposure.
"""
from __future__ import annotations

import itertools
import warnings
from dataclasses import dataclass

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


def load_monthly(start: str, tickers: list[str]) -> pd.DataFrame:
    raw = yf.download(tickers, start=start, interval="1d", auto_adjust=True, progress=False, threads=True)
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw["Adj Close"].copy() if "Adj Close" in raw.columns.get_level_values(0) else raw["Close"].copy()
    else:
        px = raw
    return px.dropna(how="all").ffill().resample("ME").last()


def max_dd(eq: pd.Series) -> float:
    return float((eq / eq.cummax() - 1).min())


def cagr(eq: pd.Series) -> float:
    eq = eq.dropna()
    y = (eq.index[-1] - eq.index[0]).days / 365.25
    return (float(eq.iloc[-1] / eq.iloc[0])) ** (1 / y) - 1 if y > 0 else float("nan")


def calmar(cg: float, mdd: float) -> float:
    return cg / abs(mdd) if mdd < -1e-12 else float("nan")


def sharpe_ann(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(12)) if len(r) > 24 and r.std() > 0 else float("nan")


def backtest(weights: pd.DataFrame, px: pd.DataFrame) -> pd.Series:
    rets = px.pct_change()
    w = weights.shift(1)
    return (w * rets).sum(axis=1, min_count=1)


def dual_mom(px: pd.DataFrame, risk: list[str], defensive: str, mom_abs: int, mom_fast: int, top_k: int) -> pd.DataFrame:
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


def gem(px: pd.DataFrame, spy_mom: int = 10) -> pd.DataFrame:
    w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    for t in px.index:
        s = float(px["SPY"].loc[t] / px["SPY"].shift(spy_mom).loc[t] - 1.0)
        b = float(px["AGG"].loc[t] / px["AGG"].shift(spy_mom).loc[t] - 1.0)
        if s <= b:
            w.loc[t, "AGG"] = 1.0
            continue
        efa_m = float(px["EFA"].loc[t] / px["EFA"].shift(6).loc[t] - 1.0)
        eem_m = float(px["EEM"].loc[t] / px["EEM"].shift(6).loc[t] - 1.0)
        w.loc[t, "EFA" if efa_m > eem_m else "EEM"] = 1.0
    return w


def vol_target_returns(unlev: pd.Series, lb: int, tgt: float, lo: float, hi: float) -> pd.Series:
    sig = unlev.rolling(lb).std() * np.sqrt(12)
    L = (tgt / sig).clip(lo, hi).shift(1)
    return unlev * L


def apply_dd_throttle_fixed(rets: pd.Series, dd_start: float, scale: float) -> pd.Series:
    eq = (1 + rets.fillna(0)).cumprod()
    peak = eq.cummax()
    dd = eq / peak - 1.0
    mult = pd.Series(1.0, index=rets.index)
    mult.iloc[1:] = np.where(dd.shift(1).iloc[1:].values < dd_start, scale, 1.0)
    return rets * mult


@dataclass
class Hit:
    name: str
    cagr: float
    calmar: float
    mdd: float
    sharpe: float
    detail: str


def main():
    px = load_monthly("2010-01-01", TICKERS).ffill().bfill()
    risk_core = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ"]
    risk_lev = risk_core + ["UPRO", "TQQQ", "TMF"]

    w_cons = dual_mom(px, risk_core, "BIL", 10, 3, 3)
    w_lev = dual_mom(px, risk_lev, "AGG", 10, 2, 3)
    w_gem = gem(px, 10)

    hits: list[Hit] = []

    # blend cons + lev
    for a in np.round(np.linspace(0, 0.45, 46), 3):
        w = (1 - a) * w_cons.fillna(0) + a * w_lev.fillna(0)
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        pr = backtest(w, px)
        eq = (1 + pr.fillna(0)).cumprod()
        cg, md = cagr(eq), max_dd(eq)
        cm = calmar(cg, md)
        if cg > 0.15 and cm > 1.0:
            hits.append(Hit(f"blend_cons_lev a={a}", cg, cm, md, sharpe_ann(pr), ""))

    # blend cons + gem
    for a in np.round(np.linspace(0, 0.5, 51), 3):
        w = (1 - a) * w_cons.fillna(0) + a * w_gem.fillna(0)
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        pr = backtest(w, px)
        eq = (1 + pr.fillna(0)).cumprod()
        cg, md = cagr(eq), max_dd(eq)
        cm = calmar(cg, md)
        if cg > 0.15 and cm > 1.0:
            hits.append(Hit(f"blend_cons_gem a={a}", cg, cm, md, sharpe_ann(pr), ""))

    # triple blend
    for a, b in itertools.product(np.round(np.linspace(0, 0.35, 8), 3), np.round(np.linspace(0, 0.35, 8), 3)):
        if a + b > 0.65:
            continue
        c = 1 - a - b
        w = c * w_cons.fillna(0) + a * w_lev.fillna(0) + b * w_gem.fillna(0)
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        pr = backtest(w, px)
        eq = (1 + pr.fillna(0)).cumprod()
        cg, md = cagr(eq), max_dd(eq)
        cm = calmar(cg, md)
        if cg > 0.15 and cm > 1.0:
            hits.append(Hit(f"triple c={c:.2f} lev={a:.2f} gem={b:.2f}", cg, cm, md, sharpe_ann(pr), ""))

    # vol-target on blended unlev return then check - base: 0.75 cons + 0.25 lev
    for a in [0.15, 0.18, 0.2, 0.22, 0.25, 0.28, 0.3]:
        w = (1 - a) * w_cons.fillna(0) + a * w_lev.fillna(0)
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        pr0 = backtest(w, px)
        for lb, tgt, lo, hi in itertools.product([6, 9, 12], [0.10, 0.11, 0.12, 0.13], [0.6, 0.8, 1.0], [1.5, 2.0, 2.5]):
            pr = vol_target_returns(pr0, lb, tgt, lo, hi)
            eq = (1 + pr.fillna(0)).cumprod()
            cg, md = cagr(eq), max_dd(eq)
            cm = calmar(cg, md)
            if cg > 0.15 and cm > 1.0:
                hits.append(
                    Hit(
                        f"voltgt blend a={a} lb={lb} tgt={tgt} L={lo}-{hi}",
                        cg,
                        cm,
                        md,
                        sharpe_ann(pr),
                        "",
                    )
                )

    # DD throttle on 0.78 cons + 0.22 lev unlev
    for a in [0.18, 0.2, 0.22, 0.24, 0.26]:
        w = (1 - a) * w_cons.fillna(0) + a * w_lev.fillna(0)
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        pr0 = backtest(w, px)
        for dd_s, sc in itertools.product([-0.08, -0.10, -0.12, -0.15], [0.35, 0.5, 0.65, 0.8]):
            pr = apply_dd_throttle_fixed(pr0, dd_s, sc)
            eq = (1 + pr.fillna(0)).cumprod()
            cg, md = cagr(eq), max_dd(eq)
            cm = calmar(cg, md)
            if cg > 0.15 and cm > 1.0:
                hits.append(Hit(f"ddthrottle a={a} dd0={dd_s} sc={sc}", cg, cm, md, sharpe_ann(pr), ""))

    # Slightly more aggressive cons: mom 10,2,4 BIL + small lev
    w_cons2 = dual_mom(px, risk_core, "BIL", 10, 2, 4)
    for a in np.round(np.linspace(0.1, 0.4, 31), 3):
        w = (1 - a) * w_cons2.fillna(0) + a * w_lev.fillna(0)
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
        pr = backtest(w, px)
        eq = (1 + pr.fillna(0)).cumprod()
        cg, md = cagr(eq), max_dd(eq)
        cm = calmar(cg, md)
        if cg > 0.15 and cm > 1.0:
            hits.append(Hit(f"blend_cons2_lev a={a}", cg, cm, md, sharpe_ann(pr), ""))

    hits.sort(key=lambda h: h.calmar * h.cagr, reverse=True)
    print(f"Range {px.index[0].date()} .. {px.index[-1].date()}")
    if hits:
        print(f"\nFound {len(hits)} configurations meeting CAGR>15% and Calmar>1\n")
        for h in hits[:15]:
            print(f"{h.name}  cagr={h.cagr:.2%}  calmar={h.calmar:.2f}  mdd={h.mdd:.2%}  sharpe={h.sharpe:.2f}")
        best = hits[0]
        print("\nBest (by Calmar*CAGR):", best)
    else:
        print("No configuration found in this grid.")
        # report near-miss
        cand = []
        for a in np.round(np.linspace(0, 0.45, 46), 3):
            w = (1 - a) * w_cons.fillna(0) + a * w_lev.fillna(0)
            w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
            pr = backtest(w, px)
            eq = (1 + pr.fillna(0)).cumprod()
            cg, md = cagr(eq), max_dd(eq)
            cand.append((a, cg, calmar(cg, md), md))
        cand.sort(key=lambda x: x[2] * x[1] if not np.isnan(x[2]) else -1, reverse=True)
        print("Top blends cons+lev by calmar*cagr:")
        for row in cand[:8]:
            print(f"  a={row[0]:.2f} cagr={row[1]:.2%} calmar={row[2]:.2f} mdd={row[3]:.2%}")


if __name__ == "__main__":
    main()
