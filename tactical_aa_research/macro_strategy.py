"""Shared macro strategy grid + execution (used by iterate_macro and validation_rigorous)."""
from __future__ import annotations

import itertools
from typing import Any

import pandas as pd

from tactical_aa_research.engine import backtest_with_costs, build_weights
from tactical_aa_research.strategy_macro import apply_macro_risk_off, macro_vol_scale

PARAM_KEYS = (
    "blend",
    "vol_lb",
    "vol_tgt",
    "lev_hi",
    "vix_z_thr",
    "vix_scale",
    "nfci_z_thr",
    "nfci_scale",
    "use_vol_scale",
    "vix_hi_scale",
    "scale_min",
)

COST_BPS_DEFAULT = 10.0


def generate_trials() -> list[dict[str, Any]]:
    trials = []
    for blend, vol_lb, vol_tgt, lev_hi in itertools.product(
        [0.10, 0.16, 0.22, 0.28],
        [9, 12],
        [0.11, 0.13],
        [3.0, 3.5, 4.0],
    ):
        for vix_thr, vix_sc, nf_thr, use_vs, vix_hi in itertools.product(
            [0.5, 1.0],
            [0.18, 0.26],
            [0.75, 1.25],
            [False, True],
            [0.9, 1.15],
        ):
            trials.append(
                dict(
                    blend=float(blend),
                    vol_lb=int(vol_lb),
                    vol_tgt=float(vol_tgt),
                    lev_hi=float(lev_hi),
                    vix_z_thr=float(vix_thr),
                    vix_scale=float(vix_sc),
                    nfci_z_thr=float(nf_thr),
                    nfci_scale=0.20,
                    use_vol_scale=bool(use_vs),
                    vix_hi_scale=float(vix_hi),
                    scale_min=0.65,
                )
            )
    return trials


def build_blend_cache(px: pd.DataFrame, trials: list[dict]) -> dict[float, pd.DataFrame]:
    return {float(b): build_weights(px, float(b)) for b in sorted({t["blend"] for t in trials})}


def run_macro_strategy(
    px: pd.DataFrame,
    mf: pd.DataFrame,
    w0: pd.DataFrame,
    t: dict,
    *,
    cost_bps: float = COST_BPS_DEFAULT,
) -> pd.Series:
    w1 = apply_macro_risk_off(
        w0,
        mf,
        vix_z_thr=t["vix_z_thr"],
        vix_scale=t["vix_scale"],
        nfci_z_thr=t["nfci_z_thr"],
        nfci_scale=t["nfci_scale"],
    )
    mult = macro_vol_scale(mf, vix_hi=t["vix_hi_scale"], scale_min=t["scale_min"]) if t["use_vol_scale"] else None
    net, _, _, _ = backtest_with_costs(
        w1,
        px,
        t["vol_lb"],
        t["vol_tgt"],
        1.0,
        t["lev_hi"],
        cost_bps_per_unit_turnover=cost_bps,
        vol_tgt_multiplier=mult,
    )
    return net
