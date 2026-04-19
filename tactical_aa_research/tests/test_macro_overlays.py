import numpy as np
import pandas as pd

from tactical_aa_research.creative_runner import run_creative_trial
from tactical_aa_research.strategy_macro import apply_macro_risk_off, macro_vol_scale


def _weights_and_macro():
    idx = pd.date_range("2021-01-31", periods=24, freq="ME")
    w = pd.DataFrame(
        {
            "UPRO": np.full(len(idx), 0.25),
            "TQQQ": np.full(len(idx), 0.25),
            "TMF": np.full(len(idx), 0.20),
            "AGG": np.full(len(idx), 0.20),
            "BIL": np.full(len(idx), 0.10),
        },
        index=idx,
    )
    # perfectly normalized starting weights
    w = w.div(w.sum(axis=1), axis=0)
    mf = pd.DataFrame(
        {
            "vix_z_12": np.linspace(0.2, 2.0, len(idx)),
            "nfci_z_12": np.linspace(0.1, 1.8, len(idx)),
        },
        index=idx,
    )
    return w, mf


def test_apply_macro_risk_off_preserves_row_normalization_and_non_negative_weights():
    w, mf = _weights_and_macro()
    out = apply_macro_risk_off(
        w,
        mf,
        vix_z_thr=0.8,
        vix_scale=0.2,
        nfci_z_thr=0.9,
        nfci_scale=0.2,
    )
    assert (out >= -1e-12).all().all()
    assert np.allclose(out.sum(axis=1).values, np.ones(len(out)))


def test_macro_vol_scale_stays_within_bounds():
    _, mf = _weights_and_macro()
    scale = macro_vol_scale(mf, vix_hi=1.0, scale_min=0.65)
    assert np.isfinite(scale).all()
    assert (scale >= 0.65 - 1e-12).all()
    assert (scale <= 1.0 + 1e-12).all()


def test_no_leverage_breadth_gate_creative_runner_executes():
    idx = pd.date_range("2020-01-31", periods=36, freq="ME")
    cols = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ", "AGG", "BIL", "UPRO", "TQQQ", "TMF", "CASH"]
    px = pd.DataFrame(index=idx, columns=cols, dtype=float)
    t = np.arange(len(idx), dtype=float)
    for i, c in enumerate(cols):
        px[c] = (95 + 2 * i) * (1 + 0.0035 * t + 0.002 * np.sin(t / 4.0 + i))

    mf = pd.DataFrame(
        {
            "vix_z_12": np.linspace(0.1, 1.8, len(idx)),
            "nfci_z_12": np.linspace(0.2, 1.3, len(idx)),
        },
        index=idx,
    )
    trial = {
        "blend": 0.12,
        "tact_share": 0.62,
        "w_eq": 0.80,
        "mom_abs": 8,
        "mom_fast": 2,
        "top_k": 2,
        "vol_lb": 9,
        "vol_tgt": 0.14,
        "lev_hi": 1.0,
        "vix_z_thr": 0.7,
        "vix_scale": 0.18,
        "nfci_z_thr": 0.8,
        "nfci_scale": 0.12,
        "use_vol_scale": True,
        "use_dd_scale": True,
        "use_breadth_gate": True,
        "breadth_mom_abs": 8,
        "breadth_thr": 0.55,
        "breadth_floor": 0.60,
        "dd_start": -0.10,
        "dd_floor": 0.65,
        "vix_hi_scale": 1.0,
        "scale_min": 0.70,
    }
    net = run_creative_trial(
        px,
        mf,
        trial,
        cost_bps=10.0,
        portfolio_leverage_allowed=False,
        portfolio_leverage_cap=1.0,
    )
    assert np.isfinite(net.fillna(0.0)).all()


def test_no_leverage_regime_override_creative_runner_executes():
    idx = pd.date_range("2020-01-31", periods=36, freq="ME")
    cols = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ", "AGG", "BIL", "UPRO", "TQQQ", "TMF", "CASH"]
    px = pd.DataFrame(index=idx, columns=cols, dtype=float)
    t = np.arange(len(idx), dtype=float)
    for i, c in enumerate(cols):
        px[c] = (96 + 1.5 * i) * (1 + 0.003 * t + 0.0025 * np.cos(t / 5.0 + i))

    mf = pd.DataFrame(
        {
            "vix_z_12": np.linspace(0.2, 1.9, len(idx)),
            "nfci_z_12": np.linspace(0.1, 1.4, len(idx)),
        },
        index=idx,
    )
    trial = {
        "blend": 0.10,
        "tact_share": 0.66,
        "w_eq": 0.76,
        "mom_abs": 8,
        "mom_fast": 2,
        "top_k": 2,
        "vol_lb": 9,
        "vol_tgt": 0.14,
        "lev_hi": 1.0,
        "vix_z_thr": 0.7,
        "vix_scale": 0.18,
        "nfci_z_thr": 0.8,
        "nfci_scale": 0.12,
        "use_vol_scale": True,
        "use_dd_scale": True,
        "use_breadth_gate": True,
        "breadth_mom_abs": 8,
        "breadth_thr": 0.55,
        "breadth_floor": 0.60,
        "use_regime_override": True,
        "regime_use_vix": True,
        "regime_use_nfci": True,
        "regime_breadth_thr": 0.45,
        "regime_vix_z_thr": 1.1,
        "regime_nfci_z_thr": 1.0,
        "regime_agg_share": 0.65,
        "regime_tmf_share": 0.20,
        "dd_start": -0.10,
        "dd_floor": 0.65,
        "vix_hi_scale": 1.0,
        "scale_min": 0.70,
    }
    net = run_creative_trial(
        px,
        mf,
        trial,
        cost_bps=10.0,
        portfolio_leverage_allowed=False,
        portfolio_leverage_cap=1.0,
    )
    assert np.isfinite(net.fillna(0.0)).all()
