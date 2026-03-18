# Model Selection for Algorithmic Trading

## Model Comparison Matrix

| Model | Best For | Min N | Interpretable? | Handles Non-Linear? | Risk of Overfit |
|-------|----------|-------|----------------|---------------------|-----------------|
| **Logistic Regression** | Baseline, tiny data | 100 | High | No | Low |
| **Ridge / Lasso** | Feature selection, regularized | 200 | High | No | Low |
| **Random Forest** | Feature importance, bagging | 500 | Medium | Yes | Medium |
| **Gradient Boosting (GBM)** | Tabular data (primary choice) | 500 | Medium | Yes | Medium-High |
| **LightGBM** | Fast GBM, large feature space | 1,000 | Medium | Yes | Medium-High |
| **XGBoost** | Regularized boosting | 1,000 | Medium | Yes | Medium |
| **CatBoost** | Categorical features, robust | 1,000 | Medium | Yes | Medium |
| **LSTM/GRU** | Sequential patterns | 5,000 | Low | Yes | High |
| **CNN** | Grid/image-like features | 10,000 | Low | Yes | High |
| **Transformer** | Multi-asset attention | 10,000+ | Low | Yes | Very High |

**Default recommendation:** Start with Gradient Boosting (GBM/LightGBM). Only move to deep learning if N > 10,000 AND sequential/spatial patterns are suspected AND GBM baseline is established.

---

## Gradient Boosting — The Workhorse

### Hyperparameter Grid by Data Size

#### Small Data (N < 2,000)

```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=100,       # 50-200; use early stopping
    max_depth=2,            # CRITICAL: keep shallow to prevent overfitting
    learning_rate=0.05,     # Lower = more regularization
    min_samples_leaf=30,    # High minimum to prevent tiny leaves
    subsample=0.8,          # Row subsampling for robustness
    max_features='sqrt',    # Column subsampling
    random_state=42,
)
```

#### Medium Data (N = 2,000-10,000)

```python
import lightgbm as lgb

model = lgb.LGBMClassifier(
    n_estimators=300,
    num_leaves=16,           # 2^max_depth equivalent; keep low
    learning_rate=0.05,
    min_child_samples=20,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,           # L1 regularization
    reg_lambda=1.0,          # L2 regularization
    random_state=42,
    verbose=-1,
)
```

#### Large Data (N > 10,000)

```python
import xgboost as xgb

model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.05,
    min_child_weight=10,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=0.1,               # Min loss reduction for split
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss',
)
```

### Hyperparameter Tuning with Purged CV

```python
from sklearn.model_selection import ParameterGrid

def purged_cv_tune(model_class, param_grid, X, y, 
                   n_splits=5, embargo_pct=0.01, scoring='accuracy'):
    """
    Tune hyperparameters using purged K-fold CV.
    See validation-backtesting.md for PurgedKFold implementation.
    """
    best_score = -np.inf
    best_params = None
    
    for params in ParameterGrid(param_grid):
        scores = []
        for train_idx, test_idx in purged_kfold_split(X, y, n_splits, embargo_pct):
            model = model_class(**params)
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            score = model.score(X.iloc[test_idx], y.iloc[test_idx])
            scores.append(score)
        
        mean_score = np.mean(scores)
        if mean_score > best_score:
            best_score = mean_score
            best_params = params
    
    return best_params, best_score

# Example grid for small data GBM
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [2, 3],
    'learning_rate': [0.01, 0.05, 0.1],
    'min_samples_leaf': [20, 30, 50],
    'subsample': [0.7, 0.8],
}
```

---

## SHAP-Driven Feature Selection

### Workflow

