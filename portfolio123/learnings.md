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
| strategy_insight | strategy-templates.md |
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
