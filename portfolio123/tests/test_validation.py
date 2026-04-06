"""PSR / DSR / validate_strategy."""

import numpy as np
import pandas as pd

from pipeline.validation import (
    deflated_sharpe_ratio,
    probabilistic_sharpe_ratio,
    validate_strategy,
)


def test_psr_finite() -> None:
    rng = np.random.default_rng(2)
    r = pd.Series(rng.standard_normal(250) * 0.01)
    out = probabilistic_sharpe_ratio(r, benchmark_sr=0.0, periods_per_year=252)
    assert 0 <= out["psr"] <= 1
    assert "sr_observed" in out


def test_dsr_single_trial_is_one() -> None:
    d = deflated_sharpe_ratio(
        observed_sharpe=1.0,
        n_trials=1,
        n_observations=200,
        skewness=0.0,
        kurtosis=3.0,
    )
    assert d == 1.0


def test_validate_strategy_keys() -> None:
    rng = np.random.default_rng(3)
    r = pd.Series(rng.standard_normal(300) * 0.01)
    v = validate_strategy(r, n_trials=3, benchmark_sr=0.0, periods_per_year=252)
    assert "psr" in v and "dsr" in v and "max_drawdown" in v
