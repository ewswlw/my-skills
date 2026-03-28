---
name: ml-algo-trading
description: >
  A comprehensive toolkit for building, validating, and deploying ML-driven algorithmic trading strategies. Covers the full lifecycle from feature engineering (fractional differentiation, alpha factors, factor grammar, symbolic regression) and labeling (triple-barrier, meta-labeling) to robust validation (purged cross-validation, deflated Sharpe ratio, factor screening gate) and deployment. Includes agentic workflow integration, discovery memory, non-linear factor aggregation, and ReAct reasoning traces. Use for tasks involving "trading strategy", "alpha factor", "backtest", "triple barrier", "meta-labeling", "purged CV", "signal generation", "walk-forward", "regime detection", "factor discovery", "factor grammar", "screening gate", "discovery memory", or any ML-driven trading workflow.
---

# ML Algorithmic Trading Toolkit

This skill provides a systematic, 9-step pipeline for developing and validating machine learning-based trading strategies. It emphasizes robustness and overfitting prevention, incorporating best practices from modern financial machine learning.

> **Reference files** for this skill live at `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\`. Wherever instructions say "read `references/[file].md` in this skill's folder", use that absolute path.

## Core Axiom

**Returns are governed by regime-dependent processes, not universal laws.** A single global predictor is structurally misspecified when regimes exist. Before building any model, ask: "What regimes might govern this market, and is my model architecture conditioned on regime state?" For the full framework, read `references/regime-philosophy.md` in this skill's folder.

---

## Strategy Development Lifecycle

Every strategy **MUST** follow this pipeline. Do not skip steps.

```
0. Install Deps -> 1. Hypothesis -> 1.5. DATA VALIDATION -> 2. Data + Predictability Gate
                                                                          |
    3. Features + Screening Gate (|t|>3) -> 4. Labels -> 5. Model + Purged CV
                                                                          |
    8. Deploy/Reject <-- 7. PSR + DSR <-- 6. Walk-Forward
