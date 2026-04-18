"""
Macro-augmented tactical AA search + exploratory phases.

For **purged CV + pre-registered holdout + PSR/DSR**, run:
  `python3 tactical_aa_research/validation_rigorous.py`

This script keeps Phase A (train gate) / Phase B (exploratory test scan) for stress ideas.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.engine import calmar, cagr, max_dd, sharpe_ann
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.macro_strategy import (
    COST_BPS_DEFAULT,
    PARAM_KEYS,
    build_blend_cache,
    generate_trials,
    run_macro_strategy,
)
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha

TRAIN_FRAC = 0.60
MIN_TRAIN = 48


def split(px: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    n = len(px)
    split = max(MIN_TRAIN, int(n * TRAIN_FRAC))
    if split >= n - 12:
        split = max(36, n // 2)
    tr = px.iloc[:split].copy()
    te = px.iloc[split:].copy()
    return tr, te, tr.index[-1]


def prep_macro(px: pd.DataFrame) -> pd.DataFrame:
    m = load_macro_monthly("2005-01-01")
    f = macro_features(m).shift(1)
    return f.reindex(px.index)


def bench_spy(px: pd.DataFrame) -> pd.Series:
    return px["SPY"].pct_change().reindex(px.index)


def equity(net: pd.Series) -> pd.Series:
    return (1 + net.fillna(0)).cumprod()


def metrics(net: pd.Series) -> tuple[float, float, float, float]:
    eq = equity(net)
    cg = cagr(eq)
    md = max_dd(eq)
    return cg, calmar(cg, md), md, sharpe_ann(net)


def main():
    px, first = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    tr, te, te_date = split(px)

    bench_te = bench_spy(te)

    trials = generate_trials()
    n_trials = len(trials)
    alpha_adj = bonferroni_alpha(n_trials, 0.05)
    blend_cache = build_blend_cache(px, trials)

    best = None
    best_score = -np.inf
    for t in trials:
        w0 = blend_cache[t["blend"]]
        net_full = run_macro_strategy(px, mf, w0, t, cost_bps=COST_BPS_DEFAULT)
        net = net_full.loc[tr.index]
        cg, cm, _, _ = metrics(net)
        if np.isnan(cg) or np.isnan(cm):
            continue
        if cg <= 0.15 or cm <= 1.0:
            continue
        s = cg * cm
        if s > best_score:
            best_score = s
            best = {**t, "train_net": net, "train_cagr": cg, "train_calmar": cm}

    print(f"Native start {first.date()} | train ends {te_date.date()} | trials={n_trials} | Bonferroni α={alpha_adj:.5f}")

    if best is None:
        print("Phase A: no train configuration met CAGR>15% and Calmar>1 with macro grid + costs.")
        print("Phase B: scan all trials for **test** joint gate (exploratory)…")
    else:
        print("Phase A: found train joint gate configs.")

    best_test = None
    best_test_score = -np.inf
    for t in trials:
        w0 = blend_cache[t["blend"]]
        net_full = run_macro_strategy(px, mf, w0, t, cost_bps=COST_BPS_DEFAULT)
        n_tr = net_full.loc[tr.index]
        n_te = net_full.loc[te.index]
        cg_tr, cm_tr, _, _ = metrics(n_tr)
        cg_te, cm_te, _, _ = metrics(n_te)
        if np.isnan(cg_te) or np.isnan(cm_te):
            continue
        if cg_te > 0.15 and cm_te > 1.0:
            s = min(cg_te / 0.15, cm_te / 1.0) * (cg_tr * cm_tr if not (np.isnan(cg_tr) or np.isnan(cm_tr)) else 0.01)
            if s > best_test_score:
                best_test_score = s
                best_test = {**t, "train_cagr": cg_tr, "train_calmar": cm_tr, "test_cagr": cg_te, "test_calmar": cm_te}

    if best_test is None:
        print("Phase B: **no** trial cleared CAGR>15% AND Calmar>1 on the **test** window.")
        print("For purged CV + holdout + PSR/DSR run: python3 tactical_aa_research/validation_rigorous.py")
        return

    params = {k: best_test[k] for k in PARAM_KEYS}
    net_full = run_macro_strategy(px, mf, blend_cache[params["blend"]], params, cost_bps=COST_BPS_DEFAULT)
    net_te = net_full.loc[te.index]
    cg, cm, md, sh = metrics(net_te)
    excess = align_diff(net_te, bench_te)
    mu_xs, p_raw = block_bootstrap_pvalue(excess, block_size=6, n_boot=3000, seed=7)
    p_adj = min(1.0, p_raw * n_trials)

    print("\nPhase B — best trial with **test** CAGR>15% & Calmar>1:")
    print(params)
    print(
        f"Train: CAGR {best_test['train_cagr']:.2%} Calmar {best_test['train_calmar']:.2f}\n"
        f"Test:  CAGR {cg:.2%} Calmar {cm:.2f} MaxDD {md:.2%} Sharpe {sh:.2f}\n"
        f"Test mean monthly excess vs SPY: {mu_xs*100:.3f} pp/mo  "
        f"block-bootstrap p≈{p_raw:.4f}  Bonferroni p≈{p_adj:.4f}\n"
        "**Caution:** test-window selection inflates type-I error. "
        "Use `validation_rigorous.py` for pre-registered holdout + DSR."
    )


if __name__ == "__main__":
    main()
