# Strategy Improvement & Optimization

Two complementary approaches depending on what you're trying to do:

- **Section A — Strategy Improver Framework**: You have a working base strategy. You want to add filters incrementally without overfitting.
- **Section B — Genetic Algorithm Optimization**: You have a large parameter/indicator search space. You want to find good combinations efficiently.

Use Section A first. Use Section B when the space is too large to search manually.

---

# Section A: Strategy Improver Framework

## Philosophy

**Improve a logical, modestly profitable base strategy by testing one economically justified filter at a time.**

Use binary on/off questions — never optimize filter parameters. Optimizing parameters to a specific dataset is curve-fitting. A filter either belongs in the strategy by design or it doesn't.

---

## Step 1: Vet the Base Strategy

All five criteria must pass before adding any filters. If the base strategy fails, fix it first.

| Criterion | Threshold | Why |
|---|---|---|
| Positive total return | > 0 | Filters can't fix a loss-making base |
| Sharpe ratio | > 0.5 | Acceptable risk-adjusted foundation |
| Max drawdown | < 30% | Manageable risk before leverage/filters |
| Profit factor | > 1.2 | Wins exceed losses by sufficient margin |
| Trade count | ≥ 50 | Minimum for statistical validity |
| Economic rationale | Must exist | No rationale = data mining |

```python
def vet_base_strategy(returns: pd.Series, trades: pd.DataFrame) -> dict:
    """
    Validate base strategy against minimum criteria before filter testing.
    
    Args:
        returns: Strategy return series
        trades: DataFrame with 'pnl' column per trade
    
    Returns:
        Dict with pass/fail per criterion and overall verdict
    """
    ann_return = (1 + returns.mean()) ** 252 - 1
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    
    equity = (1 + returns).cumprod()
    max_dd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    gross_wins = trades[trades['pnl'] > 0]['pnl'].sum()
    gross_losses = abs(trades[trades['pnl'] < 0]['pnl'].sum())
    profit_factor = gross_wins / gross_losses if gross_losses > 0 else np.inf
    
    criteria = {
        'positive_return': ann_return > 0,
        'sharpe_above_05': sharpe > 0.5,
        'max_dd_below_30': max_dd > -0.30,
        'profit_factor_above_12': profit_factor > 1.2,
        'sufficient_trades': len(trades) >= 50,
    }
    
    passed = sum(criteria.values())
    
    print(f"Base Strategy Vetting: {passed}/5 criteria passed")
    for k, v in criteria.items():
        print(f"  {'✓' if v else '✗'} {k}")
    
    return {
        'passes': all(criteria.values()),
        'criteria': criteria,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'profit_factor': profit_factor,
    }
```

---

## Step 2: Test Individual Filters

For each candidate filter, run a binary ON/OFF test. The filter is tested against the **same base strategy** — never stack filters during testing.

