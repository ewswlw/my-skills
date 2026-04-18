"""
PSR / DSR on **monthly** returns.

Mertens (2002) variance applies to the Sharpe ratio at the **same frequency** as the
returns (here: monthly). Annualized Sharpe is SR_m * sqrt(12); delta-method first order:
Var(SR_ann) ≈ 12 * Var(SR_m).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats


def sharpe_inflation_factor(n_trials: int) -> float:
    if n_trials <= 1:
        return 0.0
    return float(math.sqrt(2.0 * math.log(max(n_trials, 2))))


def sharpe_variance_monthly(sr_m: float, n: int, skew: float, excess_kurt: float) -> float:
    """Variance of monthly Sharpe ratio estimator (Mertens-style)."""
    if n < 3:
        return float("inf")
    g1, g2 = skew, excess_kurt
    num = 1.0 - g1 * sr_m + (g2 / 4.0) * (sr_m**2)
    return max(num / max(n - 1, 1), 1e-12)


def probabilistic_sharpe_ratio(
    returns: np.ndarray,
    *,
    sr_benchmark_ann: float = 0.0,
) -> tuple[float, float, float, float, float]:
    """
    Returns (sharpe_ann, psr, var_sr_ann, skew, excess_kurt) on monthly returns.
    """
    x = np.asarray(returns, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 12:
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan")
    mu = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    if sd < 1e-12:
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan")
    sr_m = mu / sd
    sr_ann = float(sr_m * math.sqrt(12.0))
    skew = float(stats.skew(x, bias=False))
    excess_kurt = float(stats.kurtosis(x, fisher=True, bias=False))
    var_m = sharpe_variance_monthly(sr_m, n, skew, excess_kurt)
    var_ann = 12.0 * var_m
    se_ann = math.sqrt(var_ann)
    z = (sr_ann - sr_benchmark_ann) / max(se_ann, 1e-12)
    psr = float(stats.norm.cdf(z))
    return sr_ann, psr, var_ann, skew, excess_kurt


def deflated_sharpe_ratio(
    returns: np.ndarray,
    *,
    n_trials: int,
    sr_benchmark_ann: float = 0.0,
) -> tuple[float, float, float]:
    """Returns (sr_ann, psr, dsr)."""
    sr, psr, var_ann, skew, ek = probabilistic_sharpe_ratio(returns, sr_benchmark_ann=sr_benchmark_ann)
    if not np.isfinite(sr):
        return sr, psr, float("nan")
    se_ann = math.sqrt(var_ann)
    bump = sharpe_inflation_factor(n_trials) * se_ann
    z_defl = (sr - sr_benchmark_ann - bump) / max(se_ann, 1e-12)
    dsr = float(stats.norm.cdf(z_defl))
    return sr, psr, dsr
