# Feature Engineering for Algorithmic Trading

## Core Principles

1. **Features encode hypotheses** — every feature should represent a testable economic belief
2. **Stationarity is required** — ML models assume stationary inputs; non-stationary features produce spurious predictions
3. **Memory matters** — aggressive differencing achieves stationarity but destroys predictive information
4. **Less is more for small datasets** — with N < 2,000, each additional feature costs statistical power

---

## Feature Families

### 1. Momentum / Trend

Rate of change over lookback window N.

```python
# Simple momentum (Rate of Change)
mom_N = (price[t] - price[t-N]) / price[t-N]

# Multi-timeframe momentum (create for each horizon)
for N in [2, 4, 8, 13, 26, 52]:  # weeks
    df[f'mom_{N}w'] = df['price'].pct_change(N)

# Exponential Moving Average crossover
ema_fast = df['price'].ewm(span=4).mean()
ema_slow = df['price'].ewm(span=12).mean()
df['ema_crossover'] = (ema_fast - ema_slow) / ema_slow
```

**When to use:** Trending assets (equity indices, FX trends, credit spreads during risk events).

**Asset-specific notes:**
- Equities: 1-12 month momentum well-documented (Jegadeesh & Titman)
- Credit: spread momentum (4w, 13w) captures risk-on/risk-off drift
- FX: 1-3 month carry + momentum combination most robust
- Commodities: 12-month momentum on front-month futures

**Pitfalls:**
- Whipsaws in range-bound markets — combine with regime filter
- Short lookbacks (1-2 weeks) are noisy; long lookbacks (>26 weeks) are laggy
- Momentum crashes during regime transitions (2008, 2020)

---

### 2. Mean Reversion / Z-Scores

Deviation from a rolling or expanding mean, normalized by standard deviation.

```python
# Expanding z-score (point-in-time safe, uses all history)
expanding_mean = df['spread'].expanding(min_periods=26).mean()
expanding_std = df['spread'].expanding(min_periods=26).std()
df['z_score'] = (df['spread'] - expanding_mean) / expanding_std

# Rolling z-score (fixed window)
roll_mean = df['spread'].rolling(52).mean()
roll_std = df['spread'].rolling(52).std()
df['z_roll_52'] = (df['spread'] - roll_mean) / roll_std

# Multi-window z-scores
for window in [13, 26, 52, 104]:
    mu = df['spread'].rolling(window).mean()
    sigma = df['spread'].rolling(window).std()
    df[f'z_{window}w'] = (df['spread'] - mu) / sigma
```

**When to use:** Spreads, pairs, credit OAS, interest rates — anything mean-reverting.

**Asset-specific notes:**
- Credit: OAS z-scores are strong mean-reversion signals; expanding window preferred for structural shifts
- FX: PPP-based z-scores for long-horizon mean reversion
- Equities: sector-relative z-scores more stable than absolute

**Pitfalls:**
- Window too short (< 13 periods) → dominated by noise
- Window too long (> 104 periods) → includes regime changes that shouldn't inform current level
- Expanding z-score avoids window choice but may be sluggish in trending markets
- **Always use min_periods** to avoid divide-by-zero with small samples

---

### 3. Fractional Differentiation (FFD)

Makes a series stationary while preserving as much long-range memory as possible. Standard integer differencing (d=1, i.e., returns) achieves stationarity but destroys memory. Fractional differencing (0 < d < 1) is the optimal compromise.

