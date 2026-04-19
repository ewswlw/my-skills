import numpy as np
import pandas as pd

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
