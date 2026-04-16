# P123 Technical Functions Reference

All technical functions operate on price/volume bar data (trading days).

Common optional parameters:
- **offset**: bars ago to start calculation (default 0 = from latest)
- **series**: price series to use (default = stock's own prices)
  - `#Close`, `#Open`, `#High`, `#Low` — stock prices
  - `#Bench` — benchmark
  - `$SPY`, `$QQQ`, etc. — specific ticker
  - `#Industry`, `#Sector` — index prices
  - `#Equity` — portfolio value (strategies only)
  - Numeric ID — specific P123 stock ID

---

## Price & Volume Functions

| Function | Description |
|----------|-------------|
| `Close(barsAgo [, series])` | Closing price N bars ago |
| `Open(barsAgo [, series])` | Opening price |
| `High(barsAgo [, series])` | High price |
| `Low(barsAgo [, series])` | Low price |
| `Volume(barsAgo)` | Volume N bars ago |
| `CloseAdj(barsAgo)` | Split-adjusted close |
| `CloseExDiv(barsAgo)` | Close excluding dividends |
| `AvgVol(bars [, offset, series])` | Average volume over N bars |
| `AvgDailyTot(bars [, offset])` | Avg daily dollar volume (price × volume) |

### Price Returns

| Function | Description |
|----------|-------------|
| `Ret%Chg(bars)` | % price change over N bars |
| `Close(0)/Close(N) - 1` | Alternative: manual return calculation |

---

## Moving Averages

| Function | Description |
|----------|-------------|
| `SMA(bars [, offset, series])` | Simple moving average |
| `EMA(bars [, offset, series])` | Exponential moving average |
| `WMA(bars [, offset, series])` | Weighted moving average |
| `DEMA(bars [, offset, series])` | Double exponential moving average |
| `TEMA(bars [, offset, series])` | Triple exponential moving average |

```
// Golden cross: 50-day SMA above 200-day SMA
SMA(50, 0) > SMA(200, 0)

// Price above 200-day moving average
Close(0) > SMA(200, 0)

// EMA crossover
EMA(12, 0) > EMA(26, 0)
```

---

## Momentum & Oscillators

| Function | Description |
|----------|-------------|
| `RSI(period [, offset, series])` | Relative Strength Index (Wilder's, period in bars) |
| `RSI_(period [, offset, series])` | RSI with period in weeks (includes holidays) |
| `MACD(offset [, series])` | MACD (26-bar EMA minus 12-bar EMA) |
| `MACDSig(period [, offset, series])` | MACD signal line (EMA of MACD) |
| `MACDHist(period [, offset, series])` | MACD histogram (MACD minus signal) |
| `StochK(period [, smoothK, offset, series])` | Stochastic %K |
| `StochD(period, smoothK, smoothD [, offset, series])` | Stochastic %D |
| `CCI(bars [, offset, series])` | Commodity Channel Index |
| `ROC(bars [, offset, series])` | Rate of change |
| `MOM(bars [, offset, series])` | Momentum (price difference) |
| `WilliamsR(period [, offset, series])` | Williams %R |

```
// RSI oversold
RSI(14) < 30

// MACD bullish crossover
MACDHist(9) > 0 AND MACDHist(9, 1) <= 0

// Slow stochastic
StochK(14, 3) > StochD(14, 3, 3)
```

---

## Volatility & Bands

| Function | Description |
|----------|-------------|
| `BBUpper(period [, deviations, offset, series])` | Bollinger Band upper |
| `BBLower(period [, deviations, offset, series])` | Bollinger Band lower |
| `ATR(bars [, offset, series])` | Average True Range |
| `ATRN(bars [, offset, series])` | Normalized ATR (% of price) |
| `StdDev(bars [, offset, series])` | Standard deviation of returns |
| `Volatility(bars [, offset])` | Annualized volatility |
| `BetaFunc(period, samples [, min_samples, offset])` | Beta calculation |

```
// Price near lower Bollinger Band (potential mean reversion)
Close(0) < BBLower(20, 2)

// Low volatility stocks
StdDev(252) < Aggregate("StdDev(252)", #All, #Median)

// Custom beta
BetaFunc(52, 104)  // 52-week period, 104 weekly samples
```

---

## Trend & Volume Indicators

| Function | Description |
|----------|-------------|
| `ADX(period, offset [, series])` | Average Directional Index |
| `PlusDI(period, offset [, series])` | Plus Directional Indicator |
| `MinusDI(period, offset [, series])` | Minus Directional Indicator |
| `ChaikinAD(period [, offset])` | Chaikin Accumulation/Distribution |
| `ChaikinMFP(period, lookback [, offset])` | Chaikin Money Flow Persistence |
| `ChaikinTrend(bars [, offset, increment, series])` | Chaikin Trend |
| `OBV(offset)` | On-Balance Volume |
| `AroonUp(period [, offset, series])` | Aroon Up |
| `AroonDn(period [, offset, series])` | Aroon Down |
| `AroonOsc(period [, offset, series])` | Aroon Oscillator |

```
// Strong uptrend
ADX(14, 0) > 25 AND PlusDI(14, 0) > MinusDI(14, 0)
```

---

## Relative Strength & Comparative

| Factor | Description |
|--------|-------------|
| `RS4WeekAvg` | Relative strength 4-week average (vs market) |
| `RS12WeekAvg` | Relative strength 12-week average |
| `RS26WeekAvg` | Relative strength 26-week average |
| `RS52WeekAvg` | Relative strength 52-week average |
| `TRSD1YD` | 1-year total return standard deviation — **practitioner-reported name, validate via doc_detail.jsp before use** |

```
// Compare with benchmark
Close(0)/Close(252) > Close(0, #Bench)/Close(252, #Bench)

// Custom relative strength
Close(0)/Close(252) - Close(0, $SPY)/Close(252, $SPY)
```

---

## Price Patterns & Extremes

| Function | Description |
|----------|-------------|
| `HiValue(bars [, offset, series])` | Highest value over N bars |
| `LoValue(bars [, offset, series])` | Lowest value over N bars |
| `HiBar(bars [, offset, series])` | Bars since highest high |
| `LoBar(bars [, offset, series])` | Bars since lowest low |
| `Close52WkHi` | 52-week high price |
| `Close52WkLo` | 52-week low price |
| `Pr52WkHi%` | Price as % of 52-week high |
| `Pr52WkLo%` | Price as % of 52-week low |

```
// Near 52-week high
Pr52WkHi% > 95

// Drawing down from peak
Close(0) / HiValue(252) < 0.80  // 20%+ drawdown from 1-year high
```

---

## Streak & Pattern Functions

| Function | Description |
|----------|-------------|
| `Streak(formula, #Positive)` | Consecutive bars with positive values |
| `Streak(formula, #NotPositive)` | Consecutive bars with non-positive values |
| `Streak(formula, #Increasing)` | Consecutive bars with increasing values |
| `Streak(formula, #NotIncreasing)` | Consecutive bars with non-increasing values |

```
// Price rising for 5+ consecutive days
Streak(Close(0) - Close(1), #Positive) >= 5

// Volume increasing streak
Streak(Volume(0) - Volume(1), #Increasing) >= 3
```

---

## Strategy-Only Functions

These work only inside P123 strategy buy/sell rules:

| Function | Description |
|----------|-------------|
| `NoBars` | Trading days since position opened |
| `NoDays` | Calendar days since position opened |
| `EntryPrice` | Price at which position was entered |
| `ExitPrice` | Exit price |
| `PortBars` | Bars since strategy inception |
| `PortValue` | Portfolio total value |
| `PosWeight%` | Current position weight % |
| `PosReturn%` | Return % of current position |
| `MaxPosPr` | Maximum price since entry |
| `MinPosPr` | Minimum price since entry |
| `MaxPosRet%` | Maximum return since entry |
| `MinPosRet%` | Minimum return since entry |
| `PrevRank` | Rank at previous rebalance |
| `RankPos` | Position in ranked list (1=top) |

```
// Trailing stop: sell if dropped 15% from peak
MinPosRet% < -15

// Time-based exit: sell after 6 months
NoBars > 125

// Sell if rank deteriorated significantly
PrevRank - RankPos > 30
```