```python
def test_filter(
    base_returns: pd.Series,
    filter_signal: pd.Series,
    base_trades: pd.DataFrame = None,
    n_bootstrap: int = 1000,
) -> dict:
    """
    Binary filter test: compare base strategy returns to filter-applied returns.
    Filter signal is boolean (True = trade is allowed, False = skip/go flat).
    
    Args:
        base_returns: Daily returns of base strategy (no filter)
        filter_signal: Boolean series — True when filter allows trading
        base_trades: Optional trade log for profit factor calculation
        n_bootstrap: Bootstrap samples for significance testing
    
    Returns:
        Dict with metrics comparison and statistical significance
    """
    filtered_returns = base_returns * filter_signal.reindex(base_returns.index).fillna(False)
    
    def compute_metrics(rets):
        ann_ret = (1 + rets.mean()) ** 252 - 1
        ann_vol = rets.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        equity = (1 + rets).cumprod()
        max_dd = ((equity - equity.cummax()) / equity.cummax()).min()
        return {'ann_return': ann_ret, 'sharpe': sharpe, 'max_dd': max_dd,
                'hit_rate': (rets > 0).mean()}
    
    base_m = compute_metrics(base_returns)
    filt_m = compute_metrics(filtered_returns)
    
    # Bootstrap significance test on Sharpe improvement
    improvements = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(len(base_returns), len(base_returns), replace=True)
        b_sample = base_returns.iloc[idx]
        f_sample = filtered_returns.iloc[idx]
        imp = (f_sample.mean() / f_sample.std()) - (b_sample.mean() / b_sample.std())
        improvements.append(imp)
    
    ci_lower = np.percentile(improvements, 2.5)
    ci_upper = np.percentile(improvements, 97.5)
    p_value = np.mean([i <= 0 for i in improvements])
    
    # Majority of metrics must improve
    metrics_improved = sum([
        filt_m['ann_return'] > base_m['ann_return'],
        filt_m['sharpe'] > base_m['sharpe'],
        filt_m['max_dd'] > base_m['max_dd'],
        filt_m['hit_rate'] > base_m['hit_rate'],
    ])
    
    return {
        'base_metrics': base_m,
        'filtered_metrics': filt_m,
        'sharpe_improvement': filt_m['sharpe'] - base_m['sharpe'],
        'ci_95': (ci_lower, ci_upper),
        'p_value': p_value,
        'statistically_significant': p_value < 0.05 and ci_lower > 0,
        'metrics_improved': metrics_improved,
        'promote': metrics_improved >= 3 and p_value < 0.05 and ci_lower > 0,
    }
```

---

## Step 3: Promote Filters

A filter is promoted if ALL four conditions are met:

1. **Multi-metric gains** — improves ≥ 3 of 4 metrics (return, Sharpe, drawdown, hit rate)
2. **Statistical significance** — p < 0.05, bootstrap 95% CI excludes zero
3. **Regime persistence** — improvement holds across at least 2 distinct market regimes
4. **Economic rationale** — can you explain in one sentence WHY this filter improves performance?

Once promoted: incorporate into base strategy, re-vet against Step 1 criteria, repeat.

```python
def check_regime_persistence(
    base_returns: pd.Series,
    filter_signal: pd.Series,
    regime_labels: pd.Series,
) -> dict:
    """
    Verify filter improvement persists across distinct market regimes.
    If improvement only appears in one regime, it's likely regime-specific overfitting.
    """
    results = {}
    
    for regime in regime_labels.unique():
        mask = regime_labels == regime
        b = base_returns[mask]
        f = base_returns[mask] * filter_signal.reindex(b.index).fillna(False)
        
        if len(b) < 20:
            continue
        
        base_sharpe = b.mean() / b.std() * np.sqrt(252) if b.std() > 0 else 0
        filt_sharpe = f.mean() / f.std() * np.sqrt(252) if f.std() > 0 else 0
        results[regime] = {
            'base_sharpe': base_sharpe,
            'filtered_sharpe': filt_sharpe,
            'improves': filt_sharpe > base_sharpe,
        }
    
    n_regimes = len(results)
    n_improves = sum(r['improves'] for r in results.values())
    
    return {
        'per_regime': results,
        'improves_in_pct': n_improves / n_regimes if n_regimes > 0 else 0,
        'regime_persistent': n_improves / n_regimes >= 0.6 if n_regimes > 0 else False,
    }
```

---

# Section B: Genetic Algorithm Optimization

## When to Use GA vs Grid Search

| Situation | Use |
|---|---|
| ≤ 20 parameters, small ranges | Grid search or Optuna |
| 20+ parameters or large ranges | **GA** |
| Multi-objective optimization (return AND Sharpe) | **GA** |
| Indicator combination search (which indicators to include) | **GA** |
| Need interpretable parameter evolution history | **GA** |

---

## GA Specification

### Population & Chromosome Structure

