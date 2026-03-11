# Validation & Backtesting for Financial ML

## Why Standard Validation Fails in Finance

1. **Temporal dependence**: Observations are not IID — standard K-Fold creates leakage
2. **Multiple testing**: Testing N strategies inflates the chance of finding a false positive
3. **Regime non-stationarity**: Past performance may not represent future regimes
4. **Label overlap**: Forward-looking labels at adjacent timestamps share common bars

---

## Purged K-Fold Cross-Validation

### Concept

Standard K-Fold randomly assigns observations to folds, allowing future information to leak into training. Purged K-Fold:
1. Splits data **chronologically** into K folds
2. **Purges** training samples whose labels overlap with the test period
3. **Embargoes** training samples that immediately follow the test period

### Implementation

```python
import numpy as np
import pandas as pd
from typing import Generator, Tuple

class PurgedKFold:
    """
    K-Fold cross-validation with purging and embargo for financial time series.
    
    Args:
        n_splits: Number of CV folds (typically 5-10)
        embargo_pct: Fraction of total samples to embargo after each test fold
        purge_window: Number of bars to purge before test fold start
                     (should match label horizon, e.g., 5 for 5-bar forward returns)
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        embargo_pct: float = 0.01,
        purge_window: int = 1,
    ):
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct
        self.purge_window = purge_window
    
    def split(
        self,
        X: pd.DataFrame,
        y: pd.Series = None,
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Generate purged train/test indices.
        
        Yields:
            Tuple of (train_indices, test_indices) as numpy arrays
        """
        n = len(X)
        embargo_size = int(n * self.embargo_pct)
        fold_size = n // self.n_splits
        
        for i in range(self.n_splits):
            test_start = i * fold_size
            test_end = min((i + 1) * fold_size, n)
            
            test_idx = np.arange(test_start, test_end)
            
            # Training indices: everything except test + purge + embargo
            purge_start = max(0, test_start - self.purge_window)
            embargo_end = min(n, test_end + embargo_size)
            
            excluded = set(range(purge_start, embargo_end))
            train_idx = np.array([j for j in range(n) if j not in excluded])
            
            if len(train_idx) == 0:
                continue
            
            yield train_idx, test_idx
    
    def get_n_splits(self):
        return self.n_splits


def purged_cv_score(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    embargo_pct: float = 0.01,
    purge_window: int = 1,
    scoring: str = 'accuracy',
    sample_weight: pd.Series = None,
) -> dict:
    """
    Evaluate model using purged K-fold CV.
    
    Returns:
        Dict with 'scores', 'mean', 'std', and per-fold details
    """
    from sklearn.base import clone
    from sklearn.metrics import accuracy_score, roc_auc_score, log_loss
    
    pkf = PurgedKFold(n_splits, embargo_pct, purge_window)
    scores = []
    fold_details = []
    
    for fold_i, (train_idx, test_idx) in enumerate(pkf.split(X, y)):
        model_clone = clone(model)
        
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        fit_kwargs = {}
        if sample_weight is not None:
            fit_kwargs['sample_weight'] = sample_weight.iloc[train_idx].values
        
        model_clone.fit(X_train, y_train, **fit_kwargs)
        
        if scoring == 'accuracy':
            score = accuracy_score(y_test, model_clone.predict(X_test))
        elif scoring == 'auc':
            score = roc_auc_score(y_test, model_clone.predict_proba(X_test)[:, 1])
        elif scoring == 'neg_log_loss':
            score = -log_loss(y_test, model_clone.predict_proba(X_test))
        else:
            score = model_clone.score(X_test, y_test)
        
        scores.append(score)
        fold_details.append({
            'fold': fold_i,
            'train_size': len(train_idx),
            'test_size': len(test_idx),
            'test_start': X.index[test_idx[0]],
            'test_end': X.index[test_idx[-1]],
            'score': score,
        })
    
    return {
        'scores': scores,
        'mean': np.mean(scores),
        'std': np.std(scores),
        'folds': pd.DataFrame(fold_details),
    }
```

