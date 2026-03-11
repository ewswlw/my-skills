# Query Results

## Momentum Factor Decay (Academic Research v3)

**Within the formation window**, the covariance between past returns and future returns decays steadily across the 11-month lookback window — more recent returns predict stronger than those from ~12 months back. The standard remedy is the 12-month lookback skipping the most recent month (to dodge short-term reversal).

**Post-formation alpha half-life** isn't given as a single clean number, but the research points to:
- Approximately **50% of mispricing corrected within the first year** (broader mispricing research)
- Return spreads for momentum anomalies have roughly **halved** post-decimalization as arbitrage activity increased
- **Residual/idiosyncratic momentum** (orthogonalized to risk factors) degrades much more slowly and avoids the long-term reversal problem that hits standard cross-sectional momentum

**Key decay accelerants:** momentum crashes during bear-to-bull regime transitions (can lose 60%+ in those episodes), low funding liquidity, and high investor sentiment environments.

---

## Transaction Cost Models (algo trading)

The sources break it into explicit (commissions, taxes) vs. implicit (spread, slippage, market impact) costs. Key modeling approaches:

- **Basis-point sensitivity analysis** — test strategy P&L at 0, 5, 10, 20 bps to find the break-even threshold
- **Market impact scaling** — retail ≈ 0 bps on liquid names; institutional ($1B+) can face ~1% impact per trade
- **RL-based execution** — modern systems use reinforcement learning on the limit order book to optimally slice large orders
- **Penalty parameters (lambda/kappa)** in portfolio optimization — forces the model to demand higher conviction before rebalancing
- **Capacity filters** — cap position size at ~5% of median daily volume; exclude illiquid names

The notebook also flags a notable warning: current LLM-based trading frameworks tend to **ignore transaction costs entirely**, making their backtested results unrealistic.

*Note: Agent called notebook_list first to find notebooks before querying (no hardcoded IDs available).*
