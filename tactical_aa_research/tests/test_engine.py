import numpy as np
import pandas as pd

from tactical_aa_research.engine import (
    backtest_with_costs,
    build_weights_flexible,
    cagr,
    calmar,
    max_dd,
    vol_target_leverage,
)


def _price_panel(n: int = 36) -> pd.DataFrame:
    idx = pd.date_range("2018-01-31", periods=n, freq="ME")
    cols = [
        "SPY",
        "QQQ",
        "IWM",
        "EFA",
        "EEM",
        "TLT",
        "GLD",
        "VNQ",
        "AGG",
        "CASH",
        "UPRO",
        "TQQQ",
        "TMF",
        "BIL",
    ]
    data = {}
    for i, c in enumerate(cols):
        # deterministic positive prices with mild trend + mild seasonality
        base = 100 + 3 * i
        t = np.arange(n, dtype=float)
        data[c] = base * (1 + 0.004 * t + 0.002 * np.sin(t / 4.0 + i))
    return pd.DataFrame(data, index=idx)


def test_build_weights_flexible_rows_normalized_non_negative():
    px = _price_panel()
    w = build_weights_flexible(
        px,
        0.2,
        mom_abs_c=10,
        mom_fast_c=3,
        top_k_c=3,
        mom_abs_l=10,
        mom_fast_l=2,
        top_k_l=3,
    )
    row_sums = w.sum(axis=1)
    assert np.allclose(row_sums.values, np.ones(len(row_sums)))
    assert (w >= 0).all().all()


def test_vol_target_leverage_respects_clip_bounds_after_warmup():
    idx = pd.date_range("2020-01-31", periods=24, freq="ME")
    unlev = pd.Series(0.01 + 0.005 * np.sin(np.arange(24)), index=idx)
    lev = vol_target_leverage(unlev, lookback=6, target_ann_vol=0.12, lo=1.0, hi=2.0)
    lev_finite = lev.dropna()
    assert not lev_finite.empty
    assert (lev_finite >= 1.0).all()
    assert (lev_finite <= 2.0).all()


def test_backtest_with_costs_cost_drag_and_non_negative_turnover():
    px = _price_panel()
    w = build_weights_flexible(
        px,
        0.25,
        mom_abs_c=10,
        mom_fast_c=3,
        top_k_c=3,
        mom_abs_l=10,
        mom_fast_l=2,
        top_k_l=3,
    )
    net0, gross0, lev0, turn0 = backtest_with_costs(
        w,
        px,
        vol_lb=6,
        vol_tgt=0.12,
        lev_lo=1.0,
        lev_hi=3.0,
        cost_bps_per_unit_turnover=0.0,
    )
    net10, gross10, lev10, turn10 = backtest_with_costs(
        w,
        px,
        vol_lb=6,
        vol_tgt=0.12,
        lev_lo=1.0,
        lev_hi=3.0,
        cost_bps_per_unit_turnover=10.0,
    )
    assert (turn0.fillna(0) >= 0).all()
    assert (turn10.fillna(0) >= 0).all()
    # same gross path regardless of costs
    assert np.allclose(gross0.fillna(0).values, gross10.fillna(0).values)
    # with positive costs, net should not exceed zero-cost net
    assert (net10.fillna(0) <= net0.fillna(0) + 1e-12).all()
    # leverage path unaffected by costs
    assert np.allclose(lev0.fillna(0).values, lev10.fillna(0).values)


def test_backtest_with_costs_can_disable_portfolio_leverage():
    px = _price_panel()
    w = build_weights_flexible(
        px,
        0.25,
        mom_abs_c=10,
        mom_fast_c=3,
        top_k_c=3,
        mom_abs_l=10,
        mom_fast_l=2,
        top_k_l=3,
    )
    net, gross, lev, turn = backtest_with_costs(
        w,
        px,
        vol_lb=6,
        vol_tgt=0.20,
        lev_lo=1.0,
        lev_hi=4.0,
        cost_bps_per_unit_turnover=10.0,
        portfolio_leverage_allowed=False,
        portfolio_leverage_cap=1.0,
    )
    assert np.allclose(lev.fillna(1.0).values, np.ones(len(lev)))
    assert np.isfinite(net.fillna(0)).all()
    assert np.isfinite(gross.fillna(0)).all()
    assert (turn.fillna(0) >= 0).all()


def test_cagr_calmar_helpers_return_finite_values_for_monotone_equity():
    idx = pd.date_range("2021-01-31", periods=24, freq="ME")
    eq = pd.Series(np.linspace(1.0, 1.6, len(idx)), index=idx)
    cg = cagr(eq)
    md = max_dd(eq)
    cm = calmar(cg, md)
    assert np.isfinite(cg)
    assert np.isfinite(md)
    # no drawdown for monotone increasing equity => calmar undefined (nan)
    assert np.isnan(cm)