### Choosing Parameters

| Parameter | Guideline | Notes |
|-----------|-----------|-------|
| `n_splits` | 5-10 | More folds = more robust but slower; 5 for small data |
| `embargo_pct` | 0.01-0.02 | 1-2% of total observations |
| `purge_window` | = label horizon | If label uses 5-bar forward return, purge 5 bars |

---

## Walk-Forward Analysis

### Concept

Simulates real-time strategy deployment by training on expanding (or rolling) historical windows and testing on the next unseen period.

### Implementation

```python
def walk_forward_analysis(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    min_train_size: int = 104,
    step_size: int = 1,
    expanding: bool = True,
    max_train_size: int = None,
) -> pd.DataFrame:
    """
    Walk-forward validation.
    
    Args:
        model: Sklearn-compatible model
        X: Feature matrix (time-ordered)
        y: Labels (time-ordered)
        min_train_size: Minimum training window (periods)
        step_size: Number of periods to step forward
        expanding: If True, training window grows; if False, rolling fixed window
        max_train_size: Maximum training window (only for rolling)
    
    Returns:
        DataFrame with per-step predictions and actuals
    """
    from sklearn.base import clone
    
    results = []
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
        
        model_clone = clone(model)
        model_clone.fit(X_train, y_train)
        
        preds = model_clone.predict(X_test)
        if hasattr(model_clone, 'predict_proba'):
            probs = model_clone.predict_proba(X_test)[:, 1]
        else:
            probs = preds.astype(float)
        
        for i in range(len(X_test)):
            results.append({
                'date': X_test.index[i],
                'train_size': len(X_train),
                'prediction': preds[i],
                'probability': probs[i],
                'actual': y_test.iloc[i],
                'correct': preds[i] == y_test.iloc[i],
            })
    
    return pd.DataFrame(results).set_index('date')


def walk_forward_metrics(wf_results: pd.DataFrame, returns: pd.Series, freq: int = 52):
    """
    Compute aggregate and per-window metrics from walk-forward results.
    """
    # Overall metrics
    overall_accuracy = wf_results['correct'].mean()
    
    # Strategy returns (predicted long → earn return; predicted cash → earn 0)
    aligned = returns.reindex(wf_results.index)
    strategy_returns = aligned * wf_results['prediction']
    
    ann_return = (1 + strategy_returns.mean()) ** freq - 1
    ann_vol = strategy_returns.std() * np.sqrt(freq)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    
    # Per-year window consistency
    yearly = strategy_returns.resample('Y').apply(lambda x: (1 + x).prod() - 1)
    pct_profitable_years = (yearly > 0).mean()
    
    # Rolling window consistency (52-week)
    rolling_sharpe = strategy_returns.rolling(52).apply(
        lambda x: x.mean() / x.std() * np.sqrt(52) if x.std() > 0 else 0
    )
    pct_positive_sharpe = (rolling_sharpe > 0).mean()
    
    return {
        'accuracy': overall_accuracy,
        'ann_return': ann_return,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'pct_profitable_years': pct_profitable_years,
        'pct_positive_rolling_sharpe': pct_positive_sharpe,
        'n_predictions': len(wf_results),
    }
```

### Walk-Forward Parameters

| Parameter | Guideline | Notes |
|-----------|-----------|-------|
| `min_train_size` | ≥ 10× n_features | Ensures adequate training data |
| `step_size` | 1 (most granular) | Use larger (4, 13) for speed |
| `expanding` vs `rolling` | Expanding default | Rolling if regime shifts make old data harmful |
| `max_train_size` (rolling) | 2-5× min_train_size | Balances recency vs sample size |

---

## Deflated Sharpe Ratio (DSR)

### The Problem

Testing N strategies and reporting the best Sharpe is selection bias. The expected maximum Sharpe from N random strategies is:

```
E[max(SR)] ≈ (1-γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N×e))
```

where γ ≈ 0.5772 (Euler-Mascheroni constant).

### Implementation

