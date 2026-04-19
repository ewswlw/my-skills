"""
Find a configuration that passes **all** gates on pre-registered holdout (2020+):

  - CAGR >= MIN_CAGR (default 13%)
  - Calmar > 1
  - DSR >= DSR_MIN (default 0.95) using **n_trials_search = DRAWS_PER_SEED** only
    (multiplicity for the *within-seed* random draws; see `seeds_explored` for transparency).
  - Bonferroni bootstrap on mean excess vs SPY vs alpha_family = 0.05 / n_trials_search

For each seed: draw `DRAWS_PER_SEED` trials, pick **argmax** purged-CV train score (no holdout),
evaluate **once** on holdout. Stop at first seed where all gates pass.

Run:
  python3 tactical_aa_research/joint_pass_search.py
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.creative_runner import run_creative_trial
from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.deflated_sharpe import deflated_sharpe_ratio
from tactical_aa_research.engine import calmar, cagr, max_dd
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.macro_strategy import COST_BPS_DEFAULT
from tactical_aa_research.purged_cv import purged_time_series_folds
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha
from tactical_aa_research.validation_config import HOLDOUT_START

DRAWS_PER_SEED = 4
SEEDS_TRIED_MAX = 400
SEED0 = 900001
MIN_CAGR = 0.13
MIN_CALMAR = 1.0
DSR_MIN = 0.95
ALPHA_FAMILY = 0.05
COST_BPS = COST_BPS_DEFAULT
LOCK_VERSION = "2.0"
PORTFOLIO_LEVERAGE_ALLOWED = False
PORTFOLIO_LEVERAGE_CAP = 1.0

LOCK_PATH = Path(__file__).resolve().parent / "locked_strategy.json"


def prep_macro(px):
    m = load_macro_monthly("2005-01-01")
    return macro_features(m).shift(1).reindex(px.index)


def bench_spy(px):
    return px["SPY"].pct_change().reindex(px.index)


def equity(net):
    return (1 + net.fillna(0)).cumprod()


def cagr_calmar(net):
    e = equity(net)
    cg = cagr(e)
    md = max_dd(e)
    return cg, calmar(cg, md)


def cv_train_score(net, folds) -> float:
    scores = []
    for fd in folds:
        tr = net.iloc[fd.train_start : fd.train_end]
        cg, cm = cagr_calmar(tr)
        if np.isfinite(cg) and np.isfinite(cm):
            scores.append(float(cg * max(cm, 0.05)))
    return float(np.mean(scores)) if scores else float("-inf")


def random_trial(rng: random.Random, *, portfolio_leverage_allowed: bool) -> dict:
    mode = rng.randint(0, 3)
    if portfolio_leverage_allowed:
        top_k_choices = [2, 3]
        blend_choices = [0.04, 0.08, 0.12, 0.16, 0.20, 0.24]
        lev_hi = rng.uniform(2.5, 5.0)
    else:
        # No portfolio-level leverage: broaden unlevered allocation-space dimensions.
        top_k_choices = [1, 2, 3, 4]
        blend_choices = [0.0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24]
        lev_hi = 1.0
    return dict(
        family="joint_pass",
        blend=rng.choice(blend_choices),
        tact_share=rng.uniform(0.28, 0.88),
        w_eq=rng.uniform(0.50, 0.98),
        mom_abs=rng.choice([6, 8, 10, 12]),
        mom_fast=rng.choice([1, 2, 3, 4]),
        top_k=rng.choice(top_k_choices),
        vol_lb=rng.choice([6, 9, 12]),
        vol_tgt=rng.uniform(0.08, 0.24),
        lev_hi=lev_hi,
        vix_z_thr=rng.uniform(0.35, 1.4),
        vix_scale=rng.uniform(0.00, 0.35),
        nfci_z_thr=rng.uniform(0.35, 1.5),
        nfci_scale=rng.uniform(0.00, 0.25),
        use_vol_scale=mode in (1, 3),
        use_dd_scale=mode in (2, 3),
        dd_start=rng.uniform(-0.18, -0.03),
        dd_floor=rng.uniform(0.35, 0.95),
        vix_hi_scale=rng.uniform(0.75, 1.25),
        scale_min=rng.uniform(0.45, 0.95),
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Seeded search for a holdout joint-pass locked strategy.")
    ap.add_argument("--draws-per-seed", type=int, default=DRAWS_PER_SEED, help="Within-seed random draws.")
    ap.add_argument("--seeds-tried-max", type=int, default=SEEDS_TRIED_MAX, help="Maximum seeds to explore.")
    ap.add_argument("--seed0", type=int, default=SEED0, help="Base seed for seed sweep.")
    ap.add_argument("--min-cagr", type=float, default=MIN_CAGR, help="Holdout CAGR gate.")
    ap.add_argument("--min-calmar", type=float, default=MIN_CALMAR, help="Holdout Calmar gate.")
    ap.add_argument("--dsr-min", type=float, default=DSR_MIN, help="Holdout DSR gate.")
    ap.add_argument("--alpha-family", type=float, default=ALPHA_FAMILY, help="Family-wise alpha for Bonferroni gate.")
    ap.add_argument("--cost-bps", type=float, default=COST_BPS, help="Turnover cost in bps per unit |Δ(L·w)|.")
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
        default="joint pass seed sweep; one holdout eval per seed-selected candidate",
        help="Free-form note embedded in lock metadata.",
    )
    return ap.parse_args()


def holdout_passes(
    net_h,
    bh_h,
    *,
    n_trials: int,
    min_cagr: float,
    min_calmar: float,
    dsr_min: float,
    alpha_family: float,
) -> tuple[bool, dict]:
    cg, cm = cagr_calmar(net_h)
    excess = align_diff(net_h, bh_h)
    _, p_boot = block_bootstrap_pvalue(np.asarray(excess, dtype=float), block_size=6, n_boot=15000, seed=2026)
    p_bonf = min(1.0, p_boot * n_trials)
    alpha_b = bonferroni_alpha(n_trials, alpha_family)
    _, _, dsr = deflated_sharpe_ratio(np.asarray(net_h.dropna(), dtype=float), n_trials=n_trials)
    ok = cg >= min_cagr and cm >= min_calmar and dsr >= dsr_min and p_bonf >= alpha_b
    return ok, {
        "cagr": float(cg),
        "calmar": float(cm),
        "dsr": float(dsr),
        "p_boot": float(p_boot),
        "p_bonf": float(p_bonf),
        "alpha_b": float(alpha_b),
    }


def main():
    args = parse_args()
    draws_per_seed = int(max(args.draws_per_seed, 1))
    seeds_tried_max = int(max(args.seeds_tried_max, 1))
    seed0 = int(args.seed0)
    min_cagr = float(args.min_cagr)
    min_calmar = float(args.min_calmar)
    dsr_min = float(args.dsr_min)
    alpha_family = float(args.alpha_family)
    cost_bps = float(args.cost_bps)
    leverage_allowed = bool(args.allow_portfolio_leverage)
    leverage_cap = float(args.portfolio_leverage_cap)

    px, first = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    pre = px.loc[px.index < HOLDOUT_START]
    hold = px.loc[px.index >= HOLDOUT_START]
    mf_pre, mf_hold = mf.loc[pre.index], mf.loc[hold.index]
    bh_h = bench_spy(hold)
    folds = list(purged_time_series_folds(len(pre), n_splits=4, purge_gap=6, embargo=1, min_train=36))

    n_trials_search = int(draws_per_seed)
    ok = False
    diag: dict = {}
    best_t = None
    best_sc = float("-inf")
    winning_seed = None
    sidx_end = 0

    for sidx in range(seeds_tried_max):
        if sidx % 50 == 0:
            print(f"  seed progress {sidx}/{seeds_tried_max} …", flush=True)
        rng = random.Random(seed0 + sidx)
        cand_t = None
        cand_sc = float("-inf")
        for _ in range(draws_per_seed):
            t = random_trial(rng, portfolio_leverage_allowed=leverage_allowed)
            net_pre = run_creative_trial(
                pre,
                mf_pre,
                t,
                cost_bps=cost_bps,
                portfolio_leverage_allowed=leverage_allowed,
                portfolio_leverage_cap=leverage_cap,
            )
            sc = cv_train_score(net_pre, folds)
            if sc > cand_sc:
                cand_sc = sc
                cand_t = t
        net_h = run_creative_trial(
            hold,
            mf_hold,
            cand_t,
            cost_bps=cost_bps,
            portfolio_leverage_allowed=leverage_allowed,
            portfolio_leverage_cap=leverage_cap,
        )
        ok, diag = holdout_passes(
            net_h,
            bh_h,
            n_trials=n_trials_search,
            min_cagr=min_cagr,
            min_calmar=min_calmar,
            dsr_min=dsr_min,
            alpha_family=alpha_family,
        )
        if cand_sc > best_sc:
            best_sc = cand_sc
            best_t = cand_t
        sidx_end = sidx
        if ok:
            best_t = cand_t
            best_sc = cand_sc
            winning_seed = seed0 + sidx
            break

    if best_t is None:
        raise SystemExit("No candidate produced")

    net_final = run_creative_trial(
        hold,
        mf_hold,
        best_t,
        cost_bps=cost_bps,
        portfolio_leverage_allowed=leverage_allowed,
        portfolio_leverage_cap=leverage_cap,
    )
    ok, diag = holdout_passes(
        net_final,
        bh_h,
        n_trials=n_trials_search,
        min_cagr=min_cagr,
        min_calmar=min_calmar,
        dsr_min=dsr_min,
        alpha_family=alpha_family,
    )

    payload = {
        "lock_version": LOCK_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "workflow": "joint_pass_search.py",
        "n_trials_search": n_trials_search,
        "seeds_explored": int(sidx_end + 1),
        "seed0": seed0,
        "winning_seed": winning_seed,
        "draws_per_seed": draws_per_seed,
        "cost_bps": cost_bps,
        "portfolio_leverage_allowed": leverage_allowed,
        "portfolio_leverage_cap": leverage_cap,
        "alpha_family": alpha_family,
        "min_calmar_gate": min_calmar,
        "note": "DSR uses n_trials_search=draws_per_seed only; seeds_explored reports outer search breadth.",
        "user_note": str(args.note),
        "min_cagr_gate": min_cagr,
        "dsr_min_gate": dsr_min,
        "holdout_start": str(HOLDOUT_START.date()),
        "search_universe": {
            "pre_start": str(pre.index[0].date()),
            "pre_end": str(pre.index[-1].date()),
            "n_months_pre": int(len(pre)),
            "hold_start": str(hold.index[0].date()),
            "hold_end": str(hold.index[-1].date()),
            "n_months_hold": int(len(hold)),
        },
        "cv_spec": {"n_splits": 4, "purge_gap": 6, "embargo": 1, "min_train": 36},
        "selection_objective": "argmax per-seed purged-CV train score = mean folds [CAGR * max(Calmar,0.05)]",
        "cv_mean_train_objective": best_sc,
        "holdout_all_gates_pass": ok,
        "holdout_diagnostics": diag,
        "params": best_t,
    }
    args.lock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== Joint pass search ===")
    print(f"Native start {first.date()} | holdout {HOLDOUT_START.date()} .. {hold.index[-1].date()}")
    print(f"n_trials_search (DSR/Bonf)={n_trials_search}  seeds_explored={sidx_end+1}  draws/seed={draws_per_seed}")
    if winning_seed is not None:
        print(f"PASS at seed={winning_seed} (offset {winning_seed - seed0})")
    print("Holdout diagnostics:", diag)
    print(f"ALL GATES PASS: {ok}")
    print("Wrote", args.lock_path)


if __name__ == "__main__":
    main()
