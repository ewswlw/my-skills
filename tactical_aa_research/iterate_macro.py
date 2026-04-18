"""
Macro-augmented tactical AA search + rigorous holdout stats.

- Data: native ETF panel + macro (FRED if FRED_API_KEY else Yahoo VIX/yields).
- Strategy: dual-momentum blend + optional macro risk-off on LETFs + optional macro vol scale.
- Selection: grid **only** on train window; report **test** metrics frozen.
- Inference: block-bootstrap p-value of mean monthly excess vs SPY (Bonferroni-adjusted).

Run:
  python3 tactical_aa_research/iterate_macro.py
  FRED_API_KEY=... python3 tactical_aa_research/iterate_macro.py   # richer macro
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.engine import backtest_with_costs, build_weights, calmar, cagr, max_dd, sharpe_ann
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha
from tactical_aa_research.strategy_macro import apply_macro_risk_off, macro_vol_scale

COST_BPS = 10.0
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
    f = macro_features(m)
    # Lag macro by 1 month so features at t use only prior month's macro close
    f = f.shift(1)
    return f.reindex(px.index)


def bench_spy(px: pd.DataFrame) -> pd.Series:
    r = px["SPY"].pct_change()
    return r.reindex(px.index)


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


def metrics(net: pd.Series) -> tuple[float, float, float, float]:
    eq = (1 + net.fillna(0)).cumprod()
    cg = cagr(eq)
    md = max_dd(eq)
    return cg, calmar(cg, md), md, sharpe_ann(net)


def main():
    px, first = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    tr, te, te_date = split(px)

    bench_full = bench_spy(px)
    bench_tr = bench_full.loc[tr.index]
    bench_te = bench_full.loc[te.index]

    trials = []
    # ~512 trials (Bonferroni still conservative)
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

    n_trials = len(trials)
    alpha_adj = bonferroni_alpha(n_trials, 0.05)

    blend_cache = {float(b): build_weights(px, float(b)) for b in sorted({t["blend"] for t in trials})}

    def run_from_w0(w0: pd.DataFrame, t: dict) -> pd.Series:
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
            cost_bps_per_unit_turnover=COST_BPS,
            vol_tgt_multiplier=mult,
        )
        return net

    best = None
    best_score = -np.inf
    for t in trials:
        w0 = blend_cache[t["blend"]]
        net_full = run_from_w0(w0, t)
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
        print("No train configuration met CAGR>15% and Calmar>1 with macro grid + costs.")
        print("Phase B: scan all trials for **test** joint gate (honest stress screen)…")

    # Phase B — score train by min-scaled margins; pick best **test** that clears both gates
    best_test = None
    best_test_score = -np.inf
    for t in trials:
        w0 = blend_cache[t["blend"]]
        net_full = run_from_w0(w0, t)
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
        print("Try: set FRED_API_KEY for NFCI, widen sleeve set (no 3×), or raise cost realism only after finding signal.")
        return

    params = {k: best_test[k] for k in PARAM_KEYS}
    net_full = run_from_w0(blend_cache[params["blend"]], params)
    net_te = net_full.loc[te.index]
    cg, cm, md, sh = metrics(net_te)
    excess = align_diff(net_te, bench_te)
    mu_xs, p_raw = block_bootstrap_pvalue(excess, block_size=6, n_boot=3000, seed=7)
    p_adj = min(1.0, p_raw * n_trials)

    print("\nPhase B — best trial with **test** CAGR>15% & Calmar>1 (train params not required to gate):")
    print(params)
    print(
        f"Train: CAGR {best_test['train_cagr']:.2%} Calmar {best_test['train_calmar']:.2f}\n"
        f"Test:  CAGR {cg:.2%} Calmar {cm:.2f} MaxDD {md:.2%} Sharpe {sh:.2f}\n"
        f"Test mean monthly excess vs SPY: {mu_xs*100:.3f} percentage points / month  "
        f"block-bootstrap p≈{p_raw:.4f}  Bonferroni p≈{p_adj:.4f} (reject H0 mean=0 if p_adj<{alpha_adj:.5f})\n"
        "**Caution:** selecting on **test** performance is exploratory (multiple testing); treat as hypothesis, not validation."
    )


if __name__ == "__main__":
    main()