```python
from scipy.stats import norm
import numpy as np

def expected_max_sharpe(n_trials: int, mean_sharpe: float = 0, std_sharpe: float = 1) -> float:
    """
    Expected maximum Sharpe ratio from n_trials independent strategies.
    Based on the Euler-Mascheroni approximation.
    """
    gamma = 0.5772156649  # Euler-Mascheroni constant
    emax = (1 - gamma) * norm.ppf(1 - 1 / n_trials) + gamma * norm.ppf(1 - 1 / (n_trials * np.e))
    return mean_sharpe + std_sharpe * emax


def deflated_sharpe_ratio(
    observed_sharpe: float,
    n_trials: int,
    n_observations: int,
    skewness: float = 0,
    kurtosis: float = 3,
    mean_sharpe: float = 0,
    std_sharpe: float = 1,
) -> float:
    """
    Compute the Deflated Sharpe Ratio.
    
    Args:
        observed_sharpe: Sharpe ratio of the selected strategy
        n_trials: Total number of strategies tested
        n_observations: Number of return observations
        skewness: Skewness of strategy returns
        kurtosis: Excess kurtosis of strategy returns
        mean_sharpe: Assumed mean Sharpe across all trials
        std_sharpe: Assumed std of Sharpe across all trials
    
    Returns:
        DSR probability (0 to 1). DSR < 0.95 suggests data snooping.
    """
    # Expected max Sharpe under null
    emax_sr = expected_max_sharpe(n_trials, mean_sharpe, std_sharpe)
    
    # Standard error of Sharpe estimate (accounting for non-normality)
    se_sr = np.sqrt(
        (1 - skewness * observed_sharpe + (kurtosis - 1) / 4 * observed_sharpe**2)
        / (n_observations - 1)
    )
    
    # DSR = P[SR* > 0 | adjustment for multiple testing]
    if se_sr == 0:
        return 0.0
    
    z = (observed_sharpe - emax_sr) / se_sr
    dsr = norm.cdf(z)
    
    return dsr


# Usage
dsr = deflated_sharpe_ratio(
    observed_sharpe=1.8,    # Best strategy's Sharpe
    n_trials=11,            # Total strategies tested (e.g., 11 iterations)
    n_observations=600,     # Training observations
    skewness=-0.3,          # Negative skew typical for credit
    kurtosis=4.5,           # Fat tails
)
print(f"DSR = {dsr:.3f}")
# DSR < 0.95 → reject: likely result of data snooping
# DSR > 0.95 → cautious acceptance
```

### Interpretation Guide

| DSR | Interpretation | Action |
|-----|---------------|--------|
| > 0.99 | Very strong evidence of genuine alpha | Deploy with confidence |
| 0.95-0.99 | Moderate evidence | Deploy with monitoring |
| 0.80-0.95 | Weak evidence, possible snooping | Investigate further |
| < 0.80 | Likely data snooping | Reject or fundamentally redesign |

---

## Combinatorial Purged Cross-Validation (CPCV)

For more robust estimation than standard purged K-Fold, CPCV tests all combinations of K-choose-2 folds:

```python
from itertools import combinations

def combinatorial_purged_cv(
    model, X, y, n_groups=6, embargo_pct=0.01, purge_window=1
):
    """
    Test all C(n_groups, 2) combinations of test groups.
    More robust than standard K-Fold, especially for small datasets.
    """
    n = len(X)
    group_size = n // n_groups
    groups = [np.arange(i * group_size, min((i+1) * group_size, n))
              for i in range(n_groups)]
    
    all_scores = []
    
    for test_combo in combinations(range(n_groups), 2):
        test_idx = np.concatenate([groups[g] for g in test_combo])
        
        # Purge + embargo
        test_start = test_idx.min()
        test_end = test_idx.max()
        purge_start = max(0, test_start - purge_window)
        embargo_end = min(n, test_end + int(n * embargo_pct))
        
        excluded = set(range(purge_start, embargo_end))
        train_idx = np.array([j for j in range(n) if j not in excluded])
        
        if len(train_idx) < 50:
            continue
        
        from sklearn.base import clone
        m = clone(model)
        m.fit(X.iloc[train_idx], y.iloc[train_idx])
        score = m.score(X.iloc[test_idx], y.iloc[test_idx])
        all_scores.append(score)
    
    return {
        'scores': all_scores,
        'mean': np.mean(all_scores),
        'std': np.std(all_scores),
        'n_combinations': len(all_scores),
    }
```