```python
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Callable

@dataclass
class Individual:
    """
    A single trading strategy represented as a chromosome.
    Each gene is a (indicator_name, parameter_value) pair.
    """
    genes: Dict           # {indicator_name: parameter_value}
    weights: np.ndarray   # normalized combination weights (sum to 1)
    thresholds: Dict      # {indicator_name: (long_threshold, short_threshold)}
    fitness: float = 0.0
    sharpe: float = 0.0


def create_individual(indicator_space: dict) -> Individual:
    """
    Create a random individual from the indicator parameter space.
    
    Args:
        indicator_space: {indicator_name: (min_val, max_val, is_int)}
    """
    genes = {}
    for name, (lo, hi, is_int) in indicator_space.items():
        val = random.uniform(lo, hi)
        genes[name] = int(val) if is_int else val
    
    n = len(indicator_space)
    weights = np.random.dirichlet(np.ones(n))  # Normalized, sum to 1
    thresholds = {name: (random.uniform(0.3, 0.7), random.uniform(0.3, 0.7))
                  for name in indicator_space}
    
    return Individual(genes=genes, weights=weights, thresholds=thresholds)
```

### Fitness Function (Multi-Objective)

```python
def evaluate_fitness(
    individual: Individual,
    prices: pd.Series,
    backtest_func: Callable,
    w_return: float = 0.6,
    w_sharpe: float = 0.4,
) -> Individual:
    """
    Multi-objective fitness: weighted combination of total return and Sharpe ratio.
    Penalize strategies that violate constraints (e.g., < 20 trades).
    
    CRITICAL: backtest_func must use ONLY historical data up to each signal date.
    No look-ahead bias allowed inside the fitness evaluation.
    """
    try:
        results = backtest_func(prices, individual.genes, individual.weights,
                                individual.thresholds)
        
        total_return = results['total_return']
        sharpe = results['sharpe']
        n_trades = results.get('n_trades', 0)
        
        # Penalize insufficient trades (statistical validity requirement)
        if n_trades < 20:
            individual.fitness = -1.0
            individual.sharpe = sharpe
            return individual
        
        # Multi-objective: combine return and risk-adjusted return
        individual.fitness = w_return * total_return + w_sharpe * sharpe
        individual.sharpe = sharpe
        
    except Exception:
        individual.fitness = -999.0
        individual.sharpe = 0.0
    
    return individual
```

### Selection, Crossover, Mutation

```python
def tournament_selection(population: List[Individual], k: int = 3) -> Individual:
    """Tournament selection: pick k random individuals, return the best."""
    candidates = random.sample(population, k)
    return max(candidates, key=lambda x: x.fitness)


def crossover(parent1: Individual, parent2: Individual,
              crossover_prob: float = 0.80) -> tuple:
    """
    Multi-point crossover of gene dictionaries.
    Preserves economically meaningful parameter ranges.
    """
    if random.random() > crossover_prob:
        return parent1, parent2
    
    keys = list(parent1.genes.keys())
    point1, point2 = sorted(random.sample(range(len(keys)), 2))
    
    child1_genes = {}
    child2_genes = {}
    
    for i, k in enumerate(keys):
        if i < point1 or i >= point2:
            child1_genes[k] = parent1.genes[k]
            child2_genes[k] = parent2.genes[k]
        else:
            child1_genes[k] = parent2.genes[k]
            child2_genes[k] = parent1.genes[k]
    
    # Blend weights
    alpha = random.random()
    child1_weights = alpha * parent1.weights + (1 - alpha) * parent2.weights
    child2_weights = (1 - alpha) * parent1.weights + alpha * parent2.weights
    
    child1 = Individual(genes=child1_genes,
                        weights=child1_weights / child1_weights.sum(),
                        thresholds=parent1.thresholds)
    child2 = Individual(genes=child2_genes,
                        weights=child2_weights / child2_weights.sum(),
                        thresholds=parent2.thresholds)
    
    return child1, child2


def mutate(
    individual: Individual,
    indicator_space: dict,
    base_mutation_rate: float = 0.10,
    population_diversity: float = 1.0,
) -> Individual:
    """
    Adaptive mutation: higher rate when population diversity is low
    (prevents premature convergence to local optima).
    """
    # Adaptive mutation rate: increase when diversity drops
    mutation_rate = base_mutation_rate / max(0.1, population_diversity)
    mutation_rate = min(0.30, mutation_rate)  # Cap at 30%
    
    for name, (lo, hi, is_int) in indicator_space.items():
        if random.random() < mutation_rate:
            val = random.uniform(lo, hi)
            individual.genes[name] = int(val) if is_int else val
    
    # Occasionally mutate weights
    if random.random() < mutation_rate:
        noise = np.random.dirichlet(np.ones(len(individual.weights)))
        individual.weights = 0.7 * individual.weights + 0.3 * noise
        individual.weights /= individual.weights.sum()
    
    return individual
```

