# Time Series Predictability Analysis

Run this analysis **before building any predictive model**. It determines whether exploitable signal exists in the series. If it doesn't, no model will extract it — skip to a different asset, timeframe, or hypothesis.

---

## Objective

Assess whether a time series contains low entropy (predictable structure) or is effectively random (high entropy, no edge). Output is a **Predictability Score 0–100** with a clear PROCEED / CAUTION / STOP recommendation. Always run before modeling — a score below 20 means no model architecture will extract signal from the series.

---

## Agent Execution Spec

> **NOTE:** The CONFIG block below is an **agent execution template** — a starting point for configuring an analysis run. Function signature defaults (e.g., `m=2` in `sample_entropy`, `order=3` in `permutation_entropy`) take precedence over CONFIG values in actual code. Override CONFIG values when running for a specific asset/context.

```python
CONFIG = {
    # === DATA SETTINGS ===
    "data_source": "path/to/data.csv",   # or DataFrame, API endpoint
    "target_column": "close",            # column to analyze
    "returns_type": "log",               # "log", "simple", or "raw"
    "frequency": "1D",                   # "1min", "5min", "1H", "1D", etc.

    # === PREPROCESSING ===
    "remove_outliers": True,
    "outlier_threshold": 4.0,            # std deviations
    "handle_missing": "ffill",           # "ffill", "interpolate", "drop"
    "min_observations": 500,             # minimum required data points

    # === ENTROPY ANALYSIS ===
    "entropy_methods": [
        "shannon", "sample_entropy",
        "approximate_entropy", "permutation_entropy", "spectral_entropy"
    ],
    "embedding_dimension": 3,            # for sample/approx entropy (function default: m=2)
    "tolerance": 0.2,                    # as fraction of std dev
    "permutation_order": 3,              # for permutation entropy (function default: order=3)

    # === PREDICTABILITY TESTS ===
    "run_autocorrelation": True,
    "max_lags": 50,
    "run_hurst_exponent": True,
    "run_bds_test": True,
    "run_runs_test": True,
    "run_variance_ratio": True,

    # === BENCHMARKING ===
    "compare_to_shuffled": True,
    "n_shuffle_samples": 100,
    "compare_to_random_walk": True,

    # === REGIME ANALYSIS ===
    "test_regime_dependence": True,
    "regime_window": 50,

    # === THRESHOLDS ===
    "entropy_threshold_low": 0.3,        # below = high predictability
    "entropy_threshold_high": 0.8,       # above = essentially random
    "significance_level": 0.05,

    # === OUTPUT ===
    "output_format": "detailed_report",  # "summary", "detailed_report", "json"
    "save_results": True,
    "output_path": "predictability_analysis.json"
}
```

### 10-Step Execution Order

1. Data Loading & Validation → check length ≥ `min_observations`, handle missing
2. Returns Transformation → log/simple/raw; standardize for entropy calculations
3. Baseline Statistics → mean, std, skew, kurtosis, ADF, Jarque-Bera; flag concerns
4. Entropy Suite → Shannon, SampEn, ApEn, Permutation, Spectral
5. Predictability Tests → ACF/PACF, Hurst, BDS, Runs, Variance Ratio
6. Benchmark Comparison → compare vs 100 shuffled versions + random walk
7. Regime-Conditional Analysis → segment by rolling vol; entropy per regime
8. Multi-Scale Analysis → resample to weekly/monthly; find strongest signal frequency
9. Predictability Score → compute composite 0–100 score with `predictability_score()`
10. Generate Report → output formatted report (template below)

### Report Output Template

