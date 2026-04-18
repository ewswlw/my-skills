"""Fast parameter scan: cache `build_weights` per blend (expensive part).

Default: **native ETF panel** (no stitching), same train/test split as `recommended_taa.py`.
Pass `--stitched` to run the legacy 2003 stitched panel + fixed 2012 split.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tactical_aa_research.data_panel import build_panel, native_panel_from_common_start, trim_from
from tactical_aa_research.engine import backtest_with_costs, build_weights, calmar, cagr, max_dd

COST_BPS = 10.0
TRAIN_FRAC = 0.60
MIN_TRAIN_MONTHS = 48


def metrics(net: pd.Series) -> tuple[float, float, float]:
    eq = (1 + net.fillna(0)).cumprod()
    cg = cagr(eq)
    md = max_dd(eq)
    return cg, calmar(cg, md), md


def split_train_test(px: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    n = len(px)
    split = max(MIN_TRAIN_MONTHS, int(n * TRAIN_FRAC))
    if split >= n - 12:
        split = max(36, n // 2)
    train = px.iloc[:split].copy()
    test = px.iloc[split:].copy()
    return train, test, train.index[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stitched", action="store_true", help="Use stitched 2003 panel + 2012 split")
    args = ap.parse_args()

    if args.stitched:
        px = trim_from(build_panel("1998-01-01"), "2003-01-01")
        train = px.loc[: pd.Timestamp("2012-12-31")]
        test = px.loc[pd.Timestamp("2012-12-31") + pd.offsets.MonthEnd(1) :]
        print("Mode: STITCHED from 2003, train ends 2012-12")
    else:
        px, first = native_panel_from_common_start("2005-01-01")
        train, test, te = split_train_test(px)
        print(f"Mode: NATIVE only, common start {first.date()}, train ends {te.date()}")

    blends = np.round(np.linspace(0.05, 0.45, 41), 3)
    weight_cache = {b: build_weights(px, float(b)) for b in blends}

    def scan_window(label: str, win: pd.DataFrame) -> list[tuple]:
        hits = []
        for b in blends:
            w = weight_cache[float(b)].loc[win.index]
            for lb, tgt, hi in itertools.product(
                [6, 9, 12, 15, 18],
                [0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18],
                [1.5, 2.0, 2.5, 3.0, 3.5],
            ):
                net, _, _, _ = backtest_with_costs(
                    w, win, int(lb), float(tgt), 1.0, float(hi), cost_bps_per_unit_turnover=COST_BPS
                )
                cg, cm, md = metrics(net)
                if cg > 0.15 and cm > 1.0:
                    hits.append((cg * cm, float(b), int(lb), float(tgt), float(hi), cg, cm, md))
        hits.sort(reverse=True)
        print(f"{label}: hits={len(hits)}")
        if hits:
            print("  best:", hits[0])
        return hits

    scan_window("FULL", px)
    tr_hits = scan_window("TRAIN", train)

    if tr_hits:
        _, b, lb, tgt, hi, _, _, _ = tr_hits[0]
        w = weight_cache[b].loc[test.index]
        net, _, _, _ = backtest_with_costs(
            w, test, lb, tgt, 1.0, hi, cost_bps_per_unit_turnover=COST_BPS
        )
        cg, cm, md = metrics(net)
        print("OOS with best TRAIN params:", dict(blend=b, vol_lb=lb, vol_tgt=tgt, lev_hi=hi))
        print(f"  CAGR={cg:.2%} Calmar={cm:.2f} MaxDD={md:.2%}")


if __name__ == "__main__":
    main()
