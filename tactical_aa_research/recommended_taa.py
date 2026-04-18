"""
Tactical AA — native-listed ETF panel only (no proxy stitching), costs, train/test.

Uses the earliest month-end where **all** strategy tickers have real Yahoo data
(see `data_panel.native_panel_from_common_start`). Parameters are fit only on the
train slice; test is the remainder (chronological).

Run:
  python3 tactical_aa_research/recommended_taa.py
"""
from __future__ import annotations

import itertools
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tactical_aa_research.data_panel import native_panel_from_common_start
from tactical_aa_research.engine import backtest_with_costs, build_weights, calmar, cagr, max_dd, sharpe_ann

warnings.filterwarnings("ignore", category=FutureWarning)

DEFAULT_COST_BPS = 10.0
# Chronological split: first 60% of months = train (min 48 months if possible)
TRAIN_FRAC = 0.60
MIN_TRAIN_MONTHS = 48


def equity(net: pd.Series) -> pd.Series:
    return (1 + net.fillna(0)).cumprod()


def evaluate(
    weights: pd.DataFrame,
    px: pd.DataFrame,
    *,
    blend: float,
    vol_lb: int,
    vol_tgt: float,
    lev_lo: float,
    lev_hi: float,
    cost_bps: float,
) -> dict:
    net, _, _, _ = backtest_with_costs(
        weights, px, vol_lb, vol_tgt, lev_lo, lev_hi, cost_bps_per_unit_turnover=cost_bps
    )
    eq = equity(net)
    cg = cagr(eq)
    md = max_dd(eq)
    return {
        "blend": blend,
        "vol_lb": vol_lb,
        "vol_tgt": vol_tgt,
        "lev_lo": lev_lo,
        "lev_hi": lev_hi,
        "cagr": cg,
        "calmar": calmar(cg, md),
        "mdd": md,
        "sharpe": sharpe_ann(net),
        "net": net,
        "eq": eq,
    }


def train_test_split(px: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    n = len(px)
    split = max(MIN_TRAIN_MONTHS, int(n * TRAIN_FRAC))
    if split >= n - 12:
        split = max(36, n // 2)
    train = px.iloc[:split].copy()
    test = px.iloc[split:].copy()
    return train, test, train.index[-1]


def pick_params_train_only(
    px_full: pd.DataFrame,
    train_end: pd.Timestamp,
    *,
    cost_bps: float,
) -> dict | None:
    train = px_full.loc[:train_end]
    blends = np.round(np.linspace(0.05, 0.45, 41), 3)
    cache = {float(b): build_weights(px_full, float(b)) for b in blends}
    best = None
    best_score = -np.inf
    for b in blends:
        w = cache[float(b)].loc[train.index]
        for vol_lb, vol_tgt, lev_hi in itertools.product(
            [6, 9, 12, 15, 18],
            [0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18],
            [1.5, 2.0, 2.5, 3.0, 3.5],
        ):
            m = evaluate(
                w,
                train,
                blend=float(b),
                vol_lb=int(vol_lb),
                vol_tgt=float(vol_tgt),
                lev_lo=1.0,
                lev_hi=float(lev_hi),
                cost_bps=cost_bps,
            )
            if np.isnan(m["cagr"]) or np.isnan(m["calmar"]):
                continue
            if m["cagr"] <= 0.15 or m["calmar"] <= 1.0:
                continue
            s = m["calmar"] * m["cagr"]
            if s > best_score:
                best_score = s
                best = {
                    "blend": float(b),
                    "vol_lb": int(vol_lb),
                    "vol_tgt": float(vol_tgt),
                    "lev_lo": 1.0,
                    "lev_hi": float(lev_hi),
                    "train_cagr": m["cagr"],
                    "train_calmar": m["calmar"],
                    "train_mdd": m["mdd"],
                }
    return best


def main(cost_bps: float = DEFAULT_COST_BPS) -> None:
    px, common_start = native_panel_from_common_start("2005-01-01")
    train, test, train_end = train_test_split(px)

    print("DeepLogic tactical AA — **native ETF prices only** (no stitching)")
    print(f"First month with all tickers non-null: {common_start.date()}")
    print(f"Panel: {px.index[0].date()} .. {px.index[-1].date()}  (n={len(px)} months)")
    print(f"Train: ..{train_end.date()} ({len(train)} mo) | Test: {len(test)} mo ({test.index[0].date()} ..)")
    print(f"Transaction cost: {cost_bps:.1f} bps per unit turnover on |Δ(L·w)|\n")

    picked = pick_params_train_only(px, train_end, cost_bps=cost_bps)
    if picked is None:
        print(
            f"TRAIN: no grid point met CAGR>15% AND Calmar>1 at {cost_bps:.0f} bps. "
            "Using fallback: blend=0.15, vol_lb=9, vol_tgt=0.13, lev_hi=2.5\n"
        )
        params = dict(blend=0.15, vol_lb=9, vol_tgt=0.13, lev_lo=1.0, lev_hi=2.5)
    else:
        params = {k: picked[k] for k in ("blend", "vol_lb", "vol_tgt", "lev_lo", "lev_hi")}
        print("TRAIN-selected parameters (frozen for test):")
        print(params)
        print(
            f"  Train: CAGR {picked['train_cagr']:.2%}  Calmar {picked['train_calmar']:.2f}  "
            f"MaxDD {picked['train_mdd']:.2%}\n"
        )

    w_full = build_weights(px, params["blend"])
    full = evaluate(w_full, px, cost_bps=cost_bps, **params)
    oos = evaluate(w_full.loc[test.index], test, cost_bps=cost_bps, **params)

    print("FULL sample (includes train period — informational):")
    print(
        f"  CAGR {full['cagr']:.2%}  Calmar {full['calmar']:.2f}  MaxDD {full['mdd']:.2%}  Sharpe {full['sharpe']:.2f}"
    )
    print("\nOUT-OF-SAMPLE (frozen params):")
    print(
        f"  CAGR {oos['cagr']:.2%}  Calmar {oos['calmar']:.2f}  MaxDD {oos['mdd']:.2%}  Sharpe {oos['sharpe']:.2f}"
    )

    print("\n--- Notes ---")
    print(
        "Native-only start is set by the **latest** ETF inception among the sleeve "
        "(typically 3× funds). No proxy stitching — earlier macro history is omitted "
        "rather than synthesized."
    )


if __name__ == "__main__":
    main()
