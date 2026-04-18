"""
Pre-registered **creative** trial family — **n_trials = 32** (stronger DSR / Bonferroni).

Hybrid SPY/AGG core + tactical dual-momentum + macro risk-off + optional
macro vol scale and/or drawdown-based vol de-risking on the *unlevered* sleeve.
"""
from __future__ import annotations

import itertools
from typing import Any

CREATIVE_PARAM_KEYS = (
    "family",
    "blend",
    "tact_share",
    "w_eq",
    "mom_abs",
    "mom_fast",
    "top_k",
    "vol_lb",
    "vol_tgt",
    "lev_hi",
    "vix_z_thr",
    "vix_scale",
    "nfci_z_thr",
    "nfci_scale",
    "use_vol_scale",
    "use_dd_scale",
    "dd_start",
    "dd_floor",
    "vix_hi_scale",
    "scale_min",
)


def generate_creative_trials() -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    for tact_share, w_eq, blend, mode in itertools.product(
        [0.48, 0.58],
        [0.78, 0.86],
        [0.07, 0.13],
        [0, 1, 2, 3],
    ):
        use_vs = mode in (1, 3)
        use_dd = mode in (2, 3)
        trials.append(
            dict(
                family="hybrid_macro_dd",
                blend=float(blend),
                tact_share=float(tact_share),
                w_eq=float(w_eq),
                mom_abs=10,
                mom_fast=3,
                top_k=3,
                vol_lb=9,
                vol_tgt=0.09,
                lev_hi=2.5,
                vix_z_thr=0.85,
                vix_scale=0.16,
                nfci_z_thr=0.9,
                nfci_scale=0.16,
                use_vol_scale=use_vs,
                use_dd_scale=use_dd,
                dd_start=-0.075,
                dd_floor=0.58,
                vix_hi_scale=1.0,
                scale_min=0.70,
            )
        )
    assert len(trials) == 32, len(trials)
    return trials
