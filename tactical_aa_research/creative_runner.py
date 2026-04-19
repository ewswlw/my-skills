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


def _breadth_risk_scale(
    breadth: pd.Series,
    *,
    breadth_thr: float,
    breadth_floor: float,
) -> pd.Series:
    thr = float(max(breadth_thr, 1e-6))
    floor = float(min(max(breadth_floor, 0.0), 1.0))
    lin = floor + (breadth / thr) * (1.0 - floor)
    scale = lin.where(breadth < thr, other=1.0)
    return scale.clip(lower=floor, upper=1.0).fillna(1.0)


def _breadth_fraction(
    px: pd.DataFrame,
    *,
    mom_abs: int,
    breadth_columns: tuple[str, ...],
) -> pd.Series:
    cols = [c for c in breadth_columns if c in px.columns]
    if not cols:
        return pd.Series(1.0, index=px.index, dtype=float)
    mom = px[cols].div(px[cols].shift(max(int(mom_abs), 1))) - 1.0
    return mom.gt(0).mean(axis=1).fillna(0.0)


def _apply_no_leverage_risk_scale(
    w: pd.DataFrame,
    risk_scale: pd.Series,
    *,
    agg_share: float = 0.70,
) -> pd.DataFrame:
    """
    Apply a risk-scaling multiplier without portfolio leverage by shrinking
    non-defensive exposures and reallocating trimmed mass to AGG/BIL.
    """
    out = w.copy()
    scale = risk_scale.reindex(out.index).astype(float).fillna(1.0).clip(lower=0.0, upper=1.0)
    defensive = [c for c in ("AGG", "BIL", "CASH") if c in out.columns]
    for t in out.index:
        s = float(scale.loc[t])
        if s >= 0.999:
            continue
        row = out.loc[t].copy()
        risky_cols = [c for c in out.columns if c not in defensive and float(row.get(c, 0.0)) > 0.0]
        if not risky_cols:
            continue
        risky_mass_before = float(row[risky_cols].sum())
        row.loc[risky_cols] = row.loc[risky_cols] * s
        trimmed = risky_mass_before - float(row[risky_cols].sum())
        if trimmed > 0:
            if "AGG" in out.columns:
                row.loc["AGG"] = float(row.get("AGG", 0.0)) + trimmed * agg_share
            if "BIL" in out.columns:
                row.loc["BIL"] = float(row.get("BIL", 0.0)) + trimmed * (1.0 - agg_share)
            if "AGG" not in out.columns and "BIL" not in out.columns and "CASH" in out.columns:
                row.loc["CASH"] = float(row.get("CASH", 0.0)) + trimmed
        srow = float(row.sum())
        if srow > 0:
            row = row / srow
        out.loc[t] = row
    return out


def _apply_regime_defensive_override(
    w: pd.DataFrame,
    *,
    trigger: pd.Series,
    agg_share: float,
    tmf_share: float,
) -> pd.DataFrame:
    out = w.copy()
    trig = trigger.reindex(out.index).fillna(False).astype(bool)
    agg = float(min(max(agg_share, 0.0), 1.0))
    tmf = float(min(max(tmf_share, 0.0), 1.0))
    bil = max(0.0, 1.0 - agg - tmf)
    target: dict[str, float] = {}
    if "AGG" in out.columns:
        target["AGG"] = agg
    if "TMF" in out.columns:
        target["TMF"] = tmf
    if "BIL" in out.columns:
        target["BIL"] = bil
    elif "CASH" in out.columns:
        target["CASH"] = bil
    for t in out.index[trig]:
        row = pd.Series(0.0, index=out.columns, dtype=float)
        active = {k: v for k, v in target.items() if v > 0.0}
        if not active:
            continue
        s = float(sum(active.values()))
        for k, v in active.items():
            row.loc[k] = float(v / s)
        out.loc[t] = row
    return out


def run_creative_trial(
    px: pd.DataFrame,
    mf: pd.DataFrame,
    t: dict[str, Any],
    *,
    cost_bps: float,
    portfolio_leverage_allowed: bool = True,
    portfolio_leverage_cap: float | None = None,
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
    if bool(t.get("use_breadth_gate", False)):
        breadth_frac = _breadth_fraction(
            px,
            mom_abs=int(t.get("breadth_mom_abs", t["mom_abs"])),
            breadth_columns=(
                "SPY",
                "QQQ",
                "IWM",
                "EFA",
                "EEM",
                "VNQ",
                "UPRO",
                "TQQQ",
                "TMF",
            ),
        )
        breadth_mult = _breadth_risk_scale(
            breadth_frac,
            breadth_thr=float(t.get("breadth_thr", 0.55)),
            breadth_floor=float(t.get("breadth_floor", 0.60)),
        )
    else:
        breadth_frac = pd.Series(1.0, index=px.index)
        breadth_mult = pd.Series(1.0, index=px.index)

    if not t["use_vol_scale"] and not bool(t.get("use_dd_scale", False)) and not bool(t.get("use_breadth_gate", False)):
        mult = None
    else:
        mult = macro_mult.astype(float) * dd_mult.astype(float) * breadth_mult.astype(float)

    if bool(t.get("use_regime_override", False)):
        breadth_thr = float(t.get("regime_breadth_thr", 0.65))
        breadth_sig = breadth_frac.reindex(w.index).fillna(1.0)
        breadth_bad = breadth_sig <= max(min(breadth_thr, 1.0), 1e-6)
        vix_z = mf.get("vix_z_12", pd.Series(0.0, index=w.index)).reindex(w.index).fillna(0.0)
        nfci_z = mf.get("nfci_z_12", pd.Series(0.0, index=w.index)).reindex(w.index).fillna(0.0)
        use_vix = bool(t.get("regime_use_vix", True))
        use_nfci = bool(t.get("regime_use_nfci", True))
        regime_trig = breadth_bad if breadth_thr > 0 else pd.Series(False, index=w.index)
        if use_vix:
            regime_trig = regime_trig | (vix_z >= float(t.get("regime_vix_z_thr", 1.2)))
        if use_nfci:
            regime_trig = regime_trig | (nfci_z >= float(t.get("regime_nfci_z_thr", 1.1)))
        w = _apply_regime_defensive_override(
            w,
            trigger=regime_trig.astype(bool),
            agg_share=float(t.get("regime_agg_share", 0.65)),
            tmf_share=float(t.get("regime_tmf_share", 0.20)),
        )

    if not portfolio_leverage_allowed and mult is not None:
        w = _apply_no_leverage_risk_scale(w, mult)
        mult = None

    net, _, _, _ = backtest_with_costs(
        w,
        px,
        int(t["vol_lb"]),
        float(t["vol_tgt"]),
        1.0,
        float(t["lev_hi"]),
        cost_bps_per_unit_turnover=cost_bps,
        vol_tgt_multiplier=mult,
        portfolio_leverage_allowed=portfolio_leverage_allowed,
        portfolio_leverage_cap=portfolio_leverage_cap,
    )
    return net
