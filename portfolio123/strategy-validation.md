# Screen Backtest vs Portfolio Simulation

When two Portfolio123 outputs disagree, assume **different economic assumptions** until proven otherwise. Use this doc before arguing that a strategy “broke” or “improved.”

## Screen backtest (rule + rank path)

- Typically applies **slippage/commission** most clearly on **reconstitution**—entering or **fully exiting** positions.
- **Equal-weight** or **weight maintenance** of **existing** holdings may be treated more generously than full round-trips (platform-specific; confirm in your run settings).
- Good for: **ranking quality**, **pass rate**, **relative** comparison of screens under shared assumptions.

## Portfolio simulation (strategy path)

- Paths **cash flows and positions** over time; may include **rebalancing** behavior closer to live trading.
- Often exposes **annual turnover**, average hold, and **transaction** detail—use for **capacity** and **friction** sanity checks.
- Practitioner reports: simulation can show **higher** or **different** performance than screen when **free** or **cheap** internal rebalancing is modeled differently.

## Rules of thumb for agents

1. **Never** compare **screen CAGR** to **simulation CAGR** without reading **slippage**, **rebalance**, and **transaction** settings side by side.
2. **Turnover** from simulation is a **sanity** statistic—extreme turnover + high slippage assumptions = stress-test execution, not “alpha.”
3. If the user’s vault has practitioner notes, cross-check: `file dump/Portfolio123/Portfolio123 Resources.md` (e.g. Layers of Return, turnover posts).

## ETF TAA — Tier 3 vs Tier 2

For **ETF rotation / TAA**, `screen_backtest` (Tier 3) evaluates the **screen / buy-side** path on a schedule. A **native Simulated Strategy** (Tier 2) models **portfolio positions**, rebalance rules, and execution together. Those surfaces can **diverge materially** for the same ranking and universe—**do not** map Tier 3 CAGR or turnover to Tier 2 with a fixed fudge factor.

**Rule:** Use Tier 2 for authoritative ETF TAA performance reporting. Use Tier 3 only for **relative** screening (ranking candidates under shared Tier 3 settings).

## ETF TAA Performance Benchmarks (2006-2026)

For ETF-only TAA strategies over 2006–2026 (covering 2008 GFC and 2020 COVID):

| Metric | Realistic range | Notes |
|--------|----------------|-------|
| CAGR | 8-12% | Best momentum rotation |
| Max Drawdown | -40% to -55% | Equity ETF exposure in 2008 |
| Calmar Ratio | 0.15-0.30 | Structurally constrained |
| Sharpe | 0.5-0.8 | Net of realistic costs |

**Structural infeasibility alert:** Targets of CAGR >15% AND Calmar >1 simultaneously are **not achievable** for ETF-only TAA over 2006-2026. Achieving Calmar >1 at 15% CAGR requires MaxDD < 15%, which is approximately what a US Treasury-only portfolio achieves — incompatible with 15%+ equity-driven CAGR. If both targets are hard requirements: restrict to post-2010 period, allow individual stocks, or relax targets (e.g., 12% CAGR + Calmar >0.5).

## Sector Attribution Diagnostic

When a strategy has unexpectedly weak sectors or you want to validate whether sector weights are driving returns, use this 4-step workflow.

**Step 1 — Run simulation with save transactions enabled**
Run or re-run the Simulated Strategy with the "save transactions" option on.

**Step 2 — Navigate to sector realized P&L**
`Transactions → Realized → Aggregate → By Sector`

**Step 3 — Flag problem sectors**
Look for sectors where:
- Average realized return per trade is **below 20%** (weak picks relative to the strategy average), AND
- Trade count is **high** (the sector is churning without adding value)

Example pattern to flag: Financials with sub-10% average realized return but high trade count = churn trap.

**Step 4 — Cross-check with isolated sector universe test**
For each flagged sector, build an isolated test:
- Universe: restrict to **one sector only**
- Positions: **10 stocks** (lower breadth requires wider tolerance)
- Rank tolerance: **50%** (wider to accommodate smaller cross-section)
- Ranking: same system as the main strategy

Compare the isolated Sharpe to the realized-trade attribution. **If they invert** (isolated Sharpe is higher than attributed P&L suggests), the signal comes from **cross-sector rotation**, not single-sector stock picking. Excluding the sector may destroy that rotation benefit.

**Caveat:** Single-path realized attribution can mislead due to regime, timing, and interactions with other sectors. Always cross-check against the isolated universe test before excluding a sector from the universe.

## Related

- [api-reference.md](api-reference.md) — endpoints, `screen_backtest` semantics, credits
- [case-studies.md](case-studies.md) — worked examples where validation discipline matters
