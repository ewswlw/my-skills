# Labeling & Sample Weighting for Financial ML

## Why Standard Labels Fail in Finance

Standard ML labeling (`y = sign(return_t+1)`) has two critical problems:
1. **Path-dependent risk**: A +0.01% return that dipped -5% intra-period is labeled the same as a smooth +0.01% return
2. **Non-IID samples**: Consecutive labels overlap in information content, violating independence assumptions

The techniques below address both problems.

### Causal alignment (lead–lag and cross-series features)

When the **feature** side uses **lagged** information from a **second** series **X** to **predict** **Y**, labels and **triple-barrier** events must be defined with **point-in-time** consistency: only information that would have been **known at the label time** for **Y** may influence the **label** or **barrier** logic. A **non-leaky** lead–lag feature paired with a **leaky** label (e.g. same-bar future information from **Y** smuggled into the “signal”) is a common footgun. See `lead-lag-predictive-inclusion.md` Section 11 and SKILL.md Step 4.

---

## Triple-Barrier Method

### Concept

Instead of labeling based on a fixed-time horizon, set three concurrent barriers:
- **Upper barrier** (profit-taking): price rises to target → label = +1
- **Lower barrier** (stop-loss): price falls to limit → label = -1
- **Vertical barrier** (time-out): max holding period expires → label = sign(return) or 0

The label is determined by **whichever barrier is touched first**.

### Implementation

```python
import pandas as pd
import numpy as np

def get_daily_volatility(close: pd.Series, span: int = 20) -> pd.Series:
    """Compute daily volatility estimate using EWMA of absolute returns."""
    return close.pct_change().ewm(span=span).std()

def get_events(
    close: pd.Series,
    timestamps: pd.DatetimeIndex,
    pt_sl: list = [1.5, 1.0],
    target: pd.Series = None,
    min_ret: float = 0.0,
    max_holding: int = 10,
) -> pd.DataFrame:
    """
    Compute triple-barrier events.
    
    Args:
        close: Price series
        timestamps: Signal timestamps (when to evaluate barriers)
        pt_sl: [profit-taking multiplier, stop-loss multiplier] × target
        target: Volatility target per timestamp (daily vol)
        min_ret: Minimum return threshold for time-barrier labels
        max_holding: Maximum bars to hold before time-out
    
    Returns:
        DataFrame with columns: t1 (first barrier time), ret (return), label
    """
    if target is None:
        target = get_daily_volatility(close)
    
    events = []
    for t0 in timestamps:
        if t0 not in close.index or t0 not in target.index:
            continue
        
        trgt = target.loc[t0]
        if pd.isna(trgt) or trgt <= 0:
            continue
        
        # Set barriers
        upper = close.loc[t0] * (1 + pt_sl[0] * trgt) if pt_sl[0] > 0 else np.inf
        lower = close.loc[t0] * (1 - pt_sl[1] * trgt) if pt_sl[1] > 0 else -np.inf
        
        # Time barrier
        t1_idx = close.index.searchsorted(t0) + max_holding
        t1 = close.index[min(t1_idx, len(close) - 1)]
        
        # Find first barrier touch
        path = close.loc[t0:t1]
        
        # Upper barrier touch
        upper_touch = path[path >= upper].index
        t_upper = upper_touch[0] if len(upper_touch) > 0 else pd.NaT
        
        # Lower barrier touch
        lower_touch = path[path <= lower].index
        t_lower = lower_touch[0] if len(lower_touch) > 0 else pd.NaT
        
        # First barrier
        first_barrier = min(
            t_upper if not pd.isna(t_upper) else t1,
            t_lower if not pd.isna(t_lower) else t1,
            t1
        )
        
        # Compute return and label
        ret = (close.loc[first_barrier] - close.loc[t0]) / close.loc[t0]
        
        if first_barrier == t1 and abs(ret) < min_ret:
            label = 0  # Below minimum return at time-out
        else:
            label = np.sign(ret)
        
        events.append({
            't0': t0, 't1': first_barrier,
            'ret': ret, 'label': int(label),
            'barrier': 'upper' if first_barrier == t_upper else
                       'lower' if first_barrier == t_lower else 'time'
        })
    
    return pd.DataFrame(events).set_index('t0')
```

