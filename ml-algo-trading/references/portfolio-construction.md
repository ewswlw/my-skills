# Portfolio Construction

## Default Choice: Hierarchical Risk Parity (HRP)

**Use HRP as the default for all multi-asset portfolio construction.** Only use mean-variance optimization when you have very accurate return estimates AND need specific return targets — which is rare in practice.

---

## Why Not Mean-Variance (Markowitz)?

Mean-variance optimization has fundamental instability problems known as **Markowitz's Curse**:

1. **Ill-conditioned covariance matrix** — small input changes cause large weight changes
2. **Concentration** — tends to allocate extreme weights to a few assets
3. **Estimation error amplification** — errors in mean/covariance estimates are amplified, not dampened
4. **Instability over time** — optimal weights change dramatically across rebalancing periods

HRP solves all four problems by requiring only the covariance matrix (no mean estimates) and using hierarchical clustering to impose diversification structure.

---

## HRP Algorithm (3 Steps)

### Step 1: Tree Clustering

Group similar assets hierarchically using correlation distance.

```python
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform

def build_correlation_distance(corr: pd.DataFrame) -> np.ndarray:
    """
    Convert correlation matrix to distance matrix for hierarchical clustering.
    Distance = sqrt((1 - corr) / 2), which satisfies triangle inequality.
    """
    dist = ((1 - corr) / 2.0) ** 0.5
    return squareform(dist.values)


def cluster_assets(corr: pd.DataFrame) -> np.ndarray:
    """
    Single-linkage hierarchical clustering of assets by correlation distance.
    Returns linkage matrix (scipy format).
    """
    dist_condensed = build_correlation_distance(corr)
    return linkage(dist_condensed, method='single')
```

### Step 2: Quasi-Diagonalization

Reorder the covariance matrix so similar assets are adjacent. This structure allows recursive bisection to work correctly.

```python
def get_quasi_diag(link: np.ndarray) -> list:
    """
    Reorder assets based on hierarchical clustering result.
    Returns sorted list of asset indices (most similar assets adjacent).
    """
    link = link.astype(int)
    sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
    num_items = link[-1, 3]
    
    while sort_ix.max() >= num_items:
        sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)
        df0 = sort_ix[sort_ix >= num_items]
        i = df0.index
        j = df0.values - num_items
        sort_ix[i] = link[j, 0]
        df0 = pd.Series(link[j, 1], index=i + 1)
        sort_ix = pd.concat([sort_ix, df0])
        sort_ix = sort_ix.sort_index()
        sort_ix.index = range(sort_ix.shape[0])
    
    return sort_ix.tolist()
```

### Step 3: Recursive Bisection

Allocate weights top-down: split the sorted assets into two halves, weight each half inversely proportional to its cluster variance.

```python
def get_inverse_variance_weights(cov: pd.DataFrame, assets: list) -> np.ndarray:
    """Inverse-variance portfolio weights for a subset of assets."""
    ivp = 1.0 / np.diag(cov.loc[assets, assets].values)
    return ivp / ivp.sum()


def get_cluster_variance(cov: pd.DataFrame, assets: list) -> float:
    """Portfolio variance of an inverse-variance weighted cluster."""
    cov_slice = cov.loc[assets, assets]
    w = get_inverse_variance_weights(cov, assets)
    return float(np.dot(w.T, np.dot(cov_slice.values, w)))


def recursive_bisection(cov: pd.DataFrame, sort_ix: list) -> pd.Series:
    """
    Allocate weights recursively by bisecting sorted asset list.
    At each split: allocate alpha to left cluster, (1-alpha) to right,
    where alpha is inversely proportional to cluster variance.
    """
    weights = pd.Series(1.0, index=sort_ix)
    clusters = [sort_ix]  # Start with all assets as one cluster
    
    while clusters:
        # Split each cluster in half
        clusters = [
            sub_cluster[j:k]
            for sub_cluster in clusters
            for j, k in ((0, len(sub_cluster) // 2),
                         (len(sub_cluster) // 2, len(sub_cluster)))
            if len(sub_cluster) > 1
        ]
        
        # Allocate between each pair of sibling clusters
        for i in range(0, len(clusters), 2):
            if i + 1 >= len(clusters):
                break
            left = clusters[i]
            right = clusters[i + 1]
            
            var_left = get_cluster_variance(cov, left)
            var_right = get_cluster_variance(cov, right)
            
            # Weight inversely proportional to variance
            alpha = 1 - var_left / (var_left + var_right)
            weights[left] *= alpha
            weights[right] *= 1 - alpha
    
    return weights
```