### Main GA Loop

```python
def run_ga(
    prices: pd.Series,
    backtest_func: Callable,
    indicator_space: dict,
    population_size: int = 100,
    max_generations: int = 100,
    elite_fraction: float = 0.10,
    convergence_threshold: float = 0.01,
    convergence_window: int = 10,
) -> dict:
    """
    Full genetic algorithm optimization loop.
    
    Args:
        prices: OHLCV price data (point-in-time, no look-ahead)
        backtest_func: Function(prices, genes, weights, thresholds) → metrics dict
        indicator_space: {name: (min, max, is_int)} parameter bounds
        population_size: 100-500 (larger = more exploration, slower)
        max_generations: 50-200
        elite_fraction: Top 10% preserved unchanged across generations
        convergence_threshold: Stop if best fitness improves < 1% for 10 generations
    
    Returns:
        Dict with best individual, convergence history, and all-time best
    """
    # Initialize population
    population = [create_individual(indicator_space) for _ in range(population_size)]
    
    # Evaluate initial fitness
    population = [evaluate_fitness(ind, prices, backtest_func) for ind in population]
    
    n_elite = max(1, int(population_size * elite_fraction))
    best_fitness_history = []
    
    for gen in range(max_generations):
        # Sort by fitness
        population.sort(key=lambda x: x.fitness, reverse=True)
        best_fitness = population[0].fitness
        best_fitness_history.append(best_fitness)
        
        # Check convergence
        if len(best_fitness_history) >= convergence_window:
            recent_improvement = (
                best_fitness_history[-1] - best_fitness_history[-convergence_window]
            ) / max(1e-9, abs(best_fitness_history[-convergence_window]))
            
            if abs(recent_improvement) < convergence_threshold:
                print(f"Converged at generation {gen}")
                break
        
        # Population diversity (std of fitness values)
        fitness_vals = [ind.fitness for ind in population]
        diversity = np.std(fitness_vals) / (np.mean(np.abs(fitness_vals)) + 1e-9)
        
        # Build next generation
        next_gen = population[:n_elite]  # Preserve elite unchanged
        
        while len(next_gen) < population_size:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, indicator_space, population_diversity=diversity)
            child2 = mutate(child2, indicator_space, population_diversity=diversity)
            next_gen.extend([child1, child2])
        
        population = next_gen[:population_size]
        population = [evaluate_fitness(ind, prices, backtest_func) for ind in population
                      if ind.fitness == 0.0]  # Re-evaluate non-elite
        
        if gen % 10 == 0:
            print(f"Gen {gen}: Best fitness = {best_fitness:.4f}, "
                  f"Diversity = {diversity:.3f}")
    
    population.sort(key=lambda x: x.fitness, reverse=True)
    best = population[0]
    
    return {
        'best_individual': best,
        'best_fitness': best.fitness,
        'best_sharpe': best.sharpe,
        'convergence_history': best_fitness_history,
        'final_population': population,
    }
```

---

## GA Walk-Forward Validation

Run GA on each training window; test on next OOS window. Parameter stability across windows is the key test.

