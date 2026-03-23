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

## Related

- [api-reference.md](api-reference.md) — [UI vs Platform — Rebalancing Semantics](api-reference.md#ui-vs-platform-rebalancing)
- [case-studies.md](case-studies.md) — worked examples where validation discipline matters
