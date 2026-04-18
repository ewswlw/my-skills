"""
Evaluate **locked** strategy from `locked_strategy.json` on pre-registered holdout.

DSR uses **n_trials_search** from discovery file (multiple testing adjustment for
the random search budget).

Run **after** `discover_strategy.py` (which only uses pre-holdout data).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.creative_runner import run_creative_trial
from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.deflated_sharpe import deflated_sharpe_ratio
from tactical_aa_research.engine import calmar, cagr, max_dd, sharpe_ann
from tactical_aa_research.macro_data import load_macro_monthly, macro_features
from tactical_aa_research.macro_strategy import COST_BPS_DEFAULT
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha
from tactical_aa_research.validation_config import HOLDOUT_START

LOCK_PATH = Path(__file__).resolve().parent / "locked_strategy.json"


def prep_macro(px):
    m = load_macro_monthly("2005-01-01")
    return macro_features(m).shift(1).reindex(px.index)


def bench_spy(px):
    return px["SPY"].pct_change().reindex(px.index)


def equity(net):
    return (1 + net.fillna(0)).cumprod()


def metrics(net):
    e = equity(net)
    cg = cagr(e)
    md = max_dd(e)
    return cg, calmar(cg, md), md, sharpe_ann(net)


def main():
    if not LOCK_PATH.exists():
        raise SystemExit(f"Missing {LOCK_PATH} — run python3 tactical_aa_research/discover_strategy.py first")

    payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    n_trials = int(payload["n_trials_search"])
    t = payload["params"]

    px, first = native_panel_from_common_start("2005-01-01")
    mf = prep_macro(px)
    hold = px.loc[px.index >= HOLDOUT_START]
    mf_h = mf.loc[hold.index]

    net = run_creative_trial(hold, mf_h, t, cost_bps=COST_BPS_DEFAULT)
    cg, cm, md, sh = metrics(net)
    bh = bench_spy(hold)
    excess = align_diff(net, bh)
    mu_xs, p_boot = block_bootstrap_pvalue(np.asarray(excess, dtype=float), block_size=6, n_boot=8000, seed=2026)
    p_bonf = min(1.0, p_boot * n_trials)
    alpha_b = bonferroni_alpha(n_trials, 0.05)
    sr_ann, psr, dsr = deflated_sharpe_ratio(np.asarray(net.dropna(), dtype=float), n_trials=n_trials)

    print("=== Locked strategy holdout ===")
    print(f"Native start {first.date()} | holdout {HOLDOUT_START.date()} .. {hold.index[-1].date()}")
    print(f"n_trials_search (DSR/Bonferroni): {n_trials}")
    print(f"CAGR {cg:.2%}  Calmar {cm:.2f}  MaxDD {md:.2%}  Sharpe {sh:.2f}")
    print(f"Excess vs SPY mean: {mu_xs*100:.3f} pp/mo  bootstrap p={p_boot:.4f}  Bonf p≈{p_bonf:.4f} (α={alpha_b:.6f})")
    print(f"SR_ann {sr_ann:.3f}  PSR {psr:.4f}  DSR {dsr:.4f}")
    print("\nGates:")
    print(f"  CAGR>15%: {'PASS' if cg>0.15 else 'FAIL'}")
    print(f"  Calmar>1: {'PASS' if cm>1 else 'FAIL'}")
    print(f"  DSR>=0.95: {'PASS' if dsr>=0.95 else 'FAIL'}")
    print(f"  Bonf boot: {'PASS' if p_bonf>=alpha_b else 'FAIL'}")


if __name__ == "__main__":
    main()
