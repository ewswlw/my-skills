import numpy as np
import pandas as pd

from tactical_aa_research.deflated_sharpe import deflated_sharpe_ratio
from tactical_aa_research.stats_rigorous import align_diff, block_bootstrap_pvalue, bonferroni_alpha


def test_align_diff_aligns_and_drops_nans():
    idx = pd.date_range("2022-01-31", periods=16, freq="ME")
    s = pd.Series(np.linspace(0.01, 0.02, len(idx)), index=idx)
    b = pd.Series(np.linspace(0.005, 0.015, len(idx)), index=idx)
    s.iloc[2] = np.nan
    b.iloc[3] = np.nan
    out = align_diff(s, b)
    # 16 rows with 2 nan rows dropped -> 14 aligned points
    assert len(out) == 14
    assert np.isfinite(out).all()


def test_block_bootstrap_pvalue_bounded_outputs():
    rng = np.random.default_rng(123)
    x = rng.normal(loc=0.002, scale=0.01, size=72)
    mu, p = block_bootstrap_pvalue(x, block_size=6, n_boot=1500, seed=9)
    assert np.isfinite(mu)
    assert np.isfinite(p)
    assert 0.0 <= p <= 1.0


def test_bonferroni_alpha_decreases_with_more_tests():
    a1 = bonferroni_alpha(1, 0.05)
    a10 = bonferroni_alpha(10, 0.05)
    a100 = bonferroni_alpha(100, 0.05)
    assert a1 > a10 > a100 > 0


def test_dsr_non_increasing_in_trial_count_for_fixed_returns():
    rng = np.random.default_rng(321)
    # positive-sharpe synthetic monthly stream
    r = rng.normal(loc=0.012, scale=0.03, size=120)
    _, _, dsr_1 = deflated_sharpe_ratio(r, n_trials=1)
    _, _, dsr_10 = deflated_sharpe_ratio(r, n_trials=10)
    _, _, dsr_100 = deflated_sharpe_ratio(r, n_trials=100)
    assert dsr_1 >= dsr_10 >= dsr_100