```python
def ga_walk_forward(
    prices: pd.Series,
    backtest_func: Callable,
    indicator_space: dict,
    train_size: int = 252,
    test_size: int = 63,
    ga_kwargs: dict = None,
) -> pd.DataFrame:
    """
    Walk-forward GA optimization.
    Re-runs GA on each training window; tests best individual on next OOS period.
    Checks if optimized parameters generalize.
    """
    if ga_kwargs is None:
        ga_kwargs = {'population_size': 50, 'max_generations': 50}
    
    results = []
    n = len(prices)
    
    for train_start in range(0, n - train_size - test_size, test_size):
        train_end = train_start + train_size
        test_end = min(train_end + test_size, n)
        
        train_prices = prices.iloc[train_start:train_end]
        test_prices = prices.iloc[train_end:test_end]
        
        # Optimize on training window
        ga_result = run_ga(train_prices, backtest_func, indicator_space, **ga_kwargs)
        best = ga_result['best_individual']
        
        # Test on OOS window
        oos_result = backtest_func(test_prices, best.genes, best.weights, best.thresholds)
        
        results.append({
            'train_start': prices.index[train_start],
            'train_end': prices.index[train_end - 1],
            'test_end': prices.index[test_end - 1],
            'train_fitness': best.fitness,
            'oos_return': oos_result['total_return'],
            'oos_sharpe': oos_result['sharpe'],
        })
    
    return pd.DataFrame(results)
```

---

## GA Pitfalls & How to Avoid Them

| Pitfall | Symptom | Fix |
|---|---|---|
| **Overfitting** | GA finds patterns that don't generalize | Walk-forward validation; OOS test after every run |
| **Data snooping** | Reporting only the best of many GA runs | Track total evaluations for DSR: n_trials ≈ population × generations × re-runs |
| **Look-ahead bias** | Future data in fitness evaluation | Strict point-in-time data inside backtest_func |
| **Survivorship bias** | Backtesting only assets that survived | Use point-in-time universe; include delistings |
| **Ignoring costs** | Optimizes gross returns, not net | Include fees + slippage inside fitness function |
| **Premature convergence** | Population becomes homogeneous | Adaptive mutation rate; diversity restart trigger |

### Critical: DSR for GA

A GA that runs 100 individuals × 100 generations evaluates ~10,000 strategies. Even if you report only one result, the DSR must account for all trials tested:

```python
# After GA completes, calculate DSR with full trial count
total_trials = population_size * n_generations * n_restarts

dsr = deflated_sharpe_ratio(
    observed_sharpe=best_result['oos_sharpe'],
    n_trials=total_trials,       # NOT 1 — account for ALL GA evaluations
    n_observations=len(oos_returns),
)
# DSR < 0.95 after GA means the result is likely data snooping despite looking good
```

---

## Technical Indicator Space (30+ Indicators)

Suggested parameter bounds for GA search:

```python
INDICATOR_SPACE = {
    # Trend
    'sma_fast': (5, 50, True),
    'sma_slow': (20, 200, True),
    'ema_period': (5, 100, True),
    'macd_fast': (5, 20, True),
    'macd_slow': (20, 50, True),
    'macd_signal': (5, 15, True),
    'adx_period': (10, 30, True),
    'aroon_period': (10, 50, True),
    # Momentum
    'rsi_period': (7, 21, True),
    'stoch_k': (5, 21, True),
    'stoch_d': (3, 9, True),
    'williams_r_period': (7, 21, True),
    'cci_period': (10, 30, True),
    'roc_period': (5, 25, True),
    'mfi_period': (10, 20, True),
    # Mean reversion
    'bb_period': (10, 30, True),
    'bb_std': (1.5, 3.0, False),
    'zscore_window': (20, 100, True),
    'keltner_period': (10, 30, True),
    # Volatility / statistical
    'atr_period': (7, 21, True),
    'vol_window': (10, 30, True),
    'corr_window': (20, 60, True),
}
```

---

## GA Edge Case Handling

