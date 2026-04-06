"""Purged K-Fold, LightGBM / ExtraTrees training, prediction export."""

from __future__ import annotations

from typing import Any, Generator, Tuple

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, roc_auc_score

try:
    import lightgbm as lgb
except ImportError:
    lgb = None  # type: ignore[assignment]


class PurgedKFold:
    """
    K-Fold cross-validation with purging and embargo for financial time series.

    Training indices exclude test fold, purge window before test, and embargo after test.
    """

    def __init__(
        self,
        n_splits: int = 5,
        embargo_pct: float = 0.01,
        purge_window: int = 1,
    ) -> None:
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct
        self.purge_window = purge_window

    def split(
        self,
        X: pd.DataFrame,
        y: pd.Series | None = None,
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        n = len(X)
        embargo_size = max(1, int(n * self.embargo_pct))
        fold_size = max(1, n // self.n_splits)

        for i in range(self.n_splits):
            test_start = i * fold_size
            test_end = min((i + 1) * fold_size, n)
            test_idx = np.arange(test_start, test_end)
            purge_start = max(0, test_start - self.purge_window)
            embargo_end = min(n, test_end + embargo_size)
            excluded = set(range(purge_start, embargo_end))
            train_idx = np.array([j for j in range(n) if j not in excluded])
            if len(train_idx) == 0:
                continue
            yield train_idx, test_idx

    def get_n_splits(self) -> int:
        return self.n_splits


def purged_cv_score(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    embargo_pct: float = 0.01,
    purge_window: int = 1,
    scoring: str = "mse",
    sample_weight: pd.Series | None = None,
) -> dict[str, Any]:
    """Evaluate regression or classification model with purged K-fold CV."""
    pkf = PurgedKFold(n_splits, embargo_pct, purge_window)
    scores: list[float] = []
    fold_details: list[dict[str, Any]] = []

    for fold_i, (train_idx, test_idx) in enumerate(pkf.split(X, y)):
        model_clone = clone(model)
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        fit_kwargs: dict[str, Any] = {}
        if sample_weight is not None:
            fit_kwargs["sample_weight"] = sample_weight.iloc[train_idx].values
        model_clone.fit(X_train, y_train, **fit_kwargs)

        if scoring == "mse":
            pred = model_clone.predict(X_test)
            score = float(mean_squared_error(y_test, pred))
        elif scoring == "accuracy":
            score = float(accuracy_score(y_test, model_clone.predict(X_test)))
        elif scoring == "auc":
            score = float(
                roc_auc_score(y_test, model_clone.predict_proba(X_test)[:, 1])
            )
        else:
            score = float(model_clone.score(X_test, y_test))

        scores.append(score)
        fold_details.append(
            {
                "fold": fold_i,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
                "test_start": X.index[test_idx[0]],
                "test_end": X.index[test_idx[-1]],
                "score": score,
            }
        )

    return {
        "scores": scores,
        "mean": float(np.mean(scores)) if scores else 0.0,
        "std": float(np.std(scores)) if scores else 0.0,
        "folds": pd.DataFrame(fold_details),
    }


DEFAULT_LGBM_PARAMS: dict[str, Any] = {
    "n_estimators": 500,
    "learning_rate": 0.01,
    "max_depth": 7,
    "num_leaves": 64,
    "min_child_samples": 100,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "verbose": -1,
}

DEFAULT_ET_PARAMS: dict[str, Any] = {
    "n_estimators": 600,
    "max_features": 0.3,
    "random_state": 42,
    "n_jobs": -1,
}


def train_lightgbm(
    X: pd.DataFrame,
    y: pd.Series,
    params: dict[str, Any] | None = None,
) -> Any:
    """Train LightGBM regressor (optional early stopping if eval_set provided by caller)."""
    if lgb is None:
        raise ImportError("lightgbm is required for train_lightgbm")
    p = {**DEFAULT_LGBM_PARAMS, **(params or {})}
    reg = lgb.LGBMRegressor(**p)
    reg.fit(X, y)
    return reg


def train_extratrees(
    X: pd.DataFrame,
    y: pd.Series,
    params: dict[str, Any] | None = None,
) -> ExtraTreesRegressor:
    """Train ExtraTrees regressor (robust baseline)."""
    p = {**DEFAULT_ET_PARAMS, **(params or {})}
    reg = ExtraTreesRegressor(**p)
    reg.fit(X, y)
    return reg


def shap_top_features(
    model: Any,
    X: pd.DataFrame,
    feature_names: list[str],
    top_n: int = 8,
) -> list[tuple[str, float]]:
    """Mean |SHAP| for LightGBM if shap available; else feature_importances_."""
    try:
        import shap

        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(X.iloc[: min(500, len(X))])
        mean_abs = np.abs(sv).mean(axis=0)
        ranked = sorted(
            zip(feature_names, mean_abs.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_n]
    except Exception:
        if hasattr(model, "feature_importances_"):
            fi = model.feature_importances_
            ranked = sorted(
                zip(feature_names, fi.tolist()),
                key=lambda x: x[1],
                reverse=True,
            )
            return ranked[:top_n]
        return []


def generate_predictions(
    model: Any,
    X: pd.DataFrame,
    dates: pd.Series | None = None,
    tickers: pd.Series | None = None,
) -> pd.DataFrame:
    """Row-aligned predictions for upload (date, ticker, value)."""
    pred = model.predict(X)
    out = pd.DataFrame({"value": pred})
    if dates is not None:
        out["date"] = dates.values
    if tickers is not None:
        out["ticker"] = tickers.values
    return out