```python
import shap
import numpy as np
import pandas as pd

def shap_feature_selection(
    model, X_train: pd.DataFrame, max_features: int = None,
    min_importance_pct: float = 0.01
) -> list:
    """
    Select features using SHAP importance.
    
    Args:
        model: Trained tree-based model
        X_train: Training features
        max_features: Maximum features to keep (default: N_train / 10)
        min_importance_pct: Minimum SHAP importance as fraction of total
    
    Returns:
        List of selected feature names
    """
    if max_features is None:
        max_features = max(5, len(X_train) // 10)
    
    # Compute SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_train)
    
    # Handle binary classification (may return list of 2 arrays)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Use positive class
    
    # Mean absolute SHAP importance
    importance = pd.Series(
        np.abs(shap_values).mean(axis=0),
        index=X_train.columns
    ).sort_values(ascending=False)
    
    # Normalize to percentages
    importance_pct = importance / importance.sum()
    
    # Apply both filters
    selected = importance_pct[importance_pct >= min_importance_pct].head(max_features)
    
    return selected.index.tolist()

# Usage
model.fit(X_train, y_train)
selected = shap_feature_selection(model, X_train, max_features=12)
print(f"Selected {len(selected)} features: {selected}")

# Retrain with selected features
model_final = GradientBoostingClassifier(**best_params)
model_final.fit(X_train[selected], y_train)
```

### Feature Importance Cross-Validation

Verify that important features are **consistently important** across folds:

```python
def cross_validated_importance(model_class, params, X, y, n_splits=5):
    """
    Check feature importance stability across CV folds.
    Features that are important in ALL folds are trustworthy.
    Features important in only 1-2 folds may be spurious.
    """
    fold_importances = []
    
    for train_idx, test_idx in purged_kfold_split(X, y, n_splits):
        model = model_class(**params)
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(X.iloc[train_idx])
        if isinstance(sv, list):
            sv = sv[1]
        
        imp = pd.Series(np.abs(sv).mean(axis=0), index=X.columns)
        fold_importances.append(imp)
    
    # Stability metrics
    imp_df = pd.DataFrame(fold_importances)
    stability = pd.DataFrame({
        'mean_importance': imp_df.mean(),
        'std_importance': imp_df.std(),
        'cv': imp_df.std() / imp_df.mean(),  # Lower = more stable
        'min_rank': imp_df.rank(ascending=False).max(),  # Worst rank across folds
    }).sort_values('mean_importance', ascending=False)
    
    # Select features with CV < 0.5 (importance doesn't vary too much across folds)
    stable_features = stability[stability['cv'] < 0.5].index.tolist()
    return stable_features, stability
```

---

## Ensemble Methods

### Random Forest (Bagging)

```python
from sklearn.ensemble import RandomForestClassifier

# Use for feature importance baseline, not primary prediction
rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=4,
    min_samples_leaf=20,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
)
```

**When RF > GBM:** Very noisy labels, highly correlated features (bagging decorrelates better than boosting).

### Stacking

```python
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression

# Stack diverse base learners with a simple meta-learner
stacked = StackingClassifier(
    estimators=[
        ('gbm', GradientBoostingClassifier(max_depth=2, n_estimators=100)),
        ('rf', RandomForestClassifier(max_depth=3, n_estimators=200)),
        ('lr', LogisticRegression(C=0.1)),
    ],
    final_estimator=LogisticRegression(C=1.0),
    cv=5,  # IMPORTANT: Replace with PurgedKFold in practice
    passthrough=False,
)
```

**Critical:** The inner CV in StackingClassifier uses standard KFold by default. For financial data, implement custom PurgedKFold and pass via the `cv` parameter.

---

## Linear Models (Baseline)

Always establish a linear baseline before using complex models.

```python
from sklearn.linear_model import LogisticRegression, RidgeClassifier

# Logistic Regression (binary classification)
lr = LogisticRegression(
    C=0.1,              # Inverse regularization strength
    penalty='l2',
    solver='lbfgs',
    max_iter=1000,
    random_state=42,
)

# Ridge Classifier (fast, L2-regularized)
ridge = RidgeClassifier(alpha=1.0, random_state=42)

# Lasso (L1 for automatic feature selection)
from sklearn.linear_model import LogisticRegression
lasso_lr = LogisticRegression(
    C=0.1, penalty='l1', solver='saga', max_iter=1000
)
```

