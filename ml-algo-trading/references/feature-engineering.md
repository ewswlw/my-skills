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
