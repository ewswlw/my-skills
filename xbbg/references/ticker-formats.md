# Bloomberg Ticker Format Reference
<!-- Last verified: xbbg 1.0.0a1 | March 2026 -->

Bloomberg tickers follow the pattern: `<Identifier> <Yellow Key>`

---

## Yellow Key (Asset Class Suffix)

| Yellow Key | Asset Class | Example |
|---|---|---|
| `Equity` | Stocks, ETFs, ADRs | `AAPL US Equity` |
| `Index` | Indices, economic | `SPX Index`, `VIX Index` |
| `Comdty` | Commodities, futures | `CL1 Comdty`, `GC1 Comdty` |
| `Curncy` | FX spot, forward, crypto | `EURUSD Curncy` |
| `Corp` | Corporate bonds | `AAPL 3 8/1/46 Corp` |
| `Govt` | Government bonds | `T 4.5 5/15/38 Govt` |
| `Mtge` | Mortgages, MBS | `FN 3.5 Mtge` |
| `Muni` | Municipal bonds | `CA 5 6/1/30 Muni` |
| `Pfd` | Preferred stock | `BAC/PB US Pfd` |
| `MM` | Money market | `US0001M Index` (LIBOR/SOFR) |

---

## Equity Tickers

### Format: `<TICKER> <EXCHANGE> Equity`

| Exchange | Code | Example |
|---|---|---|
| NYSE | `US` | `IBM US Equity` |
| NASDAQ | `US` | `AAPL US Equity` |
| London | `LN` | `SHEL LN Equity` |
| Tokyo | `JT` | `7974 JT Equity` |
| Hong Kong | `HK` | `700 HK Equity` |
| Frankfurt | `GR` | `BMW GR Equity` |
| Paris | `FP` | `TTE FP Equity` |
| Sydney | `AU` | `BHP AU Equity` |
| Toronto | `CT` | `RY CT Equity` |
| Singapore | `SP` | `D05 SP Equity` |

### ADRs
```python
'BABA US Equity'    # Alibaba ADR on NYSE
'BIDU US Equity'    # Baidu ADR on NASDAQ
```

### ETFs (same format as equity)
```python
'SPY US Equity'     # S&P 500 ETF
'QQQ US Equity'     # Nasdaq 100 ETF
'IEF US Equity'     # 7-10yr Treasury ETF
'GLD US Equity'     # Gold ETF
'EEM US Equity'     # EM equities ETF
```

---

## Index Tickers

### Equity Indices
```python
'SPX Index'         # S&P 500
'NDX Index'         # Nasdaq 100
'INDU Index'        # Dow Jones
'RTY Index'         # Russell 2000
'SX5E Index'        # Euro Stoxx 50
'UKX Index'         # FTSE 100
'NKY Index'         # Nikkei 225
'HSI Index'         # Hang Seng
'SHCOMP Index'      # Shanghai Composite
'AS51 Index'        # ASX 200
'MXWO Index'        # MSCI World
'MXEF Index'        # MSCI EM
'VIX Index'         # CBOE VIX
```

### Fixed Income Indices
```python
'LUACTRUU Index'    # Bloomberg US Agg Total Return
'LF98TRUU Index'    # Bloomberg US HY Total Return
'LMBITR Index'      # Bloomberg Muni Bond Index
'LD07TRUU Index'    # Bloomberg Global Agg
```

### Rates / SOFR / Macro
```python
'US0001M Index'     # USD LIBOR 1M (legacy)
'SOFRRATE Index'    # SOFR overnight rate
'FDTR Index'        # Fed Funds Target Rate
'USGG10YR Index'    # US 10yr Generic Govt Yield
'USGG2YR Index'     # US 2yr Generic Govt Yield
'GTDEM10Y Govt'     # German 10yr Bund yield
'CPI YOY Index'     # US CPI YoY
'GDP CQOQ Index'    # US GDP QoQ
'NFP TCH Index'     # Non-Farm Payrolls change
```

---

## Fixed Income Tickers

### US Treasuries — Generic (On-the-Run)
```python
'USGG1M Index'      # 1-month
'USGG3M Index'      # 3-month
'USGG6M Index'      # 6-month
'USGG1YR Index'     # 1-year
'USGG2YR Index'     # 2-year
'USGG5YR Index'     # 5-year
'USGG10YR Index'    # 10-year
'USGG30YR Index'    # 30-year
```

### Specific Treasury Bonds
Format: `<Country> <Coupon> <Maturity> Govt`
```python
'T 4.5 5/15/38 Govt'          # US Treasury 4.5% due 2038
'T 0 3/31/25 Govt'            # T-bill / zero coupon
'GTDEM10Y Govt'               # German generic 10yr
'GTGBP10Y Govt'               # UK gilt generic 10yr
'GTJPY10Y Govt'               # JGB generic 10yr
```

### Corporate Bonds
Format: `<ISSUER> <Coupon> <Maturity> Corp`
```python
'AAPL 3.85 5/4/43 Corp'       # Apple bond
'MSFT 2.921 3/17/52 Corp'     # Microsoft bond
'GS 5 1/27/25 Corp'           # Goldman Sachs
'JPM 3.702 5/6/30 Corp'       # JP Morgan
```

### Identifier-Based Lookup (preferred for FI)
```python
# ISIN format — works with bdp, bdh, bds
'/isin/US0378331005'          # Apple equity via ISIN
'/isin/US037833AK68'          # Apple bond via ISIN

# CUSIP format
'/cusip/037833AK6'            # Apple bond via CUSIP

# SEDOL format
'/sedol/B7TL820'              # UK equity via SEDOL
```