```markdown
PREDICTABILITY ANALYSIS REPORT
==============================

## Executive Summary
- Overall Predictability Score: XX/100
- Recommendation: [PROCEED / CAUTION / DO NOT MODEL]
- Primary Signal Source: [autocorrelation / mean-reversion / momentum / regime]

## Data Overview
- Series: [name], Frequency: [freq]
- Observations: N, Date Range: [start] to [end]
- Returns Distribution: μ=X, σ=Y, skew=Z, kurt=W

## Entropy Analysis
| Metric               | Value  | Normalized | Interpretation      |
|----------------------|--------|------------|---------------------|
| Shannon Entropy      | X.XX   | 0.XX       | [Low/Med/High]      |
| Sample Entropy       | X.XX   | -          | [Regular/Irregular] |
| Permutation Entropy  | X.XX   | 0.XX       | [Structured/Random] |
| Spectral Entropy     | X.XX   | 0.XX       | [Cyclical/Noisy]    |

## Predictability Tests
| Test                 | Statistic | P-Value | Conclusion              |
|----------------------|-----------|---------|-------------------------|
| Ljung-Box (20)       | XX.X      | 0.XXX   | [Dependence/No Dep.]    |
| Hurst Exponent       | 0.XX      | -       | [Mean-Rev/RW/Trend]     |
| BDS Test             | X.XX      | 0.XXX   | [Nonlinear/Linear]      |
| Runs Test            | X.XX      | 0.XXX   | [Serial Dep./Random]    |
| Variance Ratio (5)   | X.XX      | 0.XXX   | [Momentum/MR/RW]        |

## Benchmark Comparison
- Entropy vs Shuffled: [X]th percentile (p=0.XXX)
- Entropy vs Random Walk: [X]% [lower/higher]

## Regime Analysis
| Regime     | Entropy | Hurst | Autocorr | Tradeable? |
|------------|---------|-------|----------|------------|
| Low Vol    | 0.XX    | 0.XX  | 0.XX     | [Yes/No]   |
| Med Vol    | 0.XX    | 0.XX  | 0.XX     | [Yes/No]   |
| High Vol   | 0.XX    | 0.XX  | 0.XX     | [Yes/No]   |

## Multi-Scale Summary
| Timeframe  | Entropy | Best Signal Type  |
|------------|---------|-------------------|
| [freq 1]   | 0.XX    | [type]            |
| [freq 2]   | 0.XX    | [type]            |

## Recommendations
1. [Specific guidance based on findings]
2. [Suggested model types if signal exists]
3. [Warnings and caveats]
```

---

## Step 1: Data Preparation

```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox

def prepare_series(prices: pd.Series, returns_type: str = 'log') -> pd.Series:
    """
    Transform price series to returns and standardize for entropy calculations.
    
    Args:
        prices: Raw price series
        returns_type: 'log' (default), 'simple', or 'raw'
    
    Returns:
        Standardized returns series (zero mean, unit variance)
    """
    if returns_type == 'log':
        returns = np.log(prices / prices.shift(1)).dropna()
    elif returns_type == 'simple':
        returns = prices.pct_change().dropna()
    else:
        returns = prices.dropna()
    
    # Remove extreme outliers (beyond 4 std)
    z_scores = np.abs(stats.zscore(returns))
    returns = returns[z_scores < 4.0]
    
    # Standardize for entropy calculations
    standardized = (returns - returns.mean()) / returns.std()
    return standardized, returns


def baseline_stats(returns: pd.Series) -> dict:
    """Report distribution properties and flag concerns."""
    adf_stat, adf_p, *_ = adfuller(returns, autolag='AIC')
    jarque_stat, jarque_p = stats.jarque_bera(returns)
    
    result = {
        'n': len(returns),
        'mean': returns.mean(),
        'std': returns.std(),
        'skewness': stats.skew(returns),
        'kurtosis': stats.kurtosis(returns),
        'adf_pvalue': adf_p,          # < 0.05 = stationary (good)
        'jarque_pvalue': jarque_p,     # < 0.05 = non-normal (fat tails)
        'is_stationary': adf_p < 0.05,
    }
    
    # Flag concerns
    if result['kurtosis'] > 5:
        print("WARNING: High kurtosis (>5) — fat tails, extreme events likely")
    if not result['is_stationary']:
        print("WARNING: Series non-stationary — apply differencing or FFD before modeling")
    
    return result
```

---

## Step 2: Entropy Suite

### Shannon Entropy

Measures distributional randomness. 1.0 = uniform/random, 0.0 = deterministic.

```python
def shannon_entropy(returns: pd.Series, n_bins: int = None) -> float:
    """
    Discretized Shannon entropy, normalized to [0, 1].
    Uses Freedman-Diaconis rule for bin count if not specified.
    """
    if n_bins is None:
        iqr = np.percentile(returns, 75) - np.percentile(returns, 25)
        bin_width = 2 * iqr / (len(returns) ** (1/3))
        n_bins = max(10, int((returns.max() - returns.min()) / bin_width))
    
    counts, _ = np.histogram(returns, bins=n_bins)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    
    raw_entropy = -np.sum(probs * np.log2(probs))
    normalized = raw_entropy / np.log2(n_bins)  # Range [0, 1]
    return normalized
```

### Sample Entropy (SampEn)

Measures time-series regularity. Lower = more regular = more predictable. Values < 0.5 suggest meaningful temporal structure.

