---
name: ml-algo-trading
description: >
  Use this skill whenever the work touches systematic trading with ML or statistics — even if
  the user only says "backtest", "overfitting", "alpha", "factors", "Sharpe", "walk-forward",
  "PurgedKFold", "PSR/DSR", "triple barrier", "meta-label", "HRP", "regime", or is wiring an
  agent to do quant research. Also use for lead–lag, Granger causality, cross-asset timing,
  n_trials and data snooping, feature screening (|t|>3), predictability, fractional
  differentiation, discovery memory, genetic-algorithm factor search, or validation design.
  The skill is the canonical 9-step pipeline: hypothesis and data validation, features,
  labels, purged CV, walk-forward, deflated/probabilistic Sharpe, deploy/reject — with deep
  reference docs for each step under references/.
---

# ML Algorithmic Trading Toolkit

This skill provides a systematic, 9-step pipeline for developing and validating machine learning-based trading strategies. It emphasizes robustness and overfitting prevention, incorporating best practices from modern financial machine learning.

> **Reference files** for this skill live at `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\`. Wherever instructions say "read `references/[file].md` in this skill's folder", use that absolute path.

### Progressive disclosure (load references as needed)

| User intent | Read first |
|-------------|------------|
| Data leaks, PIT, survivorship, provenance | `data-validation.md` |
| "Is this series worth modeling?" / entropy / Hurst | `predictability-analysis.md` |
| FFD, factor grammar, screening gate | `feature-engineering.md` |
| Triple barrier, meta-label, sample weights | `labeling-weighting.md` |
| A leads B, Granger, n_trials for pairs, Epps, net-of-cost | `lead-lag-predictive-inclusion.md` |
| Purged K-fold, PSR, DSR, walk-forward, Kelly, CPCV/PBO | `validation-backtesting.md` |
| GBM tuning, SHAP, non-linear factor aggregation | `model-selection.md` |
| Regimes, HMM, live monitoring, τ stability | `regime-philosophy.md` |
| HRP, portfolio weights | `portfolio-construction.md` |
| GA, discovery memory, filter testing | `strategy-improvement.md` |

**Compatibility:** Python 3.10+ recommended; install libraries via Step 0 (`uv add pandas numpy statsmodels scikit-learn lightgbm xgboost vectorbt shap hmmlearn gplearn`).

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

Cross-asset **timing** hypotheses (A leads B) require explicit **temporal** structure, **transmission** rationale, and **rolling/OOS** validation — see `references/lead-lag-predictive-inclusion.md`. That is in addition to the standard regime axiom, not a replacement for it.

### Step 0: Install Dependencies
Install the core libraries required for most trading strategy workflows.
```bash
uv add pandas numpy statsmodels scikit-learn lightgbm xgboost vectorbt shap hmmlearn gplearn
```

`statsmodels` supports **Granger** and classical time-series tests used in `references/lead-lag-predictive-inclusion.md`. **Transfer entropy** and similar nonlinear screens are **optional** and are **not** a required `uv add` in the core skill.

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

5.  **(Conditional — A leads B / cross-series timing only)** **Information flow and transmission**: In one short paragraph, state **how** information is supposed to travel from X to Y (e.g. flows, earnings revision lag, options hedging, roll mechanics in a **proxy**). **Pre-register** the **direction** of lead (X→Y, not "both until one fits") and either a **rough lag order of magnitude** or a **small, enumerated** set of candidate lags **tied to that mechanism**. **Heatmap** or **unbounded** pair×lag **fishing** is **not** a valid substitute for (1)–(4); use discovery memory in `references/strategy-improvement.md` Section C to log **rejected** (pair, τ) attempts.

If you cannot complete all four elements (and five when timing is claimed), your hypothesis is underspecified - refine it before proceeding.

### Step 1.5: Data Validation (MANDATORY)
-   **Before any data enters the pipeline**, run it through the validation layer. Read `references/data-validation.md` for the full specification and usage examples.
-   `validate(df)` checks 7 domains: schema, calendar, alignment, bias, quality, reconciliation, provenance.
-   **Bias checks are never skippable** — look-ahead, survivorship, backfill, and corporate action checks always run.
-   Output is a `ValidatedDataset` object that carries the DataFrame plus validation metadata, fill masks, and a provenance hash chain.
-   If validation fails, fix the data issues before proceeding. Do not bypass validation to "see what happens."
-   For **synthetic, ETF, or rolled-futures** series, **reconcile** the economic claim to the **tradable** series (spot vs **rolling** product, **ETF** vs **underlying**). See `references/lead-lag-predictive-inclusion.md` and **Instrument** content in `references/data-validation.md`.

### Step 2: Data + Predictability Gate
-   Select sources matching the signal type (price, fundamental, alternative).
-   Use the `ValidatedDataset` from Step 1.5 as input — point-in-time correctness is already verified.
-   **Run predictability gate** on a representative sample of the target series using `predictability_score()` from `references/predictability-analysis.md`:
    -   **Score < 20 = STOP** - no exploitable signal exists; change asset, timeframe, or hypothesis.
    -   **Score 20-40 = CAUTION** - weak signal only; proceed only with a regime-switching approach and apply stricter thresholds (DSR > 0.97, walk-forward > 70% profitable windows).
    -   **Score > 40 = PROCEED** - sufficient signal to continue.
-   **Bivariate timing hypotheses (X→Y):** If the edge is **cross-series** timing, the marginal predictability of **Y** **alone** may be **low** while **incremental** predictability from **X** still exists. In that case, read the **Bivariate / conditional** footnote in `references/predictability-analysis.md` and `references/lead-lag-predictive-inclusion.md` before treating **Score < 20** on Y as a hard **STOP**. Do not use this as an excuse to skip validation or inflate **n_trials** informally.

### Step 3: Features + Screening Gate
-   Engineer features grounded in the hypothesis. For a full guide on feature construction  -- including autonomous factor discovery via symbolic regression and factor grammar  -- read `references/feature-engineering.md` in this skill's folder.
-   **Hedging vs positioning:** **Contemporaneous** beta and correlation are primarily for **hedge ratio** and **risk**; **directional** timing from another series usually requires **lagged** information flow. See `references/lead-lag-predictive-inclusion.md` for lead–lag, **Granger** (predictive inclusion), and how they relate to **IC**.
-   Apply fractional differentiation to achieve stationarity while preserving memory.
-   **MANDATORY Factor Screening Gate**: Every candidate factor must pass **|t-statistic| > 3.0** in a univariate IC test against forward returns before entering the model. Factors below this hurdle are excluded from the feature matrix but logged in the discovery memory (see `references/strategy-improvement.md` Section C). This prevents the "Factor Zoo" problem and limits the multiple-testing penalty at DSR time. See `screen_factors()` in `references/feature-engineering.md`. **Granger** and lead–lag diagnostics are **pre-screens** or **alignment checks** unless the hypothesis **pre-specifies** replacing the IC rule — do not silently swap gates after peeking at results.

### Step 4: Labels
-   Choose a labeling method. For implementation details, read `references/labeling-weighting.md` in this skill's folder.
-   For **X→Y** / **lagged** cross-series **features**: ensure **labels** and **barriers** use **only** information that would be available at **label time** for the **target**; avoid **same-bar** leakage of **Y**'s **future** into the effectively **causal** feature–label construction. See **Causal alignment** in `references/labeling-weighting.md` and Section 11 of `references/lead-lag-predictive-inclusion.md`.
    -   **Simple**: Forward return sign.
    -   **Better**: **Triple-Barrier Method** for dynamic profit-taking and stop-loss.
    -   **Advanced**: **Meta-Labeling** to separate the bet sizing decision from the direction.

### Step 5: Model + Purged CV
-   Select a model based on dataset size (see decision tree below).
-   **MANDATORY**: Use **Purged K-Fold Cross-Validation** to prevent data leakage. For the `PurgedKFold` class implementation, read `references/validation-backtesting.md`. For hyperparameter tuning patterns using purged CV, read `references/model-selection.md`.
-   **GA alternative**: When searching 20+ indicator parameters, use Genetic Algorithm optimization instead of grid search. Read `references/strategy-improvement.md` Section B. **Record n_trials = population_size x generations x re-runs** -- you will need this number in Step 7 for DSR.
-   **Lead–lag / Granger exploration:** If you run **pair × lag τ × maxlag** (or **bidirectional** A↔B) searches that **informed** which features entered the model, add those **counts** to the **n_trials** total for DSR in Step 7 (same **honesty** as for GA). See `references/lead-lag-predictive-inclusion.md` Section 5.

### Step 6: Walk-Forward Validation
-   Use an expanding or rolling window to simulate live trading.
-   **Pass condition**: Strategy achieves positive annualized return in >= 60% of walk-forward windows (or >= 70% if predictability score was 20-40).
-   **Trigger for Strategy Improver**: If 40-60% of windows are profitable (below threshold but not a total failure), apply the binary filter testing framework from `references/strategy-improvement.md` Section A before declaring failure. Never optimize filter parameters - test each filter as strictly binary (present vs. absent).
-   **Rolling lead–lag / Granger stability** can be treated as a **diagnostic** in the same **binary** spirit (e.g. “signal **off** when rolling Granger p-value > threshold” — **pre-specify** the rule **before** test) when diagnosing **regime-conditional** failure; see `references/lead-lag-predictive-inclusion.md`.

### Step 7: PSR + Deflated Sharpe Ratio
-   **First run PSR** (Probabilistic Sharpe Ratio) on walk-forward OOS returns: confirms the observed SR is statistically significant, accounting for fat tails and skew. **PSR < 0.95 = FAIL** - SR estimate is unreliable; do not proceed to deployment.
-   **Then run DSR** (Deflated Sharpe Ratio): adjusts for the number of strategy trials tested. **DSR < 0.95 = FAIL** - high probability of data snooping.
    -   If GA was used in Step 5: set `n_trials = population_size x generations x re-runs` (the count recorded in Step 5). Do not use n_trials = 1.
    -   If **lead–lag / Granger** grids (pair × τ × `maxlag`, including **both** directions if both were **tested to choose** features) were used, **add** that **count** to `n_trials` — it is not enough to count only the final **model** seed. See `references/lead-lag-predictive-inclusion.md` Section 5. Optional: **CPCV** and **PBO** in `references/validation-backtesting.md` for heavy combinatorial searches.
-   For both implementations, read `references/validation-backtesting.md` in this skill's folder.

### Step 8: Deploy or Reject
-   Run the final **Overfitting Prevention Checklist** below. All items must pass.
-   **Position sizing**: Use Kelly Criterion to convert model probabilities into position sizes. Half-Kelly (scale=0.5) is the standard safe choice. Read `references/validation-backtesting.md` for `probability_to_position_size()`.
-   **Multi-asset portfolios**: Use Hierarchical Risk Parity (HRP) to allocate across assets or strategies. Read `references/portfolio-construction.md`.
-   **Production monitoring**: Deploy regime probability tracker and rolling moment stability monitor. See live monitoring section in `references/regime-philosophy.md`. For **cross-series** timing features, add **lag decay** and **Granger** / **optimal-τ** **stability** checks as in `references/lead-lag-predictive-inclusion.md` Section 13.

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
| **High IC but Granger fails** | Feature may be **contemporaneous** / **beta**-like or misaligned vs **lag** hypothesis | Re-check **causal alignment**; distinguish **hedging** vs **timing**; see `references/lead-lag-predictive-inclusion.md` Section 4 |
| **Granger passes but strategy unprofitable** | **Linear** inclusion does not imply **net** edge; **costs** or **nonlinear** implementation | **Net-of-cost** IC; walk-forward with **turnover**; optional **GBM** vs **linear** — count **model** search in **n_trials** |
| **Optimal τ flips across rolling windows** | **Regime** **inversion** or **overfit** **full-sample** τ | **Regime-indexed** τ; **disable** signal when **rolling** **stability** fails; `references/regime-philosophy.md` |
| **Spurious lead at high frequency** | **Epps** / **asynchronous** **microstructure** | Do not port **daily** **shift** **pipelines** to **tick** without **HF** **discipline**; `references/lead-lag-predictive-inclusion.md` Section 8 |

---

## MANDATORY: Overfitting Prevention Checklist

**Verify ALL items before declaring any strategy validated. If ANY item fails, reject or revise.**

-   [ ] **Economic rationale**: Can you explain WHY this pattern should persist, independent of the data?
-   [ ] **Regime coverage**: Backtest spans >= 2 distinct market regimes. Single-regime backtest proves nothing about generalization. *(Fix: extend history or explicitly segment and test by regime - see `references/regime-philosophy.md` pre-flight checklist.)*
-   [ ] **Feature importance**: Top features make economic sense, verified with SHAP. *(Fix: Remove features that rank high but have no economic story; they are spurious correlations.)*
-   [ ] **OOS degradation**: OOS performance not significantly worse than IS. *(Fix: Reduce features or increase regularization.)*
-   [ ] **Walk-forward consistency**: Profitable (positive annualized return) in >= 60% of walk-forward windows. *(Fix: Add regime filter or simplify the model.)*
-   [ ] **PSR**: Probabilistic Sharpe Ratio > 0.95 on walk-forward OOS returns. *(Fix: Extend data history; or reduce benchmark SR.)*
-   [ ] **Deflated Sharpe**: DSR > 0.95 accounting for all trials (**n_trials** from Step 5, **including** lead–lag / **Granger** **grids** that **informed** feature choice). *(Fix: Test fewer variations; use GA's full evaluation count as n_trials; count pair×τ×**maxlag** as in `references/lead-lag-predictive-inclusion.md`.)*
-   [ ] **Factor screening gate**: All features in the model passed |t-statistic| > 3.0 in a univariate IC test before entering the model. *(Fix: Remove features below the hurdle; log them in discovery memory for potential refinement.)*
-   [ ] **No data snooping**: Features and thresholds were chosen *before* examining test data.
-   [ ] **Parameter robustness**: Performance survives -20% perturbation of key parameters. *(Fix: Simplify model or use ensemble.)*
-   [ ] **Stationarity**: All input features pass ADF test (p < 0.05). *(Fix: Apply fractional differentiation or use returns.)*
-   [ ] **Random data test**: Strategy fails on shuffled/surrogate data. *(Fix: If strategy profits on noise, features are too smooth or autocorrelated - increase lag, apply FFD, or remove smoothed moving-average features.)*
-   [ ] **Crisis stress test**: Strategy survives 2008-09, 2020, and 2022 drawdown periods without catastrophic loss. *(Fix: Add volatility-regime filter to reduce exposure during high-vol environments; apply half-Kelly or quarter-Kelly sizing.)*
-   [ ] **Timing / cross-series**: **Transmission** mechanism + **pre-registered** lag set (or small enumerated set); **no** **heatmap-only** discovery. *(Fix: see Step 1 element 5 and `references/lead-lag-predictive-inclusion.md`.)*
-   [ ] **Lead–lag / Granger**: **Rolling** and **OOS** **stable**; **reject** **full-sample-only** promotion. *(Fix: rolling Granger, rolling τ, walk-forward.)*
-   [ ] **n_trials**: **All** **pair×lag×maxlag** (and **bidirectional** tests if used to **choose** features) counted toward **DSR**. *(Fix: Section 5 in `references/lead-lag-predictive-inclusion.md`.)*
-   [ ] **Net-of-cost**: Feature or walk-forward evaluation uses **realistic** **costs** for the **traded** universe. *(Fix: `references/lead-lag-predictive-inclusion.md` Section 10.)*
-   [ ] **Instrument mapping**: **ETF/futures** **proxy** **matches** thesis **or** thesis **reworded** to **tradable** instrument. *(Fix: `references/data-validation.md` and `references/lead-lag-predictive-inclusion.md` Section 7.)*

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
|  ReAct trace: inefficiency -> cause -> expression -> regime   |
|  (+ transmission + lag set when A leads B — see Step 1)        |
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
5. **If the hypothesis claims A leads B:** add **element 5** from Step 1 (**transmission** + **pre-registered** direction and **lag** set)

**Protocol for any AI coding agent:**

```
Agent receives: data panel + discovery memory + search policy suggestion
Agent outputs:
  1. Reasoning trace (4 elements, or 5 when timing is claimed  -- see Step 1)
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
    For lagged / cross-series predictors, `factor_values` must be **causally aligned**
    to the decision date (no same-bar **target** leakage) — see Step 4 and
    `references/lead-lag-predictive-inclusion.md`.

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
| **Brute-force mining** | Agent generates dozens of factors without reasoning traces | Reject any factor without a complete 4- or 5-element trace (5 when A leads B) |
| **Heatmap / pair-lag mining** | Agent searches many pairs and lags without a **transmission** story | Reject; require Step 1 element 5 and **n_trials** for the full search |
| **Dual-test cherry-pick** | Agent only reports when **IC** and **Granger** both pass in-sample | **Pre-specify** one **primary** gate; the other is **diagnostic** — see `references/lead-lag-predictive-inclusion.md` Section 4 |
| **n_trials = 1** after a grid | DSR run with **n_trials = 1** after **pair×τ** exploration | **Count** all exploratory comparisons that **informed** feature choice (Step 5–7) |
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
| `predictability-analysis.md` | **Agent Execution Spec** (annotated CONFIG template + 10-step execution order + **report output template**); entropy suite (5 methods); Hurst, BDS, Runs, Variance Ratio; Predictability Score 0-100; **expanded decision rules table** (10 conditions incl. score 20-40 no-regime case); **bivariate / conditional** footnote for X→Y timing |
| `lead-lag-predictive-inclusion.md` | **Lead–lag** on **returns**; **Granger** (predictive inclusion); **|t|>3** IC **relationship**; **n_trials** (pair×τ×**maxlag**, **bidirectional**); **bivariate** predictability; **ETF/roll** hygiene; **Epps** / HF; optional **transfer entropy**; **net-of-cost**; **adversarial** naive bolt-on table; **label** **leakage**; production **lag** **decay** |
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
- If the YAML `description` field is ever edited to include characters that break parsing (e.g. unquoted `:` inside a **single-line** value), use a **block scalar** (`description: >`) as now or **quote** the string; keep frontmatter **valid YAML**.
