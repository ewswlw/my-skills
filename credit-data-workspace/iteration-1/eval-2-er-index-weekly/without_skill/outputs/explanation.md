# Explanation: US IG & HY Excess Return Index (Weekly, Base 100)

## Bloomberg Tickers Used

| Label | Ticker | Description |
|-------|--------|-------------|
| US_IG_ER | `LUACEXUU Index` | Bloomberg Barclays US Corporate Investment Grade Excess Return Index (USD Unhedged) |
| US_HY_ER | `LF98EXUU Index` | Bloomberg Barclays US High Yield Excess Return Index (USD Unhedged) |

These are the standard Bloomberg Barclays "ER" (excess return) variants of the benchmark IG and HY bond indices. Excess return strips out the duration-matched Treasury return, isolating the credit spread / carry component.

## Data Retrieval Strategy

### Primary: `PX_LAST`
The preferred approach is to pull raw index levels via `PX_LAST`. Bloomberg maintains cumulative index level history for these series. If the returned values look like index levels (median absolute value > 50), they are simply rebased:

```
rebased[t] = raw[t] / raw[first_obs] * 100
```

### Fallback: `EXCESS_RETURN_YTD`
Some Bloomberg delivery modes return YTD percentage returns that reset to 0 on the first trading day of each calendar year. In this case the code chains across year boundaries:

```
level[t] = carry_prior_year × (1 + ytd[t] / 100)
```

where `carry_prior_year` is the last index level from December of the prior year. This produces a continuous cumulative index.

## YTD-to-Cumulative Chaining Logic

The key insight is that a YTD return series has a hidden structure:

- Within a year: `level[t] = base_of_year * (1 + ytd[t])`
- At year boundary: `base_of_year_N+1 = level[last_day_of_year_N]`

The code iterates over calendar years, computes within-year levels, then rolls the "carry" forward to the next year.

## Weekly Resampling

Daily data is resampled using `resample("W-FRI").last()`, taking the last available observation for each week ending on Friday. This is consistent with standard fixed income analytics practice (calendar-week end, not business week).

## Output Format

CSV with columns: `date, US_IG_ER, US_HY_ER`  
Index values start at 100.0 on the first available observation (first Friday on or after 2015-01-01).

## Identified Uncertainties

1. **Ticker validity**: `LUACEXUU` and `LF98EXUU` are the standard Bloomberg Barclays tickers but may require specific Bloomberg terminal permissions (e.g., POINT subscription).
2. **PX_LAST vs YTD field**: Without a live Bloomberg terminal, it is unclear which field Bloomberg returns by default for these index tickers. The dual-strategy fallback handles both cases.
3. **ICE BofA alternatives**: If Bloomberg Barclays tickers are unavailable, `C0A0 Index` (IG) and `H0A0 Index` (HY) from ICE BofA would be reasonable substitutes — same approach applies.