```python
def sample_entropy(series: np.ndarray, m: int = 2, r: float = None) -> float:
    """
    Sample entropy: probability that similar patterns of length m
    remain similar at length m+1.
    
    Args:
        series: Standardized time series
        m: Embedding dimension (typically 2)
        r: Tolerance (default: 0.2 * std). Tolerance IS the std since series is standardized.
    
    Returns:
        SampEn value. < 0.5 = structured, > 1.5 = near-random
    """
    if r is None:
        r = 0.2 * np.std(series)
    
    N = len(series)
    
    def count_matches(template_len):
        count = 0
        for i in range(N - template_len):
            template = series[i:i + template_len]
            for j in range(i + 1, N - template_len):
                if np.max(np.abs(series[j:j + template_len] - template)) < r:
                    count += 1
        return count
    
    A = count_matches(m + 1)
    B = count_matches(m)
    
    if B == 0:
        return 0.0
    return -np.log(A / B)
```

### Permutation Entropy (PE)

Maps subsequences to ordinal patterns. Robust to noise and nonlinear dynamics. Values > 0.9 indicate near-randomness.

```python
def permutation_entropy(series: np.ndarray, order: int = 3, normalize: bool = True) -> float:
    """
    Permutation entropy based on ordinal patterns of length `order`.
    
    Args:
        series: Time series array
        order: Pattern length (3 = 6 possible patterns, 4 = 24 patterns)
        normalize: If True, normalize to [0, 1]
    
    Returns:
        PE value. > 0.9 = near-random, < 0.6 = structured
    """
    from itertools import permutations
    
    n = len(series)
    permutation_counts = {}
    
    for i in range(n - order + 1):
        window = series[i:i + order]
        pattern = tuple(np.argsort(window))
        permutation_counts[pattern] = permutation_counts.get(pattern, 0) + 1
    
    total = sum(permutation_counts.values())
    probs = np.array(list(permutation_counts.values())) / total
    probs = probs[probs > 0]
    
    pe = -np.sum(probs * np.log(probs))
    
    if normalize:
        max_entropy = np.log(np.math.factorial(order))
        pe = pe / max_entropy
    
    return pe


def approximate_entropy(series: np.ndarray, m: int = 2, r: float = None) -> float:
    """
    Approximate entropy — similar to SampEn but includes self-matches.
    More biased but faster to compute.
    """
    if r is None:
        r = 0.2 * np.std(series)
    
    N = len(series)
    
    def phi(template_len):
        count = np.zeros(N - template_len + 1)
        for i in range(N - template_len + 1):
            template = series[i:i + template_len]
            for j in range(N - template_len + 1):
                if np.max(np.abs(series[j:j + template_len] - template)) <= r:
                    count[i] += 1
        return np.sum(np.log(count / (N - template_len + 1))) / (N - template_len + 1)
    
    return abs(phi(m) - phi(m + 1))
```

### Spectral Entropy

Measures energy distribution across frequencies. Low = dominant cyclical patterns (exploitable), High = energy spread across all frequencies (noise-like).

```python
def spectral_entropy(series: np.ndarray, normalize: bool = True) -> float:
    """
    Spectral entropy from power spectral density.
    Low = dominant frequencies (cyclical/predictable).
    High = energy spread across frequencies (noise-like).
    """
    from scipy.signal import periodogram
    
    freqs, psd = periodogram(series)
    psd_norm = psd / psd.sum()
    psd_norm = psd_norm[psd_norm > 0]
    
    se = -np.sum(psd_norm * np.log(psd_norm))
    
    if normalize:
        se = se / np.log(len(psd_norm))
    
    return se
```

---

## Step 3: Predictability Tests

### Hurst Exponent

