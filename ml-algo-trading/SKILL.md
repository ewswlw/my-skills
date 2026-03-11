---
name: ml-algo-trading
description: >
  A comprehensive toolkit for building, validating, and deploying ML-driven algorithmic trading strategies. Covers the full lifecycle from feature engineering (fractional differentiation, alpha factors) and labeling (triple-barrier, meta-labeling) to robust validation (purged cross-validation, deflated Sharpe ratio) and deployment. Use for tasks involving "trading strategy", "alpha factor", "backtest", "triple barrier", "meta-labeling", "purged CV", "signal generation", "walk-forward", "regime detection", or any ML-driven trading workflow.
---

# ML Algorithmic Trading Toolkit

This skill provides a systematic, 9-step pipeline for developing and validating machine learning-based trading strategies. It emphasizes robustness and overfitting prevention, incorporating best practices from modern financial machine learning.

> **Reference files** for this skill live at `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\`. Wherever instructions say "read `references/[file].md` in this skill's folder", use that absolute path.

## Core Axiom

**Returns are governed by regime-dependent processes, not universal laws.** A single global predictor is structurally misspecified when regimes exist. Before building any model, ask: "What regimes might govern this market, and is my model architecture conditioned on regime state?" For the full framework, read `references/regime-philosophy.md` in this skill's folder.

---

## Strategy Development Lifecycle

Every strategy **MUST** follow this 9-step pipeline. Do not skip steps.

```
0. Install Deps ? 1. Hypothesis ? 2. Data + Predictability Gate ? 3. Features ? 4. Labels
                                                                                       ?
8. Deploy/Reject ?——— 7. PSR + DSR ?——— 6. Walk-Forward ?——— 5. Model + Purged CV
```

### Step 0: Install Dependencies
Install the core libraries required for most trading strategy workflows.
```bash
uv add pandas numpy statsmodels scikit-learn lightgbm xgboost vectorbt shap hmmlearn
```

### Step 1: Hypothesis
-   **Define the economic thesis**: Why should this pattern exist and persist? One sentence minimum.
-   **Specify regime framing**: What regimes govern this market? A strategy that works only in one regime is not a strategy — it's a regime bet. Read `references/regime-philosophy.md` for the pre-flight checklist.
-   **Economic gate**: If no economic rationale exists independent of the data, **STOP**. Data mining without a theory leads to overfit strategies.
-   *Note: The quantitative predictability gate runs in Step 2, after data is loaded.*

### Step 2: Data + Predictability Gate
-   Select sources matching the signal type (price, fundamental, alternative).
-   Verify point-in-time correctness to avoid look-ahead bias.
-   **Run predictability gate** on a representative sample of the target series using `predictability_score()` from `references/predictability-analysis.md`:
    -   **Score < 20 = STOP** — no exploitable signal exists; change asset, timeframe, or hypothesis.
    -   **Score 20–40 = CAUTION** — weak signal only; proceed only with a regime-switching approach and apply stricter thresholds (DSR > 0.97, walk-forward > 70% profitable windows).
    -   **Score > 40 = PROCEED** — sufficient signal to continue.

### Step 3: Features
-   Engineer features grounded in the hypothesis. For a full guide on feature construction, read `references/feature-engineering.md` in this skill's folder.
-   Apply fractional differentiation to achieve stationarity while preserving memory.

### Step 4: Labels
-   Choose a labeling method. For implementation details, read `references/labeling-weighting.md` in this skill's folder.
    -   **Simple**: Forward return sign.
    -   **Better**: **Triple-Barrier Method** for dynamic profit-taking and stop-loss.
    -   **Advanced**: **Meta-Labeling** to separate the bet sizing decision from the direction.

### Step 5: Model + Purged CV
-   Select a model based on dataset size (see decision tree below).
-   **MANDATORY**: Use **Purged K-Fold Cross-Validation** to prevent data leakage. For the `PurgedKFold` class implementation, read `references/validation-backtesting.md`. For hyperparameter tuning patterns using purged CV, read `references/model-selection.md`.
-   **GA alternative**: When searching 20+ indicator parameters, use Genetic Algorithm optimization instead of grid search. Read `references/strategy-improvement.md` Section B. **Record n_trials = population × generations × re-runs** — you will need this number in Step 7 for DSR.

### Step 6: Walk-Forward Validation
-   Use an expanding or rolling window to simulate live trading.
-   **Pass condition**: Strategy achieves positive annualized return in ? 60% of walk-forward windows (or ? 70% if predictability score was 20–40).
-   **Trigger for Strategy Improver**: If 40–60% of windows are profitable (below threshold but not a total failure), apply the binary filter testing framework from `references/strategy-improvement.md` Section A before declaring failure. Never optimize filter parameters — test each filter as strictly binary (present vs. absent).

### Step 7: PSR + Deflated Sharpe Ratio
-   **First run PSR** (Probabilistic Sharpe Ratio) on walk-forward OOS returns: confirms the observed SR is statistically significant, accounting for fat tails and skew. **PSR < 0.95 = FAIL** — SR estimate is unreliable; do not proceed to deployment.
-   **Then run DSR** (Deflated Sharpe Ratio): adjusts for the number of strategy trials tested. **DSR < 0.95 = FAIL** — high probability of data snooping.
    -   If GA was used in Step 5: set `n_trials = population × generations × re-runs` (the count recorded in Step 5). Do not use n_trials = 1.
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
??? N < 500          ? Linear models ONLY (Logistic Regression, Ridge)
??? N = 500–2,000    ? Gradient Boosting (shallow trees: max_depth=2–3)
??? N = 2,000–10,000 ? Full ensemble toolkit (Gradient Boosting, Random Forest, Stacking)
??? N > 10,000       ? Deep Learning viable (LSTM, CNN), but always benchmark against GBM first
```

