---
name: portfolio123
description: >
  Portfolio123 (P123) full-surface skill: automation, formula language, and data reference.
  Trigger on: Portfolio123, P123, p123api, DataMiner, ranking systems, screens, backtests,
  strategies, AI factors, universes. Also trigger for P123 formula writing (SetVar, FRank, FHist,
  Eval, NodeRank, ZScore, Aggregate, FHistRank, LoopSum), technical analysis in P123 (RSI, MACD,
  SMA, ATR, Bollinger), financial statement factors (Sales, OpInc, FCF, EPS, ROE, EBITDA, MktCap),
  macro/FRED constants (##FEDFUNDS, ##UST10YR, ##CPI, ##UNRATE), universe IDs (SP500, Prussell3000),
  and replicating academic strategies on P123 (BAB, Piotroski, momentum, value, quality, low-vol).
---

# Portfolio123 Agent Skill

Automate every supported Portfolio123 workflow: API data collection, ranking systems, universes, screens, backtests, strategy creation (browser), AI Factor training and evaluation, pipelines, and self-improvement via continual learning.

## Decision Tree — Route to Reference File

### Automation & API Tasks
| Task Type | Keywords | Read |
|-----------|----------|------|
| **Data collection** | prices, factors, universe data, data_prices, data_universe, DataMiner | [api-reference.md](api-reference.md) |
| **Ranking system** | create ranking, update ranking, test rank, rank stocks | [ranking-templates.md](ranking-templates.md) |
| **Universe creation** | create universe, update universe, filter stocks, universe rules | [ranking-templates.md](ranking-templates.md) |
| **Universe ID lookup** | SP500, Prussell3000, ALLSTOCKS, which universe string to use | [references/macros-constants.md](references/macros-constants.md) |
| **Screen / backtest** | run screen, backtest, rolling backtest, parameter sweep | [api-reference.md](api-reference.md) + [strategy-templates.md](strategy-templates.md) |
| **Strategy creation** | create strategy, Stock strategy, ETF strategy, TAA, wizard | [browser-workflows.md](browser-workflows.md) + [strategy-templates.md](strategy-templates.md) |
| **Strategy buy/sell rules** | NoBars, EntryPrice, MaxPosRet%, trailing stop, time exit, rank sell | [references/technical-functions.md](references/technical-functions.md) |
| **AI Factor** | configure, train, validate, evaluate, predictor, LightGBM, ExtraTrees | [ai-factor-guide.md](ai-factor-guide.md) + [browser-workflows.md](browser-workflows.md) |
| **Strategy Book** | book, multi-strategy, combine strategies, portfolio combination, allocation | [strategy-templates.md](strategy-templates.md) (Pipeline 4) + [browser-workflows.md](browser-workflows.md) (Strategy Book Validation) |
| **Quick factor lookup** | ~50 validated factors by category, common pitfalls | [factor-quickref.md](factor-quickref.md) |
| **Complete factor lookup** | full financial statement factor list, pre-built factor naming | [references/fundamental-data.md](references/fundamental-data.md) |
| **Pipeline** | create-and-backtest, optimize-ranking, full-strategy-build, Strategy Book build & validate | [strategy-templates.md](strategy-templates.md) |
| **Learning review** | review discoveries, promote learnings, DNA fingerprint | [learnings.md](learnings.md) |
| **UI vs API rebalance semantics** | UI partial vs API full refresh, momentum mismatch, compare CAGR | [api-reference.md](api-reference.md) — UI vs Platform — Rebalancing Semantics |
| **Screen vs simulation** | conflicting CAGR, turnover sanity, slippage interpretation | [strategy-validation.md](strategy-validation.md) |
| **Named exemplars (TAA, Core Combo, etc.)** | Ret1Y%Chg, vault strategy recipes | [case-studies.md](case-studies.md) |
| **Exhaustive factor name lookup** | factor not in quickref, spelling of pre-built names | [references/fundamental-data.md](references/fundamental-data.md) + vault `Portfolio123 Syntax Dictionary.md` OR `doc_detail.jsp` |

### Formula Language Tasks
| Task Type | Keywords | Read |
|-----------|----------|------|
| **Write any P123 formula** | screen rule, ranking formula, formula syntax, SetVar, Eval, FRank, ZScore, Aggregate, FHist, NodeRank, NA handling, Bound, IsNA | [references/formula-quick-reference.md](references/formula-quick-reference.md) |
| **Academic strategy replication** | Piotroski, BAB, momentum, value, quality, low-vol, factor investing formula | [references/formula-quick-reference.md](references/formula-quick-reference.md) + [references/fundamental-data.md](references/fundamental-data.md) |
| **Financial statement data** | balance sheet, income statement, cash flow, Sales(), OpInc(), FCF(), EPS(), EBITDA, book value, debt, working capital, pre-built factor naming | [references/fundamental-data.md](references/fundamental-data.md) |
| **Technical analysis** | RSI, MACD, SMA, EMA, Bollinger, ATR, ADX, Stochastic, volume, 52-week high, streak, relative strength | [references/technical-functions.md](references/technical-functions.md) |
| **Advanced formula logic** | FHistRank, FHistZScore, LoopSum, Group, AI Factor formula, consensus estimates, dividends, screen-only functions | [references/advanced-functions.md](references/advanced-functions.md) |
| **FHist / historical lookback** | FHist, historical average, historical rank, how did X change over time | [references/formula-quick-reference.md](references/formula-quick-reference.md) — for syntax; [references/advanced-functions.md](references/advanced-functions.md) — for FHistRank/FHistZScore |
| **Macros / constants / universes** | ##FEDFUNDS, ##UST10YR, ##CPI, ##UNRATE, FRED series, #Bench, $SPY, FX rates, #SPEPSTTM, universe ID strings | [references/macros-constants.md](references/macros-constants.md) |
| **AI Factor — extended narrative** | feature philosophy, quantile diagnostics, long methodology | [ai-factor-guide.md](ai-factor-guide.md) + vault `Portfolio123 AI Factor Reference.md` (see guide’s Deep Dive pointer) |

> **Multi-domain formula tasks** (e.g., Piotroski uses balance sheet + cash flow + formula syntax): read `formula-quick-reference.md` first, then the relevant domain file (`fundamental-data.md`, `technical-functions.md`, etc.).

## Core Rules

1. **Naming:** All P123 resources MUST start with `agent` (ranking systems, universes, strategies, screens, AI factors).
2. **API first:** Use p123api for data, rankings, universes, screens, backtests. Use browser only when API cannot do it (strategy creation, AI Factor training).
3. **Preflight:** Before major operations, show summary + estimated credit cost + ask for confirmation.
4. **Output:** Save CSV/JSON to `./p123-output/` with pattern `{operation}_{timestamp}.{csv|json}`.
5. **Credits:** Check quotaRemaining before expensive ops. Warn at 80% and 95% consumption.
6. **GUI vs XML:** Try GUI first for ranking systems; fall back to raw XML editor after 2 failures.
7. **Factor discovery:** Always use `doc_detail.jsp?factor=[NAME]` to validate factor names — never guess.
8. **Screen backtest is Tier 3 only:** `screen_backtest` is buy-side-only — overstates CAGR by 30–40%, Sharpe by 50%+. See `api-reference.md` for details.
9. **No local substitute backtesting:** NEVER use a custom Python backtester as a substitute for P123's native engine. See `strategy-templates.md` Validation Hierarchy blockquote.
10. **Mandatory native validation:** Before reporting ANY performance numbers to the user, validate via native P123 simulation. Present Tier 3/4 results only with explicit disclaimer: "ESTIMATED (Tier 3) — screen backtests typically overstate CAGR by 30–40% and Sharpe by 50%+."
11. **Portfolio math:** NEVER use weighted-average CAGR or max drawdown. Compute weighted return series first. Label all local estimates as "ESTIMATED (Tier 3/4)" in both experiment log AND user-facing messages.

## Validation Hierarchy

| Tier | Source | Reliability | Use For |
|------|--------|-------------|---------|
| 1 (Gold) | Native P123 Strategy Book simulation | Highest | Final validation, declaring targets met |
| 2 (Silver) | Native P123 Simulated Strategy | High | Individual strategy evaluation |
| 3 (Bronze) | API `screen_backtest` | Medium | Rapid screening, candidate ranking |
| 4 (Unreliable) | Local Python backtester | Low | Never use as final validation |

**Rules:**

- Never declare targets met based on Tier 3 or Tier 4 alone. Escalate to Tier 1 before reporting.
- If Tier 1 is unavailable (browser fails), use Tier 2 with explicit disclaimer to user.
- When user explicitly requests Tier 3 results, comply but ALWAYS append: "ESTIMATED (Tier 3) — screen backtests typically overstate CAGR by 30–40% and Sharpe by 50%+."

## Quick Reference Links

### Automation & Platform
- **API:** [api-reference.md](api-reference.md) — all endpoints, auth, credits, retry, pitfalls, code examples
- **Browser:** [browser-workflows.md](browser-workflows.md) — login, strategy wizard, AI Factor config, snapshot-verify
- **Rankings:** [ranking-templates.md](ranking-templates.md) — 5 XML templates, validation checklist
- **Strategies:** [strategy-templates.md](strategy-templates.md) — TAA, Small Cap Alpha, Large Cap AI Factor, pipelines
- **Validation:** [strategy-validation.md](strategy-validation.md) — screen vs simulation; [case-studies.md](case-studies.md) — vault exemplars + TAA pitfalls
- **Factors:** [factor-quickref.md](factor-quickref.md) — ~50 validated factors by category
- **AI Factor:** [ai-factor-guide.md](ai-factor-guide.md) — ML workflow, 16 presets, 4 validation methods
- **Philosophy:** [andreas-reference.md](andreas-reference.md) — robustness-first, Train Wide Filter Smart
- **Learning:** [learnings.md](learnings.md) — discoveries, promotion rules, DNA fingerprinting

### Formula Language Reference
- **Formula Quick Ref:** [references/formula-quick-reference.md](references/formula-quick-reference.md) — operators, SetVar, Eval, FRank, ZScore, Aggregate, FHist, NA handling, common patterns
- **Fundamental Data:** [references/fundamental-data.md](references/fundamental-data.md) — all balance sheet / income / cash flow functions + pre-built factor naming system
- **Technical Functions:** [references/technical-functions.md](references/technical-functions.md) — moving averages, RSI, MACD, Bollinger, ATR, ADX, streaks, strategy-only functions
- **Advanced Functions:** [references/advanced-functions.md](references/advanced-functions.md) — FHistRank, FHistZScore, LoopSum, Group, AI Factor functions, consensus estimates, dividends
- **Macros & Constants:** [references/macros-constants.md](references/macros-constants.md) — FRED series (##FEDFUNDS, ##CPI, etc.), universe IDs, price IDs, FX rates, S&P 500 aggregates

## Learning Hooks — What to Watch After Each Operation

| Operation | Watch For | Log To |
|-----------|-----------|--------|
| API call | quotaRemaining, response keys (snake_case?), actual credit cost | learnings.md → api-reference.md |
| Factor in ranking | Did it work? Exact P123 name used, any name correction needed | learnings.md → factor-quickref.md |
| Browser action | Selector that worked, text content used, any changed UI element | learnings.md → browser-workflows.md |
| Backtest result | annualized_return, sharpe_ratio, max_drawdown, ranking config | learnings.md → Strategy DNA fingerprint |
| XML save | Any validation error, fix applied | learnings.md → ranking-templates.md |
| P123 formula used | Did the formula evaluate without error? Exact syntax that worked, any NA surprises | learnings.md → references/formula-quick-reference.md |
| Financial statement factor | Exact pre-built factor name confirmed (e.g., `SalesGr%TTM` not `SalesGrowthTTM`) | learnings.md → references/fundamental-data.md |
| Technical function | Parameter order confirmed (e.g., `ATR(bars, offset, series)`), any gotchas | learnings.md → references/technical-functions.md |
| Macro constant | Was the FRED series current? Any stale data lag observed | learnings.md → references/macros-constants.md |
| Academic strategy replication | Which formula pattern worked, what the P123 equivalent of the paper's metric is | learnings.md → references/formula-quick-reference.md |
| Screen vs simulation conflict | Different CAGR/slippage/turnover between modes | learnings.md → strategy-validation.md |
| UI vs API turnover mismatch | UI shows lower turnover than API for “same” strategy | learnings.md → api-reference.md § UI vs Platform |

## Graceful Degradation

### Browser Automation Failure (after 3 attempts)
Output a manual instruction block:
1. Exact URL to navigate to
2. Field-by-field values to enter
3. Buttons to click in order
4. Expected confirmation text

Then pause: tell the user to complete the steps and type `done` to resume the pipeline.

### API `data_universe` → "data license required" error
Fall back to `client.data()` with explicit tickers instead. Inform the user that `data_universe()` requires a FactSet/Compustat data license and offer the ticker-based alternative.

### `doc_detail.jsp` unreachable for factor validation
Fall back to: (1) search `references/fundamental-data.md` for the function name, (2) search `factor-quickref.md`, (3) use the pre-built factor naming pattern from `references/fundamental-data.md` to derive the name. Warn the user the name is unconfirmed and may need manual validation.

### Ranking XML validation error on save
Apply the fix documented in `ranking-templates.md` validation checklist. If the same error persists after 2 attempts, output the corrected XML for the user to paste manually via the XML editor (Settings → Raw XML).

## Terminology

- **Ranking system** (not "ranker") — Multi-factor composite that scores stocks 0-100
- **Universe** (not "watchlist") — Stock/ETF selection pool
- **Factor** (not "variable") — Financial metric or formula used in ranking
- **Screen** — Rule-based filter, backtestable
- **Strategy** — Portfolio construction with rebalance rules
- **Strategy Book** — Multi-strategy portfolio with allocation weights

## Constitution

See [project-constitution.md](project-constitution.md) for hard boundaries (no live rebalances, no credentials in files, agent prefix, etc.).