---

## OOS Degradation Analysis

```python
def oos_degradation(
    train_metric: float,
    test_metric: float,
    threshold: float = 0.20,
) -> dict:
    """
    Compute out-of-sample degradation and flag concern.
    
    Degradation > 20% is a red flag for overfitting.
    """
    if train_metric == 0:
        degradation = 1.0
    else:
        degradation = (train_metric - test_metric) / abs(train_metric)
    
    return {
        'train': train_metric,
        'test': test_metric,
        'degradation_pct': degradation * 100,
        'passes': degradation <= threshold,
        'diagnosis': (
            'PASS' if degradation <= threshold
            else 'FAIL: likely overfitting' if degradation <= 0.40
            else 'FAIL: severe overfitting'
        )
    }
```

---

## Parameter Robustness Testing

```python
def parameter_sensitivity(
    model_class,
    base_params: dict,
    X_train, y_train, X_test, y_test,
    param_name: str,
    perturbation_range: list,
) -> pd.DataFrame:
    """
    Test how sensitive performance is to parameter changes.
    A robust strategy should survive ±20% perturbation.
    """
    results = []
    
    for pct in perturbation_range:
        params = base_params.copy()
        base_value = params[param_name]
        
        if isinstance(base_value, int):
            params[param_name] = max(1, int(base_value * (1 + pct)))
        else:
            params[param_name] = base_value * (1 + pct)
        
        model = model_class(**params)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        
        results.append({
            'perturbation': f"{pct:+.0%}",
            param_name: params[param_name],
            'score': score,
        })
    
    return pd.DataFrame(results)

# Usage
sensitivity = parameter_sensitivity(
    GradientBoostingClassifier, best_params,
    X_train, y_train, X_test, y_test,
    param_name='n_estimators',
    perturbation_range=[-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3],
)
# If score drops >5% with ±20% perturbation → fragile → red flag
```

---

## Probabilistic Sharpe Ratio (PSR)

**Run PSR before DSR.** PSR answers: "Is this Sharpe ratio statistically significant, accounting for fat tails and skew?" DSR then answers: "After testing N strategies, could this have appeared by chance?"

### Formula

```
PSR(SR*) = Φ( (SR - SR*) × √(N-1) / √(1 - γ₃×SR + (γ₄-1)/4 × SR²) )
```

Where SR* is the benchmark Sharpe (typically 0 or 1), γ₃ = skewness, γ₄ = kurtosis.

