# Portfolio123 Strategy Templates & Pipelines

3 proven configs, buy/sell rule library, pipeline definitions, parameter sweep dimensions.

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

## Pipeline 1: create-and-backtest

1. Create/select universe
2. Create ranking system (API or browser)
3. Run screen_backtest
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
3. Run simulation
4. Evaluate results
5. Export + DNA fingerprint

**Preflight:** Show full plan. Confirm. If browser fails 3x, output manual instructions; pause until user types "done".

## Graceful Degradation Format

When browser fails after 3 attempts:
1. Exact URL
2. Field-by-field values
3. Buttons to click in order
4. Expected confirmation text

Pipeline pauses until user types `done`.
