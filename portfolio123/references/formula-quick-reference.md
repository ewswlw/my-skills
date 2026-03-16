# P123 Formula Language Quick Reference

## Table of Contents
1. [Syntax Basics](#basics)
2. [Operators](#operators)
3. [Variables (SetVar)](#setvar)
4. [Conditional Logic (Eval)](#eval)
5. [Cross-Sectional Functions (FRank, ZScore, Aggregate)](#cross-sectional)
6. [Historical Functions (FHist)](#fhist)
7. [Ranking System Functions (NodeRank)](#noderank)
8. [NA Handling](#na-handling)
9. [Common Patterns & Idioms](#patterns)

---

## Syntax Basics <a name="basics"></a>

P123 formulas are used in: screen rules, ranking system factors, data retrieval, and universe definitions.

### Operators <a name="operators"></a>

**Math**: `+`, `-`, `*`, `/`, `^` (power)
**Comparison**: `=`, `!=`, `>`, `<`, `>=`, `<=`
**Logical**: `AND`, `OR`, `!` (negate)
**Precedence**: `( )` — always use parentheses when in doubt
**Comments**: `//` — everything after is ignored

### Data Types

- Numbers: `5`, `3.14`, `-20`
- Strings: `"text in quotes"`
- Boolean: `TRUE` (1), `FALSE` (0)
- NA: `NA` — missing/unavailable value
- Constants: `#Year` (251), `#Month` (21), `#Month3` (62), `#Month6` (125), `#Week` (5)

### Bars vs Days

- **Bars** = trading days (~251/year). Used by most technical functions.
- **Calendar days** = includes weekends/holidays. Used by some Account/Portfolio functions.
- Most functions use bars unless explicitly stated otherwise.

---

## Variables (SetVar) <a name="setvar"></a>

```
SetVar(@variableName, expression)
```

Variables start with `@`. They're evaluated once and reused. Multiple SetVar calls chain:

```
SetVar(@pe, PEExclXorTTM)
SetVar(@roe, ROE%TTM)
@pe < 20 AND @roe > 15
```

**Display variable in screen report**: Use `:` syntax
```
@myvar:expression    // sets @myvar, displays in report, returns expression value
```

---

## Conditional Logic (Eval) <a name="eval"></a>

```
Eval(condition, value_if_true, value_if_false)
```

Examples:
```
// Use alternate metric when PE is NA
Eval(IsNA(PEExclXorTTM), Pr2SalesTTM, PEExclXorTTM)

// Sector-specific thresholds
Eval(IndustryId = 31011010, ROE%TTM > 5, ROE%TTM > 15)

// Nested Eval for multiple conditions
Eval(MktCap > 10000, 1,
  Eval(MktCap > 2000, 2,
    Eval(MktCap > 500, 3, 4)))
```

---

## Cross-Sectional Functions <a name="cross-sectional"></a>

### FRank — Percentile rank across a group

```
FRank("formula", scope, direction [, incl_na])
```

- **scope**: `#All`, `#Sector`, `#Industry`, `#SubIndustry`
- **direction**: `#Asc` (lower=better → low values get high rank), `#Desc` (higher=better)
- **incl_na**: `#NANeg` (default, NAs rank lowest), `#NANeutral` (NAs rank middle)

```
// Top quintile by PE (lower is better)
FRank("PEExclXorTTM", #All, #Asc) > 80

// Top decile momentum within sector
FRank("Close(0)/Close(252)", #Sector, #Desc) > 90

// Bottom decile with neutral NAs
FRank("PEExclXorTTM", #All, #Asc, #NANeutral) < 10
```

**Formula argument uses backticks for complex expressions**:
```
FRank(`Close(0)/Close(252) - Close(0)/Close(21)`, #All, #Desc) > 80
```

### ZScore — Standardized score across a group

```
ZScore("formula", scope)
```

```
ZScore("PEExclXorTTM", #All)
ZScore(`ROE%TTM`, #Sector)
```

### Aggregate — Summary statistics across a group

```
Aggregate("formula", scope [, method, outlier_pct, outlier_handl, excl_zero, excl_adrs, median_fallback])
```

- **method**: `#Mean` (default), `#Median`, `#StdDev`, `#Sum`, `#Count`, `#Min`, `#Max`
- **scope**: `#All`, `#Sector`, `#Industry`, `#SubIndustry`

```
// Compare stock PE to sector median
PEExclXorTTM / Aggregate("PEExclXorTTM", #Sector, #Median)

// Industry average ROE
Aggregate("ROE%TTM", #Industry, #Mean)
```

---

## Historical Functions (FHist) <a name="fhist"></a>

### FHist — Point-in-time historical value

```
FHist("formula", samples [, weeks_increment, NA_value, NA_pct])
```

- **samples**: number of historical data points to look back
- **weeks_increment**: spacing between samples in weeks (default 13 = quarterly)
- Returns the **average** of all sampled values

```
// Average ROE over past 4 quarters (quarterly spacing)
FHist("ROE%TTM", 4, 13)

// Average PE over past 3 years (yearly spacing)
FHist("PEExclXorTTM", 3, 52)

// Historical momentum signal (monthly spacing, 12 samples)
FHist("Close(0)/Close(21)", 12, 4)
```

### FHistRank — Percentile rank of current vs historical values

```
FHistRank("formula", samples [, weeks_increment, sort, sort_style, NA_value, NA_pct])
```

```
// Is current PE high or low relative to its own history?
FHistRank("PEExclXorTTM", 12, 13)  // 0-100, higher = current is higher than usual
```

### FHistZScore — Z-Score of current vs historical values

```
FHistZScore("formula", samples [, weeks_increment, clip, NA_value, NA_pct])
```

```
// How many standard deviations is current ROE from its historical mean?
FHistZScore("ROE%TTM", 8, 13)
```

---

## Ranking System Functions <a name="noderank"></a>

### NodeRank — Access sub-ranks within a ranking system

```
NodeRank("NodeName")
```

```
// In a screen rule, access a specific node from your ranking system
NodeRank("Value") > 80
NodeRank("Quality") > 50
```

### OtherRank — Access ranks from a different ranking system

```
OtherRank("Ranking System Name")
```

### PrevRank — Previous rank value

```
PrevRank    // rank from the previous rebalance
```

### RankPos — Position within ranked list

```
RankPos     // 1 = highest ranked, N = lowest ranked
```

---

## NA Handling <a name="na-handling"></a>

### Checking for NAs

```
IsNA(expression)          // returns TRUE if expression is NA
!IsNA(PEExclXorTTM)       // stock has a PE value
```

### Fundamental function NA parameter

Every fundamental function accepts NAHandling as last parameter:
- `FALLBACK` (default): falls back to previous period if current is NA
- `KEEPNA`: keeps NA (doesn't fall back)
- `ZERONA`: replaces NA with 0

```
Sales(0, QTR, KEEPNA)     // keep NA, don't fall back
Cash(0, QTR, ZERONA)      // treat NA as 0
OpInc(0, TTM)             // default: FALLBACK
```

### Replacing NAs

```
// Replace NA with a default value
Eval(IsNA(PEExclXorTTM), 999, PEExclXorTTM)

// Use Bound to limit extreme values and NAs
Bound(PEExclXorTTM, 0, 200)              // clip to range
Bound(PEExclXorTTM, 0, 200, TRUE)        // return NA if outside range
```

---

## Common Patterns & Idioms <a name="patterns"></a>

### Multi-factor composite in a screen rule

```
SetVar(@value, FRank("PEExclXorTTM", #All, #Asc))
SetVar(@mom, FRank(`Close(0)/Close(252)`, #All, #Desc))
SetVar(@qual, FRank("ROE%TTM", #All, #Desc))
(@value + @mom + @qual) / 3 > 70
```

### Betting Against Beta (BAB) style

```
SetVar(@beta, BetaFunc(52, 104))
SetVar(@rank_beta, FRank(`BetaFunc(52, 104)`, #All, #Asc))
@rank_beta > 50    // low beta half
```

### Piotroski F-Score components

```
SetVar(@f1, Eval(NetInc(0,TTM) > 0, 1, 0))
SetVar(@f2, Eval(OpCashFl(0,TTM) > 0, 1, 0))
SetVar(@f3, Eval(ROA%TTM > ROA%PTM, 1, 0))
SetVar(@f4, Eval(OpCashFl(0,TTM) > NetInc(0,TTM), 1, 0))
@f1 + @f2 + @f3 + @f4 >= 3
```

### Earnings momentum / SUE

```
SetVar(@surprise, EPSSurprise%CQ)
SetVar(@revision, SumRevisions)
@surprise > 0 AND @revision > 0
```

### Liquidity filter

```
MktCap > 500
AvgDailyTot(63) > 500        // avg daily dollar volume > $500K over 63 bars
Close(0) > 5                  // minimum share price
```

### Sector/Industry filtering

```
SectorId != 40                  // exclude Financials
IndustryId != 40201020          // exclude REITs
```

### Using benchmarks and indices

```
Close(0, $SPY)                // SPY price
Close(0, #Bench)              // benchmark price
Close(0, #Industry)           // industry index price
Close(0) / Close(252) > Close(0, $SPY) / Close(252, $SPY)  // beat SPY momentum
```

### Utility Functions

```
Abs(expression)               // absolute value
Avg(x1, x2, ..., x20)        // average of up to 20 values
Max(x1, x2)                  // maximum
Min(x1, x2)                  // minimum
Bound(expr, min, max)         // clip to range
Between(value, min, max)      // TRUE if min <= value <= max
Log(expr)                     // natural log
Exp(expr)                     // e^x
Sqrt(expr)                    // square root
Round(expr, decimals)         // round
BarsSince(date)               // bars since YYYYMMDD date
```

### Date and Filing Functions

```
LatestFilingDt                 // date of latest filing (YYYYMMDD)
LatestActualDays               // days since latest actuals
InterimMonths                  // months in latest interim period (3 or 6)
FYEndMonth                     // fiscal year end month (1-12)
```