### Market Anomalies
- Handle extreme volatility events (crashes, bubbles) — penalize or discard in fitness
- Manage gaps and limit moves — skip signal generation on gap-up/gap-down days
- Account for low-liquidity periods — apply minimum volume filter in backtest_func
- Handle delisting and bankruptcy — point-in-time universe required

### Data Quality Guards
- Detect and flag suspicious price movements (>10 std dev single-bar moves)
- Implement data validation checkpoints before fitness evaluation
- Graceful degradation: return fitness = -999 on incomplete data, not exception

### Computational Efficiency
- For large populations (>200): use multiprocessing — parallelize `evaluate_fitness` calls
- Implement early stopping if best fitness hasn't improved for `convergence_window` generations
- Profile backtest_func — it runs `population_size × n_generations` times; must be fast

## GA Success Criteria Checklist

Before declaring a GA-optimized strategy valid:

- [ ] GA converged (best fitness plateau for ≥ 10 generations)
- [ ] OOS walk-forward shows positive return in ≥ 60% of windows
- [ ] DSR > 0.95 with `n_trials = population_size × n_generations × n_restarts`
- [ ] Parameter stability: optimal genes do not change drastically across walk-forward windows
- [ ] Temporal integrity verified: no look-ahead in backtest_func
- [ ] Transaction costs included in fitness function
- [ ] Strategy profitable net of all costs (fees, slippage, market impact)
- [ ] Tested across at least 2 distinct market regimes (see `regime-philosophy.md`)

## GA Output Documentation Requirements

When reporting GA results, always include:

1. **Strategy documentation** — final indicator list with optimized parameters, combination weights
2. **Evolution statistics** — fitness history, convergence generation, final population diversity
3. **Signal rules** — human-readable description of signal generation logic
4. **Performance analysis** — total return vs benchmark, Sharpe, max drawdown, Calmar
5. **Validation** — walk-forward OOS results, DSR with full n_trials, parameter sensitivity ±20%
6. **Visualizations** — fitness evolution chart, cumulative return vs benchmark, drawdown chart

---

# Section C: Discovery Memory & Search Policy

## Philosophy

**Strategy development is not a one-shot process — it's an iterative discovery system.** Each cycle of hypothesis, test, and result should update a persistent memory that guides future cycles. Without memory, you re-test discredited hypotheses, fail to build on near-misses, and cannot balance exploration of new ideas against exploitation of proven patterns.

---

## Discovery Memory Format

After every factor discovery or strategy development cycle, log a structured record — regardless of whether the result passed or failed.

```python
import json
from datetime import datetime
from pathlib import Path

MEMORY_PATH = Path("discovery_memory.jsonl")

def log_discovery(
    hypothesis: str,
    factor_expression: str,
    reasoning_trace: dict,
    screening_result: dict,
    oos_result: dict = None,
    failure_mode: str = None,
    tags: list = None,
) -> dict:
    """
    Log a single discovery cycle to persistent memory.

    Args:
        hypothesis: One-sentence economic thesis
        factor_expression: Factor grammar expression tested
        reasoning_trace: The 4-element reasoning trace from Step 1
        screening_result: Output of screen_factors() — t_stat, IC, passed/failed
        oos_result: Walk-forward OOS metrics (if factor passed screening)
        failure_mode: Why it failed (if applicable)
        tags: Category tags (e.g., ['momentum', 'credit', 'volume'])

    Returns:
        The logged record
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "hypothesis": hypothesis,
        "factor_expression": factor_expression,
        "reasoning_trace": reasoning_trace,
        "screening": {
            "t_stat": screening_result.get("t_stat"),
            "ic": screening_result.get("ic"),
            "passed": screening_result.get("passed", False),
        },
        "oos": oos_result,
        "failure_mode": failure_mode,
        "tags": tags or [],
        "status": "passed" if (oos_result and oos_result.get("sharpe", 0) > 0) else "failed",
    }

    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def load_memory() -> list:
    """Load all discovery records."""
    if not MEMORY_PATH.exists():
        return []
    records = []
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records
```