### Calibrating Barrier Parameters

| Parameter | Guideline | Notes |
|-----------|-----------|-------|
| `pt_sl[0]` (profit-taking) | 1.0-2.0 × daily_vol | Higher = more patient; captures larger moves |
| `pt_sl[1]` (stop-loss) | 0.5-1.5 × daily_vol | Lower = tighter stop; more defensive |
| `max_holding` | 5-20 bars | Match to strategy horizon |
| `min_ret` | 0.0-0.5 × daily_vol | Filter out noise labels at time barrier |

**Asymmetric barriers** (pt > sl) are common: let winners run, cut losers early.

### Label Distribution Diagnostics

```python
# After labeling, check distribution
label_counts = events['label'].value_counts()
barrier_counts = events['barrier'].value_counts()

# Red flags:
# - >80% time-barrier labels → barriers too wide or holding too short
# - <5% of either upper/lower → one barrier is unreachable
# - Extreme class imbalance (>4:1) → may need resampling or class weights
```

---

## Meta-Labeling

### Concept

A two-model architecture:
1. **Primary model** decides the **side** of the trade (long or short)
2. **Secondary model** (meta-labeler) learns **when the primary is correct** and the **bet size**

This separates the "what to trade" decision from the "how much to risk" decision.

### Implementation

```python
def meta_label(
    primary_side: pd.Series,
    forward_returns: pd.Series,
) -> pd.Series:
    """
    Create meta-labels from primary model predictions and actual returns.
    
    Args:
        primary_side: Primary model output (+1 = long, -1 = short, 0 = no trade)
        forward_returns: Actual next-period returns
    
    Returns:
        Binary series: 1 = primary was correct, 0 = primary was wrong
    """
    # Only label where primary has a position
    active = primary_side != 0
    
    meta_y = pd.Series(0, index=primary_side.index)
    meta_y[active] = (primary_side[active] * forward_returns[active] > 0).astype(int)
    
    return meta_y

# Full workflow
# Step 1: Primary model (can be rule-based, simple ML, or human discretion)
primary_side = rule_based_model.predict(X)  # +1, -1, or 0

# Step 2: Create meta-labels
meta_y = meta_label(primary_side, forward_returns)

# Step 3: Train meta-model (only on observations where primary has a position)
active_mask = primary_side != 0
meta_model = GradientBoostingClassifier(max_depth=2, n_estimators=100)
meta_model.fit(X_train[active_mask], meta_y[active_mask])

# Step 4: Predict
prob_correct = meta_model.predict_proba(X_test)[:, 1]

# Step 5: Final position
# Option A: Binary filter
position = primary_side * (prob_correct > 0.55).astype(int)

# Option B: Continuous sizing
position = primary_side * prob_correct  # Scale by confidence
```

### When to Use Meta-Labeling

| Scenario | Recommended? | Why |
|----------|-------------|-----|
| Strong primary model with variable accuracy | **Yes** | Meta-learner captures when primary works best |
| Weak primary model | No | "Garbage in, garbage out" — fix primary first |
| Combining discretionary + systematic | **Yes** | Human picks direction, ML sizes the bet |
| Binary long/cash strategy | **Yes** | Primary = always long, meta-learner = when to go to cash |

### Key Implementation Notes

- Train meta-model using **Purged K-Fold CV** (label overlap is a leakage risk)
- Meta-model features can differ from primary model features
- The probability threshold (e.g., 0.55) should be tuned on validation data
- Meta-labeling naturally handles class imbalance (most primary signals are correct → ~60-70% positive labels)

---

## Sample Uniqueness & Weighting

### The Problem