---

## FX Tickers

### Spot Rates (always `Curncy`)
```python
'EURUSD Curncy'    # EUR/USD spot
'USDJPY Curncy'    # USD/JPY spot
'GBPUSD Curncy'    # GBP/USD spot
'USDCHF Curncy'    # USD/CHF spot
'AUDUSD Curncy'    # AUD/USD spot
'USDCAD Curncy'    # USD/CAD spot
'USDCNH Curncy'    # USD/CNH (offshore RMB)
'USDKRW Curncy'    # USD/KRW
'USDBRL Curncy'    # USD/BRL
'USDMXN Curncy'    # USD/MXN
```

### FX Forwards — Tenor-Based
```python
# Format: <CCY PAIR><TENOR> Curncy  (e.g. EUR1M, GBP3M)
'EURUSD1M Curncy'  # EUR/USD 1-month forward
'EURUSD3M Curncy'  # EUR/USD 3-month forward
'EURUSD1Y Curncy'  # EUR/USD 1-year forward
```

### FX Implied Vols
```python
'EURUSDV1M Curncy'   # EUR/USD 1M ATM vol
'EURUSDV3M Curncy'   # EUR/USD 3M ATM vol
'EURUSD25R1M Curncy' # EUR/USD 1M 25D risk reversal
'EURUSD25B1M Curncy' # EUR/USD 1M 25D butterfly
```

---

## Futures Tickers

### Generic (Rolling) Futures
Format: `<ROOT><N> <YK>` where N=1 (front), 2 (second), etc.
```python
# Equities
'ES1 Index'         # S&P 500 futures, front month
'ES2 Index'         # S&P 500 futures, second month
'NQ1 Index'         # Nasdaq 100 futures
'VX1 Index'         # VIX futures front month

# Commodities
'CL1 Comdty'        # WTI crude oil front
'CO1 Comdty'        # Brent crude oil front
'GC1 Comdty'        # Gold front
'SI1 Comdty'        # Silver front
'NG1 Comdty'        # Natural gas front
'HG1 Comdty'        # Copper front

# Rates/Bonds
'TY1 Comdty'        # 10yr US T-Note futures
'FV1 Comdty'        # 5yr US T-Note futures
'TU1 Comdty'        # 2yr US T-Note futures
'WN1 Comdty'        # 30yr US T-Bond futures
'RX1 Comdty'        # Euro Bund futures
'G 1 Comdty'        # UK Gilt futures

# FX Futures
'EC1 Curncy'        # EUR/USD futures front
'JY1 Curncy'        # JPY futures front
```

### Specific (Non-Rolling) Contracts
Format: `<ROOT><MONTH_CODE><YY>` e.g. `ESH25 Index`

Month codes: F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun, N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec

```python
'ESH25 Index'       # S&P 500 Mar 2025
'CLZ24 Comdty'      # WTI Dec 2024

# Resolve generic → specific using xbbg utility
blp.fut_ticker('ES1 Index', '2024-01-15', freq='ME')   # → 'ESH24 Index'
blp.active_futures('ESA Index', '2024-01-15')           # volume-based selection
```

---

## Credit / CDX Tickers

```python
# CDX Generic
'CDX IG CDSI GEN 5Y Corp'     # CDX IG on-the-run 5yr
'CDX HY CDSI GEN 5Y Corp'     # CDX HY on-the-run 5yr
'ITRAXX EUROPE CDSI GEN 5Y Corp' # iTraxx Europe 5yr

# CDX Specific (Series)
'CDX IG CDSI S45 5Y Corp'     # CDX IG Series 45

# Resolve generic → specific series
blp.cdx_ticker('CDX IG CDSI GEN 5Y Corp', '2024-01-15')
blp.active_cdx('CDX IG CDSI GEN 5Y Corp', '2024-01-15')
```

---

## Ticker Lookup Utilities

```python
# Search by company name
blp.lookupSecurity('Apple', yellowkey='eqty', max_results=10)
blp.lookupSecurity('Goldman', yellowkey='eqty', max_results=5)

# Yellowkey options: 'eqty', 'bond', 'crncy', 'comdty', 'index', 'muni', 'pfd', 'mmkt'

# Verify a ticker is valid
result = blp.bdp('AAPL US Equity', 'PX_LAST')
# If returns empty DataFrame → ticker not found or no entitlement

# Get exchange timezone for intraday operations
blp.exchange_tz('AAPL US Equity')     # → 'America/New_York'
blp.exchange_tz('7974 JT Equity')     # → 'Asia/Tokyo'
blp.exchange_tz('BHP AU Equity')      # → 'Australia/Sydney'
blp.exchange_tz('SHEL LN Equity')     # → 'Europe/London'
```

---

## Common Ticker Pitfalls

| Mistake | Correct | Wrong |
|---|---|---|
| Missing exchange code | `AAPL US Equity` | `AAPL Equity` |
| Missing yellow key | `SPX Index` | `SPX` |
| Wrong yellow key | `EURUSD Curncy` | `EURUSD Equity` |
| Futures with wrong YK | `ES1 Index` | `ES1 Equity` |
| OTC bond missing coupon/maturity | `AAPL 3.85 5/4/43 Corp` | `AAPL Corp` |
| Using Yahoo format | `AAPL US Equity` | `AAPL` |
| Wrong month code | `ESH25 Index` | `ES032025 Index` |
