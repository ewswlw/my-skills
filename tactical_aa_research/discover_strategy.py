"""
Discover strategy parameters using **only** pre-holdout data (never touches holdout).

Random search + purged CV score; writes `locked_strategy.json` with:
  - params dict for `run_creative_trial`
  - n_trials_search: number of random draws (for DSR multiplicity)

Run:
  python3 tactical_aa_research/discover_strategy.py
Then:
  python3 tactical_aa_research/validation_locked.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.creative_runner import run_creative_trial
from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.purged_cv import purged_time_series_folds
from tactical_aa_research.validation_config import HOLDOUT_START

LOCK_PATH = Path(__file__).resolve().parent / "locked_strategy.json"
# Pre-registered search budget — **DSR/Bonferroni in `validation_locked.py` use this exact count**.
# Larger N is more honest about data-mining but **lowers DSR** for the same holdout Sharpe.
N_SEARCH = 2500
SEED = 12345


def prep_macro(px: pd.DataFrame) -> pd.DataFrame:
    m = load_macro_monthly("2005-01-01")
    return macro_features(m).shift(1).reindex(px.index)


def train_score(net: pd.Series) -> float:
    """Emphasize **Calmar** (drawdown control) while keeping CAGR in the mix."""
    x = net.dropna().astype(float)
    if len(x) < 24:
        return float("-inf")
    eq = (1 + x).cumprod()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    if years <= 0:
        return float("-inf")
    cg = (float(eq.iloc[-1] / eq.iloc[0])) ** (1 / years) - 1
    dd = float((eq / eq.cummax() - 1).min())
    cm = cg / abs(dd) if dd < -1e-9 else 0.0
    # Upweight Calmar tail; soft floor on CAGR to avoid trivial cash-only wins
    return float((max(cm, 0.01) ** 1.35) * max(cg, 0.02))


def random_trial(rng: random.Random) -> dict:
    mode = rng.randint(0, 3)
    return dict(
        family="discovered",
        blend=rng.choice([0.05, 0.08, 0.11, 0.14, 0.18, 0.22]),
        tact_share=rng.uniform(0.42, 0.78),
        w_eq=rng.uniform(0.62, 0.90),
        mom_abs=rng.choice([8, 10, 12]),
        mom_fast=rng.choice([2, 3]),
        top_k=rng.choice([2, 3]),
        vol_lb=rng.choice([6, 9, 12]),
        vol_tgt=rng.uniform(0.075, 0.155),
        lev_hi=rng.uniform(2.4, 4.5),
        vix_z_thr=rng.uniform(0.45, 1.15),
        vix_scale=rng.uniform(0.08, 0.30),
        nfci_z_thr=rng.uniform(0.55, 1.35),
        nfci_scale=0.17,
        use_vol_scale=mode in (1, 3),
        use_dd_scale=mode in (2, 3),
        dd_start=rng.uniform(-0.11, -0.045),
        dd_floor=rng.uniform(0.48, 0.78),
        vix_hi_scale=rng.uniform(0.82, 1.18),
        scale_min=rng.uniform(0.62, 0.82),
    )


def main():
    px, _ = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    pre = px.loc[px.index < HOLDOUT_START].copy()
    mf_pre = mf.loc[pre.index]

    folds = list(purged_time_series_folds(len(pre), n_splits=4, purge_gap=6, embargo=1, min_train=36))
    rng = random.Random(SEED)

    best_t = None
    best_sc = float("-inf")
    for _ in range(N_SEARCH):
        t = random_trial(rng)
        net_full = run_creative_trial(pre, mf_pre, t, cost_bps=10.0)
        scores = []
        for fd in folds:
            tr = net_full.iloc[fd.train_start : fd.train_end]
            scores.append(train_score(tr))
        sc = float(np.mean([s for s in scores if np.isfinite(s)])) if scores else float("-inf")
        if sc > best_sc:
            best_sc = sc
            best_t = t

    payload = {
        "n_trials_search": N_SEARCH,
        "seed": SEED,
        "cv_mean_train_score": best_sc,
        "params": best_t,
    }
    LOCK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Wrote", LOCK_PATH)
    print("Best CV mean train score:", best_sc)
    print(json.dumps(best_t, indent=2))


if __name__ == "__main__":
    main()