```python
def hurst_exponent(series: np.ndarray) -> float:
    """
    Hurst exponent via R/S analysis.
    H < 0.5: mean-reverting (potentially predictable)
    H = 0.5: random walk (unpredictable)
    H > 0.5: trending (potentially predictable)
    Distance from 0.5 indicates strength of memory.
    """
    lags = range(2, min(100, len(series) // 4))
    tau = []
    
    for lag in lags:
        sub_series = [series[i:i + lag] for i in range(0, len(series) - lag, lag)]
        if len(sub_series) < 2:
            continue
        
        rs_values = []
        for sub in sub_series:
            mean_sub = np.mean(sub)
            deviation = np.cumsum(sub - mean_sub)
            r = deviation.max() - deviation.min()
            s = np.std(sub, ddof=1)
            if s > 0:
                rs_values.append(r / s)
        
        if rs_values:
            tau.append(np.mean(rs_values))
    
    if len(tau) < 2:
        return 0.5
    
    lags_used = range(2, 2 + len(tau))
    poly = np.polyfit(np.log(list(lags_used)), np.log(tau), 1)
    return poly[0]


def autocorrelation_analysis(returns: pd.Series, max_lags: int = 50) -> dict:
    """
    ACF/PACF analysis + Ljung-Box test for serial dependence.
    Significant lags outside 95% CI bands indicate exploitable structure.
    """
    acf_values = acf(returns, nlags=max_lags, alpha=0.05)
    acf_vals, conf_int = acf_values[0], acf_values[1]
    
    # Count significant lags (outside 95% confidence bands)
    ci_width = conf_int[:, 1] - acf_vals
    significant_lags = [
        lag for lag in range(1, max_lags + 1)
        if abs(acf_vals[lag]) > ci_width[lag]
    ]
    
    # Ljung-Box test at key lags
    lb_result = acorr_ljungbox(returns, lags=[10, 20, 50], return_df=True)
    
    return {
        'significant_lags': significant_lags,
        'n_significant': len(significant_lags),
        'ljung_box_pvalues': lb_result['lb_pvalue'].to_dict(),
        'serial_dependence_detected': lb_result['lb_pvalue'].min() < 0.05,
    }


def variance_ratio_test(returns: pd.Series, horizons: list = None) -> dict:
    """
    Variance ratio test at multiple horizons.
    VR > 1: momentum (positive autocorrelation)
    VR < 1: mean reversion (negative autocorrelation)
    VR = 1: random walk
    """
    if horizons is None:
        horizons = [2, 5, 10, 20]
    
    var_1 = returns.var()
    results = {}
    
    for k in horizons:
        k_period_returns = returns.rolling(k).sum().dropna()
        var_k = k_period_returns.var()
        vr = var_k / (k * var_1)
        results[k] = {
            'variance_ratio': vr,
            'signal': 'momentum' if vr > 1.1 else 'mean_reversion' if vr < 0.9 else 'random_walk'
        }
    
    return results
```

---

## Step 4: Regime-Conditional Predictability

```python
def regime_predictability(returns: pd.Series, window: int = 50) -> pd.DataFrame:
    """
    Check if predictability is concentrated in specific regimes.
    Lower entropy in a specific regime = conditional signal (regime-specific model may work).
    """
    rolling_vol = returns.rolling(window).std()
    vol_tertiles = pd.qcut(rolling_vol.rank(pct=True), q=3,
                           labels=['low_vol', 'med_vol', 'high_vol'])
    
    results = []
    for regime in ['low_vol', 'med_vol', 'high_vol']:
        mask = vol_tertiles == regime
        regime_returns = returns[mask]
        
        if len(regime_returns) < 50:
            continue
        
        standardized, _ = prepare_series(regime_returns.reset_index(drop=True), 'raw')
        
        results.append({
            'regime': regime,
            'n': len(regime_returns),
            'shannon_entropy': shannon_entropy(regime_returns),
            'permutation_entropy': permutation_entropy(regime_returns.values),
            'hurst': hurst_exponent(regime_returns.values),
            'tradeable': shannon_entropy(regime_returns) < 0.7 or
                         abs(hurst_exponent(regime_returns.values) - 0.5) > 0.1,
        })
    
    return pd.DataFrame(results)
```

---

## Step 5: Predictability Score (0–100)

