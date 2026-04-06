"""Feature screening and FFD."""

import numpy as np
import pandas as pd

from pipeline.feature_engineering import (
    compute_ffd,
    screen_factors,
    screen_factors_panel,
)


def test_screen_factors_passes_strong_correlation() -> None:
    rng = np.random.default_rng(42)
    x = rng.standard_normal(200)
    y = 0.5 * x + 0.1 * rng.standard_normal(200)
    idx = pd.RangeIndex(200)
    r = screen_factors(pd.Series(x, index=idx), pd.Series(y, index=idx), threshold=3.0)
    assert r["passed"] is True
    assert abs(r["t_stat"]) > 3.0


def test_screen_factors_panel() -> None:
    rows = []
    for d in pd.date_range("2020-01-01", periods=10, freq="W"):
        for _t in range(30):
            rows.append(
                {
                    "date": d,
                    "ticker": f"T{_t}",
                    "f1": np.random.randn(),
                    "fwd": np.random.randn() * 0.01,
                }
            )
    df = pd.DataFrame(rows)
    out = screen_factors_panel(df, ["f1"], "fwd", min_names_per_date=10, threshold=1.0)
    assert "f1" in out


def test_ffd_produces_series() -> None:
    rng = np.random.default_rng(0)
    price = pd.Series(np.cumsum(rng.standard_normal(300)) + 100)
    ffd = compute_ffd(price, d=0.4, threshold=1e-4)
    valid = ffd.dropna()
    assert len(valid) > 10
    assert np.isfinite(valid.values).all()
