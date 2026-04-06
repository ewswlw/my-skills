# Portfolio123 Skill — Continual Learning Journal

Structured discoveries from execution. Append-only. Promote to reference files after 3+ confirmations (or 1 high-confidence).

## Schema (per entry)

```
---
id: LEARN-YYYYMMDD-NNN
type: factor|browser_selector|api_behavior|xml_quirk|strategy_insight|credit_cost|hyperparameter
confidence: high|medium|low
confirmations: 0
promoted: false
---
**Context:** [What operation was running]
**Discovery:** [What worked or failed]
**Action:** [Add to factor-quickref | Update browser-workflows | etc.]
```

## Promotion Rules

- **3+ confirmations** → Auto-promote to target reference file (additive only)
- **1 high-confidence** (e.g., validated factor name) → Promote immediately
- **Contradiction** (new learning conflicts existing) → Flag for user review, do not auto-update

## Auto-Update Targets

| Discovery Type | Target File |
|----------------|-------------|
| factor | factor-quickref.md |
| browser_selector | browser-workflows.md |
| api_behavior, credit_cost | api-reference.md |
| xml_quirk | ranking-templates.md |
| strategy_insight | strategy-templates.md, case-studies.md, strategy-validation.md |
| hyperparameter | ai-factor-guide.md |

## Strategy DNA Fingerprinting Schema

Extract from every backtest, append to this file:

```
---
dna_id: DNA-YYYYMMDD-NNN
ranking_config: [factor names, weights, rank directions]
universe: [name or ID]
rebal_freq: Every 4 Weeks
positions: 20
sharpe: X.XX
annualized_return: X.X%
max_drawdown: -X.X%
regime_notes: [if split analysis available]
---
```

Use for personalized recommendations after 5+ fingerprints.

## Discoveries (append below)

<!-- New entries go here. Do not delete. -->

---
id: LEARN-20260317-001
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33 — "Why Your High IQ Won't Help You in Markets"
---
**Context:** AI Factor hyperparameter robustness testing
**Discovery:** ALL hyperparameter presets must produce positive lift — not just the top 3 or majority. If a signal only works under one configuration, it is fragile by definition. Real signals survive hyperparameter variance.
**Action:** Promoted to ai-factor-guide.md (All-Must-Perform Rule section)

---
id: LEARN-20260317-002
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33
---
**Context:** AI Factor outlier / preprocessing configuration
**Discovery:** Default outlier cap should be **5 sigma** (not the common 2.5 sigma). Test up to 10 sigma. Clipping at 2.5 sigma collapses signal gradient — model loses ability to distinguish "strong" from "extreme." Fat tails carry real signal.
**Action:** Promoted to ai-factor-guide.md (Preprocessing section) and andreas-reference.md (Outlier Limit Philosophy)

---
id: LEARN-20260317-003
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33
---
**Context:** Full AI Factor deployment lifecycle
**Discovery:** The workflow has 6 phases, not 3: Probe (train once 2003–2020.06) → Sense (15+ preset robustness test) → Respond (retrain exact same setup) → Verify (5-year pseudo-OOS) → Deploy (go live) → Confirm (OOS Live tracks OOS Pseudo). Each gate is binary: pass or kill and restart.
**Action:** Promoted to andreas-reference.md (Full 6-Phase Workflow section)

---
id: LEARN-20260317-004
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33
---
**Context:** Live model monitoring / retirement decision
**Discovery:** Model retirement rule — run until OOS Live stops tracking OOS Pseudo. Monthly check: market up → strategy goes up harder; market down → strategy goes down less. No calendar, no committee, no "feeling." The market decides.
**Action:** Promoted to andreas-reference.md (OOS Health Check section)

---
id: LEARN-20260317-005
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: AI-Driven Quant Investment Strategies Substack #34 — "Visualizing the Learning Logic #3: LightGBM (3/4)"
---
**Context:** LightGBM internals and overfitting risk in stock data
**Discovery:** LightGBM uses histogram binning (~255 bins per feature) for fast split search. Overfitting manifests as learning past noise as "laws" — when conditions don't repeat, produces huge directional misses. Key anti-overfitting hyperparameters: lower learning_rate + more trees, min_data_in_leaf (extremely important for stocks), constrain num_leaves/max_depth, apply feature_fraction/bagging_fraction, use time-series validation + early stopping.
**Action:** Promoted to ai-factor-guide.md (LightGBM Learning Logic, Overfitting Risk, Anti-Overfitting Hyperparameters sections)

---
id: LEARN-20260317-006
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: AI-Driven Quant Investment Strategies Substack #34
---
**Context:** Choosing between ExtraTrees and LightGBM
**Discovery:** Default to ExtraTrees for baseline/conservative use (stable, easy to explain). Upgrade to LightGBM only when features have genuine predictive power AND regularization is applied. For stock-ranking strategies (score 500 stocks, buy top N), evaluate by hit rate in top X% — not just regression error — to better expose overfitting risk.
**Action:** Promoted to ai-factor-guide.md (ExtraTrees vs. LightGBM Decision Guideline)

---
id: LEARN-20260323-001
type: api_behavior
confidence: high
confirmations: 1
promoted: true
source: Skill sync — Portfolio123 API Guide + vault Notes
---
**Context:** Comparing UI simulation to API backtest / live workflow
**Discovery:** **UI rebalancing** behaves as **partial / if-needed** (lower turnover, positions persist). **API**-driven and many scripted flows imply **full refresh** to model ranks unless coded otherwise—**higher turnover**. Momentum strategies are especially sensitive; numbers are not interchangeable without checking semantics.
**Action:** Promoted to api-reference.md (UI vs Platform — Rebalancing Semantics)

