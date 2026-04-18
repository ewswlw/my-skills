"""Dual-momentum tactical AA + vol targeting + transaction cost drag."""
from __future__ import annotations

import numpy as np
import pandas as pd

RISK_CORE = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ"]
RISK_LEV = RISK_CORE + ["UPRO", "TQQQ", "TMF"]


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


def hybrid_static_tactical(
    px: pd.DataFrame,
    tac_w: pd.DataFrame,
    w_eq: float,
    w_agg: float,
    tact_share: float,
) -> pd.DataFrame:
    """(1-tact_share)*(w_eq*SPY + w_agg*AGG) + tact_share*tactical_weights; row-normalized."""
    static = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    if "SPY" in static.columns:
        static["SPY"] = w_eq
    if "AGG" in static.columns:
        static["AGG"] = w_agg
    s = static.sum(axis=1).replace(0, np.nan)
    static = static.div(s, axis=0).fillna(0)
    out = (1.0 - tact_share) * static + tact_share * tac_w.reindex(px.index).fillna(0)
    return out.div(out.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)


def vol_target_leverage(
    unlev_ret: pd.Series,
    lookback: int,
    target_ann_vol: float,
    lo: float,
    hi: float,
    target_multiplier: pd.Series | None = None,
) -> pd.Series:
    sig = unlev_ret.rolling(lookback).std() * np.sqrt(12)
    tgt = float(target_ann_vol)
    if target_multiplier is not None:
        m = target_multiplier.reindex(unlev_ret.index).astype(float).fillna(1.0)
        eff = tgt * m
    else:
        eff = pd.Series(tgt, index=unlev_ret.index)
    return (eff / sig).clip(lo, hi).shift(1)


def backtest_with_costs(
    weights: pd.DataFrame,
    px: pd.DataFrame,
    vol_lb: int,
    vol_tgt: float,
    lev_lo: float,
    lev_hi: float,
    cost_bps_per_unit_turnover: float = 10.0,
    vol_tgt_multiplier: pd.Series | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Signal at month-end t in `weights[t]`; execution for month t+1 return:
    w_exec[t+1] = weights[t]. Leverage L[t+1] from vol of unlevered series through t.

    Returns: net_ret, gross_ret, L, turnover (fraction of NAV; L1 change in L*w_exec).
    """
    rets = px.pct_change()
    w_exec = weights.shift(1).fillna(0.0)

    unlev = (w_exec * rets).sum(axis=1, min_count=1)
    L = vol_target_leverage(unlev, vol_lb, vol_tgt, lev_lo, lev_hi, vol_tgt_multiplier)

    gross = unlev * L

    pos = w_exec.mul(L, axis=0)
    turn = pos.diff().abs().sum(axis=1)
    turn.iloc[0] = pos.iloc[0].abs().sum()

    cost = (cost_bps_per_unit_turnover / 10000.0) * turn
    net = gross - cost
    return net, gross, L, turn


def cagr(eq: pd.Series) -> float:
    eq = eq.dropna()
    if len(eq) < 2:
        return float("nan")
    y = (eq.index[-1] - eq.index[0]).days / 365.25
    return (float(eq.iloc[-1] / eq.iloc[0])) ** (1 / y) - 1 if y > 0 else float("nan")


def max_dd(eq: pd.Series) -> float:
    return float((eq / eq.cummax() - 1).min())


def calmar(cg: float, mdd: float) -> float:
    return cg / abs(mdd) if mdd < -1e-12 else float("nan")


def sharpe_ann(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(12)) if len(r) > 24 and r.std() > 0 else float("nan")


def build_weights(px: pd.DataFrame, blend_lev: float) -> pd.DataFrame:
    return build_weights_flexible(
        px,
        blend_lev,
        mom_abs_c=10,
        mom_fast_c=3,
        top_k_c=3,
        mom_abs_l=10,
        mom_fast_l=2,
        top_k_l=3,
    )


def build_weights_flexible(
    px: pd.DataFrame,
    blend_lev: float,
    *,
    mom_abs_c: int,
    mom_fast_c: int,
    top_k_c: int,
    mom_abs_l: int,
    mom_fast_l: int,
    top_k_l: int,
) -> pd.DataFrame:
    w_c = dual_mom(px, RISK_CORE, "CASH", mom_abs_c, mom_fast_c, top_k_c)
    w_l = dual_mom(px, RISK_LEV, "AGG", mom_abs_l, mom_fast_l, top_k_l)
    w = (1 - blend_lev) * w_c.fillna(0) + blend_lev * w_l.fillna(0)
    return w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