### Memory Record Schema

| Field | Type | Purpose |
|---|---|---|
| `timestamp` | ISO datetime | When the cycle ran |
| `hypothesis` | str | One-sentence economic thesis |
| `factor_expression` | str | Grammar expression (e.g., `rank(mom_13w) * z_score(spread)`) |
| `reasoning_trace` | dict | The 4-element trace from SKILL.md Step 1 |
| `screening.t_stat` | float | Univariate t-statistic from screening gate |
| `screening.ic` | float | Information coefficient |
| `screening.passed` | bool | Whether it cleared |t| > 3.0 |
| `oos.sharpe` | float | Walk-forward OOS Sharpe (if reached that stage) |
| `oos.regime_performance` | dict | Per-regime Sharpe breakdown |
| `failure_mode` | str | Why it failed (e.g., "regime-specific", "below hurdle", "OOS collapse") |
| `tags` | list | Category tags for search |
| `status` | str | "passed" or "failed" |

---

## Negative Memory

**Failed hypotheses are as valuable as successes.** Explicitly recording *why* something failed prevents:
1. Re-testing the same discredited idea in a future session
2. Making the same structural mistake (e.g., "momentum features always fail below 4w lookback in this asset class")
3. Wasting the multiple-testing budget on known dead-ends

```python
def get_failed_patterns(memory: list) -> dict:
    """
    Extract recurring failure patterns from discovery memory.

    Returns:
        Dict grouping failures by failure_mode with counts and examples
    """
    failures = [r for r in memory if r["status"] == "failed"]
    patterns = {}
    for r in failures:
        mode = r.get("failure_mode", "unknown")
        if mode not in patterns:
            patterns[mode] = {"count": 0, "examples": []}
        patterns[mode]["count"] += 1
        patterns[mode]["examples"].append({
            "hypothesis": r["hypothesis"],
            "factor": r["factor_expression"],
            "t_stat": r["screening"]["t_stat"],
        })
    return patterns
```

---

## Exploration vs Exploitation Balance

The search policy must balance two competing needs:
- **Exploitation**: Refine existing successful factors (tweak lookback, add cross-asset confirmation)
- **Exploration**: Test entirely new hypothesis families (different asset, different inefficiency type)

### Policy Rules

1. **After 3 consecutive exploitation cycles** (refinements of the same factor family), the next cycle **must** be exploratory — a new hypothesis family not present in memory
2. **Near-miss factors** (t-stat 2.0-3.0) are exploitation candidates — the hypothesis was directionally correct but the expression needs refinement
3. **Factors with regime-specific failures** should be re-tested with a regime filter, not abandoned entirely — this counts as exploitation
4. **If the last 5 discoveries all failed**, step back and re-run the predictability gate (Step 2) — the target series may have shifted regime

```python
def suggest_next_action(memory: list, max_exploit_streak: int = 3) -> dict:
    """
    Analyze discovery memory and suggest whether to explore or exploit.

    Returns:
        Dict with 'action' ('explore' or 'exploit'), 'reason', and 'candidates'
    """
    if not memory:
        return {"action": "explore", "reason": "empty memory", "candidates": []}

    recent = memory[-max_exploit_streak:]
    recent_tags = [set(r.get("tags", [])) for r in recent]

    # Check if recent cycles are all in the same family
    if len(recent) >= max_exploit_streak:
        common_tags = recent_tags[0]
        for tags in recent_tags[1:]:
            common_tags = common_tags.intersection(tags)
        if common_tags:
            return {
                "action": "explore",
                "reason": f"last {max_exploit_streak} cycles all in family: {common_tags}",
                "candidates": _suggest_unexplored_families(memory),
            }

    # Check for near-misses to exploit
    near_misses = [
        r for r in memory
        if not r["screening"]["passed"]
        and r["screening"]["t_stat"] is not None
        and abs(r["screening"]["t_stat"]) > 2.0
    ]
    if near_misses:
        return {
            "action": "exploit",
            "reason": f"{len(near_misses)} near-miss factors to refine",
            "candidates": near_misses[-3:],
        }

    # Check for consecutive failure streak
    recent_5 = memory[-5:]
    if all(r["status"] == "failed" for r in recent_5):
        return {
            "action": "explore",
            "reason": "last 5 discoveries failed -- re-run predictability gate",
            "candidates": [],
        }

    return {"action": "explore", "reason": "default -- seek new hypotheses", "candidates": []}


def _suggest_unexplored_families(memory: list) -> list:
    """Identify tag families not yet tested."""
    all_tags = set()
    for r in memory:
        all_tags.update(r.get("tags", []))

    known_families = [
        "momentum", "mean_reversion", "volatility", "carry", "liquidity",
        "sentiment", "flow", "structural", "cross_asset", "yield_curve",
    ]
    unexplored = [f for f in known_families if f not in all_tags]
    return unexplored
```