### Complete HRP Implementation

```python
class HierarchicalRiskParity:
    """
    Full HRP portfolio optimizer.
    
    Args:
        returns: DataFrame (rows=time, columns=assets)
        min_periods: Minimum observations required for covariance estimation
    """
    
    def __init__(self, returns: pd.DataFrame, min_periods: int = 30):
        self.returns = returns
        self.cov = returns.cov(min_periods=min_periods)
        self.corr = returns.corr(min_periods=min_periods)
    
    def optimize(self) -> pd.Series:
        """
        Run HRP optimization. Returns portfolio weights summing to 1.0.
        """
        # Step 1: Cluster
        link = cluster_assets(self.corr)
        
        # Step 2: Quasi-diagonalize
        sort_ix = get_quasi_diag(link)
        sort_ix = self.corr.index[sort_ix].tolist()
        
        # Step 3: Recursive bisection
        weights = recursive_bisection(self.cov, sort_ix)
        
        return weights.sort_index()
    
    def rolling_optimize(self, window: int = 252) -> pd.DataFrame:
        """
        Rolling HRP weights. Use for backtesting with periodic rebalancing.
        Point-in-time safe: only uses data up to each rebalancing date.
        """
        weights_history = []
        
        for i in range(window, len(self.returns) + 1):
            window_returns = self.returns.iloc[i - window:i]
            hrp = HierarchicalRiskParity(window_returns)
            w = hrp.optimize()
            w.name = self.returns.index[i - 1]
            weights_history.append(w)
        
        return pd.DataFrame(weights_history)


# Usage
returns = pd.DataFrame(
    np.random.randn(500, 5) * 0.01,
    columns=['SPY', 'TLT', 'GLD', 'EEM', 'VNQ']
)

hrp = HierarchicalRiskParity(returns)
weights = hrp.optimize()
print("HRP Weights:")
print(weights.sort_values(ascending=False))
# Weights will be diversified — no extreme concentrations
```

---

## HRP for Strategy Allocation

Treat multiple strategy return streams as "assets" and use HRP to allocate capital:

```python
def allocate_strategies_hrp(strategy_returns: pd.DataFrame,
                             lookback: int = 252) -> pd.Series:
    """
    Allocate capital across strategies using HRP.
    More robust than equal-weight or Sharpe-weight allocation.
    
    Args:
        strategy_returns: DataFrame where each column is one strategy's daily returns
        lookback: Rolling window for covariance estimation
    
    Returns:
        Series of strategy weights (sum to 1.0)
    """
    recent_returns = strategy_returns.tail(lookback).dropna(axis=1, how='any')
    
    if recent_returns.shape[1] < 2:
        # Single strategy — full allocation
        return pd.Series(1.0, index=strategy_returns.columns)
    
    hrp = HierarchicalRiskParity(recent_returns)
    return hrp.optimize()
```

---

## When to Use Mean-Variance Instead

```python
from scipy.optimize import minimize

def mean_variance_optimization(
    returns: pd.DataFrame,
    target_return: float = None,
    risk_free_rate: float = 0.0,
) -> np.ndarray:
    """
    Traditional Markowitz optimization. Use only when:
    1. You have very accurate return estimates (rare in practice)
    2. You need a specific return target
    3. Assets are relatively uncorrelated (avoids extreme weights)
    
    In most cases, prefer HRP.
    """
    n = returns.shape[1]
    mu = returns.mean().values
    cov = returns.cov().values
    
    def portfolio_variance(w):
        return w @ cov @ w
    
    constraints = [{'type': 'eq', 'fun': lambda w: w.sum() - 1}]
    if target_return is not None:
        constraints.append({'type': 'eq', 'fun': lambda w: w @ mu - target_return})
    
    bounds = [(0, 1)] * n
    x0 = np.ones(n) / n
    
    result = minimize(portfolio_variance, x0, method='SLSQP',
                      bounds=bounds, constraints=constraints)
    return result.x


# Decision guide
print("""
Use HRP when:
  - Return estimates are uncertain (most of the time)
  - Assets are highly correlated (HRP handles this better)
  - You want stable weights over time

Use Mean-Variance when:
  - You have reliable return forecasts (e.g., from a strong alpha model)
  - You need to hit a specific return target
  - N < 5 assets (small N reduces Markowitz instability)
""")
```