**When to stop at linear:** If linear model achieves > 55% accuracy with AUC > 0.55, non-linear models may add overfitting risk without proportional gain (especially for N < 500).

---

## Model Evaluation Metrics for Trading

Standard ML metrics (accuracy, AUC) don't fully capture trading performance. Supplement with:

| Metric | Formula | Target | Why |
|--------|---------|--------|-----|
| **Hit Rate** | Correct predictions / total | > 52% (weekly) | Minimum for profitability after costs |
| **Information Coefficient** | corr(predicted, actual) | > 0.05 | Measures signal quality |
| **Alpha** | Strategy return - benchmark return (annualized) | Asset-class dependent | The bottom line |
| **Sharpe Ratio** | Mean excess return / σ (annualized) | > 1.0 | Risk-adjusted return |
| **Calmar Ratio** | Annualized return / max drawdown | > 1.0 | Return per unit of worst loss |
| **Profit Factor** | Gross profit / gross loss | > 1.5 | Reward-to-risk on trades |

```python
def trading_metrics(returns: pd.Series, benchmark: pd.Series = None, freq: int = 52):
    """Compute trading-specific model evaluation metrics."""
    ann_return = (1 + returns.mean()) ** freq - 1
    ann_vol = returns.std() * np.sqrt(freq)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    max_dd = (returns.cumsum() - returns.cumsum().cummax()).min()
    calmar = ann_return / abs(max_dd) if max_dd != 0 else np.inf
    
    metrics = {
        'ann_return': ann_return,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'calmar': calmar,
        'hit_rate': (returns > 0).mean(),
    }
    
    if benchmark is not None:
        alpha = ann_return - ((1 + benchmark.mean()) ** freq - 1)
        ic = returns.corr(benchmark)
        metrics['alpha'] = alpha
        metrics['information_coefficient'] = ic
    
    return metrics
```

---

## Non-Linear Factor Aggregation

### Why Not Just Average Factors?

A simple IC-weighted linear combination of alpha factors assumes:
- Each factor contributes independently (no interactions)
- Factor weights are constant across all market regimes
- Returns scale linearly with factor exposure

All three assumptions are wrong in practice. A LightGBM synthesis layer captures:
- **Interaction effects**: two correlated momentum factors don't stack linearly — the GBM learns diminishing returns
- **Regime-dependent thresholds**: factor X works only when factor Y is above a certain level
- **Non-linear payoffs**: a volatility factor may be valuable only in its extremes, not linearly

### Pattern: Factors as Inputs, GBM as Synthesizer

This is distinct from using GBM as a direct predictor on raw features. Here, each input to the GBM is an **already-validated alpha factor** (passed the |t| > 3.0 screening gate). The GBM's job is to learn optimal *combination logic*, not raw prediction.

```
Raw Data -> Primitives -> Factor Grammar -> Screening Gate (|t|>3) -> Validated Factors
                                                                          |
                                                              GBM Synthesis Layer
                                                                          |
                                                              Combined Alpha Signal
```

### Implementation

