"""
Rigorous lightweight inference on **monthly** return differences vs benchmark.

- Block bootstrap of mean(excess) with circular / block resampling (preserves some autocorrelation).
- Bonferroni adjustment for multiple strategy trials.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def align_diff(
    strat: pd.Series,
    bench: pd.Series,
) -> np.ndarray:
    s = strat.astype(float)
    b = bench.astype(float)
    df = pd.concat([s, b], axis=1).dropna()
    if len(df) < 12:
        return np.array([])
    return (df.iloc[:, 0] - df.iloc[:, 1]).values


def block_bootstrap_pvalue(
    excess: np.ndarray,
    *,
    block_size: int = 6,
    n_boot: int = 4000,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Circular block bootstrap of the mean. H0: mean = 0 (two-sided percentile p-value).
    Returns (mean_excess, p_value).
    """
    x = np.asarray(excess, dtype=float)
    n = len(x)
    if n < 12:
        return float("nan"), float("nan")
    mu = float(np.mean(x))
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_size))
    # circular blocks

    def one_stat() -> float:
        starts = rng.integers(0, n, size=n_blocks)
        samp = []
        for st in starts:
            samp.append(x[(np.arange(block_size, dtype=int) + int(st)) % n])
        samp = np.concatenate(samp)[:n]
        return float(np.mean(samp))

    boots = np.array([one_stat() for _ in range(n_boot)])
    p = 2 * min(float(np.mean(boots >= mu)), float(np.mean(boots <= mu)), 0.5)
    return mu, float(np.clip(p, 0.0, 1.0))


def bonferroni_alpha(n_tests: int, family_alpha: float = 0.05) -> float:
    return family_alpha / max(int(n_tests), 1)


def sharpe_monthly(r: pd.Series) -> float:
    x = r.dropna().astype(float)
    if len(x) < 12 or float(x.std()) < 1e-12:
        return float("nan")
    return float(x.mean() / x.std() * np.sqrt(12))
