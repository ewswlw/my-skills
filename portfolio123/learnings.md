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