---
id: LEARN-20260323-002
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Skill sync — Systvest / vault Resources synthesis
---
**Context:** Screen backtest vs portfolio simulation disagreement
**Discovery:** Differences often come from **where slippage applies** (reconstitution vs ongoing weight maintenance) and **rebalance economics**, not necessarily a “bug.” Use simulation **turnover** as a sanity check on costs.
**Action:** Promoted to strategy-validation.md

---
id: LEARN-20260323-003
type: factor
confidence: high
confirmations: 1
promoted: true
source: Vault Portfolio123 Notes — formula trials
---
**Context:** Ranking / screen formulas
**Discovery:** Names such as `Prc2FCFY`, `#PE`, `Prc2Earn`, `ROE`, `ROA` **failed** in some ranking contexts; verified alternatives include `EPSExclXorGr%TTM`, `SalesGr%TTM`, `Momentum(20)`, `Ret1Y%Chg`. Always validate with **doc_detail.jsp**—do not assume doc labels equal evaluable names.
**Action:** Cross-ref api-reference.md Common Pitfalls; factor-quickref

---
id: LEARN-20260323-004
type: browser_selector
confidence: medium
confirmations: 1
promoted: true
source: Vault Portfolio123 Notes
---
**Context:** Strategy wizard long backtest
**Discovery:** UI may reset backtest window to a short default on Run Simulation; API bypasses.
**Action:** Promoted to browser-workflows.md (Known platform quirks)

---
id: LEARN-20260405-001
type: api_behavior
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Strategy Book optimization loop using screen_backtest API + local Python ETF model
**Discovery:** `screen_backtest` is a BUY-SIDE-ONLY backtest. It does NOT include sell rules, position-level execution, cash drag, or realistic slippage. It overstated CAGR by 40% (32.79% vs 23.43%) and Sharpe by 52% (1.37 vs 0.90) compared to the same strategy run as a native P123 Simulated Strategy. Max drawdown was understated by 25pp (-40% vs -65%). NEVER treat screen_backtest results as equivalent to a full strategy simulation.
**Action:** Added critical warning to api-reference.md. Added Validation Hierarchy to SKILL.md. Added Core Rules 8-11.

---
id: LEARN-20260405-002
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** ETF momentum sleeve computed locally in Python vs P123 native ETF simulation
**Discovery:** A custom Python momentum rotation model (12-month momentum + SMA market timing) produced ~23% CAGR on SPY/TLT/GLD. The same 3-ETF universe with P123's best native ranking system (ETF Rotation - Basic) produced only 10.82% CAGR. The local model has implicit look-ahead bias (month-end resampling), zero transaction costs on rotation, and perfect execution timing. NEVER use a local Python backtester as a substitute for P123's native simulation engine.
**Action:** Added guardrail to SKILL.md Core Rule 9. Added warning to strategy-templates.md.

---
id: LEARN-20260405-003
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Portfolio combination math in evaluate.py
**Discovery:** Weighted-average CAGR (`sum(w * cagr)`) overestimates the true portfolio CAGR. Weighted-average max drawdown is meaningless (drawdowns can coincide or offset). Sharpe computed from estimated portfolio vol using average pairwise correlation is unreliable. Correct approach: compute weighted portfolio return series first, then derive all metrics from the combined series.
**Action:** Added Core Rule 11 to SKILL.md. Added validation blockquote to strategy-templates.md.

---
id: LEARN-20260405-004
type: api_behavior
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** screen_backtest API parameter format
**Discovery:** The `screen_backtest` endpoint accepts EITHER a nested screen object (`{'type':'stock','universe':'nasdaq100'}`) OR an integer screen ID directly. The existing api-reference.md only documented the nested object form. Using a screen ID is more reliable for backtesting existing user screens. Also: `startDt` is clamped to ~2006-01-01 for Standard membership — earlier dates are silently ignored.
**Action:** Added screen ID integer form and membership date limits to api-reference.md.

---
id: LEARN-20260405-005
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Correlation calculation between screen backtest returns and local ETF model returns
**Discovery:** Near-zero pairwise correlation (0.017) between screen backtest cumulative returns and locally-computed ETF returns was an artifact of: (a) different data sources, (b) different rebalancing frequencies embedded in the return streams, (c) temporal misalignment. This inflated the diversification bonus and made the composite metric misleadingly high. Correlation should only be computed between return series from the SAME simulation engine at the SAME frequency.
**Action:** Added warning to strategy-templates.md validation blockquote.

---
id: LEARN-20260405-006
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Full Strategy Book experiment loop (14 experiments)
**Discovery:** The entire experiment loop optimized against a synthetic composite metric combining incompatible data sources. The loop declared victory (CAGR 26.26%, Sharpe 2.00) but the native P123 book showed 18.68% CAGR and 1.05 Sharpe — neither target was met. MANDATORY RULE: Any Strategy Book configuration MUST be validated via native P123 Strategy Book simulation (browser automation) before being declared as meeting targets. API screen backtests and local models are acceptable for rapid iteration/screening only, never for final validation.
**Action:** Added Pipeline 4 to strategy-templates.md. Added Strategy Book Validation Workflow to browser-workflows.md. Added Core Rule 10 to SKILL.md.