```

### Step 0: Install Dependencies
Install the core libraries required for most trading strategy workflows.
```bash
uv add pandas numpy statsmodels scikit-learn lightgbm xgboost vectorbt shap hmmlearn gplearn
```

### Step 1: Hypothesis + Reasoning Trace

**Before any code is written in Steps 2-5, produce a written reasoning trace.** This is a structural regularizer against data-mining - it forces economic thinking before empirical testing, following the Reasoning-Action (ReAct) paradigm.

-   **Define the economic thesis**: Why should this pattern exist and persist? One sentence minimum.
-   **Specify regime framing**: What regimes govern this market? A strategy that works only in one regime is not a strategy - it's a regime bet. Read `references/regime-philosophy.md` for the pre-flight checklist.
-   **Economic gate**: If no economic rationale exists independent of the data, **STOP**. Data mining without a theory leads to overfit strategies.
-   *Note: The quantitative predictability gate runs in Step 2, after data is loaded.*

**MANDATORY Reasoning Trace** - write all four elements before proceeding:

1.  **Market inefficiency identified**: What specific inefficiency are you exploiting? (e.g., "liquidity supply/demand imbalance after index rebalancing")
2.  **Behavioral or structural cause**: Why does this inefficiency persist? (e.g., "forced selling by passive funds creates temporary mispricing that active managers are slow to arbitrage")
3.  **Expected factor expression**: What mathematical form should the signal take? Use the factor grammar from `references/feature-engineering.md`. (e.g., "`rank(volume_spike_4w) * z_score(spread_13w)`")
4.  **Expected regime sensitivity**: In which regimes should this work, and where might it break? (e.g., "should work in normal vol; may fail during flights to quality when correlations spike")

If you cannot complete all four elements, your hypothesis is underspecified - refine it before proceeding.

### Step 1.5: Data Validation (MANDATORY)
-   **Before any data enters the pipeline**, run it through the validation layer. Read `references/data-validation.md` for the full specification and usage examples.
-   `validate(df)` checks 7 domains: schema, calendar, alignment, bias, quality, reconciliation, provenance.
-   **Bias checks are never skippable** — look-ahead, survivorship, backfill, and corporate action checks always run.
-   Output is a `ValidatedDataset` object that carries the DataFrame plus validation metadata, fill masks, and a provenance hash chain.
-   If validation fails, fix the data issues before proceeding. Do not bypass validation to "see what happens."

### Step 2: Data + Predictability Gate
-   Select sources matching the signal type (price, fundamental, alternative).
-   Use the `ValidatedDataset` from Step 1.5 as input — point-in-time correctness is already verified.
-   **Run predictability gate** on a representative sample of the target series using `predictability_score()` from `references/predictability-analysis.md`:
    -   **Score < 20 = STOP** - no exploitable signal exists; change asset, timeframe, or hypothesis.
    -   **Score 20-40 = CAUTION** - weak signal only; proceed only with a regime-switching approach and apply stricter thresholds (DSR > 0.97, walk-forward > 70% profitable windows).
    -   **Score > 40 = PROCEED** - sufficient signal to continue.

### Step 3: Features + Screening Gate
-   Engineer features grounded in the hypothesis. For a full guide on feature construction  -- including autonomous factor discovery via symbolic regression and factor grammar  -- read `references/feature-engineering.md` in this skill's folder.
-   Apply fractional differentiation to achieve stationarity while preserving memory.
-   **MANDATORY Factor Screening Gate**: Every candidate factor must pass **|t-statistic| > 3.0** in a univariate IC test against forward returns before entering the model. Factors below this hurdle are excluded from the feature matrix but logged in the discovery memory (see `references/strategy-improvement.md` Section C). This prevents the "Factor Zoo" problem and limits the multiple-testing penalty at DSR time. See `screen_factors()` in `references/feature-engineering.md`.

### Step 4: Labels
-   Choose a labeling method. For implementation details, read `references/labeling-weighting.md` in this skill's folder.
    -   **Simple**: Forward return sign.
    -   **Better**: **Triple-Barrier Method** for dynamic profit-taking and stop-loss.
    -   **Advanced**: **Meta-Labeling** to separate the bet sizing decision from the direction.

### Step 5: Model + Purged CV
-   Select a model based on dataset size (see decision tree below).
-   **MANDATORY**: Use **Purged K-Fold Cross-Validation** to prevent data leakage. For the `PurgedKFold` class implementation, read `references/validation-backtesting.md`. For hyperparameter tuning patterns using purged CV, read `references/model-selection.md`.
-   **GA alternative**: When searching 20+ indicator parameters, use Genetic Algorithm optimization instead of grid search. Read `references/strategy-improvement.md` Section B. **Record n_trials = population_size x generations x re-runs** -- you will need this number in Step 7 for DSR.

### Step 6: Walk-Forward Validation
-   Use an expanding or rolling window to simulate live trading.
-   **Pass condition**: Strategy achieves positive annualized return in >= 60% of walk-forward windows (or >= 70% if predictability score was 20-40).
-   **Trigger for Strategy Improver**: If 40-60% of windows are profitable (below threshold but not a total failure), apply the binary filter testing framework from `references/strategy-improvement.md` Section A before declaring failure. Never optimize filter parameters - test each filter as strictly binary (present vs. absent).

### Step 7: PSR + Deflated Sharpe Ratio
-   **First run PSR** (Probabilistic Sharpe Ratio) on walk-forward OOS returns: confirms the observed SR is statistically significant, accounting for fat tails and skew. **PSR < 0.95 = FAIL** - SR estimate is unreliable; do not proceed to deployment.
-   **Then run DSR** (Deflated Sharpe Ratio): adjusts for the number of strategy trials tested. **DSR < 0.95 = FAIL** - high probability of data snooping.
    -   If GA was used in Step 5: set `n_trials = population_size x generations x re-runs` (the count recorded in Step 5). Do not use n_trials = 1.
-   For both implementations, read `references/validation-backtesting.md` in this skill's folder.

### Step 8: Deploy or Reject
-   Run the final **Overfitting Prevention Checklist** below. All items must pass.
-   **Position sizing**: Use Kelly Criterion to convert model probabilities into position sizes. Half-Kelly (scale=0.5) is the standard safe choice. Read `references/validation-backtesting.md` for `probability_to_position_size()`.
-   **Multi-asset portfolios**: Use Hierarchical Risk Parity (HRP) to allocate across assets or strategies. Read `references/portfolio-construction.md`.
-   **Production monitoring**: Deploy regime probability tracker and rolling moment stability monitor. See live monitoring section in `references/regime-philosophy.md`.

---

## Decision Tree: Which Model to Use?

```
Dataset size?
|-- N < 500          -> Linear models ONLY (Logistic Regression, Ridge)
|-- N = 500-2,000    -> Gradient Boosting (shallow trees: max_depth=2-3)
|-- N = 2,000-10,000 -> Full ensemble toolkit (Gradient Boosting, Random Forest, Stacking)
|-- N > 10,000       -> Deep Learning viable (LSTM, CNN), but always benchmark against GBM first
```

---

## Troubleshooting Common Issues

| Problem | Diagnosis | Fix |
|---|---|---|
| OOS degradation > 30% (gradual decay from start) | Overfitting to training data | Reduce features (SHAP top 5-8); reduce model complexity (shallower trees, more regularization). |
| **Sudden OOS collapse** - was profitable, then sharp one-time failure | **Regime mismatch** - new regime entered, not overfitting | Check regime-mismatch vs. overfitting table in `references/regime-philosophy.md`. Add regime filter or separate per-regime models. |
| Walk-forward profitable in some date clusters but consistently fails in others | Regime-specific failure pattern | Add regime feature and split training by regime. See regime detection code in `references/advanced-techniques.md`. |
| Class imbalance > 4:1 | Labels dominated by one class | Use `class_weight='balanced'`; or adjust triple-barrier thresholds; or use meta-labeling. |
| ADF fails after FFD at d=0.5 | Series may be near I(1) | Try d=0.6-0.8; or use returns of the FFD series. |
| DSR fails (< 0.95) | Multiple testing penalty too high | Reduce iterations tested; combine via ensemble instead of creating new variations. If GA: record all evaluations in n_trials. |
| **Predictability score < 20** | No exploitable signal in the series | Change asset, timeframe, or hypothesis entirely. Do not build a model. |
| **Predictability score 20-40** | Weak signal only | Use regime-switching approach only; apply stricter walk-forward (70%) and DSR (0.97) thresholds. |
| PSR < 0.95 | SR estimate statistically unreliable | Extend data history; or lower benchmark SR threshold; or accept edge is marginal and reduce position sizing. |

---

## MANDATORY: Overfitting Prevention Checklist

**Verify ALL items before declaring any strategy validated. If ANY item fails, reject or revise.**

-   [ ] **Economic rationale**: Can you explain WHY this pattern should persist, independent of the data?
-   [ ] **Regime coverage**: Backtest spans >= 2 distinct market regimes. Single-regime backtest proves nothing about generalization. *(Fix: extend history or explicitly segment and test by regime - see `references/regime-philosophy.md` pre-flight checklist.)*
-   [ ] **Feature importance**: Top features make economic sense, verified with SHAP. *(Fix: Remove features that rank high but have no economic story; they are spurious correlations.)*
-   [ ] **OOS degradation**: OOS performance not significantly worse than IS. *(Fix: Reduce features or increase regularization.)*
-   [ ] **Walk-forward consistency**: Profitable (positive annualized return) in >= 60% of walk-forward windows. *(Fix: Add regime filter or simplify the model.)*
-   [ ] **PSR**: Probabilistic Sharpe Ratio > 0.95 on walk-forward OOS returns. *(Fix: Extend data history; or reduce benchmark SR.)*
-   [ ] **Deflated Sharpe**: DSR > 0.95 accounting for all trials (n_trials from Step 5). *(Fix: Test fewer variations; use GA's full evaluation count as n_trials.)*
-   [ ] **Factor screening gate**: All features in the model passed |t-statistic| > 3.0 in a univariate IC test before entering the model. *(Fix: Remove features below the hurdle; log them in discovery memory for potential refinement.)*
-   [ ] **No data snooping**: Features and thresholds were chosen *before* examining test data.
-   [ ] **Parameter robustness**: Performance survives -20% perturbation of key parameters. *(Fix: Simplify model or use ensemble.)*
-   [ ] **Stationarity**: All input features pass ADF test (p < 0.05). *(Fix: Apply fractional differentiation or use returns.)*
-   [ ] **Random data test**: Strategy fails on shuffled/surrogate data. *(Fix: If strategy profits on noise, features are too smooth or autocorrelated - increase lag, apply FFD, or remove smoothed moving-average features.)*
-   [ ] **Crisis stress test**: Strategy survives 2008-09, 2020, and 2022 drawdown periods without catastrophic loss. *(Fix: Add volatility-regime filter to reduce exposure during high-vol environments; apply half-Kelly or quarter-Kelly sizing.)*

---

## Agentic Workflow Integration

This section describes how to use an AI coding agent (Cursor, Claude Code, Manus, Windsurf, or any ReAct-capable agent) as an active participant in the strategy development lifecycle. The agent is not just a code generator  -- it operates as a **reasoning engine** that proposes hypotheses, validates them empirically, and evolves its search policy based on accumulated results.

### Architecture: Four Layers

```
+-------------------------------------------------------------+
|  Layer 1: PERCEPTION (Data Setup)                           |
|  Standardized data panel, primitives, normalization         |
+-------------------------------------------------------------+
|  Layer 2: REASONING (Agent as Hypothesis Generator)         |
|  ReAct trace: inefficiency -> cause -> expression -> regime |
+-------------------------------------------------------------+
|  Layer 3: STRATEGY (Automated Backtesting)                  |
|  Factor computation, screening gate, walk-forward, DSR      |
+-------------------------------------------------------------+
|  Layer 4: FEEDBACK (Memory Update & Refinement)             |
|  Log results, update search priors, suggest next action     |
+-------------------------------------------------------------+
```

### Layer 1: Perception (Data Setup)

Create a standardized data panel script that any agent session can invoke. The primitives should include raw fields and their normalized forms.

```python
# perception.py  -- standardized data panel
# Agent generates this once; all future sessions reuse it