```python
from scipy.stats import norm, skew, kurtosis
import numpy as np

def probabilistic_sharpe_ratio(
    returns: pd.Series,
    benchmark_sr: float = 1.0,
    periods_per_year: int = 252,
) -> dict:
    """
    Probabilistic Sharpe Ratio: probability that the true SR exceeds a benchmark,
    accounting for non-normality (fat tails and skew in financial returns).
    
    Args:
        returns: Strategy return series
        benchmark_sr: Benchmark to test against (default 1.0 = "is SR > 1?")
        periods_per_year: 252 for daily, 52 for weekly, 12 for monthly
    
    Returns:
        Dict with PSR, observed SR, and interpretation
    
    Interpretation:
        PSR > 0.95: Strong evidence SR exceeds benchmark
        PSR 0.80-0.95: Moderate evidence
        PSR < 0.80: SR estimate is unreliable (insufficient data or fat tails)
    """
    sr_obs = returns.mean() / returns.std() * np.sqrt(periods_per_year)
    n = len(returns)
    skewness = skew(returns)
    kurt = kurtosis(returns, fisher=False)  # Excess kurtosis; normal = 3
    
    # Sharpe ratio standard error accounting for non-normality
    numerator = (sr_obs - benchmark_sr) * np.sqrt(n - 1)
    denominator = np.sqrt(
        1 - skewness * sr_obs + (kurt - 1) / 4 * sr_obs ** 2
    )
    
    if denominator <= 0:
        return {'psr': 0.0, 'sr_obs': sr_obs, 'error': 'denominator non-positive'}
    
    psr = norm.cdf(numerator / denominator)
    
    return {
        'psr': psr,
        'sr_observed': sr_obs,
        'benchmark_sr': benchmark_sr,
        'skewness': skewness,
        'kurtosis': kurt,
        'n_observations': n,
        'passes': psr > 0.95,
        'interpretation': (
            f"PSR = {psr:.3f}: "
            + ("Strong evidence SR > benchmark" if psr > 0.95
               else "Moderate evidence" if psr > 0.80
               else "Weak evidence — unreliable SR estimate")
        ),
    }


# Usage: always run PSR first, then DSR
psr_result = probabilistic_sharpe_ratio(strategy_returns, benchmark_sr=1.0)
print(psr_result['interpretation'])

# If PSR passes, then check for data snooping with DSR
if psr_result['passes']:
    dsr = deflated_sharpe_ratio(
        observed_sharpe=psr_result['sr_observed'],
        n_trials=n_strategies_tested,
        n_observations=len(strategy_returns),
        skewness=psr_result['skewness'],
        kurtosis=psr_result['kurtosis'],
    )
    print(f"DSR = {dsr:.3f} ({'PASS' if dsr > 0.95 else 'FAIL'})")
```

### PSR vs DSR: When to Use Each

| Test | Question Answered | When to Use |
|---|---|---|
| **PSR** | Is this SR statistically significant given its distribution? | Always — first significance gate |
| **DSR** | After testing N strategies, could this SR have appeared by chance? | When N > 1 strategies were tested |

---

## Drawdown Analysis

Drawdown analysis is critical for understanding strategy risk and recovery characteristics. Required for crisis stress-testing and the overfitting prevention checklist.

```python
import pandas as pd
import numpy as np


def calculate_drawdown(equity_curve: pd.Series) -> dict:
    """
    Calculate drawdown series from an equity curve.

    Args:
        equity_curve: Cumulative portfolio value (e.g., (1 + returns).cumprod())

    Returns:
        Dict with keys:
            'series'      — pd.DataFrame with columns: drawdown, running_max, underwater
            'max_drawdown' — float, maximum drawdown (most negative value, e.g. -0.32)
    """
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max

    return {
        'series': pd.DataFrame({
            'drawdown': drawdown,
            'running_max': running_max,
            'underwater': drawdown < 0,
        }),
        'max_drawdown': float(drawdown.min()),
    }


def time_under_water(drawdown_series: pd.Series) -> pd.DataFrame:
    """
    Identify all drawdown periods and their durations.

    Args:
        drawdown_series: Drawdown values (negative when underwater)

    Returns:
        DataFrame with columns: start, end, duration_days, max_drawdown_in_period
    """
    underwater = drawdown_series < 0
    periods = []
    start = None

    for date, is_underwater in underwater.items():
        if is_underwater and start is None:
            start = date
        elif not is_underwater and start is not None:
            period_dd = drawdown_series[start:date].min()
            periods.append({
                'start': start,
                'end': date,
                'duration_days': (date - start).days,
                'max_drawdown_in_period': period_dd,
            })
            start = None

    # Handle open drawdown at end of series
    if start is not None:
        periods.append({
            'start': start,
            'end': drawdown_series.index[-1],
            'duration_days': (drawdown_series.index[-1] - start).days,
            'max_drawdown_in_period': drawdown_series[start:].min(),
        })

    return pd.DataFrame(periods)
```

---

## Kelly Criterion & Dynamic Position Sizing

Convert model probabilities into position sizes. Never size positions without reference to edge.

