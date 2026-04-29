---
rubric_name: trading_strategy_anchor
domain_confidence: high
composite_formula: weighted_arithmetic_mean_with_hard_gates
composite_direction: higher
trip_wire_enabled: true
iso_generated_at: "2026-04-29T11:20:00-04:00"
criteria:
  - name: sharpe_quality
    weight: 0.30
    threshold: 0.7
    hard_gate: false
    definition: "Annualized risk-adjusted return measured by Sharpe ratio on the held-out backtest window."
    what_9_of_10_looks_like: "Sharpe ≥ 1.5 on out-of-sample data with no parameter tuning on the test set; computed on net returns after slippage and commission."
    gameability_note: "Easy to inflate by tuning on the test window itself or by ignoring transaction costs. Counter: enforce strict train/test split (sealed test) and always-include cost model. The /auto researcher loop should never see test-window returns during exploration."
  - name: max_drawdown_control
    weight: 0.25
    threshold: 0.6
    hard_gate: false
    definition: "Worst peak-to-trough equity decline during the backtest as a fraction of peak equity, scored higher when smaller."
    what_9_of_10_looks_like: "Max DD ≤ 12 percent on out-of-sample, with the longest underwater period under 90 trading days."
    gameability_note: "Trivially gamed by trading less or by smoothing the equity curve with averaging. Counter-criterion: turnover_efficiency below; do not pair with it without it."
  - name: turnover_efficiency
    weight: 0.15
    threshold: 0.6
    hard_gate: false
    definition: "Risk-adjusted return per unit of turnover, penalizing strategies that churn the portfolio for marginal alpha."
    what_9_of_10_looks_like: "Net Sharpe (after costs) within 10 percent of gross Sharpe; average holding period above the assumed cost decay horizon for the asset class."
    gameability_note: "Could be gamed by trading once and holding forever (turnover near zero, ratio explodes). Counter: minimum-position-changes hard gate or annual-rebalance requirement when desired."
  - name: statistical_significance
    weight: 0.15
    threshold: 0.65
    hard_gate: false
    definition: "Likelihood that the observed performance is not a fluke, expressed via deflated Sharpe, t-stat, or bootstrap p-value."
    what_9_of_10_looks_like: "Deflated Sharpe ratio (López de Prado) above 0.95 OR bootstrap p-value below 0.01 across 1000 block resamples."
    gameability_note: "Multiple-testing inflation: running 100 backtests and reporting the best yields false significance. Counter: count n_trials and apply the deflation in the metric itself, not as an afterthought."
  - name: regime_robustness
    weight: 0.15
    threshold: 0.6
    hard_gate: false
    definition: "Performance stability across distinct market regimes (bull, bear, high-vol, low-vol)."
    what_9_of_10_looks_like: "Positive net return in at least 3 of 4 documented regime buckets; no single regime contributes more than 60 percent of total PnL."
    gameability_note: "Could be gamed by labeling the entire backtest as one regime. Counter: regimes must be defined a priori (VIX terciles, NBER, or similar) before the run, never carved out post hoc."
  - name: regression_trip_wire
    weight: 0
    threshold: 0
    hard_gate: true
    definition: "Catastrophic-output detector: empty equity curve, NaN/inf returns, runaway runtime, or malformed result schema."
    what_9_of_10_looks_like: "Never fires on valid backtests; always fires on degenerate ones (zero trades, NaN-poisoned PnL, infinite-loop indicator computations, missing required columns)."
    gameability_note: "Not a quality criterion; pure failure detector. Disabling this for /auto researcher loops invites the agent to discover and exploit degenerate-output shortcuts."
    checks:
      - empty_output
      - nan_or_error
      - runtime_exceeded
      - structure_invalid
---

# Trading Strategy Anchor Rubric

> Reference rubric for systematic trading strategy backtest evaluation. Used by `grading-rubric` as a high-confidence anchor when the user's task involves alpha generation, signal optimization, or systematic-strategy development. **Do not use this rubric verbatim for a real loop — adapt criteria, weights, and thresholds to the specific strategy.**

## When to use this anchor

Match against this anchor when the user's task description contains signals like:
- Backtesting a strategy on equities, futures, FX, or crypto
- Optimizing entry/exit signals, holding periods, or position sizing
- Evaluating risk-adjusted returns (Sharpe, Sortino, Calmar)
- Comparing strategies across regimes or asset classes

## Adversarial Reviewer Persona

A portfolio manager who has 30 minutes before allocating real capital. They read the backtest report critically, mentally subtracting overfitting and frictions, and ask: "Will this survive contact with a live market?" They distrust gross Sharpe, in-sample t-stats, and "robust across all regimes" claims. Used only when scorer is in `llm_judge` mode (otherwise ignored).

## Anti-pattern Warnings

- **Goodhart on Sharpe.** Optimizing for Sharpe alone reliably produces strategies that ignore drawdown and tail risk. The `max_drawdown_control` and `regime_robustness` criteria above exist to keep Sharpe honest.
- **Cost-naive scoring.** A backtest without transaction costs and slippage is fiction. The `sharpe_quality` definition above explicitly requires net returns; do not relax this.
- **Turnover-drawdown trade-off blindness.** A strategy that trades once and holds forever has perfect turnover_efficiency and great drawdown control — and zero alpha. Pair the two carefully; consider a minimum-trades hard gate.
- **Multiple-testing inflation.** /auto researcher will run dozens of variants. The `statistical_significance` criterion must use deflated Sharpe (or equivalent multiple-test correction), not raw t-stats.

## Scorer Implementation Notes

- **Mode:** `deterministic` is preferred — Sharpe, drawdown, turnover, and statistical significance are all computable from the equity curve and trade log. Use `llm_judge` mode only if you also want narrative-quality scoring of the strategy description.
- **Inputs the scorer expects:** an equity curve (timestamp + equity columns) and a trade log (timestamp + size + side + price). Both as CSV or Parquet under the user's `outputs_dir`.
- **Trip-wire `runtime_exceeded`** baseline: capture from the first successful backtest; subsequent runs are flagged if they exceed 10× that baseline (often a sign of an inadvertent infinite loop in indicator code).
- **`statistical_significance` requires `n_trials`** as a sidecar value (number of distinct hypothesis tests run during exploration); the scorer reads this from a `n_trials.txt` file the user maintains, defaulting to 1 if absent (which intentionally over-credits significance — surface this in the warning at delivery).