```python
def predictability_score(returns: pd.Series, verbose: bool = True) -> dict:
    """
    Composite Predictability Score combining all tests.
    
    Score interpretation:
        0-20:  NO SIGNAL  — Do not proceed with modeling
        20-40: WEAK       — High model risk; extensive validation required
        40-60: MODERATE   — Proceed with caution; modest edge
        60-80: GOOD       — Favorable conditions for modeling
        80-100: STRONG    — High predictability (verify it's not a data error)
    
    Returns:
        Dict with 'score', 'recommendation', and per-component scores
    """
    standardized, _ = prepare_series(returns, 'raw')
    arr = standardized.values
    
    components = {}
    
    # 1. Entropy score (inverted — lower entropy = higher score): 25 pts
    avg_entropy = np.mean([
        shannon_entropy(returns),
        permutation_entropy(arr),
        spectral_entropy(arr),
    ])
    components['entropy'] = (1 - avg_entropy) * 25
    
    # 2. Hurst distance from 0.5: 20 pts
    H = hurst_exponent(arr)
    components['hurst'] = abs(H - 0.5) * 2 * 20
    
    # 3. Significant autocorrelation lags: 15 pts
    acf_result = autocorrelation_analysis(returns)
    components['autocorrelation'] = min(15, (acf_result['n_significant'] / 50) * 15)
    
    # 4. Ljung-Box test rejection: 15 pts
    lb_p = min(acf_result['ljung_box_pvalues'].values())
    components['ljung_box'] = 15 if lb_p < 0.05 else 0
    
    # 5. Variance ratio deviation: 10 pts
    vr_results = variance_ratio_test(returns)
    avg_vr_dev = np.mean([abs(v['variance_ratio'] - 1) for v in vr_results.values()])
    components['variance_ratio'] = min(10, avg_vr_dev * 10)
    
    # 6. Shuffle test (compare to 100 random shuffles): 15 pts
    actual_pe = permutation_entropy(arr)
    shuffled_pes = [
        permutation_entropy(np.random.permutation(arr))
        for _ in range(100)
    ]
    p_value = np.mean([s <= actual_pe for s in shuffled_pes])
    components['shuffle_test'] = 15 if actual_pe < np.percentile(shuffled_pes, 95) else 0
    
    total = sum(components.values())
    total = min(100, max(0, total))
    
    if total < 20:
        recommendation = "STOP — No predictive model will work on this series"
    elif total < 40:
        recommendation = "CAUTION — Weak signal; use regime-switching approach only"
    elif total < 60:
        recommendation = "PROCEED with caution — modest edge expected"
    elif total < 80:
        recommendation = "PROCEED — good conditions for modeling"
    else:
        recommendation = "STRONG SIGNAL — verify this is not a data error before proceeding"
    
    if verbose:
        print(f"\nPREDICTABILITY SCORE: {total:.1f}/100")
        print(f"RECOMMENDATION: {recommendation}")
        print(f"Hurst Exponent: {H:.3f} ({'mean-rev' if H < 0.45 else 'trending' if H > 0.55 else 'random walk'})")
        print(f"Component breakdown: {components}")
    
    return {
        'score': total,
        'recommendation': recommendation,
        'hurst': H,
        'components': components,
    }
```

---

## Decision Rules

| Condition | Action |
|---|---|
| Score < 20 | **STOP** — No predictive model will work on this series |
| All entropy measures > 0.85 normalized | **STOP** — Series is indistinguishable from random |
| Hurst ≈ 0.5 AND no significant ACF | **STOP** — Pure random walk; change asset/timeframe/hypothesis |
| Score 20–40 AND regime variation exists | Consider regime-switching approach **only**; apply stricter thresholds (DSR > 0.97, walk-forward > 70%) |
| Score 20–40 AND no regime variation | **STOP** — Weak signal without conditional structure; do not model |
| BDS significant but ACF not | Nonlinear models (GBM, trees) — linear structure already removed; hidden patterns remain |
| Strong ACF but BDS not significant | Linear models (ARIMA, Ridge) sufficient; no need for deep nonlinearity |
| Low entropy at specific regime only | Focus strategy on that regime; regime filter required in production |
| Strong signal at one frequency only | Focus strategy on that timeframe; do not force to other scales |
| Score > 80 | Verify data integrity — extremely high predictability may indicate a data error |

### Bivariate / conditional predictability (footnote for Step 2)

The rules above apply to **univariate** predictability of the **target** series *Y* (the default and mandatory starting point in the skill). For hypotheses where edge comes from **cross-series timing** (e.g. “macro **X** leads asset **Y** by τ”), **Y** can score **low** on marginal predictability while **incremental** predictability from **X** (conditional on lags of **Y**) is still meaningful.

In that case: **do not** treat **Score < 20** on **Y** alone as an automatic **STOP** without reading the **bivariate** guidance in `lead-lag-predictive-inclusion.md` (Section 6) and running any **pre-specified** conditional checks with the same **PIT and OOS** discipline. The univariate score remains the **default gate** for **single-asset, single-series** strategies.

---

## Multi-Scale Check

```python
def multi_scale_predictability(prices: pd.Series) -> pd.DataFrame:
    """
    Check predictability at multiple timeframes.
    Guides which frequency to focus the strategy on.
    """
    results = []
    
    for freq, label in [('D', 'daily'), ('W', 'weekly'), ('ME', 'monthly')]:
        try:
            resampled = prices.resample(freq).last().dropna()
            if len(resampled) < 100:
                continue
            _, returns = prepare_series(resampled)
            result = predictability_score(returns, verbose=False)
            results.append({'timeframe': label, 'score': result['score'],
                            'hurst': result['hurst']})
        except Exception:
            continue
    
    return pd.DataFrame(results).sort_values('score', ascending=False)
```

---

## See Also

- `regime-philosophy.md` — why regime-conditional predictability matters
- `feature-engineering.md` — fractional differentiation to achieve stationarity while preserving memory
- `validation-backtesting.md` — purged CV, DSR after model is built