```python
# Fixed-width window Fractional Differentiation (FFD)
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def frac_diff_ffd(series: pd.Series, d: float, threshold: float = 1e-4) -> pd.Series:
    """
    Apply fixed-width window fractional differentiation.
    
    Args:
        series: Input price/level series
        d: Fractional differencing order (0 < d < 1)
           d=0 → original series (full memory, non-stationary)
           d=1 → standard returns (stationary, no memory)
           d=0.3-0.5 → sweet spot for most financial series
        threshold: Minimum weight to include (controls window width)
    
    Returns:
        Fractionally differenced series
    """
    # Compute weights
    weights = [1.0]
    k = 1
    while abs(weights[-1]) >= threshold:
        w = -weights[-1] * (d - k + 1) / k
        weights.append(w)
        k += 1
    weights = np.array(weights[::-1])
    width = len(weights)
    
    # Apply filter
    result = pd.Series(index=series.index, dtype=float)
    for i in range(width - 1, len(series)):
        result.iloc[i] = np.dot(weights, series.iloc[i - width + 1:i + 1].values)
    
    return result.dropna()

# Finding optimal d: binary search for minimum d that passes ADF
def find_min_d(series: pd.Series, max_d: float = 1.0, significance: float = 0.05) -> float:
    """Find minimum d that achieves stationarity (ADF p < significance)."""
    for d in np.arange(0.0, max_d + 0.05, 0.05):
        diffed = frac_diff_ffd(series, d)
        if len(diffed) < 20:
            continue
        adf_pvalue = adfuller(diffed.dropna(), maxlag=1)[1]
        if adf_pvalue < significance:
            return round(d, 2)
    return max_d

# Usage
df['cad_oas_ffd'] = frac_diff_ffd(df['cad_oas'], d=0.4)
df['vix_ffd'] = frac_diff_ffd(df['vix'], d=0.3)
```

**Typical d values by asset:**
| Series Type | Typical d | Notes |
|-------------|-----------|-------|
| Equity prices | 0.3-0.5 | Prices are I(1), need moderate differencing |
| Credit spreads | 0.2-0.4 | Spreads are more mean-reverting, need less |
| VIX | 0.2-0.4 | Mean-reverting but persistent |
| Interest rates | 0.3-0.6 | Can be quite persistent |
| FX rates | 0.4-0.6 | Close to random walk |

**Pitfalls:**
- d too high (> 0.7) → destroys memory, approaches standard returns
- d too low (< 0.2) → may still be non-stationary
- Always verify with ADF test after differencing
- FFD width (controlled by threshold) affects how many lagged observations are used

---

### 4. Volatility Features

```python
# Rolling realized volatility
for window in [4, 8, 13, 26, 52]:
    df[f'vol_{window}w'] = df['return'].rolling(window).std() * np.sqrt(52)  # annualized

# EWMA volatility (more responsive)
df['vol_ewma'] = df['return'].ewm(span=12).std() * np.sqrt(52)

# Volatility of volatility (regime instability indicator)
df['vol_of_vol'] = df['vol_13w'].rolling(13).std()

# Parkinson volatility (if high/low available)
df['vol_parkinson'] = np.sqrt(
    (1 / (4 * np.log(2))) * (np.log(df['high'] / df['low'])) ** 2
).rolling(20).mean() * np.sqrt(252)

# Volatility regime (binary)
vol_percentile = df['vol_13w'].expanding().rank(pct=True)
df['high_vol_regime'] = (vol_percentile > 0.80).astype(int)
```

**When to use:** Risk management, position sizing, regime detection, volatility targeting.

**Pitfalls:**
- Lookback window must match strategy horizon
- Annualization factor depends on frequency (252 daily, 52 weekly, 12 monthly)
- Volatility clustering means recent vol is most informative → EWMA often better than SMA

---

### 5. Cross-Asset Features

```python
# Lead-lag relationships (e.g., US IG leads CAD IG)
df['us_ig_mom_4w'] = df['us_ig_index'].pct_change(4)
df['us_hy_mom_4w'] = df['us_hy_index'].pct_change(4)

# Rolling correlation
df['corr_cad_spx_26w'] = df['cad_ig_return'].rolling(26).corr(df['spx_return'])

# Spread between related assets
df['cad_us_ig_diff'] = df['cad_oas'] - df['us_ig_oas']

# Rolling beta
cov = df['cad_ig_return'].rolling(52).cov(df['spx_return'])
var = df['spx_return'].rolling(52).var()
df['beta_to_spx'] = cov / var
```