```python
def kelly_fraction(
    win_prob: float,
    win_loss_ratio: float = 1.0,
    kelly_scale: float = 0.5,
) -> float:
    """
    Kelly Criterion: optimal fraction of capital to bet.
    
    Args:
        win_prob: Model's predicted probability of winning (0.5 to 1.0)
        win_loss_ratio: Expected win size / expected loss size (default 1:1)
        kelly_scale: Scale factor for safety (0.5 = half-Kelly recommended)
    
    Returns:
        Fraction of capital to allocate (0 to 1)
    
    Note:
        Full Kelly is theoretically optimal but practically too aggressive.
        Half-Kelly (kelly_scale=0.5) is the standard institutional choice.
        Quarter-Kelly for high-uncertainty strategies.
    """
    loss_prob = 1 - win_prob
    full_kelly = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
    scaled = max(0.0, full_kelly * kelly_scale)
    return min(1.0, scaled)  # Cap at 100% of capital


def probability_to_position_size(
    prediction_prob: float,
    base_size: float = 1.0,
    kelly_scale: float = 0.5,
    min_prob_threshold: float = 0.55,
) -> float:
    """
    Convert model output probability to position size.
    
    Args:
        prediction_prob: Model's P(positive return) — between 0.5 and 1.0
        base_size: Maximum position size (1.0 = fully invested)
        kelly_scale: Kelly fraction safety scale
        min_prob_threshold: Minimum probability to take any position (default 55%)
    
    Returns:
        Position size between 0 and base_size
    """
    if prediction_prob < min_prob_threshold:
        return 0.0
    
    # Assume 1:1 win/loss ratio — adjust if model outputs expected returns
    size = base_size * kelly_fraction(prediction_prob, kelly_scale=kelly_scale)
    return size


# Usage: size positions by model confidence
probabilities = model.predict_proba(X_test)[:, 1]
position_sizes = np.array([
    probability_to_position_size(p, base_size=1.0, kelly_scale=0.5)
    for p in probabilities
])

# Strategy returns = market returns × position sizes
strategy_returns = market_returns * position_sizes
```

---

## Composite Validation Helper

> **ANNOTATION — convenience reference only.** `validate_strategy()` wraps
> `probabilistic_sharpe_ratio()`, `deflated_sharpe_ratio()`, and `calculate_drawdown()`
> into one call for quick inspection. It is **not a production function.** In production,
> call each function directly to retain full parameter control and avoid silent failures
> from default values that may not match your data frequency or benchmark.

```python
def validate_strategy(
    returns: pd.Series,
    n_trials: int = 1,
    benchmark_sr: float = 1.0,
    periods_per_year: int = 252,
) -> dict:
    """
    Convenience composite: PSR + DSR + drawdown + basic stats in one call.

    Args:
        returns: Strategy return series (daily by default)
        n_trials: Total strategies tested — used for DSR multiple-testing correction
        benchmark_sr: Benchmark Sharpe for PSR gate (default 1.0 = "is SR > 1?")
        periods_per_year: 252 daily, 52 weekly, 12 monthly

    Returns:
        Dict with keys: sharpe_ratio, psr, psr_passes, dsr, dsr_passes,
                        max_drawdown, total_return, volatility

    NOTE: Use individual functions in production for full control.
    """
    sr = returns.mean() / returns.std() * np.sqrt(periods_per_year)
    psr_result = probabilistic_sharpe_ratio(returns, benchmark_sr, periods_per_year)
    dsr = deflated_sharpe_ratio(
        observed_sharpe=sr,
        n_trials=n_trials,
        n_observations=len(returns),
        skewness=psr_result['skewness'],
        kurtosis=psr_result['kurtosis'],
    )

    equity_curve = (1 + returns).cumprod()
    dd = calculate_drawdown(equity_curve)

    return {
        'sharpe_ratio': sr,
        'psr': psr_result['psr'],
        'psr_passes': psr_result['passes'],
        'dsr': dsr,
        'dsr_passes': dsr > 0.95,
        'max_drawdown': dd['max_drawdown'],      # float, e.g. -0.32
        'total_return': equity_curve.iloc[-1] - 1,
        'volatility': returns.std() * np.sqrt(periods_per_year),
    }
```
