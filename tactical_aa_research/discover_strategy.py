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

import argparse
import json
import random
import sys
from datetime import datetime, timezone
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
COST_BPS = 10.0
MIN_CAGR_GATE = 0.13
MIN_CALMAR_GATE = 1.0
DSR_MIN_GATE = 0.95
ALPHA_FAMILY = 0.05
LOCK_VERSION = "2.0"
PORTFOLIO_LEVERAGE_ALLOWED = False
PORTFOLIO_LEVERAGE_CAP = 1.0


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


def random_trial(rng: random.Random, *, portfolio_leverage_allowed: bool) -> dict:
    mode = rng.randint(0, 3)
    if portfolio_leverage_allowed:
        top_k_choices = [2, 3]
        blend_choices = [0.05, 0.08, 0.11, 0.14, 0.18, 0.22]
        lev_hi = rng.uniform(2.4, 4.5)
    else:
        # No portfolio-level leverage: broaden unlevered allocation-space dimensions.
        top_k_choices = [1, 2, 3, 4]
        blend_choices = [0.0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24]
        lev_hi = 1.0
    return dict(
        family="discovered",
        blend=rng.choice(blend_choices),
        tact_share=rng.uniform(0.30, 0.86),
        w_eq=rng.uniform(0.55, 0.98),
        mom_abs=rng.choice([6, 8, 10, 12]),
        mom_fast=rng.choice([1, 2, 3, 4]),
        top_k=rng.choice(top_k_choices),
        vol_lb=rng.choice([6, 9, 12]),
        vol_tgt=rng.uniform(0.08, 0.22),
        lev_hi=lev_hi,
        vix_z_thr=rng.uniform(0.35, 1.40),
        vix_scale=rng.uniform(0.00, 0.35),
        nfci_z_thr=rng.uniform(0.35, 1.50),
        nfci_scale=rng.uniform(0.00, 0.25),
        use_vol_scale=mode in (1, 3),
        use_dd_scale=mode in (2, 3),
        dd_start=rng.uniform(-0.18, -0.03),
        dd_floor=rng.uniform(0.35, 0.95),
        vix_hi_scale=rng.uniform(0.75, 1.25),
        scale_min=rng.uniform(0.45, 0.95),
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Pre-holdout discovery search for tactical AA lock file.")
    ap.add_argument("--n-search", type=int, default=N_SEARCH, help="Number of random trials (n_trials_search).")
    ap.add_argument("--seed", type=int, default=SEED, help="RNG seed for random trial generation.")
    ap.add_argument("--cost-bps", type=float, default=COST_BPS, help="Turnover cost in bps per unit |Δ(L·w)|.")
    ap.add_argument("--min-cagr-gate", type=float, default=MIN_CAGR_GATE, help="Downstream holdout CAGR gate.")
    ap.add_argument("--min-calmar-gate", type=float, default=MIN_CALMAR_GATE, help="Downstream holdout Calmar gate.")
    ap.add_argument("--dsr-min-gate", type=float, default=DSR_MIN_GATE, help="Downstream holdout DSR gate.")
    ap.add_argument("--alpha-family", type=float, default=ALPHA_FAMILY, help="Family-wise alpha for Bonferroni gate.")
    ap.add_argument(
        "--allow-portfolio-leverage",
        action="store_true",
        default=PORTFOLIO_LEVERAGE_ALLOWED,
        help="Enable portfolio-level leverage scaling in backtest engine.",
    )
    ap.add_argument(
        "--portfolio-leverage-cap",
        type=float,
        default=PORTFOLIO_LEVERAGE_CAP,
        help="Maximum allowed portfolio leverage when leverage is enabled.",
    )
    ap.add_argument(
        "--lock-path",
        type=Path,
        default=LOCK_PATH,
        help="Output lock JSON path (default: tactical_aa_research/locked_strategy.json).",
    )
    ap.add_argument(
        "--note",
        type=str,
        default="pre-holdout random search; holdout untouched",
        help="Free-form note embedded in lock metadata.",
    )
    return ap.parse_args()


def main():
    args = parse_args()
    n_search = int(max(args.n_search, 1))
    leverage_allowed = bool(args.allow_portfolio_leverage)
    leverage_cap = float(args.portfolio_leverage_cap)

    px, _ = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    pre = px.loc[px.index < HOLDOUT_START].copy()
    mf_pre = mf.loc[pre.index]

    folds = list(purged_time_series_folds(len(pre), n_splits=4, purge_gap=6, embargo=1, min_train=36))
    rng = random.Random(int(args.seed))

    best_t = None
    best_sc = float("-inf")
    for _ in range(n_search):
        t = random_trial(rng, portfolio_leverage_allowed=leverage_allowed)
        net_full = run_creative_trial(
            pre,
            mf_pre,
            t,
            cost_bps=float(args.cost_bps),
            portfolio_leverage_allowed=leverage_allowed,
            portfolio_leverage_cap=leverage_cap,
        )
        scores = []
        for fd in folds:
            tr = net_full.iloc[fd.train_start : fd.train_end]
            scores.append(train_score(tr))
        sc = float(np.mean([s for s in scores if np.isfinite(s)])) if scores else float("-inf")
        if sc > best_sc:
            best_sc = sc
            best_t = t

    payload = {
        "lock_version": LOCK_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "workflow": "discover_strategy.py",
        "n_trials_search": n_search,
        "seed": int(args.seed),
        "cost_bps": float(args.cost_bps),
        "portfolio_leverage_allowed": leverage_allowed,
        "portfolio_leverage_cap": leverage_cap,
        "alpha_family": float(args.alpha_family),
        "min_cagr_gate": float(args.min_cagr_gate),
        "min_calmar_gate": float(args.min_calmar_gate),
        "dsr_min_gate": float(args.dsr_min_gate),
        "holdout_start": str(HOLDOUT_START.date()),
        "search_universe": {
            "pre_start": str(pre.index[0].date()),
            "pre_end": str(pre.index[-1].date()),
            "n_months_pre": int(len(pre)),
        },
        "cv_spec": {"n_splits": 4, "purge_gap": 6, "embargo": 1, "min_train": 36},
        "selection_objective": "mean_fold_train_score where fold score=(max(Calmar,0.01)^1.35)*max(CAGR,0.02)",
        "cv_mean_train_score": best_sc,
        "note": str(args.note),
        "params": best_t,
    }
    args.lock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Wrote", args.lock_path)
    print("Best CV mean train score:", best_sc)
    print(json.dumps(best_t, indent=2))


if __name__ == "__main__":
    main()