def build_data_panel(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw data into the primitive feature set.
    Z-score and winsorize all cross-sectional features.
    """
    panel = raw_data.copy()

    # Lagged returns at multiple horizons
    for N in [1, 4, 8, 13, 26, 52]:
        panel[f'ret_{N}w'] = panel['price'].pct_change(N)

    # Volume ratios
    panel['vol_ratio_4_26'] = (
        panel['volume'].rolling(4).mean() / panel['volume'].rolling(26).mean()
    )

    # Volatility state
    panel['realized_vol_13w'] = panel['ret_1w'].rolling(13).std() * np.sqrt(52)
    panel['vol_zscore'] = (
        (panel['realized_vol_13w'] - panel['realized_vol_13w'].expanding().mean())
        / panel['realized_vol_13w'].expanding().std()
    )

    # Cross-sectional normalization (winsorize at 3 sigma)
    for col in panel.select_dtypes(include=[np.number]).columns:
        mu = panel[col].expanding().mean()
        sigma = panel[col].expanding().std()
        panel[col] = panel[col].clip(lower=mu - 3*sigma, upper=mu + 3*sigma)

    return panel
```

### Layer 2: Reasoning (Agent as Hypothesis Generator)

Instruct the agent with a persistent system prompt or context that enforces the ReAct paradigm. The agent must:

1. **Identify a market inefficiency**  -- check discovery memory for prior attempts on the same theme
2. **Propose a factor expression** using the factor grammar from `references/feature-engineering.md`
3. **State a behavioral or structural rationale**  -- this is the reasoning trace from Step 1
4. **Only then** write code to compute and test the factor

**Protocol for any AI coding agent:**

```
Agent receives: data panel + discovery memory + search policy suggestion
Agent outputs:
  1. Reasoning trace (4 elements  -- see Step 1)
  2. Factor computation code (using grammar primitives)
  3. Screening gate results
  4. If passed: walk-forward backtest
  5. Memory log entry (passed or failed, with failure mode)
```

The agent must **never** skip the reasoning trace and jump to code. If it does, the output is invalid  -- reject and re-prompt. This structural constraint is what prevents the agent from degenerating into a brute-force data miner.

### Layer 3: Strategy (Automated Backtesting)

Create a backtest execution script that the agent can call with any factor recipe. This decouples hypothesis generation from evaluation.

```python
# strategy_executor.py -- receives factor recipe, returns metrics
# Uses screen_factors() from references/feature-engineering.md
# Uses walk_forward_analysis() from references/validation-backtesting.md

import pandas as pd
import numpy as np
from scipy import stats

def execute_factor_test(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    freq: int = 52,
) -> dict:
    """
    Standard factor evaluation: screening gate + quintile spread + walk-forward.
    The agent calls this with pre-computed factor values.

    Returns:
        Dict with screening_result, quintile spread, walk_forward pass/fail
    """
    # 1. Screening gate (inline -- see references/feature-engineering.md for full version)
    valid = factor_values.dropna()
    aligned = forward_returns.reindex(valid.index).dropna()
    common = valid.index.intersection(aligned.index)

    if len(common) < 30:
        return {'stage': 'screening', 'passed': False,
                'screening': {'t_stat': 0, 'ic': 0, 'passed': False}}

    ic = valid.loc[common].corr(aligned.loc[common])
    n = len(common)
    t_stat = ic * np.sqrt(n - 2) / np.sqrt(1 - ic**2) if abs(ic) < 1 else 0

    screening = {'t_stat': round(t_stat, 2), 'ic': round(ic, 4),
                 'passed': abs(t_stat) > 3.0}

    if not screening['passed']:
        return {'stage': 'screening', 'passed': False, 'screening': screening}

    # 2. Top/bottom quintile spread (annualized)
    quintile = pd.qcut(factor_values.loc[common], 5, labels=False, duplicates='drop')
    top = aligned.loc[common][quintile == quintile.max()].mean()
    bottom = aligned.loc[common][quintile == quintile.min()].mean()
    spread_ann = (top - bottom) * freq

    # 3. Walk-forward consistency check
    signal = (factor_values > factor_values.expanding().median()).astype(int)
    signal_returns = forward_returns * signal.reindex(forward_returns.index).fillna(0)
    rolling_sr = signal_returns.rolling(freq).apply(
        lambda x: x.mean() / x.std() * np.sqrt(freq) if x.std() > 0 else 0
    ).dropna()
    pct_profitable = float((rolling_sr > 0).mean())

    return {
        'stage': 'walk_forward',
        'passed': pct_profitable >= 0.60,
        'screening': screening,
        'quintile_spread_ann': round(spread_ann, 4),
        'pct_profitable_windows': round(pct_profitable, 3),
    }
```

### Layer 4: Feedback (Memory Update & Refinement)

After every test  -- pass or fail  -- the agent logs results and consults the search policy.

**Refinement prompt pattern:**

> "The Sharpe ratio for this [factor description] was [X] due to [diagnosis]. The factor worked in [regime A] but failed in [regime B]. Revise the factor expression to [specific improvement goal] while maintaining [constraint]. Check discovery memory for prior attempts on this hypothesis family before proposing a revision."

This emulates the memory-update mechanism from `references/strategy-improvement.md` Section C and prevents the agent from blindly repeating failed approaches.

### Anti-Patterns to Prevent

| Anti-Pattern | How It Manifests | Prevention |
|---|---|---|
| **Brute-force mining** | Agent generates dozens of factors without reasoning traces | Reject any factor without a complete 4-element trace |
| **Parameter tweaking loops** | Agent keeps adjusting the same factor's lookback window | Enforce exploration after 3 consecutive exploitation cycles |
| **Ignoring negative memory** | Agent re-tests a hypothesis that already failed | Require memory check before every new hypothesis |
| **Skipping the screening gate** | Agent feeds unscreened factors directly into GBM | Gate is mandatory  -- no exceptions |
| **Reporting cherry-picked results** | Agent shows only the best walk-forward window | Require full walk-forward and DSR with correct n_trials |

---

## Reference Files

| File | What's In It |
|---|---|
| `data-validation.md` | **Step 1.5 mandatory validation layer**; `validate()` API; `ValidatedDataset` wrapper; 7 validation domains (schema, calendar, alignment, bias, quality, reconciliation, provenance); `ValidationConfig` with 25+ fields; bias prevention (look-ahead shift-and-correlate + AST audit, survivorship, selection, backfill, corporate actions); asset-class-specific gap thresholds; provenance SHA-256 hash chain; edge case handling (12 cases); usage examples |
| `regime-philosophy.md` | Core regime axiom; **What Shifts Across Regimes table** (means, variances, autocorrelations, factor loadings); tactical checklist; HMM + threshold detection; failure diagnostics; **Asset & Timeframe Adaptations table** (daily/weekly/monthly/intraday); live monitoring; intervention triggers |
| `predictability-analysis.md` | **Agent Execution Spec** (annotated CONFIG template + 10-step execution order + **report output template**); entropy suite (5 methods); Hurst, BDS, Runs, Variance Ratio; Predictability Score 0-100; **expanded decision rules table** (10 conditions incl. score 20-40 no-regime case) |
| `feature-engineering.md` | Fractional differentiation, alpha factors, information-driven bars; **Autonomous Factor Discovery** (factor grammar, interpretable primitives, symbolic regression via `gplearn`, LLM-assisted ideation); **Factor Screening Gate** (`screen_factors()`, |t-stat| > 3.0 hurdle, temporal isolation) |
| `labeling-weighting.md` | Triple-barrier method, meta-labeling, sample weights |
| `model-selection.md` | Model comparison matrix, GBM hyperparameter grids, SHAP feature selection, tuning with purged CV; **Non-Linear Factor Aggregation** (`build_synthesis_layer()`, GBM as factor combiner vs direct predictor, IC-weighted linear baseline comparison, guard rails) |
| `validation-backtesting.md` | PurgedKFold class; walk-forward; DSR; PSR; OOS degradation; Kelly Criterion; parameter robustness; **Drawdown Analysis** (`calculate_drawdown`, `time_under_water`); **`validate_strategy()` convenience composite** |
| `advanced-techniques.md` | Deep learning (LSTM, CNN), NLP, reinforcement learning, regime detection code, block bootstrap |
| `strategy-improvement.md` | Section A: Strategy Improver Framework (binary filter testing, base criteria); Section B: GA optimization, multi-objective fitness, DSR for GA, **GA edge case handling**, **GA success criteria checklist**, **GA output documentation requirements**; **Section C: Discovery Memory & Search Policy** (`log_discovery()`, negative memory, exploration vs exploitation balance, `suggest_next_action()`, policy evolution via `compute_search_priors()`) |
| `eda-ml-practices.md` | **EDA statistical techniques** (8 methods); **17-point required EDA output format**; **ML trading best practices** (8 items); **ML trading pitfalls table** (5 items); **four-phase validation checklist** (pre-development -> development -> validation -> documentation) |
| `portfolio-construction.md` | HRP full implementation; MVO comparison; strategy allocation via HRP; rebalancing rules; **Performance Optimization**: vectorization patterns, **`mp_pandas_obj()` atoms-and-molecules multiprocessing**, `PortfolioManager` class |

---

## Compatibility Notes

- Install command: `uv add` replaces `sudo uv pip install --system`.
- All reference file paths use absolute form: `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\[file].md`.
- Python-only workflow, fully compatible with Windows and any AI coding agent (Cursor, Claude Code, Manus, Windsurf, etc.).