---

## Rebalancing Rules

```python
def should_rebalance(
    current_weights: pd.Series,
    target_weights: pd.Series,
    threshold: float = 0.05,
    min_days_between: int = 21,
    days_since_last: int = 0,
) -> bool:
    """
    Rebalance only when weight drift exceeds threshold AND minimum time has passed.
    Avoids excessive transaction costs from over-rebalancing.
    
    Args:
        threshold: Maximum allowed weight deviation before rebalancing (default 5%)
        min_days_between: Minimum days between rebalances (default ~monthly)
    """
    if days_since_last < min_days_between:
        return False
    
    max_drift = (current_weights - target_weights).abs().max()
    return max_drift > threshold
```

---

---

## Performance Optimization

Production portfolio and feature-calculation code must be vectorized and parallelized.
Loops over arrays/DataFrames are 10–100× slower than equivalent vectorized operations.

### Vectorization Patterns

Always prefer vectorized NumPy/Pandas operations over Python loops.

```python
import numpy as np
import pandas as pd

# ❌ Loop-based — avoid
def calculate_returns_loop(prices: np.ndarray) -> np.ndarray:
    returns = np.zeros(len(prices) - 1)
    for i in range(1, len(prices)):
        returns[i - 1] = (prices[i] - prices[i - 1]) / prices[i - 1]
    return returns

# ✅ Vectorized — use this (~100× faster)
def calculate_returns_vectorized(prices: np.ndarray) -> np.ndarray:
    return np.diff(prices) / prices[:-1]


# ✅ Pandas vectorized feature engineering — all operations broadcast over full array
def vectorized_features(prices: pd.Series) -> pd.DataFrame:
    """Calculate technical features using fully vectorized operations."""
    df = pd.DataFrame({'price': prices})
    df['returns']    = df['price'].pct_change()
    df['sma_20']     = df['price'].rolling(20).mean()
    df['volatility'] = df['returns'].rolling(20).std()
    df['zscore']     = (df['price'] - df['sma_20']) / df['price'].rolling(20).std()
    return df
```

**Key vectorization rules:**
1. Avoid Python loops over arrays or DataFrames — use `.rolling()`, `.shift()`, `.diff()`, `np.where()`
2. Vectorize conditionals: `np.where(condition, true_val, false_val)`
3. Batch operations — process entire arrays at once, not row by row
4. Use `pd.eval()` for complex multi-column expressions (avoids intermediate copies)

### Multiprocessing: Atoms and Molecules

For CPU-bound tasks (e.g., feature calculation across a large date range, rolling backtest runs),
use López de Prado's atoms-and-molecules pattern to parallelize pandas operations.

