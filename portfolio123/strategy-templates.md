# Portfolio123 Strategy Templates & Pipelines

3 proven configs, buy/sell rule library, pipeline definitions, parameter sweep dimensions.

## Where Rules Live — Design Principle

Every P123 strategy has three layers. Putting logic in the wrong layer causes distorted ranks, hidden costs, or missed signals.

| Layer | What belongs here | What does NOT belong here |
|-------|-------------------|---------------------------|
| **Universe** | Hard filters: illiquidity, penny stocks, exchange access, min liquidity, max size percentile, sector/country exclusions | Relative attractiveness scoring |
| **Ranking** | Relative attractiveness: value, momentum, quality, liquidity composite, ML score | Hard binary filters (use universe instead) |
| **Strategy (sim)** | Execution: position count, rank tolerance, sell rules (`RankPos`, `Rank < x`), force-in-universe, rebalance cadence | Hard universe-level screens |

**Common errors:** sector exclusions in buy rules (distorts ranking cross-section), relative scores in universe rules (wastes cross-sectional information), liquidity minimums in sell rules instead of universe.

> **All performance reporting is governed by the Validation Hierarchy in SKILL.md.** Key rules:
> - Screen backtests (API) are Tier 3 — buy-side-only, not equivalent to a full simulation
> - Local Python models are Tier 4 — implicit look-ahead bias, zero transaction costs
> - Weighted-average CAGR/max drawdown are mathematically incorrect — compute weighted return series first
> - Cross-engine correlation (e.g., screen returns vs. local ETF returns) produces artifacts
> - See SKILL.md Core Rules 8–11 and Validation Hierarchy table for full details

## Template 1: TAA (ETF Momentum Rotation)

| Setting | Value |
|---------|-------|
| Type | ETF |
| Rebalance | Every 4 Weeks |
| Positions | 1 (100%) |
| Universe | Ticker("SPY,EFA,AGG") |
| Ranking | Trend Measurement |
| Buy Rules | Ret1Y%Chg > 0 |
| Sell Rules | (blank) |
| Transaction Cost | 0.005/share |

**Critical:** Ret1Y%Chg > 0 is the absolute momentum filter. TotRet(252) > 0 fails.

## Template 2: Small Cap Alpha (Multi-Factor + Risk Reduction)

| Setting | Value |
|---------|-------|
| Universe | Easy to Trade North America $2min |
| Ranking | Small and Micro Cap Focus Resorted (or copy) |
| Rebalance | Every 4 Weeks |
| Positions | 20 |
| Buy Rules | avgdailytot(20) > 100000, close(0) > 2, mktcap > 50 and mktcap < 500, si%float < 6, fcfttm > 0 and (OperCashFlQ - CapExQ) > 0 |
| Sell Rules | fcfttm < 0 or (OperCashFlQ - CapExQ) < 0, gainpct - benchpct > 20, gainpct - benchpct < -20, LoopSum("Close(CTR)>BBUpper(50,1.75,CTR)",5)>=3 and rank < 99 |

## Template 3: Large Cap AI Factor (S&P 500 ML)

| Setting | Value |
|---------|-------|
| Universe | sp500 |
| Ranking | AI Factor (AIFactorValidation) |
| Rebalance | Every 4 Weeks |
| Positions | 20 |
| Buy Rules | rank > 90, rank > rankprev(1) + 10 |
| Sell Rules | rank > 50 (or RankPos > 50) |
| Transaction Cost | 0.005/share |

**Rank momentum:** rank > rankprev(1) + 10 buys stocks with recent rank improvement.

## Buy/Sell Rule Library

**Buy:** Rank > 85, Close(0) > 1.2, AvgDailyTot(20) > 300000, NetFCfTtm > 0, mktcap > 50
**Sell:** Close(0) < 1, gainpct - benchpct < -20, gainpct - benchpct > 20, RankPos > 50, fcfttm < 0

## Parameter Sweep Dimensions (optimize-ranking)

- Factor weights: 5% increments
- Rebalance frequency: Every Day, Every Week, Every 4 Weeks
- Position count: 5, 10, 15, 20, 25, 30
- Sell rank threshold: 30, 50, 80
- Buy rank threshold: 80, 85, 90, 95

**Default cap:** 20 combinations per batch. Override requires explicit user confirmation.

### Rank Tolerance Guidance

Rank tolerance is the band around a holding's rank percentile within which it is **not replaced** on a rebalance check — it reduces churn and slippage from borderline rotations.

| Ranking style | Suggested tolerance |
|---------------|---------------------|
| Slow value (quarterly factor updates) | Narrow: 1–5% |
| Fast momentum / growth (weekly price signals) | Wider: 10–20% |

**Rule:** Always tune rebalance frequency and rank tolerance **together** on the same ranking system — they interact. A practitioner default is **weekly rebalance check + 5% rank tolerance**, which targets ~180% annual turnover and ~6-month average hold for a 30-stock multifactor strategy.

### Position Count (N) Heuristics

- For **N > 10** with a stable, consistent ranking system: expect a **negative** relationship between N and risk-adjusted return — more names dilute the signal edge.
- Below **N ≈ 10**: idiosyncratic noise from individual positions begins to dominate, increasing volatility unpredictably.
- A practical live target for concentrated multifactor: **~30 long positions**.

### Size Filter Heuristic

