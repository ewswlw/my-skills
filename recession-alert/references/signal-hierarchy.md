# Signal Hierarchy and Position Logic

Summarized from `Guides/RecessAlert_Complete_Encyclopedia.md` (Parts 5 and 7). Use as **economic priors**, not guaranteed rules—always validate OOS.

---

## Six-layer framework (conceptual)

**Data availability:** Layer 2 often cites **CMHI-2** (de-trended CMHI). That series lives on **CMHI_DATA → WEEKLY or MONTHLY**, not on the **DAILY** sheet. The stock `load_cmhi()` path in `spx_timing_strategy.py` loads **DAILY** only—so either extend loaders to include weekly CMHI-2 merged to daily, or use **daily CMHI** alone as a regime proxy and document the substitution.

| Layer | Role | Primary inputs |
|-------|------|----------------|
| 1 — Recession gate | Hard risk-off | RFE-6, LEADING PROB, NBER |
| 2 — Regime gate | Bull vs bear equity risk | CMHI, CMHI-2, monthly CMHI |
| 3 — Daily timing | Entry/exit speed | OPTIMUM TRADE, STM |
| 4 — Breadth confirmation | Conviction / participation | MTLV2, SIGS, DCOM |
| 5 — Probability context | Top/bottom conviction | Gen-2 P(TOP)/P(BOT), MF NET AVG, Trendex TOP/BOT |
| 6 — Valuation context | Strategic allocation tilt | RAVI (levels—not forward columns) |

Not every strategy uses all layers; **non-SPX** projects may map layers to other assets (e.g. credit spreads, vol) using the same recession/regime signals as filters.

---

## Ranked recession risk (historical framing)

| Rank | Signal | Source | Threshold idea |
|------|--------|--------|----------------|
| 1 | RFE-6 | MonthlyData RFE VARIANTS | =1 → ensemble recession warning |
| 2 | RFE-5 | Same | Slightly earlier, more noise |
| 3 | CMHI-2 < 0 | CMHI WEEKLY/MONTHLY | Bear regime |
| 4 | LEADING PROB | Monthly DATA | >0.5 recession probability |
| 5 | WLEI2 < 0 | Weekly LEI's | Macro deterioration |

---

## Ranked bull entry (conviction)

Examples from encyclopedia: ZBT BUY, BIGBOT, OPT-1=1, combined TRADE+MTLV2+SIGS, P(BOT)>0.8, BOT score high, CMHI-2 crossing above 0.

---

## Ranked bear exit

Examples: RFE-6=1, BIGTOP, OPT-1=-1, combined TRADE/MTLV2/SIGS bearish, P(TOP)>0.8, TOP score high, CMHI-2 below 0.

---

## Master pseudo-code (illustrative)

This is **not** production code—illustrates how layers stack. Adjust thresholds per project.

```
# Requires CMHI-2 on the panel (weekly/monthly CMHI merged to daily)—not from load_cmhi DAILY-only.
if RFE_6 == 1:
    position = 0.0   # layer 1 — cash
elif CMHI_2 < 0:     # layer 2 — regime (use weekly/monthly CMHI-2)
    position = 0.0
else:
    # layer 3–5 — timing + breadth + probability (simplified)
    if TRADE == 2 and MTLV2 >= 3 and SIGS >= 8:
        position = 2.0
    elif TRADE == 1 and MTLV2 >= 2:
        position = 1.0
    elif TRADE == 1 and MTLV2 == 1:
        position = 0.5
    elif TRADE == -1 and SIGS <= 3:
        position = -1.0
    else:
        position = 0.0

# layer 5 — optional conviction multipliers (clip to risk limits)
if P_BOT_medium > 0.80 and BOT_score >= 6:
    position = min(position * 1.5, 2.0)
if P_TOP_medium > 0.80 and TOP_score >= 6:
    position = position * 0.5
```

Map `TRADE`, `MTLV2`, `SIGS`, etc., from merged daily columns (`opt_trade`, `MTLV2`, `SIGS`, …).

---

## Position sizing patterns

| Pattern | Idea |
|---------|------|
| DIFF / 7 | Fractional equity from CMHI diffusion count |
| RAVI-based | Smaller equity when expected returns low (use non-lookahead RAVI fields only) |
| Probability tilt | Scale by P(BOT)/P(TOP) distance from 0.5 |
| Vol targeting | Scale gross exposure by inverse realized vol |

Always apply **risk limits** (max leverage, max sector/asset) per project—encyclopedia examples are not sized for your leverage constraint.

---

## Asset allocation research (e.g. “2% alpha since 1990”)

1. Define **benchmark** (e.g. SPXT) and **evaluation window** (overlap of SPXT + merged panel).
2. Map layers to **weights** on equity vs cash (or multi-asset sleeves)—pseudo-code is a starting point.
3. Run **holdout / walk-forward**; report **DSR** if many parameters were searched (`ml-algo-trading`).
4. Disclose **ffill** and **in-sample OPTIMUM** limitations in any write-up.