```python
import lightgbm as lgb
import numpy as np
import pandas as pd

def build_synthesis_layer(
    factor_matrix: pd.DataFrame,
    forward_returns: pd.Series,
    n_splits: int = 5,
    embargo_pct: float = 0.01,
) -> dict:
    """
    Train a LightGBM model to combine validated alpha factors non-linearly.

    Args:
        factor_matrix: DataFrame where each column is a validated factor
                       (all must have passed |t-stat| > 3.0)
        forward_returns: Next-period returns for labeling
        n_splits: Purged CV folds
        embargo_pct: Embargo fraction for purged CV

    Returns:
        Dict with trained model, feature importance, and CV scores
    """
    labels = (forward_returns > 0).astype(int)
    common = factor_matrix.dropna().index.intersection(labels.dropna().index)
    X = factor_matrix.loc[common]
    y = labels.loc[common]

    model = lgb.LGBMClassifier(
        n_estimators=200,
        num_leaves=8,           # Shallow — factors are already informative
        learning_rate=0.05,
        min_child_samples=30,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        verbose=-1,
    )

    # Use purged CV for evaluation (see validation-backtesting.md)
    from sklearn.base import clone

    cv_scores = []
    cv_probas = pd.Series(dtype=float, index=common)

    fold_size = len(X) // n_splits
    embargo_size = int(len(X) * embargo_pct)

    for i in range(n_splits):
        test_start = i * fold_size
        test_end = min((i + 1) * fold_size, len(X))
        test_idx = list(range(test_start, test_end))

        purge_start = max(0, test_start - 1)
        embargo_end = min(len(X), test_end + embargo_size)
        excluded = set(range(purge_start, embargo_end))
        train_idx = [j for j in range(len(X)) if j not in excluded]

        m = clone(model)
        m.fit(X.iloc[train_idx], y.iloc[train_idx])
        proba = m.predict_proba(X.iloc[test_idx])[:, 1]
        score = m.score(X.iloc[test_idx], y.iloc[test_idx])

        cv_scores.append(score)
        cv_probas.iloc[test_idx] = proba

    # Train final model on all data
    model.fit(X, y)

    return {
        "model": model,
        "cv_scores": cv_scores,
        "cv_mean": np.mean(cv_scores),
        "cv_std": np.std(cv_scores),
        "oos_probas": cv_probas,
        "feature_importance": pd.Series(
            model.feature_importances_, index=X.columns
        ).sort_values(ascending=False),
    }
```

### Linear Baseline Comparison

Always compare the GBM synthesis layer against a simple IC-weighted linear combination. If the GBM doesn't meaningfully outperform, prefer the linear model for its transparency.

```python
def ic_weighted_combination(
    factor_matrix: pd.DataFrame,
    forward_returns: pd.Series,
) -> pd.Series:
    """
    Baseline: combine factors using IC-weighted linear combination.
    Compare against GBM synthesis to justify non-linear complexity.
    """
    ics = {}
    for col in factor_matrix.columns:
        valid = factor_matrix[col].dropna()
        aligned = forward_returns.reindex(valid.index).dropna()
        common = valid.index.intersection(aligned.index)
        if len(common) > 30:
            ics[col] = valid.loc[common].corr(aligned.loc[common])

    ic_series = pd.Series(ics)
    weights = ic_series / ic_series.sum()

    combined = (factor_matrix[weights.index] * weights).sum(axis=1)
    return combined


def compare_aggregation_methods(
    factor_matrix: pd.DataFrame,
    forward_returns: pd.Series,
    gbm_probas: pd.Series,
    freq: int = 52,
) -> pd.DataFrame:
    """
    Compare GBM synthesis vs IC-weighted linear combination.
    The GBM must outperform to justify its complexity.
    """
    linear_signal = ic_weighted_combination(factor_matrix, forward_returns)

    # Convert signals to returns
    common = forward_returns.dropna().index
    linear_returns = forward_returns.loc[common] * (linear_signal.reindex(common) > linear_signal.median()).astype(int)
    gbm_returns = forward_returns.loc[common] * (gbm_probas.reindex(common) > 0.5).astype(int)

    results = {}
    for name, rets in [("linear_ic_weighted", linear_returns), ("gbm_synthesis", gbm_returns)]:
        ann_ret = (1 + rets.mean()) ** freq - 1
        ann_vol = rets.std() * np.sqrt(freq)
        results[name] = {
            "ann_return": round(ann_ret, 4),
            "sharpe": round(ann_ret / ann_vol, 2) if ann_vol > 0 else 0,
            "hit_rate": round((rets > 0).mean(), 3),
        }

    return pd.DataFrame(results).T
```

### Guard Rails

- The synthesis layer itself **must pass walk-forward validation and DSR** (Steps 6-7) — non-linear aggregation can overfit faster than linear
- Use **shallow trees** (num_leaves=8, max_depth=3) — the inputs are already validated signals, not raw noisy features
- Monitor **feature importance stability** across CV folds — if importance rankings shift dramatically, the GBM is fitting noise
- If GBM Sharpe is < 10% better than linear baseline, prefer the linear model for auditability