---

## Policy Evolution

After each discovery cycle, update search priors based on accumulated evidence.

```python
def compute_search_priors(memory: list) -> dict:
    """
    Compute empirical success rates by tag family to guide future search.

    Returns:
        Dict of {tag: {'attempts': N, 'successes': N, 'avg_t_stat': float, 'priority': str}}
    """
    tag_stats = {}
    for r in memory:
        for tag in r.get("tags", []):
            if tag not in tag_stats:
                tag_stats[tag] = {"attempts": 0, "successes": 0, "t_stats": []}
            tag_stats[tag]["attempts"] += 1
            if r["status"] == "passed":
                tag_stats[tag]["successes"] += 1
            t = r["screening"].get("t_stat")
            if t is not None:
                tag_stats[tag]["t_stats"].append(abs(t))

    result = {}
    for tag, stats in tag_stats.items():
        success_rate = stats["successes"] / stats["attempts"] if stats["attempts"] > 0 else 0
        avg_t = sum(stats["t_stats"]) / len(stats["t_stats"]) if stats["t_stats"] else 0
        result[tag] = {
            "attempts": stats["attempts"],
            "successes": stats["successes"],
            "success_rate": round(success_rate, 2),
            "avg_t_stat": round(avg_t, 2),
            "priority": "high" if success_rate > 0.3 else "medium" if success_rate > 0.1 else "low",
        }

    return dict(sorted(result.items(), key=lambda x: x[1]["success_rate"], reverse=True))
```

### Using Priors in Practice

- **High-priority families** (success rate > 30%): allocate more exploitation cycles here
- **Medium-priority families** (10-30%): occasional exploration, combine with regime filters
- **Low-priority families** (< 10%): only explore with a genuinely new hypothesis, not parameter tweaks
- **Untested families**: always worth at least one exploration cycle

---

## Integration with the Pipeline

Discovery memory connects to the main pipeline at three points:

1. **Step 1 (Hypothesis)**: Before writing the reasoning trace, check memory for prior attempts on the same inefficiency. Build on successes, avoid repeating failures.
2. **Step 3 (Screening Gate)**: Log every screened factor — passed or failed — with its t-stat and IC.
3. **Step 6 (Walk-Forward)**: Log OOS results and regime-specific performance for factors that reached this stage.

---

## See Also

- `feature-engineering.md` — Factor Screening Gate logs results to discovery memory; factor grammar and symbolic regression
- `SKILL.md` Step 1 — Reasoning Trace should reference prior discoveries
- `model-selection.md` — Non-Linear Factor Aggregation uses validated factors from the screening gate
- `regime-philosophy.md` — Regime-specific failures are a key failure mode to track; test across regimes not just time
- `validation-backtesting.md` — DSR calculation for multiple trials (essential after GA); drawdown analysis
- `predictability-analysis.md` — Run predictability score before GA to confirm signal exists
- `eda-ml-practices.md` — EDA methodology and ML best practices applicable before and after GA runs