---

## Troubleshooting Common Issues

| Problem | Diagnosis | Fix |
|---|---|---|
| OOS degradation > 30% (gradual decay from start) | Overfitting to training data | Reduce features (SHAP top 5–8); reduce model complexity (shallower trees, more regularization). |
| **Sudden OOS collapse** — was profitable, then sharp one-time failure | **Regime mismatch** — new regime entered, not overfitting | Check regime-mismatch vs. overfitting table in `references/regime-philosophy.md`. Add regime filter or separate per-regime models. |
| Walk-forward profitable in some date clusters but consistently fails in others | Regime-specific failure pattern | Add regime feature and split training by regime. See regime detection code in `references/advanced-techniques.md`. |
| Class imbalance > 4:1 | Labels dominated by one class | Use `class_weight='balanced'`; or adjust triple-barrier thresholds; or use meta-labeling. |
| ADF fails after FFD at d=0.5 | Series may be near I(1) | Try d=0.6–0.8; or use returns of the FFD series. |
| DSR fails (< 0.95) | Multiple testing penalty too high | Reduce iterations tested; combine via ensemble instead of creating new variations. If GA: record all evaluations in n_trials. |
| **Predictability score < 20** | No exploitable signal in the series | Change asset, timeframe, or hypothesis entirely. Do not build a model. |
| **Predictability score 20–40** | Weak signal only | Use regime-switching approach only; apply stricter walk-forward (70%) and DSR (0.97) thresholds. |
| PSR < 0.95 | SR estimate statistically unreliable | Extend data history; or lower benchmark SR threshold; or accept edge is marginal and reduce position sizing. |

---

## MANDATORY: Overfitting Prevention Checklist

**Verify ALL items before declaring any strategy validated. If ANY item fails, reject or revise.**