**Asset-specific patterns:**
- Credit: US IG/HY often leads CAD IG by 1-4 weeks (larger, more liquid market)
- Equities: SPX momentum predicts risk-on/risk-off in credit
- FX: Rate differentials lead carry returns
- Commodities: Equity-commodity correlation regime shifts signal macro changes

---

### 6. Yield Curve Features

```python
# Slope
df['yc_slope'] = df['us_10y'] - df['us_2y']  # or 10y - 3m

# Curvature (butterfly)
df['yc_curvature'] = 2 * df['us_5y'] - df['us_2y'] - df['us_10y']

# Level (average of 2y, 5y, 10y)
df['yc_level'] = (df['us_2y'] + df['us_5y'] + df['us_10y']) / 3

# Changes
for N in [1, 4, 13]:
    df[f'yc_slope_chg_{N}w'] = df['yc_slope'].diff(N)
    df[f'yc_level_chg_{N}w'] = df['yc_level'].diff(N)
```

**When to use:** Fixed income, credit, and macro-sensitive equity strategies.

---

### 7. Entropy Features

Shannon entropy measures market "disorder" — proxy for information arrival rate and market efficiency.

```python
import numpy as np

def shannon_entropy(returns: pd.Series, n_bins: int = 10) -> float:
    """Compute Shannon entropy of return distribution."""
    counts, _ = np.histogram(returns.dropna(), bins=n_bins)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

# Rolling entropy
df['entropy_20w'] = df['return'].rolling(20).apply(
    lambda x: shannon_entropy(x, n_bins=8), raw=False
)
```

**When to use:** Market efficiency proxy — high entropy = more random, low entropy = more predictable.

**Pitfalls:** Sensitive to bin count and window size. Use n_bins = 8-12 and window ≥ 20.

---

### 8. Kalman Filter (Adaptive Trend)

```python
from pykalman import KalmanFilter

def kalman_trend(series: pd.Series, n_dim_state: int = 2) -> pd.Series:
    """
    Extract trend using Kalman filter (local linear trend model).
    State: [level, slope]. Observation: price.
    """
    kf = KalmanFilter(
        transition_matrices=np.array([[1, 1], [0, 1]]),
        observation_matrices=np.array([[1, 0]]),
        initial_state_mean=[series.iloc[0], 0],
        em_vars=['transition_covariance', 'observation_covariance',
                 'initial_state_covariance']
    )
    kf = kf.em(series.values, n_iter=10)
    state_means, _ = kf.filter(series.values)
    return pd.Series(state_means[:, 0], index=series.index, name='kalman_trend')

df['kalman_level'] = kalman_trend(df['price'])
df['kalman_slope'] = df['kalman_level'].diff()
```

---

## Feature Selection Workflow

### SHAP-Driven Selection (Recommended)

```python
import shap

# 1. Train initial model with all features
model.fit(X_train, y_train)

# 2. Compute SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)

# 3. Rank by mean absolute SHAP value
importance = pd.Series(
    np.abs(shap_values).mean(axis=0),
    index=X_train.columns
).sort_values(ascending=False)

# 4. Select top features (rule of thumb: N_features ≤ N_train / 10)
n_select = min(len(importance), len(X_train) // 10)
selected_features = importance.head(n_select).index.tolist()
```

### Feature Importance Methods Comparison

| Method | Pros | Cons | When to Use |
|--------|------|------|-------------|
| **SHAP** | Theoretically grounded, handles interactions | Slow for large datasets | Primary method for final selection |
| **MDI** (Mean Decrease Impurity) | Fast, built into tree models | Biased toward high-cardinality features | Quick initial screening |
| **MDA** (Mean Decrease Accuracy) | Unbiased, permutation-based | Slow, affected by correlated features | Validation of SHAP results |
| **Recursive Feature Elimination** | Wrapper method, model-agnostic | Very slow | Small feature sets only |

### Stationarity Verification

