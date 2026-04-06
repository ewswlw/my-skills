"""HMM regime detection, upload as DataSeries, P123 formula snippets."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

from .factor_upload import upload_data_series
from .data_pull import get_client


def fit_hmm_regimes(
    returns: pd.Series,
    n_regimes: int = 2,
    n_iter: int = 100,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Fit Gaussian HMM on (return, rolling vol); return regime labels and probabilities.

    Regimes ordered by mean return (0 = worst, n_regimes-1 = best).
    """
    r = returns.dropna()
    vol = r.rolling(20).std()
    features = pd.DataFrame({"return": r, "vol": vol}).dropna()
    if len(features) < n_regimes * 10:
        raise ValueError("Insufficient history for HMM")

    model = GaussianHMM(
        n_components=n_regimes,
        covariance_type="full",
        n_iter=n_iter,
        random_state=random_state,
    )
    X = features.values
    model.fit(X)
    hidden = model.predict(X)
    probs = model.predict_proba(X)
    result = pd.DataFrame(index=features.index)
    result["regime"] = hidden
    for i in range(n_regimes):
        result[f"prob_regime_{i}"] = probs[:, i]

    # Order regimes by mean return
    rets_on = returns.reindex(features.index)
    regime_means = {
        s: float(rets_on.iloc[hidden == s].mean()) if (hidden == s).any() else 0.0
        for s in range(n_regimes)
    }
    sorted_r = sorted(regime_means, key=regime_means.get)
    order_map = {sorted_r[i]: i for i in range(n_regimes)}
    result["regime_ordered"] = result["regime"].map(order_map)
    return result


def regime_series_for_upload(regime_df: pd.DataFrame) -> pd.DataFrame:
    """Build date + value (use regime_ordered as float) for DataSeries."""
    idx = regime_df.index
    dates = pd.to_datetime(idx)
    return pd.DataFrame(
        {
            "date": dates,
            "value": regime_df["regime_ordered"].astype(float).values,
        }
    )


def upload_regime_signal(
    regime_df: pd.DataFrame,
    name: str = "agent_hmm_regime",
) -> dict[str, Any]:
    """Push regime state to P123 as DataSeries."""
    s = regime_series_for_upload(regime_df)
    with get_client() as client:
        return upload_data_series(
            client,
            name,
            s,
            description="HMM regime from pipeline",
        )


def generate_regime_buy_rules(series_name: str) -> list[str]:
    """Example buy-rule strings referencing DataSeries."""
    return [
        f'DataSeries("{series_name}") < 0.5 AND Rank > 90',
        f'Eval(DataSeries("{series_name}") > 0.5, Rank > 85, Rank > 90)',
    ]


def monitor_regime_health(
    returns: pd.Series,
    regime_df: pd.DataFrame,
    window: int = 52,
) -> dict[str, Any]:
    """Rolling Sharpe by regime; intervention-style flags."""
    r = returns.reindex(regime_df.index).dropna()
    reg = regime_df["regime_ordered"].reindex(r.index).dropna()
    common = r.index.intersection(reg.index)
    r = r.loc[common]
    reg = reg.loc[common]
    by_reg: dict[str, float] = {}
    for label in sorted(reg.unique()):
        rr = r[reg == label]
        if len(rr) < 10:
            continue
        sr = float(rr.mean() / rr.std() * np.sqrt(52)) if rr.std() > 0 else 0.0
        by_reg[f"regime_{int(label)}_sharpe_annual"] = sr
    roll = r.rolling(window).apply(
        lambda x: x.mean() / x.std() * np.sqrt(52) if x.std() > 0 else 0.0
    )
    bad_streak = int((roll < 0).rolling(4).sum().iloc[-1] >= 4) if len(roll) >= 4 else 0
    return {
        "by_regime": by_reg,
        "rolling_sharpe_lt0_4weeks": bool(bad_streak),
    }
