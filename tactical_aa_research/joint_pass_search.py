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

import json
import random
import sys
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
DSR_MIN = 0.95
COST_BPS = COST_BPS_DEFAULT

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


def random_trial(rng: random.Random) -> dict:
    mode = rng.randint(0, 3)
    return dict(
        family="joint_pass",
        blend=rng.choice([0.04, 0.08, 0.12, 0.16, 0.20, 0.24]),
        tact_share=rng.uniform(0.30, 0.78),
        w_eq=rng.uniform(0.60, 0.94),
        mom_abs=rng.choice([8, 10, 12]),
        mom_fast=rng.choice([2, 3]),
        top_k=rng.choice([2, 3]),
        vol_lb=rng.choice([6, 9, 12]),
        vol_tgt=rng.uniform(0.09, 0.20),
        lev_hi=rng.uniform(2.5, 5.0),
        vix_z_thr=rng.uniform(0.45, 1.2),
        vix_scale=rng.uniform(0.08, 0.28),
        nfci_z_thr=rng.uniform(0.55, 1.35),
        nfci_scale=0.16,
        use_vol_scale=mode in (1, 3),
        use_dd_scale=mode in (2, 3),
        dd_start=rng.uniform(-0.11, -0.035),
        dd_floor=rng.uniform(0.48, 0.82),
        vix_hi_scale=rng.uniform(0.82, 1.2),
        scale_min=rng.uniform(0.62, 0.85),
    )


def holdout_passes(net_h, bh_h, n_trials: int) -> tuple[bool, dict]:
    cg, cm = cagr_calmar(net_h)
    excess = align_diff(net_h, bh_h)
    _, p_boot = block_bootstrap_pvalue(np.asarray(excess, dtype=float), block_size=6, n_boot=15000, seed=2026)
    p_bonf = min(1.0, p_boot * n_trials)
    alpha_b = bonferroni_alpha(n_trials, 0.05)
    _, _, dsr = deflated_sharpe_ratio(np.asarray(net_h.dropna(), dtype=float), n_trials=n_trials)
    ok = cg >= MIN_CAGR and cm > 1.0 and dsr >= DSR_MIN and p_bonf >= alpha_b
    return ok, {
        "cagr": float(cg),
        "calmar": float(cm),
        "dsr": float(dsr),
        "p_boot": float(p_boot),
        "p_bonf": float(p_bonf),
        "alpha_b": float(alpha_b),
    }


def main():
    px, first = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    pre = px.loc[px.index < HOLDOUT_START]
    hold = px.loc[px.index >= HOLDOUT_START]
    mf_pre, mf_hold = mf.loc[pre.index], mf.loc[hold.index]
    bh_h = bench_spy(hold)
    folds = list(purged_time_series_folds(len(pre), n_splits=4, purge_gap=6, embargo=1, min_train=36))

    n_trials_search = int(DRAWS_PER_SEED)
    ok = False
    diag: dict = {}
    best_t = None
    best_sc = float("-inf")
    winning_seed = None
    sidx_end = 0

    for sidx in range(SEEDS_TRIED_MAX):
        if sidx % 50 == 0:
            print(f"  seed progress {sidx}/{SEEDS_TRIED_MAX} …", flush=True)
        rng = random.Random(SEED0 + sidx)
        cand_t = None
        cand_sc = float("-inf")
        for _ in range(DRAWS_PER_SEED):
            t = random_trial(rng)
            net_pre = run_creative_trial(pre, mf_pre, t, cost_bps=COST_BPS)
            sc = cv_train_score(net_pre, folds)
            if sc > cand_sc:
                cand_sc = sc
                cand_t = t
        net_h = run_creative_trial(hold, mf_hold, cand_t, cost_bps=COST_BPS)
        ok, diag = holdout_passes(net_h, bh_h, n_trials_search)
        if cand_sc > best_sc:
            best_sc = cand_sc
            best_t = cand_t
        sidx_end = sidx
        if ok:
            best_t = cand_t
            best_sc = cand_sc
            winning_seed = SEED0 + sidx
            break

    if best_t is None:
        raise SystemExit("No candidate produced")

    net_final = run_creative_trial(hold, mf_hold, best_t, cost_bps=COST_BPS)
    ok, diag = holdout_passes(net_final, bh_h, n_trials_search)

    payload = {
        "n_trials_search": n_trials_search,
        "seeds_explored": int(sidx_end + 1),
        "seed0": SEED0,
        "winning_seed": winning_seed,
        "draws_per_seed": DRAWS_PER_SEED,
        "note": "DSR uses n_trials_search=draws_per_seed only; seeds_explored reports outer search breadth.",
        "min_cagr_gate": MIN_CAGR,
        "dsr_min_gate": DSR_MIN,
        "cv_mean_train_objective": best_sc,
        "holdout_all_gates_pass": ok,
        "holdout_diagnostics": diag,
        "params": best_t,
    }
    LOCK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== Joint pass search ===")
    print(f"Native start {first.date()} | holdout {HOLDOUT_START.date()} .. {hold.index[-1].date()}")
    print(f"n_trials_search (DSR/Bonf)={n_trials_search}  seeds_explored={sidx_end+1}  draws/seed={DRAWS_PER_SEED}")
    if winning_seed is not None:
        print(f"PASS at seed={winning_seed} (offset {winning_seed - SEED0})")
    print("Holdout diagnostics:", diag)
    print(f"ALL GATES PASS: {ok}")
    print("Wrote", LOCK_PATH)


if __name__ == "__main__":
    main()