Financial labels overlap in time. If a 5-bar forward return is used, the label at time t shares 4 bars with the label at t+1. This violates the IID assumption and causes:
- Overweighting of crowded periods
- Inflated cross-validation scores
- Underestimation of model uncertainty

### Average Uniqueness

```python
def get_avg_uniqueness(
    label_start: pd.Series,
    label_end: pd.Series,
    timestamps: pd.DatetimeIndex,
) -> pd.Series:
    """
    Compute average uniqueness for each label.
    
    Uniqueness at time t = 1 / (number of labels active at time t)
    Average uniqueness for label i = mean uniqueness across label i's lifespan.
    
    Args:
        label_start: Start timestamp of each label
        label_end: End timestamp of each label
        timestamps: All observation timestamps
    
    Returns:
        Series of average uniqueness values (0 to 1)
    """
    # Build concurrency matrix
    concurrency = pd.Series(0.0, index=timestamps)
    for start, end in zip(label_start, label_end):
        concurrency.loc[start:end] += 1
    
    # Compute uniqueness per label
    uniqueness = []
    for start, end in zip(label_start, label_end):
        concurrent = concurrency.loc[start:end]
        avg_u = (1.0 / concurrent).mean()
        uniqueness.append(avg_u)
    
    return pd.Series(uniqueness, index=label_start.index)

# Usage
sample_weights = get_avg_uniqueness(events['t0'], events['t1'], df.index)

# Apply as sample weights in model training
model.fit(X_train, y_train, sample_weight=sample_weights)
```

### Sequential Bootstrap

Standard bootstrap fails for overlapping labels — it draws "independent" samples that are actually dependent. The sequential bootstrap draws samples based on their average uniqueness given already-drawn samples.

```python
def sequential_bootstrap(
    indicator_matrix: pd.DataFrame,
    n_samples: int = None,
) -> list:
    """
    Draw bootstrap sample respecting label overlap.
    
    Args:
        indicator_matrix: Binary matrix (rows=timestamps, cols=labels)
                         1 where label i is active at timestamp t
        n_samples: Number of samples to draw (default = number of labels)
    
    Returns:
        List of selected label indices
    """
    if n_samples is None:
        n_samples = indicator_matrix.shape[1]
    
    selected = []
    for _ in range(n_samples):
        # Compute avg uniqueness of each candidate given already selected
        avg_u = []
        for j in range(indicator_matrix.shape[1]):
            # Count concurrency from selected + candidate j
            concurrent = indicator_matrix.iloc[:, selected + [j]].sum(axis=1)
            active = indicator_matrix.iloc[:, j] > 0
            u = (1.0 / concurrent[active]).mean()
            avg_u.append(u)
        
        # Probability of selection proportional to uniqueness
        probs = np.array(avg_u)
        probs /= probs.sum()
        selected.append(np.random.choice(len(avg_u), p=probs))
    
    return selected
```

---

## Label Quality Diagnostics

After creating labels, verify quality:

```python
def label_diagnostics(events: pd.DataFrame, returns: pd.Series):
    """Print diagnostic statistics for labels."""
    print("=== Label Distribution ===")
    print(events['label'].value_counts(normalize=True))
    
    print("\n=== Barrier Distribution ===")
    if 'barrier' in events.columns:
        print(events['barrier'].value_counts(normalize=True))
    
    print("\n=== Average Return by Label ===")
    print(events.groupby('label')['ret'].mean())
    
    print("\n=== Label Autocorrelation (lag 1-5) ===")
    for lag in range(1, 6):
        ac = events['label'].autocorr(lag=lag)
        print(f"  Lag {lag}: {ac:.3f}")
    
    # Red flags:
    # - Autocorrelation > 0.3 at lag 1 → labels are highly persistent → model will learn "stay in same state"
    # - Mean return for label=+1 ≈ mean return for label=-1 → labels are uninformative
    # - >90% one class → severe imbalance, use class_weight='balanced' or SMOTE
```
