"""
Rigorous validation pipeline:

1. **Pre-registered holdout** (`validation_config.HOLDOUT_START`) — never used in selection.
2. **Purged time-series CV** on the pre-holdout sample: for each trial, mean in-fold
   **train Sharpe** (no peek at fold test when selecting trial).
3. **Pick one trial** = argmax CV train Sharpe score.
4. **Single evaluation** on holdout: CAGR, Calmar, excess vs SPY, **PSR** and **DSR**
   (`n_trials` = full grid size).

Run:
  python3 tactical_aa_research/validation_rigorous.py
  FRED_API_KEY=... python3 tactical_aa_research/validation_rigorous.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.deflated_sharpe import deflated_sharpe_ratio
from tactical_aa_research.engine import calmar, cagr, max_dd, sharpe_ann
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.macro_strategy import (
    COST_BPS_DEFAULT,
    PARAM_KEYS,
    build_blend_cache,
    generate_trials,
    run_macro_strategy,
)
from tactical_aa_research.purged_cv import purged_time_series_folds
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha
from tactical_aa_research.validation_config import HOLDOUT_START


def prep_macro(px: pd.DataFrame) -> pd.DataFrame:
    m = load_macro_monthly("2005-01-01")
    f = macro_features(m).shift(1)
    return f.reindex(px.index)


def bench_spy(px: pd.DataFrame) -> pd.Series:
    return px["SPY"].pct_change().reindex(px.index)


def equity_from_net(net: pd.Series) -> pd.Series:
    return (1 + net.fillna(0)).cumprod()


def metrics_cagr_calmar(net: pd.Series) -> tuple[float, float, float, float]:
    eq = equity_from_net(net)
    cg = cagr(eq)
    md = max_dd(eq)
    return cg, calmar(cg, md), md, sharpe_ann(net)


def sharpe_monthly_series(net: pd.Series) -> float:
    x = net.dropna().astype(float)
    if len(x) < 6 or float(x.std(ddof=1)) < 1e-12:
        return float("nan")
    return float(x.mean() / x.std(ddof=1) * np.sqrt(12.0))


def main():
    px_full, first = native_panel_from_common_start("2005-01-01")
    mf_full = prep_macro(px_full)

    pre = px_full.loc[px_full.index < HOLDOUT_START].copy()
    hold = px_full.loc[px_full.index >= HOLDOUT_START].copy()
    mf_pre = mf_full.loc[pre.index]
    mf_hold = mf_full.loc[hold.index]

    if len(pre) < 80 or len(hold) < 24:
        raise SystemExit(f"Insufficient rows: pre={len(pre)} hold={len(hold)} — adjust HOLDOUT_START.")

    trials = generate_trials()
    n_trials = len(trials)
    cache = build_blend_cache(px_full, trials)

    # Precompute each trial's net on **pre-holdout** panel only (signals use pre history)
    nets_pre: dict[int, pd.Series] = {}
    for i, t in enumerate(trials):
        w0 = cache[t["blend"]].loc[pre.index]
        nets_pre[i] = run_macro_strategy(pre, mf_pre, w0, t, cost_bps=COST_BPS_DEFAULT)

    n = len(pre)
    # Shorter pre-holdout history (~10y): use modest purge + fewer splits so folds exist
    folds = list(purged_time_series_folds(n, n_splits=4, purge_gap=6, embargo=1, min_train=36))
    if not folds:
        raise SystemExit("No CV folds generated — relax parameters or extend history.")

    cv_scores = []
    for i in range(len(trials)):
        train_srs = []
        for fd in folds:
            tr = nets_pre[i].iloc[fd.train_start : fd.train_end]
            train_srs.append(sharpe_monthly_series(tr))
        train_srs = [s for s in train_srs if np.isfinite(s)]
        cv_scores.append(float(np.mean(train_srs)) if train_srs else float("-inf"))

    best_i = int(np.argmax(cv_scores))
    best_t = trials[best_i]
    print("=== Rigorous validation ===")
    print(f"Native common start: {first.date()}")
    print(f"Pre-holdout: {pre.index[0].date()} .. {pre.index[-1].date()} (n={len(pre)})")
    print(f"Holdout (pre-registered): {HOLDOUT_START.date()} .. {hold.index[-1].date()} (n={len(hold)})")
    print(f"Grid trials: {n_trials} | Purged CV folds: {len(folds)}")
    print(f"Selection rule: argmax mean in-fold **train** Sharpe (no holdout peek)\n")
    print("Selected trial index", best_i, "CV mean train Sharpe", cv_scores[best_i])
    print("Params:", {k: best_t[k] for k in PARAM_KEYS})

    # Fold-wise OOS diagnostics (informational — not used for selection)
    oos_srs = []
    for fd in folds:
        te = nets_pre[best_i].iloc[fd.test_start : fd.test_end]
        oos_srs.append(sharpe_monthly_series(te))
    print(
        "Purged-CV test-window Sharpe (same trial, not used to pick trial):",
        [round(s, 3) for s in oos_srs if np.isfinite(s)],
        "median=",
        float(np.nanmedian(oos_srs)) if oos_srs else float("nan"),
    )

    # --- Holdout: single shot ---
    w0_h = cache[best_t["blend"]].loc[hold.index]
    net_hold = run_macro_strategy(hold, mf_hold, w0_h, best_t, cost_bps=COST_BPS_DEFAULT)
    cg, cm, md, sh = metrics_cagr_calmar(net_hold)
    bench_h = bench_spy(hold)
    excess = align_diff(net_hold, bench_h)
    mu_xs, p_boot = block_bootstrap_pvalue(np.asarray(excess, dtype=float), block_size=6, n_boot=5000, seed=42)
    p_bonf = min(1.0, p_boot * n_trials)
    alpha_b = bonferroni_alpha(n_trials, 0.05)

    sr_ann, psr, dsr = deflated_sharpe_ratio(np.asarray(net_hold.dropna(), dtype=float), n_trials=n_trials)

    print("\n=== HOLDOUT (evaluated once) ===")
    print(f"CAGR {cg:.2%}  Calmar {cm:.2f}  MaxDD {md:.2%}  Sharpe(ann) {sh:.2f}")
    print(f"Mean monthly excess vs SPY: {mu_xs*100:.3f} pp/mo")
    print(f"Block-bootstrap p (mean excess=0): {p_boot:.4f}  ×{n_trials} Bonferroni p≈{p_bonf:.4f} (α_family={alpha_b:.5f})")
    print(f"Holdout monthly SR (ann.): {sr_ann:.3f}  PSR vs 0: {psr:.4f}  DSR (n_trials={n_trials}): {dsr:.4f}")

    gates_ok = cg > 0.15 and cm > 1.0
    stats_ok = dsr >= 0.95 and p_bonf >= alpha_b
    print("\nPre-registered gates (holdout):")
    print(f"  CAGR > 15%: {'PASS' if cg > 0.15 else 'FAIL'} ({cg:.2%})")
    print(f"  Calmar > 1: {'PASS' if cm > 1.0 else 'FAIL'} ({cm:.2f})")
    print(f"  DSR >= 0.95 (n_trials={n_trials}): {'PASS' if dsr >= 0.95 else 'FAIL'} ({dsr:.4f})")
    print(f"  Bonferroni bootstrap (excess vs SPY): {'PASS' if p_bonf >= alpha_b else 'FAIL'} (p≈{p_bonf:.4f})")
    print(f"  Deploy heuristic (all four): {'PASS' if gates_ok and stats_ok else 'FAIL'}")

    print("\nInterpretation:")
    print(
        "- Trial choice used **only** pre-holdout purged-CV **train** Sharpe.\n"
        "- Holdout metrics are **one draw**; DSR/PSR use conservative multiplicity bump.\n"
        "- If DSR < 0.95 or Bonferroni bootstrap rejects your tolerance, do not deploy."
    )


if __name__ == "__main__":
    main()
