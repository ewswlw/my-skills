"""
Tactical AA — from 2003, stitched proxies, transaction costs, train / test split.

DeepLogic (see DEELOGIC.md): parameters are chosen **only** on 2003–2012; 2013+ is
reported out-of-sample with those frozen settings. Full-sample numbers are labeled.

We do **not** claim unconditional live edge; synthetic pre-LETF 3× history is biased high.
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

from tactical_aa_research.data_panel import build_panel, trim_from
from tactical_aa_research.engine import backtest_with_costs, build_weights, calmar, cagr, max_dd, sharpe_ann

warnings.filterwarnings("ignore", category=FutureWarning)

TRAIN_END = pd.Timestamp("2012-12-31")
DEFAULT_COST_BPS = 10.0


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
    w = weights if weights is not None else build_weights(px, blend)
    net, _, _, _ = backtest_with_costs(
        w, px, vol_lb, vol_tgt, lev_lo, lev_hi, cost_bps_per_unit_turnover=cost_bps
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


def pick_params_train_only(
    px_full: pd.DataFrame,
    *,
    cost_bps: float,
) -> dict | None:
    """
    Grid search **only** on train window; maximize Calmar*CAGR subject to both gates.
    Uses cached weights per blend for speed.
    """
    train = px_full.loc[:TRAIN_END]
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
    px = trim_from(build_panel("1998-01-01"), "2003-01-01")
    test = px.loc[TRAIN_END + pd.offsets.MonthEnd(1) :]

    print("DeepLogic tactical AA — stitched panel from 2003, monthly, costs")
    print(f"Panel: {px.index[0].date()} .. {px.index[-1].date()}  (n={len(px)})")
    print(f"Transaction cost: {cost_bps:.1f} bps per unit turnover on |Δ(L·w)|\n")

    picked = pick_params_train_only(px, cost_bps=cost_bps)
    if picked is None:
        print("TRAIN (2003–2012): no grid point met CAGR>15% AND Calmar>1 at this cost level.")
        print("Using documented fallback (not train-optimal): blend=0.15, vol_lb=9, vol_tgt=0.13, lev_hi=2.5\n")
        params = dict(blend=0.15, vol_lb=9, vol_tgt=0.13, lev_lo=1.0, lev_hi=2.5)
    else:
        params = {k: picked[k] for k in ("blend", "vol_lb", "vol_tgt", "lev_lo", "lev_hi")}
        print("TRAIN-selected parameters (frozen for test):")
        print(params)
        print(
            f"  Train metrics: CAGR {picked['train_cagr']:.2%}  Calmar {picked['train_calmar']:.2f}  "
            f"MaxDD {picked['train_mdd']:.2%}\n"
        )

    w_full = build_weights(px, params["blend"])
    full = evaluate(w_full, px, cost_bps=cost_bps, **params)
    oos = evaluate(w_full.loc[test.index], test, cost_bps=cost_bps, **params)

    print("FULL sample (informational — includes train period):")
    print(
        f"  CAGR {full['cagr']:.2%}  Calmar {full['calmar']:.2f}  MaxDD {full['mdd']:.2%}  Sharpe {full['sharpe']:.2f}"
    )
    print("\nOUT-OF-SAMPLE (2013–present, frozen params):")
    print(
        f"  CAGR {oos['cagr']:.2%}  Calmar {oos['calmar']:.2f}  MaxDD {oos['mdd']:.2%}  Sharpe {oos['sharpe']:.2f}"
    )

    print("\n--- DeepLogic verdict ---")
    if picked is not None and (oos["cagr"] < 0.15 or oos["calmar"] < 1.0):
        print(
            "Train-period tuning found parameters that met both gates historically on 2003–2012, "
            "but **out-of-sample** performance does not simultaneously clear CAGR>15% and Calmar>1 "
            f"at {cost_bps:.0f} bps/month turnover costs. Treat live deployment as experimental.\n"
        )
    print(
        "Synthetic stitched 3× LETF history before listing **overstates** achievable returns vs "
        "real funds; raising costs to ~12–15 bps/unit turnover typically removes all train-period "
        "solutions that meet both gates.\n"
        "No Yahoo-backtested strategy warrants **full confidence** for live capital; validate with "
        "paper trading, smaller size, and a platform-grade simulator (e.g. Portfolio123) if available."
    )


if __name__ == "__main__":
    main()