In value/momentum multifactor strategies, excluding the **top ~25% of stocks by market cap** (roughly >$1.3B in mid-2020s terms) has been shown to improve risk-adjusted returns. Use **percentile-based** size screens rather than fixed dollar thresholds — they remain stable across decades as market caps inflate.

## Strategy Stack — Build Order

Objects must be created in dependency order. Skipping levels or reusing the wrong surface produces misleading results.

```text
Universe (base)
    → Ranking System (classic multifactor)
        → Screen backtests   [Tier 3 — fast iteration on N, frequency, tolerance, slippage]
        → Simulated Strategy [Tier 2 — turnover, path realism, force-in-universe, sell rules]
    → AI Factor(s) (train per region optional)
        → Ranking System (add AIFactorValidation nodes; blend weights with classic)
            → Simulated Strategy (again, with blended rank)
                → Strategy Book [Tier 1 — multi-strategy allocation, correlations]
                    → Optional: separate short Simulated Strategies + L/S Book
```

**Snapshot checklist (record for every Screen and Sim run):**
- Universe name + rule text (or ID)
- Ranking system full structure (XML export or screenshot)
- Start/end dates, rebalance frequency, rank tolerance, slippage %, positions, benchmark
- CAGR, Sharpe, max DD; for sims also annual turnover and average hold

## Pipeline 1: create-and-backtest

1. Create/select universe
2. Create ranking system (API or browser)
3. Run screen_backtest — **Results are Tier 3 (ESTIMATED). Append disclaimer when presenting to user.**
4. Export results to ./p123-output/

**Preflight:** Show steps + estimated credits. Confirm before execute.

## Pipeline 2: optimize-ranking

1. Base ranking system + universe
2. Sweep parameter dimensions (weights, rebalFreq, positions, thresholds)
3. Run backtests (max 20 per batch)
4. Compare results, extract best config
5. Log Strategy DNA fingerprint

**Preflight:** Show sweep config + credit estimate. Confirm.

## Pipeline 3: full-strategy-build

1. Universe → Ranking system
2. Strategy creation via browser (Strategy Wizard)
3. Run simulation — **Results are Tier 2 (Silver)**
4. Evaluate results
5. Export + DNA fingerprint

**Preflight:** Show full plan. Confirm. If browser fails 3x, output manual instructions; pause until user types "done".

## Pipeline 4: Strategy Book Build & Validate

1. Identify candidate strategies (API screen_backtest for rapid screening — Tier 3)
2. Create each component as a native P123 Simulated Strategy (browser wizard — Tier 2)
3. Verify each component's native simulation results individually
4. Create Strategy Book via browser (RESEARCH → Books → New → Simulated)
5. Add component strategies as Assets, set allocation weights
6. **Book rebalance cadence:** Use **annual** rebalance at the book level. More frequent book-level rebalancing does not improve performance in practitioner tests and adds costs. Component sims run at their own cadence (e.g., weekly).
7. Run native Book simulation (Tier 1 — Gold)
8. Compare native results to any prior API/local estimates
9. ONLY declare targets met based on Tier 1 native Book results
10. Export + DNA fingerprint

**Preflight:** Show full plan. Confirm. If browser fails 3x, output manual instructions; pause until user types "done".

## Pipeline 5: Long/Short Book

**Prerequisites:** Pipeline 4 (long Strategy Book) already validated at Tier 1. Short-side ranking system built (Template 7 in ranking-templates.md).

1. Define short universe in a separate P123 Universe: largest ~1500 stocks by market cap (~$7B+ cap), targeting borrow availability and low borrow cost (typically <0.5% on IBKR for most names)
2. Build short Simulated Strategy using short-side ranking system; add extra liquidity screen in buy rules (e.g., `AvgDailyTot(20) > 100000`) to avoid artifacts
3. Set short costs: **1% carry cost** + variable slippage
4. Tune sell rule (`RankPos` threshold) to land near ~600% annual turnover for comparability across variants
5. Evaluate standalone short strategy — expect negative expected return; value is in negative correlation to long book
6. Compare short sleeve to ETF hedge baseline (e.g., IWM short) — ETF short is simpler and often competitive on Sharpe
7. Create Long/Short Strategy Book: **75% long** (split evenly across regional long strategies, e.g., 25% each US/ExUS/Global) + **25% short**
8. Run native Book simulation (Tier 1 — Gold); evaluate net Sharpe vs long-only book
9. **Evaluate timing overlays at the book level, not standalone** — crash filters that improve standalone short CAGR can desync long/short beta and hurt net Sharpe

**Costs note:** Short book costs include borrow (carry), slippage, and potential short squeeze/gap risk. Watch gross leverage and margin requirements on the long book if leverage is applied.

**Preflight:** Show full plan. Confirm. If browser fails 3x, output manual instructions; pause until user types "done".

## Graceful Degradation Format

When browser fails after 3 attempts:
1. Exact URL
2. Field-by-field values
3. Buttons to click in order
4. Expected confirmation text

Pipeline pauses until user types `done`.

---

## Extended exemplars & validation

- **[case-studies.md](case-studies.md)** — TAA pitfalls (`Ret1Y%Chg` vs `TotRet`), Core Combo pointer, vault index table.
- **[strategy-validation.md](strategy-validation.md)** — when **screen** and **simulation** disagree.
- **[api-reference.md](api-reference.md#ui-vs-platform-rebalancing)** — **UI vs API** rebalance semantics before comparing turnover or CAGR across environments.