```python
from statsmodels.tsa.stattools import adfuller

def check_stationarity(df: pd.DataFrame, features: list, significance: float = 0.05):
    """Verify all features are stationary."""
    results = {}
    for feat in features:
        adf_stat, p_value, *_ = adfuller(df[feat].dropna(), maxlag=4)
        results[feat] = {'adf_stat': adf_stat, 'p_value': p_value,
                         'stationary': p_value < significance}
    return pd.DataFrame(results).T

# Usage: all features should have stationary=True
stationarity = check_stationarity(df, feature_cols)
failing = stationarity[~stationarity['stationary']]
# → Apply fractional differentiation to failing features
```

---

## Autonomous Factor Discovery

Traditional feature engineering relies on a static cookbook of known features. Autonomous factor discovery uses **symbolic reasoning** to systematically compose novel alpha factors from interpretable primitives, governed by a strict grammar that keeps results auditable.

### Interpretable Primitives

All composed factors must be built from these base primitives. Never use raw price levels — always use transforms that are economically interpretable.

| Category | Primitives | Examples |
|---|---|---|
| **Price-relative** | `pct_change(N)`, `rank(pct_change(N))`, `log_return(N)` | 4w momentum, cross-sectional return rank |
| **Volume** | `volume_ratio(N)`, `volume_zscore(N)`, `obv_slope(N)` | Volume vs 20-day average, OBV trend |
| **Volatility state** | `realized_vol(N)`, `vol_ratio(fast, slow)`, `vol_zscore(N)` | Vol regime, vol compression/expansion |
| **Mean-reversion** | `z_score(series, N)`, `percentile(series, N)` | Spread z-score, percentile rank |
| **Structural** | `slope(series, N)`, `curvature(a, b, c)`, `correlation(x, y, N)` | Yield curve slope, rolling beta |

### Factor Grammar

Composed factors are expressions built by applying **operators** to primitives. The grammar enforces auditability.

```
FACTOR       := OPERATOR(PRIMITIVE, ...) | OPERATOR(FACTOR, PRIMITIVE)
OPERATOR     := rank | z_score | lag | diff | ratio | product | max | min | conditional
PRIMITIVE    := (see table above)
MAX_DEPTH    := 3   (no more than 3 nested operations)
```

**Composition rules:**
1. Every leaf node must be an interpretable primitive — no magic numbers or opaque transforms
2. Maximum nesting depth of 3 — deeper compositions are unauditable
3. Every composed factor must have a one-sentence economic rationale *before* computation
4. Cross-sectional operators (`rank`, `z_score`) are preferred over raw values for comparability

```python
# Example: composing a "liquidity-adjusted momentum" factor
# Rationale: momentum signals are stronger when confirmed by above-average volume

# Primitives
mom_13w = df['price'].pct_change(13)
vol_ratio = df['volume'].rolling(4).mean() / df['volume'].rolling(26).mean()

# Composed factor (depth=2): product(rank(momentum), rank(volume_ratio))
factor = mom_13w.rank(pct=True) * vol_ratio.rank(pct=True)

# Depth check: rank(pct_change) = depth 1, product(rank, rank) = depth 2 ✓
```

### Symbolic Regression for Factor Search

When the hypothesis space is large, use symbolic regression to search over factor grammar expressions programmatically.

```python
from gplearn.genetic import SymbolicRegressor

def symbolic_factor_search(
    X: pd.DataFrame,
    y: pd.Series,
    population_size: int = 500,
    generations: int = 20,
    parsimony_coefficient: float = 0.01,
) -> dict:
    """
    Search for novel factor expressions via symbolic regression.

    Args:
        X: Primitive features (columns = interpretable primitives)
        y: Forward returns or labels
        population_size: GP population size
        generations: Evolution generations
        parsimony_coefficient: Penalty for complexity (higher = simpler expressions)

    Returns:
        Dict with best program expression, fitness, and complexity
    """
    sr = SymbolicRegressor(
        population_size=population_size,
        generations=generations,
        parsimony_coefficient=parsimony_coefficient,
        function_set=['add', 'sub', 'mul', 'div', 'sqrt', 'abs', 'max', 'min'],
        max_samples=0.8,
        random_state=42,
        n_jobs=-1,
    )
    sr.fit(X.values, y.values)

    return {
        'expression': str(sr._program),
        'fitness': sr._program.fitness_,
        'complexity': sr._program.length_,
        'feature_names': X.columns.tolist(),
    }

# CRITICAL: record total evaluations for DSR
# n_trials = population_size * generations
# Every expression tested counts toward the multiple-testing penalty
```

