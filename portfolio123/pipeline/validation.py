"""PSR, DSR, walk-forward analysis, drawdown, parameter robustness."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kurtosis as scipy_kurtosis
from scipy.stats import norm, skew as scipy_skew

from . import config


def calculate_drawdown(equity_curve: pd.Series) -> dict[str, Any]:
    """Max drawdown from cumulative equity curve."""
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    return {
        "series": pd.DataFrame(
            {
                "drawdown": drawdown,
                "running_max": running_max,
            }
        ),
        "max_drawdown": float(drawdown.min()),
    }


def probabilistic_sharpe_ratio(
    returns: pd.Series,
    benchmark_sr: float = 1.0,
    periods_per_year: int = 252,
) -> dict[str, Any]:
    """PSR: significance of Sharpe vs benchmark (ml-algo-trading reference)."""
    r = returns.dropna()
    if len(r) < 10 or r.std() == 0:
        return {
            "psr": 0.0,
            "sr_observed": 0.0,
            "passes": False,
            "skewness": 0.0,
            "kurtosis": 3.0,
        }
    sr_obs = float(r.mean() / r.std() * math.sqrt(periods_per_year))
    n = len(r)
    skewness = float(scipy_skew(r, nan_policy="omit"))
    kurt = float(scipy_kurtosis(r, fisher=False, nan_policy="omit"))
    numerator = (sr_obs - benchmark_sr) * math.sqrt(n - 1)
    denom_sq = 1 - skewness * sr_obs + (kurt - 1) / 4 * sr_obs**2
    if denom_sq <= 0:
        return {
            "psr": 0.0,
            "sr_observed": sr_obs,
            "passes": False,
            "skewness": skewness,
            "kurtosis": kurt,
        }
    psr = float(norm.cdf(numerator / math.sqrt(denom_sq)))
    return {
        "psr": psr,
        "sr_observed": sr_obs,
        "benchmark_sr": benchmark_sr,
        "skewness": skewness,
        "kurtosis": kurt,
        "n_observations": n,
        "passes": psr > config.PSR_THRESHOLD,
    }


def expected_max_sharpe(n_trials: int, mean_sharpe: float = 0.0, std_sharpe: float = 1.0) -> float:
    """Expected maximum Sharpe under null from n independent trials."""
    gamma = 0.5772156649
    emax = (1 - gamma) * norm.ppf(1 - 1 / n_trials) + gamma * norm.ppf(
        1 - 1 / (n_trials * np.e)
    )
    return mean_sharpe + std_sharpe * emax


def deflated_sharpe_ratio(
    observed_sharpe: float,
    n_trials: int,
    n_observations: int,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    mean_sharpe: float = 0.0,
    std_sharpe: float = 1.0,
) -> float:
    """
    DSR probability (0–1). Uses total Pearson kurtosis (normal = 3).
    """
    if n_observations <= 1 or observed_sharpe <= 0:
        return 0.0
    if n_trials <= 1:
        return 1.0
    emax_sr = expected_max_sharpe(n_trials, mean_sharpe, std_sharpe)
    variance = (
        1.0 - skewness * observed_sharpe + (kurtosis - 1.0) / 4.0 * observed_sharpe**2
    ) / max(n_observations - 1, 1)
    if variance <= 0:
        return 0.0
    se_sr = math.sqrt(variance)
    z = (observed_sharpe - emax_sr) / se_sr
    return float(np.clip(norm.cdf(z), 0.0, 1.0))


def validate_strategy(
    returns: pd.Series,
    n_trials: int = 1,
    benchmark_sr: float = 1.0,
    periods_per_year: int = 252,
) -> dict[str, Any]:
    """Composite: SR, PSR, DSR, drawdown, vol."""
    r = returns.dropna()
    psr_result = probabilistic_sharpe_ratio(r, benchmark_sr, periods_per_year)
    sr = psr_result.get("sr_observed", 0.0)
    dsr = deflated_sharpe_ratio(
        observed_sharpe=sr,
        n_trials=n_trials,
        n_observations=len(r),
        skewness=psr_result.get("skewness", 0.0),
        kurtosis=psr_result.get("kurtosis", 3.0),
    )
    equity = (1 + r).cumprod()
    dd = calculate_drawdown(equity)
    vol = float(r.std() * math.sqrt(periods_per_year))
    return {
        "sharpe_ratio": sr,
        "psr": psr_result["psr"],
        "psr_passes": psr_result["passes"],
        "dsr": dsr,
        "dsr_passes": dsr > config.DSR_THRESHOLD,
        "max_drawdown": dd["max_drawdown"],
        "total_return": float(equity.iloc[-1] - 1) if len(equity) else 0.0,
        "volatility": vol,
        "skewness": psr_result.get("skewness"),
        "kurtosis": psr_result.get("kurtosis"),
    }


def walk_forward_analysis(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    min_train_size: int = 104,
    step_size: int = 1,
    expanding: bool = True,
    max_train_size: int | None = None,
) -> pd.DataFrame:
    """Walk-forward: train on history, predict next step (sklearn clone)."""
    from sklearn.base import clone

    results: list[dict[str, Any]] = []
    n = len(X)
    for test_start in range(min_train_size, n, step_size):
        test_end = min(test_start + step_size, n)
        if expanding:
            train_start = 0
        else:
            train_start = max(0, test_start - (max_train_size or min_train_size))
        X_train = X.iloc[train_start:test_start]
        y_train = y.iloc[train_start:test_start]
        X_test = X.iloc[test_start:test_end]
        y_test = y.iloc[test_start:test_end]
        m = clone(model)
        m.fit(X_train, y_train)
        preds = m.predict(X_test)
        for i in range(len(X_test)):
            results.append(
                {
                    "date": X_test.index[i],
                    "train_size": len(X_train),
                    "prediction": preds[i],
                    "actual": float(y_test.iloc[i]),
                }
            )
    return pd.DataFrame(results).set_index("date")


def parameter_robustness_test(
    model_factory: Any,
    X: pd.DataFrame,
    y: pd.Series,
    base_params: dict[str, Any],
    param_keys: list[str],
    perturbation: float = 0.2,
) -> pd.DataFrame:
    """Perturb selected params by ±perturbation; report test MSE."""
    from sklearn.base import clone
    from sklearn.metrics import mean_squared_error
    from sklearn.model_selection import train_test_split

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, shuffle=False
    )
    rows: list[dict[str, Any]] = []
    for key in param_keys:
        base_v = base_params[key]
        for mult in (1 - perturbation, 1 + perturbation):
            p = {**base_params}
            if isinstance(base_v, int):
                p[key] = max(1, int(round(base_v * mult)))
            else:
                p[key] = base_v * mult
            m = model_factory(**p)
            m.fit(X_tr, y_tr)
            pred = m.predict(X_te)
            rows.append(
                {
                    "param": key,
                    "multiplier": mult,
                    "mse": float(mean_squared_error(y_te, pred)),
                }
            )
    return pd.DataFrame(rows)
