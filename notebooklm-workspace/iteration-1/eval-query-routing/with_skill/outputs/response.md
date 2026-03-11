# Query Results

## Academic Research v3 — Momentum Factor Decay

Your research shows decay operating at two levels:

**Within the formation window:** Predictive power peaks at the most recent months of the 12-month lookback and weakens steadily toward t-12. The standard t-1 skip is a direct response to short-term reversal (negative autocorrelation from microstructure frictions). Even during holding, roughly 28% of gross momentum profit is eroded by reversal effects on non-momentum weekdays.

**Post-publication / secular decay:** Momentum is a clear victim of its own fame. Post-decimalization, anomaly returns including momentum have approximately halved. Outside microcaps, hedge returns have been statistically zero since ~2003 — consistent with the McLean & Pontiff finding that documented anomalies fade as capital arbitrages them away.

**What still has legs:** Idiosyncratic/residual momentum (iMOM) shows *no long-term reversals* and delivers roughly 2x the risk-adjusted returns of standard momentum — probably because residual returns are harder to arbitrage. Intermediate momentum (t-12 to t-7 window) also outperforms in some samples, especially in large/liquid stocks. Long-horizon predictability (5-year cumulative alpha) has decayed less than monthly return predictability.

**Sources referenced**
- Academic Research v3: Multiple sources on momentum anomaly persistence, McLean & Pontiff replication studies, residual momentum papers

---

## algo trading — Transaction Cost Models

Your notebook covers this through the lens of strategy viability and capacity:

- **Flat bps stress-testing:** A news-based equity strategy was tested at 0/5/10/20 bps — strategy broke even around 10 bps and consistently lost money at 20 bps despite accurate directional predictions.
- **IRL reward function modeling:** The most sophisticated approach documented — Inverse Reinforcement Learning embeds transaction costs as explicit reward parameters, allowing researchers to reverse-engineer how much a manager implicitly prioritizes cost minimization.
- **Capacity estimation:** Cost modeling used to bound strategy capacity (one volatility system: $140M–$450M depending on implementation).
- **LLM agent critique:** Your sources specifically call out that modern AI trading agents typically ignore transaction costs and assume perfect liquidity — a material realism gap.
- **Factor complexity trade-off:** Scaled PCA to compress the factor zoo to 8–15 signals is recommended partly on cost grounds — fewer factors = less turnover.

**Sources referenced**
- algo trading: News-based strategy studies, RL execution papers, capacity estimation frameworks

---

**Follow-up suggestions**
- Ask Academic Research v3: "What does the research say about momentum after controlling for quality factors (QMJ)?"
- Ask algo trading: "What does my notebook say about optimal rebalancing frequency to minimize transaction costs?"
- Consider creating an audio overview from Academic Research v3 to get a synthesized podcast on factor decay research