### LLM-Assisted Factor Ideation

When using an AI coding agent, the agent itself can act as a factor hypothesis generator. The protocol:

1. **Agent proposes** a market inefficiency and a factor expression using the grammar above
2. **Agent provides** a one-sentence behavioral or structural rationale (the ReAct reasoning trace — see SKILL.md Step 1)
3. **Only then** does the agent write code to compute and test the factor
4. If the factor fails the screening gate (see below), the agent logs the failure and proposes a *different* hypothesis — not a parameter tweak of the same one

This prevents the agent from degenerating into a brute-force parameter optimizer.

---

## Factor Screening Gate

**MANDATORY** — run after feature construction, before labeling (Step 4). Every candidate factor must pass this gate to enter the model. This prevents the "Factor Zoo" problem and limits the multiple-testing penalty at DSR time.

**Cross-series timing (lead–lag, Granger):** If the factor uses **lagged** values of another series to predict a **target** return, use `lead-lag-predictive-inclusion.md` for **causal alignment**, **transmission** story, and how **|t|>3** IC fits together with **Granger** (predictive inclusion) — the screening gate still applies to factors **as they enter the model**; do not replace it with a single full-sample test.

### Hurdle: |t-statistic| > 3.0

```python
from scipy import stats

def screen_factors(
    factors: pd.DataFrame,
    forward_returns: pd.Series,
    t_threshold: float = 3.0,
) -> dict:
    """
    Screen candidate factors via univariate t-test against forward returns.

    Args:
        factors: DataFrame where each column is a candidate factor
        forward_returns: Next-period returns (point-in-time, no look-ahead)
        t_threshold: Minimum |t-stat| to pass (default 3.0)

    Returns:
        Dict with 'passed' (list of names), 'failed' (list), and 'details' (DataFrame)
    """
    results = []
    for col in factors.columns:
        valid = factors[col].dropna()
        aligned_returns = forward_returns.reindex(valid.index).dropna()
        common = valid.index.intersection(aligned_returns.index)

        if len(common) < 30:
            results.append({'factor': col, 't_stat': 0, 'p_value': 1.0,
                            'ic': 0, 'passed': False, 'reason': 'insufficient_data'})
            continue

        ic = valid.loc[common].corr(aligned_returns.loc[common])

        # t-stat for information coefficient
        n = len(common)
        t_stat = ic * np.sqrt(n - 2) / np.sqrt(1 - ic**2) if abs(ic) < 1 else 0

        results.append({
            'factor': col,
            't_stat': round(t_stat, 2),
            'p_value': round(2 * (1 - stats.t.cdf(abs(t_stat), df=n-2)), 4),
            'ic': round(ic, 4),
            'passed': abs(t_stat) > t_threshold,
            'reason': 'passed' if abs(t_stat) > t_threshold else 'below_hurdle',
        })

    details = pd.DataFrame(results)
    passed = details[details['passed']]['factor'].tolist()
    failed = details[~details['passed']]['factor'].tolist()

    print(f"Factor Screening: {len(passed)}/{len(details)} passed (|t| > {t_threshold})")
    for _, row in details.iterrows():
        status = '✓' if row['passed'] else '✗'
        print(f"  {status} {row['factor']}: t={row['t_stat']}, IC={row['ic']}")

    return {'passed': passed, 'failed': failed, 'details': details}
```

### Temporal Isolation

- **Screening** uses only in-sample data (the training set from Step 5)
- **OOS validation** in Steps 6-7 must use data the factor has never seen during screening
- Never screen on full data then validate on a subset — this leaks information

### Integration with Discovery Memory

Every screened factor — passed or failed — should be logged in the discovery memory (see `strategy-improvement.md` Section C). Failed factors with near-miss t-stats (2.0-3.0) are candidates for refinement in the next discovery cycle.
