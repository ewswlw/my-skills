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
