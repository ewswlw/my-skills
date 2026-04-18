"""
Rigorous validation — **pre-registered creative family** (n_trials=32).

1. Holdout boundary: `validation_config.HOLDOUT_START` (fixed).
2. Purged time-series CV on pre-holdout: score each trial by **train-only** composite
   (mean over folds of CAGR×max(Calmar,0.2) on in-fold train returns).
3. Select **one** trial = argmax CV score (no holdout peek).
4. Single holdout evaluation: CAGR, Calmar, excess vs SPY, block-bootstrap × n_trials,
   PSR/DSR with **n_trials = 32**.

If the selected trial fails gates, prints **oracle** best-in-family on holdout (exploratory only).

Run:
  python3 tactical_aa_research/validation_rigorous.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.creative_runner import run_creative_trial
from tactical_aa_research.creative_trials import CREATIVE_PARAM_KEYS, generate_creative_trials
from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.deflated_sharpe import deflated_sharpe_ratio
from tactical_aa_research.engine import calmar, cagr, max_dd, sharpe_ann
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.macro_strategy import COST_BPS_DEFAULT
from tactical_aa_research.purged_cv import purged_time_series_folds
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha
from tactical_aa_research.validation_config import HOLDOUT_START


def prep_macro(px: pd.DataFrame) -> pd.DataFrame:
    m = load_macro_monthly("2005-01-01")
    return macro_features(m).shift(1).reindex(px.index)


def bench_spy(px: pd.DataFrame) -> pd.Series:
    return px["SPY"].pct_change().reindex(px.index)


def equity_from_net(net: pd.Series) -> pd.Series:
    return (1 + net.fillna(0)).cumprod()


def metrics_cagr_calmar(net: pd.Series) -> tuple[float, float, float, float]:
    eq = equity_from_net(net)
    cg = cagr(eq)
    md = max_dd(eq)
    return cg, calmar(cg, md), md, sharpe_ann(net)


def train_cagr_calmar_score(net: pd.Series) -> float:
    """Univariate objective on a return slice (higher = better)."""
    cg, cm, _, _ = metrics_cagr_calmar(net)
    if not np.isfinite(cg) or not np.isfinite(cm):
        return float("-inf")
    return float(cg * max(cm, 0.05))


def main():
    px_full, first = native_panel_from_common_start("2005-01-01")
    mf_full = prep_macro(px_full)

    pre = px_full.loc[px_full.index < HOLDOUT_START].copy()
    hold = px_full.loc[px_full.index >= HOLDOUT_START].copy()
    mf_pre = mf_full.loc[pre.index]
    mf_hold = mf_full.loc[hold.index]

    if len(pre) < 80 or len(hold) < 24:
        raise SystemExit(f"Insufficient rows: pre={len(pre)} hold={len(hold)}")

    trials = generate_creative_trials()
    n_trials = len(trials)
    assert n_trials == 32

    nets_pre: dict[int, pd.Series] = {}
    for i, t in enumerate(trials):
        nets_pre[i] = run_creative_trial(pre, mf_pre, t, cost_bps=COST_BPS_DEFAULT)

    n = len(pre)
    folds = list(purged_time_series_folds(n, n_splits=4, purge_gap=6, embargo=1, min_train=36))
    if not folds:
        raise SystemExit("No CV folds")

    cv_scores = []
    for i in range(n_trials):
        fold_scores = []
        for fd in folds:
            tr = nets_pre[i].iloc[fd.train_start : fd.train_end]
            fold_scores.append(train_cagr_calmar_score(tr))
        fold_scores = [s for s in fold_scores if np.isfinite(s)]
        cv_scores.append(float(np.mean(fold_scores)) if fold_scores else float("-inf"))

    best_i = int(np.argmax(cv_scores))
    best_t = trials[best_i]

    print("=== Rigorous validation (creative family, n=32) ===")
    print(f"Native start: {first.date()}")
    print(f"Pre-holdout: {pre.index[0].date()} .. {pre.index[-1].date()} (n={len(pre)})")
    print(f"Holdout: {HOLDOUT_START.date()} .. {hold.index[-1].date()} (n={len(hold)})")
    print(f"n_trials={n_trials} | CV folds={len(folds)}")
    print("Selection: argmax mean-fold **train** score = CAGR × max(Calmar,0.05)\n")
    print("Selected index", best_i, "CV score", cv_scores[best_i])
    print("Params:", {k: best_t[k] for k in CREATIVE_PARAM_KEYS})

    net_hold = run_creative_trial(hold, mf_hold, best_t, cost_bps=COST_BPS_DEFAULT)
    cg, cm, md, sh = metrics_cagr_calmar(net_hold)
    bench_h = bench_spy(hold)
    excess = align_diff(net_hold, bench_h)
    mu_xs, p_boot = block_bootstrap_pvalue(np.asarray(excess, dtype=float), block_size=6, n_boot=5000, seed=42)
    p_bonf = min(1.0, p_boot * n_trials)
    alpha_b = bonferroni_alpha(n_trials, 0.05)
    sr_ann, psr, dsr = deflated_sharpe_ratio(np.asarray(net_hold.dropna(), dtype=float), n_trials=n_trials)

    print("\n=== HOLDOUT (selected trial, one eval) ===")
    print(f"CAGR {cg:.2%}  Calmar {cm:.2f}  MaxDD {md:.2%}  Sharpe {sh:.2f}")
    print(f"Mean excess vs SPY: {mu_xs*100:.3f} pp/mo")
    print(f"Bootstrap p: {p_boot:.4f}  Bonferroni p≈{p_bonf:.4f} (α_family={alpha_b:.5f})")
    print(f"SR_ann {sr_ann:.3f}  PSR {psr:.4f}  DSR {dsr:.4f}")

    gates_ok = cg > 0.15 and cm > 1.0
    stats_ok = dsr >= 0.95 and p_bonf >= alpha_b
    print("\nGates:")
    print(f"  CAGR>15%: {'PASS' if cg>0.15 else 'FAIL'}")
    print(f"  Calmar>1: {'PASS' if cm>1 else 'FAIL'}")
    print(f"  DSR>=0.95: {'PASS' if dsr>=0.95 else 'FAIL'}")
    print(f"  Bonf boot: {'PASS' if p_bonf>=alpha_b else 'FAIL'}")
    print(f"  ALL FOUR: {'PASS' if gates_ok and stats_ok else 'FAIL'}")

    # --- Oracle (exploratory): which trial is closest on holdout? NOT valid inference ---
    best_oracle = None
    best_dist = float("inf")
    for i, t in enumerate(trials):
        nh = run_creative_trial(hold, mf_hold, t, cost_bps=COST_BPS_DEFAULT)
        c, m, _, _ = metrics_cagr_calmar(nh)
        if not (np.isfinite(c) and np.isfinite(m)):
            continue
        dist = max(0.0, 0.15 - c) + max(0.0, 1.0 - m)
        if dist < best_dist:
            best_dist = dist
            best_oracle = (i, t, c, m)

    if best_oracle is not None:
        oi, ot, oc, om = best_oracle
        net_o = run_creative_trial(hold, mf_hold, ot, cost_bps=COST_BPS_DEFAULT)
        ex = align_diff(net_o, bench_h)
        _, pb = block_bootstrap_pvalue(np.asarray(ex, dtype=float), block_size=6, n_boot=3000, seed=99)
        pbon = min(1.0, pb * n_trials)
        sr, ps, ds = deflated_sharpe_ratio(np.asarray(net_o.dropna(), dtype=float), n_trials=n_trials)
        print("\n=== ORACLE (holdout-scanned; for closeness only — invalid for deployment) ===")
        print(
            f"Best L1 distance to (15%, Calmar=1) idx={oi}  CAGR={oc:.2%} Calmar={om:.2f}  "
            f"SR_ann={sr:.3f} DSR={ds:.3f} Bonf_p≈{pbon:.3f}"
        )
        print({k: ot[k] for k in CREATIVE_PARAM_KEYS})

    print(
        "\nNote: Oracle line **uses holdout to rank trials** — it answers 'how close can this "
        "fixed trial family get on 2020+', not 'validated strategy'."
    )


if __name__ == "__main__":
    main()
