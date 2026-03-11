# EDA Methodology & ML Trading Best Practices

Perform comprehensive EDA **before** strategy development to understand the data, avoid
wasted modeling effort, and establish a clean baseline. Also reference when evaluating
ML model results and documenting strategy decisions.

---

## EDA Statistical Techniques

Apply these techniques during exploratory analysis:

1. **Bootstrapped Confidence Intervals** — calculate CIs for all key statistics; use
   bootstrap resampling to account for non-normality in return distributions
2. **Multiple Testing Corrections** — apply Bonferroni, FDR, or Holm correction when
   testing many hypotheses; document degrees of freedom consumed
3. **Time-Series Cross-Validation** — purged k-fold with embargo (see `validation-backtesting.md`);
   never standard k-fold (creates look-ahead bias)
4. **Monte Carlo Tail Probes** — stress test with Monte Carlo simulation; analyze tail risk
   and extreme scenarios to find failure modes before deployment
5. **Walk-Forward and Out-of-Sample Testing** — minimum 20% OOS; never use in-sample
   results for strategy selection
6. **Crisis Stress Tests** — test on 2008–09, 2020, and 2022 explicitly; identify failure modes
7. **Cross-Asset Robustness** — verify signal persists across multiple assets/universes;
   if only works on one asset, likely data-mined
8. **Live-Execution Replication** — simulate realistic execution constraints including
   transaction costs, slippage, and market impact; verify profitability after costs

---

## Required EDA Output Format

Every EDA should produce documentation covering all 17 areas:

1. **Executive Summary** — key findings, recommendations, risk warnings
2. **Hypothesis Testing (with Corrections)** — all statistical tests with p-values, multiple
   testing corrections applied, confidence intervals for key statistics
3. **Attribution Statistics** — performance attribution, factor exposures, return decomposition
4. **Robustness Checks** — results across time periods, parameter ranges, and market regimes
5. **Visual Evidence** — charts and graphs: time series, distributions, heatmaps, regime plots
6. **Codable Trading/Risk Rules** — clear, implementable trading rules and risk constraints
7. **Regime Filters** — conditions for strategy activation/deactivation; transition handling
8. **Automation Protocols** — data pipeline specs, model retraining schedule, monitoring rules
9. **Parameter Tuning** — sensitivity analysis, optimal parameter ranges, overfitting guards
10. **Full Performance Metrics (with Confidence Intervals)** — returns, Sharpe, drawdown,
    Calmar, Sortino, win rate, profit factor, expectancy; bootstrap CIs for all
11. **Driver Breakdowns** — what drives strategy performance; key risk factors; attribution
12. **Failure Analysis** — when and why strategy fails; failure modes; conditions to avoid
13. **System Architecture** — data requirements, computational requirements, infrastructure
14. **Data/Production Requirements** — data quality standards, latency requirements, scalability
15. **Pitfalls Documentation** — known limitations, assumptions and validity, edge cases
16. **Regime Mapping** — strategy performance by regime; regime transition behavior;
    optimal regimes for strategy activation
17. **Model-Risk Assessment** — model uncertainty quantification, parameter sensitivity,
    model limitations and assumptions

### EDA Validation Quick Checklist

✓ **Statistical Power** — sufficient sample size for reliable inference (N ≥ 500 minimum)
✓ **Bias Prevention** — no look-ahead, survivorship, or selection bias
✓ **Realistic Costs** — transaction costs, slippage, market impact included
✓ **Regime Robustness** — performance validated across multiple regimes

---

## ML Trading Best Practices

For every ML trading strategy, compute and report these performance metrics:

| Metric | Purpose |
|---|---|
| RMSE / MAE | Prediction error (regression targets) |
| Correlation (predicted vs actual) | Signal quality |
| Strategy Returns | Actual trading performance |
| Sharpe Ratio | Risk-adjusted performance |
| Max Drawdown | Risk measurement |
| Hit Rate | Percentage of correct directional predictions |
| Profit Factor | Sum of wins / sum of losses |

### Implementation Best Practices

1. **Clean and Validate Data** — handle missing values, detect outliers, verify data quality
   and consistency; normalize and scale features appropriately
2. **Avoid Look-Ahead Bias** — use only past data for predictions; verify feature calculation
   is point-in-time; shift signals by 1 bar for next-bar execution; test for future data leaks
3. **Adjust for Corporate Actions** — handle stock splits, dividends, mergers; maintain price
   continuity; use adjusted prices
4. **Watch for Overfitting** — compare train vs test performance; use purged k-fold CV;
   monitor performance decay over time; regularize (L1/L2, depth limits, min_samples_leaf)
5. **Retrain Regularly** — update models with new data; monitor model drift;
   define and schedule retraining cadence; version models
6. **Apply Robust Risk Management** — position sizing based on model confidence (Kelly);
   stop-loss and take-profit levels; maximum position limits; portfolio-level risk controls
7. **Stress Test** — test on crisis periods; simulate extreme scenarios;
   test robustness to parameter changes ±20%; analyze failure modes explicitly
8. **Feature Importance Sanity Check** — verify SHAP top features make economic sense;
   remove features that rank high but have no economic story (spurious correlations)

---

## ML Trading Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| **Survivorship Bias** | Only includes assets that survived the full period | Use point-in-time universes; include delistings |
| **Data Snooping** | Testing many models, reporting the best | Pre-register hypotheses; DSR to correct for multiple testing |
| **Regime Ignorance** | Strong IS, sudden OOS collapse | Test across regimes; add regime feature or filter |
| **Latency/Scaling Failures** | Model too slow for live trading | Test computational requirements; optimize; profile code |
| **Overfitting** | Model fits noise in training data | Regularization; purged CV; OOS testing; parameter robustness |

---

## Four-Phase Validation Checklist

### Phase 1: Pre-Development

- [ ] Data quality verified and documented
- [ ] Point-in-time data sources confirmed (no future leaks)
- [ ] Economic rationale for strategy clearly stated (one sentence minimum)
- [ ] Null hypothesis defined and documented
- [ ] Predictability score run on target series (see `predictability-analysis.md`)

### Phase 2: Development Phase

- [ ] No look-ahead bias in features or signals
- [ ] All features calculated point-in-time
- [ ] Signals shifted 1 bar for next-bar execution
- [ ] Transaction costs included in backtest
- [ ] Slippage and market impact modeled
- [ ] Corporate actions handled correctly

### Phase 3: Validation Phase

- [ ] Out-of-sample testing performed (≥ 20% of data)
- [ ] Statistical significance tested (PSR > 0.95)
- [ ] Multiple testing corrections applied (DSR > 0.95 with correct n_trials)
- [ ] Bootstrap confidence intervals calculated for key metrics
- [ ] Performance validated across regimes (≥ 2 distinct regimes)
- [ ] Crisis stress tests performed (2008–09, 2020, 2022)
- [ ] Overfitting checks passed (OOS degradation < 30%)
- [ ] Parameter stability verified (±20% perturbation)
- [ ] Random data test: strategy fails on shuffled data (confirms signal is real)

### Phase 4: Documentation

- [ ] All assumptions documented
- [ ] All tests and results recorded with reproducible code
- [ ] Limitations clearly stated
- [ ] Failure modes identified and documented
- [ ] Production requirements specified (data, compute, latency)

---

## See Also

- `regime-philosophy.md` — regime framework applied throughout EDA phases
- `predictability-analysis.md` — run before development (Phase 1 checklist)
- `validation-backtesting.md` — PSR, DSR, purged CV implementations (Phase 3 checklist)
- `strategy-improvement.md` — iterative improvement framework after base strategy passes EDA
