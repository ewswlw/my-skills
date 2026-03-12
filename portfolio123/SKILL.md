---
name: portfolio123
description: Full-surface automation for Portfolio123 quantitative investing platform. API integration (p123api), browser automation for strategy creation and AI Factor training, ranking systems, universes, screens, backtests, factor discovery, and continual learning. Use when working with Portfolio123, P123, ranking systems, backtests, AI factors, screens, universes, or quantitative strategy development.
---

# Portfolio123 Agent Skill

Automate every supported Portfolio123 workflow: API data collection, ranking systems, universes, screens, backtests, strategy creation (browser), AI Factor training and evaluation, pipelines, and self-improvement via continual learning.

## Decision Tree — Route to Reference File

| Task Type | Keywords | Read |
|-----------|----------|------|
| **Data collection** | prices, factors, universe data, data_prices, data_universe | [api-reference.md](api-reference.md) |
| **Ranking system** | create ranking, update ranking, test rank, rank stocks | [ranking-templates.md](ranking-templates.md) |
| **Universe** | create universe, update universe, filter stocks, Ticker | [ranking-templates.md](ranking-templates.md) |
| **Screen / backtest** | run screen, backtest, rolling backtest, parameter sweep | [api-reference.md](api-reference.md) + [strategy-templates.md](strategy-templates.md) |
| **Strategy creation** | create strategy, Stock strategy, ETF strategy, TAA, wizard | [browser-workflows.md](browser-workflows.md) + [strategy-templates.md](strategy-templates.md) |
| **AI Factor** | configure, train, validate, evaluate, predictor, LightGBM, ExtraTrees | [ai-factor-guide.md](ai-factor-guide.md) + [browser-workflows.md](browser-workflows.md) |
| **Factor lookup** | find factor name, P123 syntax, doc_detail | [factor-quickref.md](factor-quickref.md) |
| **Pipeline** | create-and-backtest, optimize-ranking, full-strategy-build | [strategy-templates.md](strategy-templates.md) |
| **Learning review** | review discoveries, promote learnings, DNA fingerprint | [learnings.md](learnings.md) |

## Core Rules

1. **Naming:** All P123 resources MUST start with `agent` (ranking systems, universes, strategies, screens, AI factors).
2. **API first:** Use p123api for data, rankings, universes, screens, backtests. Use browser only when API cannot do it (strategy creation, AI Factor training).
3. **Preflight:** Before major operations, show summary + estimated credit cost + ask for confirmation.
4. **Output:** Save CSV/JSON to `./p123-output/` with pattern `{operation}_{timestamp}.{csv|json}`.
5. **Credits:** Check quotaRemaining before expensive ops. Warn at 80% and 95% consumption.
6. **GUI vs XML:** Try GUI first for ranking systems; fall back to raw XML editor after 2 failures.
7. **Factor discovery:** Always use `doc_detail.jsp?factor=[NAME]` to validate factor names — never guess.

## Quick Reference Links

- **API:** [api-reference.md](api-reference.md) — endpoints, auth, credits, retry, code examples
- **Browser:** [browser-workflows.md](browser-workflows.md) — login, strategy wizard, AI Factor config, snapshot-verify
- **Rankings:** [ranking-templates.md](ranking-templates.md) — 5 XML templates, validation checklist
- **Strategies:** [strategy-templates.md](strategy-templates.md) — TAA, Small Cap Alpha, Large Cap AI Factor, pipelines
- **Factors:** [factor-quickref.md](factor-quickref.md) — ~50 validated factors by category
- **AI Factor:** [ai-factor-guide.md](ai-factor-guide.md) — ML workflow, 16 presets, 4 validation methods
- **Philosophy:** [andreas-reference.md](andreas-reference.md) — robustness-first, Train Wide Filter Smart
- **Learning:** [learnings.md](learnings.md) — discoveries, promotion rules, DNA fingerprinting

## Learning Hooks — What to Watch After Each Operation

| Operation | Watch For | Log To |
|-----------|-----------|--------|
| API call | quotaRemaining, response keys (snake_case?), credit cost | learnings.md → api-reference.md |
| Factor in ranking | Did it work? Exact P123 name used | learnings.md → factor-quickref.md |
| Browser action | Selector that worked, text content used | learnings.md → browser-workflows.md |
| Backtest result | annualized_return, sharpe_ratio, max_drawdown, ranking config | learnings.md → Strategy DNA fingerprint |
| XML save | Any validation error, fix applied | learnings.md → ranking-templates.md |

## Graceful Degradation

When browser automation fails after 3 attempts, output:
1. Exact URL to navigate to
2. Field-by-field values to enter
3. Buttons to click in order
4. Expected confirmation text

Pipeline pauses until user types `done`.

## Terminology

- **Ranking system** (not "ranker") — Multi-factor composite that scores stocks 0-100
- **Universe** (not "watchlist") — Stock/ETF selection pool
- **Factor** (not "variable") — Financial metric or formula used in ranking
- **Screen** — Rule-based filter, backtestable
- **Strategy** — Portfolio construction with rebalance rules

## Constitution

See [project-constitution.md](project-constitution.md) for hard boundaries (no live rebalances, no credentials in files, agent prefix, etc.).