-   [ ] **Economic rationale**: Can you explain WHY this pattern should persist, independent of the data?
-   [ ] **Regime coverage**: Backtest spans ? 2 distinct market regimes. Single-regime backtest proves nothing about generalization. *(Fix: extend history or explicitly segment and test by regime — see `references/regime-philosophy.md` pre-flight checklist.)*
-   [ ] **Feature importance**: Top features make economic sense, verified with SHAP. *(Fix: Remove features that rank high but have no economic story; they are spurious correlations.)*
-   [ ] **OOS degradation**: OOS performance not significantly worse than IS. *(Fix: Reduce features or increase regularization.)*
-   [ ] **Walk-forward consistency**: Profitable (positive annualized return) in ? 60% of walk-forward windows. *(Fix: Add regime filter or simplify the model.)*
-   [ ] **PSR**: Probabilistic Sharpe Ratio > 0.95 on walk-forward OOS returns. *(Fix: Extend data history; or reduce benchmark SR.)*
-   [ ] **Deflated Sharpe**: DSR > 0.95 accounting for all trials (n_trials from Step 5). *(Fix: Test fewer variations; use GA's full evaluation count as n_trials.)*
-   [ ] **No data snooping**: Features and thresholds were chosen *before* examining test data.
-   [ ] **Parameter robustness**: Performance survives ±20% perturbation of key parameters. *(Fix: Simplify model or use ensemble.)*
-   [ ] **Stationarity**: All input features pass ADF test (p < 0.05). *(Fix: Apply fractional differentiation or use returns.)*
-   [ ] **Random data test**: Strategy fails on shuffled/surrogate data. *(Fix: If strategy profits on noise, features are too smooth or autocorrelated — increase lag, apply FFD, or remove smoothed moving-average features.)*
-   [ ] **Crisis stress test**: Strategy survives 2008–09, 2020, and 2022 drawdown periods without catastrophic loss. *(Fix: Add volatility-regime filter to reduce exposure during high-vol environments; apply half-Kelly or quarter-Kelly sizing.)*

---

## Reference Files

| File | What's In It |
|---|---|
| `regime-philosophy.md` | Core regime axiom; **What Shifts Across Regimes table** (means, variances, autocorrelations, factor loadings); tactical checklist; HMM + threshold detection; failure diagnostics; **Asset & Timeframe Adaptations table** (daily/weekly/monthly/intraday); live monitoring; intervention triggers |
| `predictability-analysis.md` | **Agent Execution Spec** (annotated CONFIG template + 10-step execution order + **report output template**); entropy suite (5 methods); Hurst, BDS, Runs, Variance Ratio; Predictability Score 0–100; **expanded decision rules table** (10 conditions incl. score 20–40 no-regime case) |
| `feature-engineering.md` | Fractional differentiation, alpha factors, information-driven bars |
| `labeling-weighting.md` | Triple-barrier method, meta-labeling, sample weights |
| `model-selection.md` | Model comparison matrix, GBM hyperparameter grids, SHAP feature selection, tuning with purged CV |
| `validation-backtesting.md` | PurgedKFold class; walk-forward; DSR; PSR; OOS degradation; Kelly Criterion; parameter robustness; **Drawdown Analysis** (`calculate_drawdown`, `time_under_water`); **`validate_strategy()` convenience composite** |
| `advanced-techniques.md` | Deep learning (LSTM, CNN), NLP, reinforcement learning, regime detection code, block bootstrap |
| `strategy-improvement.md` | Section A: Strategy Improver Framework (binary filter testing, base criteria); Section B: GA optimization, multi-objective fitness, DSR for GA, **GA edge case handling**, **GA success criteria checklist**, **GA output documentation requirements** |
| `eda-ml-practices.md` | **EDA statistical techniques** (8 methods); **17-point required EDA output format**; **ML trading best practices** (8 items); **ML trading pitfalls table** (5 items); **four-phase validation checklist** (pre-development ? development ? validation ? documentation) |
| `portfolio-construction.md` | HRP full implementation; MVO comparison; strategy allocation via HRP; rebalancing rules; **Performance Optimization**: vectorization patterns, **`mp_pandas_obj()` atoms-and-molecules multiprocessing**, `PortfolioManager` class |

---

## Windows/Cursor Compatibility Notes

- Install command: `uv add` replaces `sudo uv pip install --system`.
- All reference file paths use absolute form: `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\[file].md`.
- Python-only workflow, fully compatible with Windows/Cursor.
