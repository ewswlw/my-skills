"""Execute one creative trial (hybrid static + macro tactical + vol multipliers)."""
from __future__ import annotations

from typing import Any

import pandas as pd

from tactical_aa_research.engine import backtest_with_costs, build_weights_flexible, hybrid_static_tactical
from tactical_aa_research.strategy_macro import apply_macro_risk_off, macro_vol_scale


def _dd_vol_multiplier(unlev: pd.Series, *, dd_start: float, floor: float) -> pd.Series:
    eq = (1 + unlev.fillna(0)).cumprod()
    dd = eq / eq.cummax() - 1.0
    mult = pd.Series(1.0, index=unlev.index)
    bad = dd.shift(1) < dd_start
    return mult.where(~bad, other=floor)


def run_creative_trial(
    px: pd.DataFrame,
    mf: pd.DataFrame,
    t: dict[str, Any],
    *,
    cost_bps: float,
) -> pd.Series:
    w_tac = build_weights_flexible(
        px,
        float(t["blend"]),
        mom_abs_c=int(t["mom_abs"]),
        mom_fast_c=int(t["mom_fast"]),
        top_k_c=int(t["top_k"]),
        mom_abs_l=int(t["mom_abs"]),
        mom_fast_l=int(t["mom_fast"]),
        top_k_l=int(t["top_k"]),
    )
    w_tac = apply_macro_risk_off(
        w_tac,
        mf,
        vix_z_thr=float(t["vix_z_thr"]),
        vix_scale=float(t["vix_scale"]),
        nfci_z_thr=float(t["nfci_z_thr"]),
        nfci_scale=float(t["nfci_scale"]),
    )
    w_agg = round(1.0 - float(t["w_eq"]), 6)
    w = hybrid_static_tactical(px, w_tac, float(t["w_eq"]), w_agg, float(t["tact_share"]))

    macro_mult = (
        macro_vol_scale(mf, vix_hi=float(t["vix_hi_scale"]), scale_min=float(t["scale_min"]))
        if t["use_vol_scale"]
        else pd.Series(1.0, index=px.index)
    )

    rets = px.pct_change()
    w_exec = w.shift(1).fillna(0.0)
    unlev = (w_exec * rets).sum(axis=1, min_count=1)
    dd_mult = (
        _dd_vol_multiplier(
            unlev,
            dd_start=float(t.get("dd_start", -0.12)),
            floor=float(t.get("dd_floor", 0.65)),
        )
        if bool(t.get("use_dd_scale", False))
        else pd.Series(1.0, index=px.index)
    )

    if not t["use_vol_scale"] and not bool(t.get("use_dd_scale", False)):
        mult = None
    else:
        mult = macro_mult.astype(float) * dd_mult.astype(float)

    net, _, _, _ = backtest_with_costs(
        w,
        px,
        int(t["vol_lb"]),
        float(t["vol_tgt"]),
        1.0,
        float(t["lev_hi"]),
        cost_bps_per_unit_turnover=cost_bps,
        vol_tgt_multiplier=mult,
    )
    return net