```python
import multiprocessing as mp
import numpy as np
import pandas as pd
from typing import Callable, Any


def mp_pandas_obj(
    func: Callable,
    pd_obj: tuple,
    num_threads: int = None,
    **kwargs: Any,
) -> pd.DataFrame | pd.Series:
    """
    Parallelize a pandas operation using the atoms-and-molecules pattern.

    Split the index (atoms) into chunks (molecules), process each chunk in a
    separate process, then concatenate results.

    Args:
        func: Function to apply. Must accept a 'molecule' positional arg (list of indices)
              plus any additional **kwargs.
        pd_obj: Tuple of ('molecule', pd.Index or pd.Series) — the index to split.
        num_threads: Number of parallel processes (default: CPU count).
        **kwargs: Additional arguments forwarded to func.

    Returns:
        Concatenated results (DataFrame or Series).

    Example:
        features = mp_pandas_obj(
            calculate_features_single,
            ('molecule', prices.index),
            num_threads=8,
            prices=prices,
        )
    """
    if num_threads is None:
        num_threads = mp.cpu_count()

    _, molecule_data = pd_obj
    atoms = molecule_data.index if isinstance(molecule_data, pd.Series) else molecule_data
    molecules = np.array_split(atoms, min(num_threads, len(atoms)))

    pool = mp.Pool(processes=num_threads)
    jobs = [pool.apply_async(func, args=(mol,), kwds=kwargs) for mol in molecules]
    pool.close()
    pool.join()

    results = [job.get() for job in jobs]

    if isinstance(results[0], pd.DataFrame):
        return pd.concat(results).sort_index()
    elif isinstance(results[0], pd.Series):
        return pd.concat(results).sort_index()
    else:
        return pd.Series(results)


# Example: parallel feature calculation over a large date index
def calculate_features_single(molecule: pd.Index, prices: pd.Series) -> pd.DataFrame:
    """Calculate features for a subset of dates (one molecule)."""
    features = pd.DataFrame(index=molecule)
    for date in molecule:
        hist = prices[:date]
        features.loc[date, 'sma_20']     = hist.iloc[-20:].mean() if len(hist) >= 20 else np.nan
        features.loc[date, 'volatility'] = hist.iloc[-20:].std()  if len(hist) >= 20 else np.nan
    return features


# Usage
# features = mp_pandas_obj(
#     calculate_features_single,
#     ('molecule', prices.index),
#     num_threads=8,
#     prices=prices,
# )
```

### PortfolioManager Convenience Class

```python
class PortfolioManager:
    """
    Wraps HRP and MVO construction with rebalancing logic.
    Use for backtesting workflows that need periodic reallocation.
    """

    def __init__(self, returns: pd.DataFrame):
        """
        Args:
            returns: Asset returns (rows=time, columns=assets)
        """
        self.returns = returns
        self.weights: pd.Series | None = None

    def construct(self, method: str = 'hrp') -> pd.Series:
        """
        Build portfolio weights.

        Args:
            method: 'hrp' (default) or 'mean_variance'

        Returns:
            Portfolio weights summing to 1.0
        """
        if method == 'hrp':
            hrp = HierarchicalRiskParity(self.returns)
            self.weights = hrp.optimize()
        elif method == 'mean_variance':
            w = mean_variance_optimization(self.returns)
            self.weights = pd.Series(w, index=self.returns.columns)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'hrp' or 'mean_variance'.")
        return self.weights

    def rebalance(self, new_returns: pd.DataFrame, method: str = 'hrp') -> pd.Series:
        """
        Update returns data and reoptimize weights.

        Args:
            new_returns: Updated return data
            method: Portfolio construction method

        Returns:
            New portfolio weights
        """
        self.returns = new_returns
        return self.construct(method)

    def portfolio_returns(self, weights: pd.Series = None) -> pd.Series:
        """
        Calculate portfolio returns given weights.

        Args:
            weights: Weights to apply (default: self.weights)

        Returns:
            Weighted portfolio return series
        """
        w = weights if weights is not None else self.weights
        if w is None:
            raise ValueError("Call construct() before portfolio_returns()")
        return (self.returns * w).sum(axis=1)
```

### Performance Optimization Rules Summary

| Principle | Rule |
|---|---|
| **Vectorize** | No Python loops over arrays/DataFrames; use NumPy/Pandas built-ins |
| **Parallelize CPU work** | Use `mp_pandas_obj` for feature calculation and rolling backtests |
| **Parallelize I/O work** | Use `asyncio` for data fetching (not `multiprocessing`) |
| **Profile first** | Measure before optimizing; `cProfile` or `line_profiler` |
| **Cache expensive calls** | Use `functools.lru_cache` or `joblib.Memory` for repeated computations |
| **Memory efficiency** | Use `float32` instead of `float64` when precision allows; avoid `.copy()` |

---

## See Also

- `regime-philosophy.md` — regime-conditional position sizing and how regimes affect portfolio construction
- `strategy-improvement.md` — Section B (GA) for multi-strategy signal combination
- `validation-backtesting.md` — walk-forward validation of portfolio construction decisions
