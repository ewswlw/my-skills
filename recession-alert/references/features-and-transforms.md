# Features and Transforms

Derived from `engineer_features` in `spx_timing_strategy.py` (`ROLLING_WINDOW` is typically 252). Adjust windows per project.

---

## Rolling z-scores

**CMHI / DIFF:**

```
cmhi_z = (CMHI - rolling_mean(CMHI, 252)) / rolling_std(CMHI, 252)
diff_z = (DIFF - rolling_mean(DIFF, 252)) / rolling_std(DIFF, 252)
```

- Replace 0 std with NaN, then inf with NaN, then **fillna(0)** for downstream ML stability.
- **Use:** Regime-normalized positioning; comparability across years.

---

## Momentum and changes

| Feature | Formula / rule | Notes |
|---------|----------------|-------|
| `cmhi_mom` | `CMHI.pct_change(20)` | Short trend of composite |
| `super_4w`, `super_13w` | `SUPERINDEX.pct_change(20)`, `.pct_change(65)` | ~1m / ~3m macro momentum; requires `SUPERINDEX` on merged panel |
| `wli_4w`, `wli_13w` | Same on `WLIr` if column exists | If `WLIr` absent, reference code still runs but those columns may be all-zero—**test** when WLIr is optional |
| `hy_ret_20d`, `hy_ret_60d` | `pct_change` on HY index column | Credit cycle context |
| `hy_z60` | Z-score of `hy_ret_60d` over 252-day window | Stressed credit vs history |

---

## Passthroughs (daily panel after merge)

| Output col | Source | Fill rule |
|------------|--------|-----------|
| `rfe6` | RFE_6 | `fillna(0)` — treat missing as no recession flag |
| `tdiff`, `net_p` | TDIFF, NET P | `fillna(0)` |
| `p_bot_med`, `p_top_med` | P(BOT).1 or P(BOT), P(TOP).1 or P(TOP) | `fillna(0.5)` |
| `mtlv2` | MTLV2 | `fillna(0)` |
| `sigs` | SIGS | `fillna(0)` after merge |
| `opt_trade`, `opt_diffn`, `opt_cmhi` | TRADE, DIFFN, OPT-CMHI | `fillna(0)` if columns exist |
| `top_score`, `bot_score` | TOP, BOT | `fillna(0)` |
| `net_avg`, `net_top3`, `bigtop`, `bigbot`, `net_diff_mf` | MF prob columns | `fillna(0)` |
| `dcom` | DCOM | `fillna(0)` |
| `vix` | VIX | `fillna(20)` |
| `pct_above_50dma` | %>50DMA | `fillna(50)` |

Probabilities defaulting to **0.5** and VIX to **20** are **discretionary** defaults—document in project config if you change them.

---

## Statistical properties (economic context)

- **CMHI** long-run mean ≈ **+0.3**; **CMHI-2** centers near zero by subtracting MEAN.
- **DIFF** (weekly) is integer **0–7** in many exports; daily DIFF may be normalized—check your sheet.
- **RFE-6** is binary **{0,1}** in RFE VARIANTS.
- **TRADE** typically in **{-1, 0, 1, 2}** (short, flat, long, leveraged).
- **NET VOL** and **WLEI** (weekly CMHI components) are often cited as highest-conviction CMHI ingredients.

---

## Additional transforms (optional)

Use when hypothesis calls for them; add tests before relying on them.

| Transform | When |
|-----------|------|
| Fractional differentiation | Stationarity with memory preservation (see `ml-algo-trading`) |
| Regime dummies | Bull/bear from CMHI>0 or CMHI-2<0 |
| Cross-terms | e.g. `cmhi_z * mtlv2` for “healthy breadth × regime” |
| Rolling correlation | CMHI vs breadth over 63d |
| Diffusion velocity | `DIFF.diff()` or change in count of RFE models firing |
| Rank / percentile | Cross-sectional rank if combining multiple normalized columns |

---

## Anti-patterns

- Using **RAVI forward return** columns as features (lookahead).
- Z-scoring without handling **zero std** (divide-by-zero inf).
- Filling NaN with arbitrary constants **without** documenting them in the project config.
