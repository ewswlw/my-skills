# P123 Advanced Functions Reference

## Table of Contents
1. [SetVar — Variables](#setvar)
2. [Eval — Conditional Logic](#eval)
3. [FRank — Cross-Sectional Percentile Rank](#frank)
4. [ZScore — Cross-Sectional Z-Score](#zscore)
5. [Aggregate — Cross-Sectional Statistics](#aggregate)
6. [FHist — Historical Time Series](#fhist)
7. [FHistRank & FHistZScore — Historical Ranking](#fhistrank)
8. [NodeRank & Other Ranking Functions](#noderank)
9. [Group Functions](#group)
10. [Loop & Iteration Functions](#loop)
11. [AI Factor Functions](#aifactor)
12. [Screen-Only Functions](#screen-only)
13. [Consensus Estimate Functions](#consensus)
14. [Dividend & Corporate Action Functions](#dividends)

---

## SetVar — Variables <a name="setvar"></a>

```
SetVar(@name, expression)
```

- Variable names start with `@`
- Evaluated once, cached for the stock being processed
- Chain multiple SetVars; use in subsequent expressions
- **Display in report**: `@name:expression` (colon syntax)

```
SetVar(@pe, PEExclXorTTM)
SetVar(@cheap, @pe < 15)
SetVar(@quality, ROE%TTM > 15 AND GrMgn%TTM > 40)
@cheap AND @quality

// Display variables in screen report
@pe_rank:FRank("PEExclXorTTM", #All, #Asc)
```

---

## Eval — Conditional Logic <a name="eval"></a>

```
Eval(condition, true_value, false_value)
```

- If condition is non-zero → returns true_value
- If condition is zero or FALSE → returns false_value
- Nesting is allowed for multi-branch logic

```
// Basic usage
Eval(IsNA(PEExclXorTTM), 999, PEExclXorTTM)

// Sector-specific logic
Eval(SectorId = 40, 
     DebtToEqQ < 15,       // Financials: higher debt OK
     DebtToEqQ < 2)         // Others: strict

// Multi-branch (nested)
Eval(MktCap > 10000, "Large",
  Eval(MktCap > 2000, "Mid",
    Eval(MktCap > 300, "Small", "Micro")))

// Winsorize extreme values
Eval(PEExclXorTTM > 100, 100,
  Eval(PEExclXorTTM < 0, 0, PEExclXorTTM))
```

---

## FRank — Cross-Sectional Percentile Rank <a name="frank"></a>

```
FRank("formula", scope, direction [, incl_na])
```

**Parameters**:
- **formula**: P123 formula in quotes. Use backticks `` ` `` for complex expressions
- **scope**: `#All`, `#Sector`, `#Industry`, `#SubIndustry`
- **direction**: `#Asc` (low values → high rank, e.g., PE), `#Desc` (high values → high rank, e.g., ROE)
- **incl_na**: `#NANeg` (default — NAs get lowest rank), `#NANeutral` (NAs get middle rank)

**Returns**: 0-100 percentile rank

```
// Top quintile value (low PE = good)
FRank("PEExclXorTTM", #All, #Asc) > 80

// Top decile momentum
FRank(`Close(0)/Close(252)`, #All, #Desc) > 90

// Sector-relative quality
FRank("ROE%TTM", #Sector, #Desc) > 70

// With neutral NA handling
FRank("PEExclXorTTM", #All, #Asc, #NANeutral) > 80

// Complex formula with backticks
FRank(`Eval(IsNA(PEExclXorTTM), Pr2SalesTTM * 15, PEExclXorTTM)`, #All, #Asc) > 75
```

### Composite scores with FRank

```
SetVar(@val, FRank("PEExclXorTTM", #All, #Asc))
SetVar(@mom, FRank(`Close(0)/Close(252) - Close(0)/Close(21)`, #All, #Desc))
SetVar(@qual, FRank("ROE%TTM", #All, #Desc))
SetVar(@composite, 0.4 * @val + 0.3 * @mom + 0.3 * @qual)
@composite > 70
```

---

## ZScore — Cross-Sectional Z-Score <a name="zscore"></a>

```
ZScore("formula", scope)
```

Returns: number of standard deviations from the cross-sectional mean.

```
ZScore("PEExclXorTTM", #All)
ZScore("ROE%TTM", #Sector)

// Combine z-scores
SetVar(@z_pe, -1 * ZScore("PEExclXorTTM", #All))  // negate so low PE = positive z
SetVar(@z_roe, ZScore("ROE%TTM", #All))
@z_pe + @z_roe > 1
```

---

## Aggregate — Cross-Sectional Statistics <a name="aggregate"></a>

```
Aggregate("formula", scope [, method, outlier_pct, outlier_handl, excl_zero, excl_adrs, median_fallback])
```

**Parameters**:
- **method**: `#Mean` (default), `#Median`, `#StdDev`, `#Sum`, `#Count`, `#Min`, `#Max`
- **scope**: `#All`, `#Sector`, `#Industry`, `#SubIndustry`
- **outlier_pct**: percentile for outlier detection (0-50, default 0)
- **outlier_handl**: `#Clip` (default), `#Exclude`
- **excl_zero**: `TRUE`/`FALSE` (exclude zeros from calculation)
- **excl_adrs**: `TRUE`/`FALSE` (exclude ADRs)

```
// Stock's PE relative to sector median
PEExclXorTTM / Aggregate("PEExclXorTTM", #Sector, #Median)

// Industry average ROE
Aggregate("ROE%TTM", #Industry, #Mean)

// Number of stocks in the sector
Aggregate("1", #Sector, #Count)

// Sector standard deviation of returns (for dispersion)
Aggregate("Close(0)/Close(21)-1", #Sector, #StdDev)

// With outlier handling
Aggregate("PEExclXorTTM", #All, #Mean, 5, #Clip)  // clip 5th/95th percentile
```

---

## FHist — Historical Time Series <a name="fhist"></a>

```
FHist("formula", samples [, weeks_increment, NA_value, NA_pct])
```

**Parameters**:
- **samples**: number of historical observations to collect
- **weeks_increment**: spacing between samples in weeks (default 13 = quarterly)
- **NA_value**: value to substitute for NAs (default: exclude from calculation)
- **NA_pct**: maximum % of NAs allowed before returning NA (0-100, default 50)

**Returns**: average of all sampled historical values

```
// Average quarterly ROE over past year (4 samples, 13 weeks apart)
FHist("ROE%TTM", 4, 13)

// Average annual PE over 5 years
FHist("PEExclXorTTM", 5, 52)

// Monthly momentum readings over past year
FHist("Close(0)/Close(21)", 12, 4)

// Trailing 3-year average dividend yield
FHist("DivYield%TTM", 3, 52)
```

### FHistRank <a name="fhistrank"></a>

```
FHistRank("formula", samples [, weeks_increment, sort, sort_style, NA_value, NA_pct])
```

Returns: 0-100 percentile of current value vs its own history.

- **sort**: `#Desc` (default — 100=current is highest historically), `#Asc`
- **sort_style**: `#Pct` (default — percentile rank), `#Rank` (absolute rank position)

```
// Is current PE historically high? (100 = at historical peak)
FHistRank("PEExclXorTTM", 12, 13)

// Is current ROE historically strong?
FHistRank("ROE%TTM", 8, 13)

// Mean reversion signal: PE historically low
FHistRank("PEExclXorTTM", 20, 13) < 20
```

### FHistZScore

```
FHistZScore("formula", samples [, weeks_increment, clip, NA_value, NA_pct])
```

Returns: Z-score of current value vs historical samples.

```
// Current PE is unusually low relative to its own history
FHistZScore("PEExclXorTTM", 12, 13) < -1.5

// Operating margin improving relative to history
FHistZScore("OpMgn%TTM", 8, 13) > 1
```

---

## NodeRank & Ranking System Functions <a name="noderank"></a>

| Function | Description |
|----------|-------------|
| `NodeRank("name")` | Rank of a specific node in the current ranking system |
| `OtherRank("Ranking Name")` | Overall rank from a different ranking system |
| `PrevRank` | Rank at the previous rebalance |
| `RankPos` | Absolute position in ranked list (1=highest) |
| `RankBars` | Number of bars since rank was last calculated |

```
// In screen buy rules, using nodes from your ranking system
NodeRank("Value") > 80 AND NodeRank("Quality") > 60

// Rank improvement filter
PrevRank - RankPos > 0  // rank improved since last rebal
```

---

## Group Functions <a name="group"></a>

Used within ranking systems to compute group-level statistics:

| Function | Description |
|----------|-------------|
| `GroupAvg("formula", scope)` | Group average |
| `GroupMedian("formula", scope)` | Group median |
| `GroupStdDev("formula", scope)` | Group standard deviation |
| `GroupSum("formula", scope)` | Group sum |
| `GroupCnt(scope)` | Group count |
| `GroupMin("formula", scope)` | Group minimum |
| `GroupMax("formula", scope)` | Group maximum |
| `GroupRank("formula", scope)` | Rank within group |
| `GroupZScore("formula", scope)` | Z-score within group |
| `OrderInGroup(scope)` | Position order within group |

**Scope**: `#All`, `#Sector`, `#Industry`, `#SubIndustry`

```
// Within ranking factor: PE relative to industry median
PEExclXorTTM / GroupMedian("PEExclXorTTM", #Industry)

// Rank within sector
GroupRank("ROE%TTM", #Sector)
```

---

## Loop & Iteration Functions <a name="loop"></a>

### LoopRank — Rolling historical ranks

```
LoopRank("formula", "rank_formula", N, increment)
```

Computes rank values at N historical dates and averages them.

### LoopFHist — Historical function iteration

Used for complex backtesting logic within formulas.

---

## AI Factor Functions <a name="aifactor"></a>

```
AIFactor("AI Factor Name", "Predictor Name")
AIFactorValidation("AI Factor Name", "Model Name" [, "dup_id"])
```

P123's built-in ML factors. Use in screens or rankings:

```
// Use AI factor prediction
AIFactor("My AI Factor", "lightgbm II predictor")

// Rank by AI factor
FRank(`AIFactor("My AI Factor", "lightgbm II predictor")`, #All, #Desc) > 80
```

---

## Screen-Only Functions <a name="screen-only"></a>

| Function | Description |
|----------|-------------|
| `IndustryCount()` | Number of stocks from same industry in current screen results |
| `SectorCount()` | Number of stocks from same sector in current screen results |
| `ShowCorrel(N)` | Show correlation matrix in screen report for top N holdings |

```
// Limit concentration: max 3 stocks per industry
IndustryCount() <= 3

// Max 5 per sector
SectorCount() <= 5
```

### Account/Portfolio/Watchlist Holdings

```
Account("My Account")           // TRUE if stock is held
AccountOpen("My Account")       // days since position opened
AccountClose("My Account")      // days since position closed
Portfolio("My Strategy")        // same for strategies
Watchlist("My List")            // same for watchlists
```

---

## Consensus Estimate Functions <a name="consensus"></a>

```
ConsEstMean(cons_item [, period, weekAgo])
ConsEstMedian(cons_item [, period, weekAgo])
ConsEstHi(cons_item [, period, weekAgo])
ConsEstLow(cons_item [, period, weekAgo])
ConsEstCnt(cons_item [, period, weekAgo])
ConsEstStdDev(cons_item [, period, weekAgo])
ConsEstUp(cons_item [, period, weekAgo])      // upward revisions
ConsEstDn(cons_item [, period, weekAgo])      // downward revisions
ConsEstRSD(cons_item [, period, weekAgo])     // relative std dev
```

**cons_item**: `#EPS`, `#Sales`, `#EBITDA`, `#CapEx`, `#FCF`, `#DPS`
**period**: `#CQ` (current quarter), `#NQ`, `#CY`, `#NY`, `#2Y`
**weekAgo**: 0 (current), 1, 2, ... (for revision tracking)

```
// EPS revision breadth
ConsEstUp(#EPS, #CY) - ConsEstDn(#EPS, #CY)

// Sales estimate trend (current vs 4 weeks ago)
ConsEstMean(#Sales, #CY) / ConsEstMean(#Sales, #CY, 4) - 1

// Number of analysts covering
ConsEstCnt(#EPS, #CY)
```

### Historical Estimates

```
HistEstEPS(offset, periodType, weekAgo)
HistEstSales(offset, periodType, weekAgo)
HistEstNumAnalysts(offset, periodType, weekAgo)
```

### Recommendation Functions

```
ConsRec(rec_stat [, weekAgo])
```

**rec_stat**: `#Mean`, `#Median`, `#Buy`, `#Outperform`, `#Hold`, `#Underperform`, `#Sell`, `#Total`

```
// Average recommendation (1=Strong Buy to 5=Strong Sell)
ConsRec(#Mean)

// Recommendation improvement
ConsRec(#Mean) - ConsRec(#Mean, 4) < 0  // lower = more bullish
```

---

## Dividend & Corporate Action Functions <a name="dividends"></a>

| Function | Description |
|----------|-------------|
| `DivInPeriod(offset, type)` | Dividends paid in a filing period |
| `IndDivA` | Indicated annual dividend |
| `DivGr%3Y` | Dividend growth rate 3-year |
| `DivGr%5Y` | Dividend growth rate 5-year |
| `DivGr%10Y` | Dividend growth rate 10-year |
| `PayoutRatio%TTM` | Payout ratio |
| `DivDays` | Days since ex-dividend date |
| `SplitFactor` | Recent split factor |
| `FutDivFactor` | Future dividend factor |
| `FutSplitFactor` | Future split factor |

---

## Insider & Institutional Functions

| Factor | Description |
|--------|-------------|
| `InsiderBuySell%3Mo` | Insider buy/sell ratio (3 month) |
| `InsiderBuySell%6Mo` | Insider buy/sell ratio (6 month) |
| `InsiderBuyShares3Mo` | Insider shares bought (3 month) |
| `InsiderSellShares3Mo` | Insider shares sold (3 month) |
| `InstOwn%` | Institutional ownership % |
| `InstOwnChg%QoQ` | Institutional ownership change QoQ |
| `ShortInt%` | Short interest as % of float |
| `ShortIntRatio` | Short interest ratio (days to cover) |

---

## Unverified — Practitioner-Reported Functions

> **Warning:** The functions below were observed in practitioner formulas (Systematic Investing, Substack — Layers of Return series). Their exact syntax has **not** been independently validated against the P123 documentation. Before using in any production ranking system or screen, verify each via `https://www.portfolio123.com/doc/doc_detail.jsp?factor=[NAME]` and test in a screen before relying on the result.

### GetSeries — External Ticker Series

Fetches a time series for an external ticker (e.g., an ETF trading on a US exchange).

```
GetSeries(`TICKER:EXCHANGE`)
```

- Used inside other functions to reference market-wide series (e.g., global drawdown via an ETF)
- Example: `GetSeries(\`VEA:USA\`)` — returns the price series for VEA (Vanguard FTSE Developed Markets ETF)
- Typically combined with `HighPct_W()` and `FHistMin()` for drawdown-based regime gates

```
// Global drawdown condition (52-week high drawdown of VEA)
FHistMin("HighPct_W(52, GetSeries(`VEA:USA`))", 52) < -30
```

### HighPct_W — Weekly High Percentage

Returns the percentage of the current price relative to the N-week high (i.e., how far from peak).

```
HighPct_W(bars, series)
```

- `bars`: lookback in weekly bars (e.g., 52 = 1 year)
- `series`: price series reference (e.g., result of `GetSeries()`)
- Returns a negative value when price is below the peak (e.g., -30 means 30% below 52-week high)

### FHistMin — Historical Minimum

Returns the **minimum** value of a formula across sampled historical dates (counterpart to `FHist()` which returns the average).

```
FHistMin("formula", samples [, weeks_increment])
```

- **samples**: number of historical observations
- **weeks_increment**: spacing in weeks (default 13 = quarterly; use 1 for weekly)
- Example: `FHistMin("HighPct_W(52, GetSeries(\`VEA:USA\`))", 52)` — minimum of the 52-week high drawdown reading over the past 52 weekly samples (i.e., worst drawdown in the past year)
