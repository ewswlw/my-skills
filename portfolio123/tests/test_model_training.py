"""Purged K-Fold splits."""

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from pipeline.model_training import PurgedKFold, purged_cv_score


def test_purged_kfold_excludes_test_region() -> None:
    X = pd.DataFrame(np.arange(100).reshape(100, 1), columns=["a"])
    y = pd.Series(np.arange(100))
    pkf = PurgedKFold(n_splits=5, embargo_pct=0.02, purge_window=3)
    for train_idx, test_idx in pkf.split(X, y):
        ex = set(range(max(0, test_idx.min() - 3), min(100, test_idx.max() + int(100 * 0.02) + 1)))
        assert not set(train_idx) & set(test_idx)
        assert len(train_idx) > 0


def test_purged_cv_score_runs() -> None:
    rng = np.random.default_rng(1)
    X = pd.DataFrame(rng.standard_normal((80, 3)), columns=["a", "b", "c"])
    y = pd.Series(rng.standard_normal(80))
    m = Ridge(alpha=1.0)
    out = purged_cv_score(m, X, y, n_splits=3, scoring="mse")
    assert "mean" in out
    assert len(out["scores"]) >= 1
