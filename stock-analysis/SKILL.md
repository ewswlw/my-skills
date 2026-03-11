---
name: stock-analysis
description: "Analyze stocks and companies using financial market data via yfinance. Get company profiles, technical insights, price charts, insider holdings, and financial statements for comprehensive stock research."
---

# Stock Analysis

Comprehensive stock and company analysis using the `yfinance` Python library for real-time and historical market data.

## Setup

```bash
uv add yfinance pandas numpy
```

## Core Capabilities

- **Company Research**: Business profile, sector, industry, employee count, executives
- **Price & Chart Data**: Historical OHLCV, adjusted close, 52-week range
- **Fundamental Analysis**: Income statement, balance sheet, cash flow, analyst recommendations
- **Insider Activity**: Major holders, institutional holders, insider transactions
- **Financial Data**: Earnings history, dividends, splits, options chain

## Common Workflows

### 1. Company Overview → Deep Dive

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Business profile
info = ticker.info
print(info.get("longBusinessSummary"))
print(f"Sector: {info.get('sector')} | Industry: {info.get('industry')}")
print(f"Employees: {info.get('fullTimeEmployees')}")

# Technical outlook: analyst recommendations
recs = ticker.recommendations
print(recs.tail(10))

# Recent price performance
hist = ticker.history(period="3mo")
print(hist.tail())
```

### 2. Technical Analysis → Fundamental Check

```python
import yfinance as yf

ticker = yf.Ticker("TSLA")

# Price trends
hist = ticker.history(period="1y", interval="1d")
print(f"52w High: {hist['High'].max():.2f}  52w Low: {hist['Low'].min():.2f}")
print(f"Current: {hist['Close'].iloc[-1]:.2f}")

# Analyst target price and rating
info = ticker.info
print(f"Target Price: {info.get('targetMeanPrice')}")
print(f"Recommendation: {info.get('recommendationKey')}")
```

### 3. Insider Activity Analysis

```python
import yfinance as yf

ticker = yf.Ticker("NVDA")

# Institutional and major holders
print(ticker.institutional_holders)
print(ticker.major_holders)

# Company context
info = ticker.info
print(f"Company: {info.get('shortName')} | Sector: {info.get('sector')}")
```

### 4. Due Diligence Package

```python
import yfinance as yf
import pandas as pd

ticker = yf.Ticker("MSFT")
info = ticker.info

# 1. Company background
print(f"Name: {info.get('longName')}")
print(f"Business: {info.get('longBusinessSummary')[:300]}...")

# 2. Valuation
print(f"P/E: {info.get('trailingPE'):.2f}  Forward P/E: {info.get('forwardPE'):.2f}")
print(f"Market Cap: ${info.get('marketCap'):,.0f}")
print(f"EV/EBITDA: {info.get('enterpriseToEbitda'):.2f}")

# 3. Historical performance
hist = ticker.history(period="2y")
annual_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
print(f"2Y Return: {annual_return:.1f}%")

# 4. Insider sentiment
print(ticker.major_holders)

# 5. Recent financials
print(ticker.quarterly_financials)
```

### 5. Multi-Stock Comparison

```python
import yfinance as yf
import pandas as pd

symbols = ["AAPL", "MSFT", "GOOGL"]
data = yf.download(symbols, period="1y", auto_adjust=True)["Close"]

# Normalize to 100 for comparison
normalized = (data / data.iloc[0]) * 100
print(normalized.tail())

# Compare key metrics
for sym in symbols:
    t = yf.Ticker(sym)
    info = t.info
    print(f"{sym}: P/E={info.get('trailingPE', 'N/A'):.1f}  "
          f"Mkt Cap=${info.get('marketCap', 0)/1e9:.0f}B  "
          f"Rec={info.get('recommendationKey', 'N/A')}")
```

### 6. Sector Research

```python
import yfinance as yf

tickers = ["AAPL", "NVDA", "AMD"]
for sym in tickers:
    t = yf.Ticker(sym)
    info = t.info
    hist = t.history(period="1y")
    ytd_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
    print(f"{sym} | {info.get('shortName')} | {info.get('sector')} | "
          f"1Y Return: {ytd_return:.1f}% | P/E: {info.get('trailingPE', 'N/A')}")
```

## Key yfinance API Reference

### Ticker Object

```python
ticker = yf.Ticker("SYMBOL")
```

| Attribute | Description |
|---|---|
| `ticker.info` | Full company profile dict (500+ fields) |
| `ticker.history(period, interval)` | OHLCV price history |
| `ticker.recommendations` | Analyst buy/sell recommendations |
| `ticker.institutional_holders` | Top institutional holders |
| `ticker.major_holders` | % held by insiders, institutions |
| `ticker.quarterly_financials` | Income statement (quarterly) |
| `ticker.balance_sheet` | Annual balance sheet |
| `ticker.cashflow` | Cash flow statement |
| `ticker.earnings` | Annual/quarterly earnings |
| `ticker.dividends` | Dividend history |
| `ticker.splits` | Stock split history |
| `ticker.options` | Available options expiry dates |

### Bulk Download

```python
# Single or multi-ticker historical data
df = yf.download("AAPL", start="2023-01-01", end="2024-01-01", auto_adjust=True)
df = yf.download(["AAPL", "MSFT"], period="1y", interval="1d", auto_adjust=True)
```

### Common `info` Keys

| Key | Description |
|---|---|
| `longName`, `shortName` | Company name |
| `longBusinessSummary` | Business description |
| `sector`, `industry` | Classification |
| `fullTimeEmployees` | Headcount |
| `marketCap` | Market capitalisation |
| `trailingPE`, `forwardPE` | Price/earnings ratios |
| `targetMeanPrice` | Analyst consensus target |
| `recommendationKey` | buy / hold / sell |
| `52WeekHigh`, `52WeekLow` | Price range |
| `dividendYield` | Dividend yield |
| `beta` | Beta vs market |

### Chart Intervals & Periods

| Parameter | Values |
|---|---|
| `interval` | `1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo` |
| `period` | `1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max` |

## When to Use This Skill

**Invoke when users mention:**
- Stock symbols: "AAPL", "TSLA", "$MSFT", "stock price", "stock info"
- Analysis: "analyze", "research", "look into", "tell me about [STOCK]"
- Comparison: "compare", "vs", "versus", "which is better"
- Price queries: "price", "chart", "performance", "trend"
- Insider activity: "insider", "holdings", "who owns"
- Financials: "earnings", "revenue", "P/E", "balance sheet", "cash flow"
- Company info: "what does [company] do", "who runs", "about [company]"

## Best Practices

1. **Start with `ticker.info`** — it contains most profile + valuation data in one call
2. **Use `auto_adjust=True`** in `yf.download()` to get split/dividend adjusted prices
3. **Multi-ticker downloads** are faster than looping individual `.history()` calls
4. **Rate limiting** — yfinance uses Yahoo Finance's public API; add `time.sleep(0.5)` between rapid successive calls to avoid throttling
5. **Data availability** — some fields (e.g., insider transactions detail) may be sparse for small-cap or non-US stocks

---

## Windows/Cursor Compatibility Notes

- Complete rewrite: all `Yahoo/get_stock_*` MCP API calls replaced with `yfinance` Python library.
- Install: `uv add yfinance pandas numpy`.
- No MCP connector required — yfinance calls Yahoo Finance's public API directly.
- The original `references/yahoo-api.md` documents the old Manus Yahoo MCP parameters; it remains for reference but is no longer the active calling convention.
- Run any of the above code snippets with `uv run python your_script.py`.
