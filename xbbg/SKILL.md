# /xbbg — Bloomberg API Skill (xbbg Python Library)

## Skill Metadata
- **Trigger**: Activate when user mentions `xbbg`, `Bloomberg data`, `BDP`, `BDH`, `BDS`, `BEQS`,
  `Bloomberg terminal`, `Bloomberg API`, `blpapi`, or financial data pull via Python Bloomberg.
- **Tested versions**: xbbg `1.0.0a1` (Rust-based, recommended) | xbbg `0.7.x` (pure-Python legacy)
- **References**: See `references/field-reference.md`, `references/ticker-formats.md`, `references/override-cheatsheet.md`, `references/data-pipeline-validation.md`
- **Tests**: See `tests/test_xbbg_skill.py`

---

## Version Compatibility

| xbbg version | Branch | Architecture | Python | blpapi | Status |
|---|---|---|---|---|---|
| `1.0.0a1`+ | `main` | Rust core + async-first | 3.10–3.14 | 3.12.1+ | **Recommended** |
| `0.8.x` | `release/0.x` | Pure Python | 3.9+ | 3.8+ | Common in production |
| `0.7.x` | `release/0.x` | Pure Python | 3.8+ | 3.8+ | Legacy, stable |
| `< 0.7` | archived | Pure Python | 3.6+ | 3.8+ | Do not use |

### Critical v0.x vs v1.x Differences

| Feature | v0.x (0.7–0.8) | v1.x (current) |
|---|---|---|
| Intraday function | `bdib()` ✅ | `bdib()` ✅ |
| Async support | ❌ None | ✅ `abdp()`, `abdh()`, `abdib()` |
| Multi-backend | pandas only | pandas, polars, pyarrow, duckdb |
| Output format | MultiIndex (tickers × fields) | Configurable: `Format.WIDE`, `Format.LONG` |
| Real-time | `live()`, `subscribe()` ✅ | `live()`, `subscribe()`, `stream()` |
| Overrides | `ovrds={}` dict | Keyword args (preferred) or dict |
| `exchange_tz()` | ❌ Not available | ✅ v1.x only |
| `yas()` / `blp.yas` | ❌ Not in `blp` | ✅ v1.x only (use `bds` + `YLD_YTM_MID` in v0.x) |
| `fieldSearch()` / `lookupSecurity()` | ❌ Not in `blp` | ✅ v1.x only |
| `etf_holdings()` | ❌ Not in `blp` | ✅ v1.x only |
| `bflds()` / `fieldInfo()` | ❌ Not in `blp` | ✅ v1.x only |

### v0.8.x Available Functions (production baseline)
```python
# Functions confirmed in xbbg 0.8.x blp module:
# active_cdx, active_futures, adjust_ccy, bdh, bdib, bdp, bds, bdtick,
# beqs, bql, bsrch, cdx_ticker, connect, dividend, earning,
# fut_ticker, live, subscribe, turnover
```

> **⚠️ Version Guard**: Throughout this skill, functions marked `# v1.x only` are NOT
> available in xbbg 0.7.x or 0.8.x. On those versions, use the v0.x alternative shown
> or fall back to `blp.bdp(ticker, 'FIELD_NAME')` directly.

```python
import xbbg
print(xbbg.__version__)   # Always log version — API changes between releases
```

---

## Installation & Setup

```python
# Install (requires Bloomberg Terminal running on localhost:8194)
pip install xbbg
pip install blpapi --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/

# Optional: copy blpapi3_64.dll to BLPAPI_ROOT (Bloomberg's blp/DAPI folder)

# Remote Bloomberg server
from xbbg import blp
kwargs = {'server': '192.168.1.100', 'port': 18194}
blp.bdp('AAPL US Equity', 'PX_LAST', **kwargs)

# Cache location for intraday data (Parquet)
import os
os.environ['BBG_ROOT'] = 'C:/data/bbg_cache'  # set before import
```

---

## Quick Reference Cheat Sheet

| Function | Use Case | Returns |
|---|---|---|
| `blp.bdp(tickers, flds)` | Current/reference snapshot | `DataFrame` (tickers × fields) |
| `blp.bdh(tickers, flds, start, end)` | Historical time series | `DataFrame` (dates × tickers/fields) |
| `blp.bds(ticker, fld)` | Bulk/tabular data | `DataFrame` (rows of data) |
| `blp.beqs(screen, asof)` | Equity screen results | `DataFrame` (securities) |
| `blp.bdib(ticker, dt)` | Intraday OHLCV bars | `DataFrame` (time × OHLCV) |
| `blp.bdtick(ticker, dt)` | Tick-by-tick data | `DataFrame` (trades/quotes) |
| `blp.live(tickers, flds)` | Real-time streaming | Async context manager |
| `blp.subscribe(tickers, flds, callback)` | Real-time subscription | Event callbacks |
| `blp.yas(ticker)` | YAS fixed income analytics | `DataFrame` (bond analytics) |
| `blp.dividend(tickers, ...)` | Dividend/split history | `DataFrame` |
| `blp.earning(ticker, ...)` | Earnings breakdown | `DataFrame` |
| `blp.fut_ticker(ticker, dt)` | Resolve futures contract | `str` |
| `blp.active_futures(ticker, dt)` | Volume-based front contract | `str` |
| `blp.adjust_ccy(df, ccy)` | Currency conversion | `DataFrame` |
| `blp.exchange_tz(ticker)` | Exchange timezone | `str` (IANA tz) | **v1.x only** |
| `blp.fieldSearch(keyword)` | Find fields by keyword | `DataFrame` | **v1.x only** |
| `blp.lookupSecurity(name)` | Find tickers by name | `DataFrame` | **v1.x only** |

### Async Counterparts (v1.x only — not available in v0.8.x)
| Sync | Async |
|---|---|
| `bdp()` | `abdp()` |
| `bdh()` | `abdh()` |
| `bds()` | `abds()` |
| `bdib()` | `abdib()` |

---

## 1. Static Reference Data — `bdp()`

```python
from xbbg import blp

# Single ticker, single field
blp.bdp('AAPL US Equity', 'PX_LAST')
# Out:
#                px_last
# AAPL US Equity  182.63

# Single ticker, multiple fields
blp.bdp('NVDA US Equity', ['Security_Name', 'GICS_Sector_Name', 'CUR_MKT_CAP'])
# Out:
#                security_name        gics_sector_name  cur_mkt_cap
# NVDA US Equity   NVIDIA Corp  Information Technology  2241839.50

# Multiple tickers, multiple fields
blp.bdp(
    ['AAPL US Equity', 'MSFT US Equity', 'GOOGL US Equity'],
    ['PX_LAST', 'PE_RATIO', 'EQY_DVD_YLD_IND', 'CUR_MKT_CAP']
)

# With keyword override (e.g. VWAP for specific date)
blp.bdp('AAPL US Equity', 'Eqy_Weighted_Avg_Px', VWAP_Dt='20240115')

# Using ISIN (fixed income / cross-asset)
blp.bdp('/isin/US0378331005', ['Security_Name', 'PX_LAST'])

    # Field search before querying (v1.x only — use Bloomberg terminal FLDS<GO> in v0.x)
    blp.fieldSearch('earnings yield')   # v1.x only
    blp.bflds(fields=['PE_RATIO'])       # v1.x only
```

### bdp Output Shape
- **Single ticker**: `(1, n_fields)` DataFrame, index = ticker
- **Multiple tickers**: `(n_tickers, n_fields)` DataFrame, index = tickers
- **Columns**: lowercase field names (Bloomberg normalises case)

### bdp N/A Handling
```python
import pandas as pd
result = blp.bdp(tickers, flds)

# Bloomberg returns N/A for missing/unavailable fields — xbbg maps these to NaN
result = result.replace('N/A', float('nan'))   # belt-and-suspenders
result = result.dropna(how='all')              # drop completely empty rows

# Check which securities returned no data
empty = result[result.isna().all(axis=1)]
if not empty.empty:
    print(f"No data for: {empty.index.tolist()}")
```

---

## 2. Historical Time Series — `bdh()`

```python
from xbbg import blp

# Simple daily close
blp.bdh('SPX Index', 'PX_LAST', '2024-01-01', '2024-12-31')
# Out:
#            SPX Index
#            last_price
# 2024-01-02   4742.83
# 2024-01-03   4697.24

# OHLCV for equities
blp.bdh('AAPL US Equity', ['open', 'high', 'low', 'close', 'volume'],
        '2024-01-01', '2024-01-31')

# Multiple tickers (output is wide format with ticker-level MultiIndex on columns)
blp.bdh(
    ['AAPL US Equity', 'MSFT US Equity'],
    ['px_last', 'volume'],
    start_date='2024-01-01', end_date='2024-01-10'
)
# Out:
#            AAPL US Equity             MSFT US Equity
#                   px_last      volume        px_last      volume
# 2024-01-02         185.85  45000000.0         375.28  20000000.0

# Fully adjusted prices for backtesting
blp.bdh('AAPL US Equity', 'px_last', '2010-01-01', '2024-12-31', adjust='all')

# Weekly with forward fill
blp.bdh('SPX Index', 'PX_LAST', '2024-01-01', '2024-12-31', Per='W', Fill='P')

# Monthly with all calendar days
blp.bdh('USGG10YR Index', 'PX_LAST', '2000-01-01', '2024-12-31', Per='M', Days='A')
```

### bdh Periodicity Options
| `Per` | Meaning |
|---|---|
| `'D'` | Daily (default) |
| `'W'` | Weekly |
| `'M'` | Monthly |
| `'Q'` | Quarterly |
| `'S'` | Semi-annual |
| `'Y'` | Yearly |

### bdh Fill Options
| `Fill` | Meaning |
|---|---|
| `'A'` | All dates returned |
| `'B'` | Back-fill from previous trading day |
| `'F'` | Forward-fill from next trading day |
| `'P'` | Previous value carry (most common) |

### ⚠️ Critical: bdh Output Shape Depends on Number of Tickers

> **Single ticker → FLAT columns** (DatetimeIndex × field names — NO MultiIndex)
> **Multiple tickers → MultiIndex columns** (level 0 = ticker, level 1 = field)
> This difference is the #1 source of silent bugs when switching from 1 security to N.

```python
# SINGLE ticker: flat columns
df = blp.bdh('AAPL US Equity', ['px_last', 'volume'], '2024-01-01', '2024-01-31')
df.columns           # Index(['px_last', 'volume'], dtype='object')  ← flat
df['px_last']        # works

# MULTIPLE tickers: MultiIndex columns (ticker, field)
df = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], 'px_last', '2024-01-01', '2024-01-31')
df.columns           # MultiIndex([('AAPL US Equity','px_last'), ('MSFT US Equity','px_last')])
df['px_last']        # KeyError! ← common crash when switching from single to multi
```

### Flattening the MultiIndex (Multiple Tickers)
```python
# bdh with multiple tickers returns MultiIndex columns: (ticker, field)
df = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], 'px_last',
             '2024-01-01', '2024-12-31')

# Method 1: droplevel — when there's only one field
prices = df.droplevel(1, axis=1)
# Columns: ['AAPL US Equity', 'MSFT US Equity']

# Method 2: xs — cross-section for a specific ticker
aapl = df.xs('AAPL US Equity', axis=1, level=0)

# Method 3: stack for tidy/long format
long = df.stack(level=0).reset_index()
long.columns = ['date', 'ticker', 'px_last']

# Method 4: pivot from long format
pivot = long.pivot(index='date', columns='ticker', values='px_last')

# Method 5: use Format.LONG (xbbg v1 native)
from xbbg import blp, Format
df_long = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], 'px_last',
                  '2024-01-01', '2024-12-31', format=Format.LONG)
# Columns: ticker, field, date, value
```

---

## 3. Bulk / Tabular Reference Data — `bds()`

```python
from xbbg import blp

# Dividend history
blp.bds('AAPL US Equity', 'DVD_Hist_All',
        DVD_Start_Dt='20230101', DVD_End_Dt='20231231')
# Out:
#                declared_date     ex_date  dividend_amount dividend_frequency
# AAPL US Equity    2023-02-02  2023-02-10             0.23            Quarter

# Bond cash flow schedule (via ISIN)
blp.bds('/isin/US037833AK68', 'DES_CASH_FLOW', SETTLE_DT='20240301')
# Out:
#                      payment_date  coupon_amount  principal_amount
# /isin/US037833AK68     2025-05-04         1625.0               0.0

# Index constituents (current)
blp.bds('SPX Index', 'INDX_MEMBERS')
# Out:
#            member_ticker_and_exchange_code
# SPX Index  AAPL US Equity
# SPX Index  MSFT US Equity ...

# Index weights (current)
blp.bds('SPX Index', 'INDX_MWEIGHT')

# Historical index membership as of date
blp.bds('SPX Index', 'INDX_MWEIGHT_HIST', END_DATE_OVERRIDE='20230101')

# Option chain (calls expiring Jan 2025)
blp.bds('AAPL US Equity', 'OPT_CHAIN', Expiry_Dt='20250117', OPT_PUT_CALL='Call')

# ETF holdings (easier alternative: use blp.etf_holdings)
blp.etf_holdings('SPY US Equity')
```

### bds Output Shape
- Returns a `DataFrame` with one row per bulk data item
- Ticker appears as the index (may be repeated for multi-row results)
- Column names are field-specific (Bloomberg defines the schema)

---

## 4. Equity Screening — `beqs()`

```python
from xbbg import blp

# Run a saved Bloomberg equity screen
blp.beqs(screen='MyValueScreen', asof='2024-01-01')
# Returns: DataFrame with matching securities

# Public screens (Bloomberg-provided)
blp.beqs(screen='TOTAL_RETURN_SCREEN', screen_type='PUBLIC')

# Usage pattern: screen → pull fundamentals
screen_results = blp.beqs(screen='MyScreen', asof='2024-01-01')
tickers = screen_results.index.tolist()
fundamentals = blp.bdp(tickers, ['PX_LAST', 'PE_RATIO', 'CUR_MKT_CAP'])
```

---

## 5. Intraday Bars — `bdib()`

> **Note**: The correct function name is `bdib()`, NOT `bdhd()`. Use `bdib` in all code.

```python
from xbbg import blp

# 1-minute bars (default) — returns exchange-local timezone
blp.bdib(ticker='AAPL US Equity', dt='2024-01-15')
# Out (MultiIndex columns: ticker → OHLCV):
#                           AAPL US Equity
#                                    open    high     low   close  volume  num_trds
# 2024-01-15 09:31:00-05:00        185.25  185.45  185.10  185.30   52000       340

# 5-minute bars
blp.bdib('SPY US Equity', dt='2024-01-15', interval=5)

# 30-minute bars
blp.bdib('ES1 Index', dt='2024-01-15', interval=30)

# Sub-minute: 10-second bars (xbbg unique feature)
blp.bdib('AAPL US Equity', dt='2024-01-15', interval=10, intervalHasSeconds=True)

# Session filtering
blp.bdib('SPY US Equity', dt='2024-01-15', session='day')            # regular hours
blp.bdib('SPY US Equity', dt='2024-01-15', session='day_open_30')    # first 30 min
blp.bdib('SPY US Equity', dt='2024-01-15', session='day_close_20')   # last 20 min
blp.bdib('SPY US Equity', dt='2024-01-15', session='allday')         # pre+regular+post
blp.bdib('7974 JT Equity', dt='2024-01-15', session='am')            # Tokyo AM session
blp.bdib('7974 JT Equity', dt='2024-01-15', session='am_open_30')    # Tokyo AM first 30min

# UTC output instead of exchange local
blp.bdib('SPY US Equity', dt='2024-01-15', tz='UTC')

# Reference exchange for timezone resolution (e.g. rolled futures)
blp.bdib('ESM0 Index', dt='2024-01-15', ref='ES1 Index')

# Disable automatic Parquet cache
blp.bdib('AAPL US Equity', dt='2024-01-15', cache=False)

# Force reload even if cached
blp.bdib('AAPL US Equity', dt='2024-01-15', reload=True)

# Look up exchange timezone — v1.x only; not in v0.8.x
blp.exchange_tz('AAPL US Equity')    # → 'America/New_York'  # v1.x only
blp.exchange_tz('BHP AU Equity')     # → 'Australia/Sydney'  # v1.x only
blp.exchange_tz('7974 JT Equity')    # → 'Asia/Tokyo'        # v1.x only
# v0.x: hardcode from IANA tz list or use pandas_market_calendars.get_calendar()
```

### bdib Session Names
| Session | Description |
|---|---|
| `'allday'` | Full day including pre/post market |
| `'day'` | Regular trading hours |
| `'pre'` | Pre-market |
| `'post'` | Post-market |
| `'am'` | Morning session (Asian markets with 2 sessions) |
| `'pm'` | Afternoon session |
| `'night'` | Night session (ASX futures etc.) |
| `'day_open_N'` | First N minutes of regular session |
| `'day_close_N'` | Last N minutes of regular session |
| `'am_open_N'` | First N minutes of AM session |
| `'day_normal_N_M'` | Skip first N and last M minutes |
| `'day_exact_HHMM_HHMM'` | Exact time window in exchange local time |

### Intraday Caching
```python
# xbbg automatically caches bdib() data as Parquet in:
# Windows: %APPDATA%\xbbg\{asset_class}\{ticker}\TRADE\{interval}\{date}.parq
# Custom: set BBG_ROOT env var before import

import os
os.environ['BBG_ROOT'] = 'D:/data/bbg'  # must be set BEFORE 'from xbbg import blp'
from xbbg import blp

# Cache is only written for past (completed) sessions — never for today's partial day
```

---

## 6. Tick-by-Tick Data — `bdtick()`

```python
from xbbg import blp

# All ticks (trades + quotes) for a session
blp.bdtick(ticker='AAPL US Equity', dt='2024-01-15', session='day')

# Trade events only
blp.bdtick(ticker='AAPL US Equity', dt='2024-01-15', session='day',
           types=['TRADE'])

# Quote events only
blp.bdtick(ticker='AAPL US Equity', dt='2024-01-15', session='day',
           types=['BID', 'ASK'])

# With timeout (milliseconds) — increase for large requests
blp.bdtick(ticker='AAPL US Equity', dt='2024-01-15', timeout=5000)

# bdtick output columns:
# value, volume, typ (TRADE/BID/ASK), cond (condition code), exch, trd_time
```

---

## 7. Real-Time Streaming — `live()` / `subscribe()` / `stream()`

> **v0.8.x**: `live()` and `subscribe()` available. `stream()` is **v1.x only**.

```python
import asyncio
from xbbg import blp

# --- Pattern 1: Async context manager (cleanest) ---
async def monitor_prices():
    async with blp.live(['AAPL US Equity', 'MSFT US Equity'],
                        ['LAST_PRICE', 'BID', 'ASK']) as stream:
        async for update in stream:
            print(update)
            # update is a dict: {'ticker': ..., 'field': ..., 'value': ...}

asyncio.run(monitor_prices())

# --- Pattern 2: subscribe() with callback ---
def on_update(event):
    """Called on every field update."""
    print(f"{event['ticker']}: {event['field']} = {event['value']}")

blp.subscribe(
    ['AAPL US Equity', 'MSFT US Equity'],
    ['LAST_PRICE', 'BID', 'ASK'],
    callback=on_update
)

# Subscribe with update interval (seconds)
blp.subscribe(['AAPL US Equity'], interval=10)   # throttle to 10-second updates

# --- Pattern 3: stream() — modern async generator ---
async def stream_data():
    async for update in blp.stream(['AAPL US Equity'], ['LAST_PRICE']):
        print(update)
        if should_stop():
            break

# --- Jupyter notebook: use await directly ---
# async with blp.live(['AAPL US Equity'], ['LAST_PRICE']) as stream:
#     async for update in stream:
#         print(update)
```

### Real-Time Common Fields
```python
['LAST_PRICE', 'BID', 'ASK', 'BID_SIZE', 'ASK_SIZE', 'VOLUME',
 'TRADE_UPDATE_STAMP_RT', 'RT_PX_CHG_NET_1D', 'RT_PX_CHG_PCT_1D']
```

---

## 8. Fixed Income Analytics — `yas()`

> **v1.x only** — `blp.yas()` does not exist in xbbg 0.7.x or 0.8.x.
> **v0.x alternative**: Use `blp.bdp(ticker, 'YLD_YTM_MID')` for yield,
> `blp.bdp(ticker, ['DUR_MID', 'CONVEXITY_MID', 'DV01'])` for risk metrics.

```python
from xbbg import blp
from xbbg.api.fixed_income import YieldType  # v1.x only

# YTM (default)
blp.yas('T 4.5 5/15/38 Govt')
# Out:    YAS_BOND_YLD
# ticker
# T 4.5..      4.348

# Multiple analytics
blp.yas('T 4.5 5/15/38 Govt', ['YAS_BOND_YLD', 'YAS_MOD_DUR', 'YAS_ASW_SPREAD'])

# Price from yield
blp.yas('T 4.5 5/15/38 Govt', flds='YAS_BOND_PX', yield_=4.8)

# Yield from price
blp.yas('T 4.5 5/15/38 Govt', price=95.0)

# Yield to call
blp.yas('AAPL 2.65 5/11/50 Corp', yield_type=YieldType.YTC)

# With settlement date
blp.yas('T 4.5 5/15/38 Govt', settle_dt='20240315')

# Spread to benchmark
blp.yas('AAPL 3.85 5/4/43 Corp', benchmark='T 4.5 5/15/38 Govt',
        flds='YAS_ISPREAD_TO_GOVT')
```

### Extended Bond Analytics — `xbbg.ext` (v1.x only)

> **v1.x only** — `xbbg.ext` module does not exist in v0.x.
> **v0.x alternative**: Use `blp.bdp(ticker, ['MATURITY','COUPON','RTG_SP','DUR_MID'])` directly.

```python
from xbbg.ext import bond_info, bond_risk, bond_spreads, bond_cashflows  # v1.x only

bond_info('T 4.5 5/15/38 Govt')          # ratings, maturity, coupon, amount
bond_risk('T 4.5 5/15/38 Govt')          # modified duration, convexity, DV01
bond_spreads('AAPL 3.85 5/4/43 Corp')    # OAS, Z-spread, I-spread, ASW
bond_cashflows('T 4.5 5/15/38 Govt')     # coupon + principal schedule
```

---

## 9. Options Analytics

> **`xbbg.ext` is v1.x only.** In v0.x, use `blp.bds(ticker, 'OPT_CHAIN')` +
> `blp.bdp(option_tickers, ['DELTA_MID_RT', 'IVOL_MID', 'OPT_STRIKE_PX'])` directly.

```python
from xbbg.ext import option_info, option_greeks, option_chain, option_chain_bql  # v1.x only

# Single option contract
option_info('AAPL US 01/17/25 C200 Equity')    # strike, expiry, type, underlying
option_greeks('AAPL US 01/17/25 C200 Equity')  # delta, gamma, theta, vega, IV

# Option chain — all strikes for one expiry
chain = option_chain('AAPL US Equity')          # via CHAIN_TICKERS override
chain_bql = option_chain_bql('AAPL US Equity', expiry='2025-01-17')

# SPX options open interest by expiry (BQL example)
# blp.bql("get(sum(group(open_int))) for(filter(options('SPX Index'), expire_dt=='2025-01-17'))")
```

---

## 10. Async Operations (v1.x only — NOT available in v0.8.x)

```python
import asyncio
from xbbg import blp

# Single async call
async def get_data():
    return await blp.abdp('AAPL US Equity', ['PX_LAST', 'PE_RATIO'])

data = asyncio.run(get_data())

# Parallel concurrent requests (fastest pattern for large universes)
async def get_universe_data(tickers, flds):
    tasks = [blp.abdp(t, flds) for t in tickers]
    results = await asyncio.gather(*tasks)
    import pandas as pd
    return pd.concat(results)

# In Jupyter — just use await directly
# df = await blp.abdp('AAPL US Equity', ['PX_LAST'])

# Historical + reference in parallel
async def combined():
    hist, ref = await asyncio.gather(
        blp.abdh('AAPL US Equity', 'PX_LAST', '2024-01-01', '2024-12-31'),
        blp.abdp('AAPL US Equity', ['PE_RATIO', 'CUR_MKT_CAP'])
    )
    return hist, ref
```

---

## 11. Multi-Backend Output (v1.x only — NOT available in v0.8.x)

```python
from xbbg import blp, Backend, Format

# Output as Polars DataFrame (10-100x faster for large data)
df_polars = blp.bdp('AAPL US Equity', 'PX_LAST', backend=Backend.POLARS)

# Output as PyArrow Table (zero-copy, memory efficient)
table = blp.bdh('SPX Index', 'PX_LAST', '2024-01-01', '2024-12-31',
                backend=Backend.PYARROW)

# Output formats
df_long  = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], 'px_last',
                   '2024-01-01', '2024-12-31', format=Format.LONG)
# Columns: ticker, field, date, value

df_typed = blp.bdp(['AAPL US Equity', 'MSFT US Equity'],
                   ['PX_LAST', 'PE_RATIO'], format=Format.LONG_TYPED)
# Type-safe: separate value columns per dtype, no casting needed

# Set session-wide defaults
from xbbg import set_backend, set_format
set_backend(Backend.POLARS)
set_format(Format.LONG)

# Check available backends
from xbbg import get_available_backends
print(get_available_backends())  # ['pandas', 'polars', 'pyarrow', ...]
```

### Output Format Summary
| Format | Shape | Best For |
|---|---|---|
| `Format.WIDE` | tickers as columns | Time series alignment, Excel-like |
| `Format.LONG` | ticker, field, value columns | Analysis, joins, aggregations |
| `Format.LONG_TYPED` | typed value columns by dtype | Type-safe analysis |
| `Format.LONG_METADATA` | string values + dtype column | Serialization, debugging |
| `Format.SEMI_LONG` | one row per ticker | Quick inspection |

---

## 12. Pandas Integration Patterns

### Flattening MultiIndex (Wide Format)

```python
import pandas as pd
from xbbg import blp

tickers = ['AAPL US Equity', 'MSFT US Equity', 'GOOGL US Equity']

# bdh returns MultiIndex columns: (ticker, field)
df = blp.bdh(tickers, 'px_last', '2024-01-01', '2024-12-31')

# --- Extract clean price matrix ---
prices = df.droplevel(1, axis=1)          # drop field level (when single field)
prices.columns.name = None               # remove 'ticker' label from column axis

# --- Compute log returns ---
import numpy as np
returns = np.log(prices / prices.shift(1)).dropna()

# --- Compute correlation matrix ---
corr = returns.corr()

# --- Resample to monthly ---
monthly = prices.resample('ME').last()

# --- bdp result: straightforward tickers × fields ---
fundamentals = blp.bdp(tickers, ['PE_RATIO', 'EV_EBITDA', 'CUR_MKT_CAP'])
# fundamentals.index → ticker names
# fundamentals['pe_ratio'] → Series of P/E values

# --- Handle mixed dtypes from bdp ---
fundamentals['pe_ratio'] = pd.to_numeric(fundamentals['pe_ratio'], errors='coerce')
```

### Time Zone Handling

```python
import pandas as pd
from xbbg import blp
import pandas_market_calendars as mcal

# bdib returns exchange-local tz-aware timestamps
bars = blp.bdib('AAPL US Equity', dt='2024-01-15')
print(bars.index.tz)  # America/New_York

# Convert to UTC
bars_utc = bars.tz_convert('UTC')

# Convert to another timezone
bars_london = bars.tz_convert('Europe/London')

# Business day calendar for a market
nyse = mcal.get_calendar('NYSE')
trading_days = nyse.valid_days(start_date='2024-01-01', end_date='2024-12-31')

# Filter history to trading days only
df = blp.bdh('SPX Index', 'PX_LAST', '2024-01-01', '2024-12-31')
df = df[df.index.isin(trading_days)]

# Bloomberg date input formats (all accepted by xbbg):
# '2024-01-15', '20240115', datetime.date(2024, 1, 15), pd.Timestamp('2024-01-15')
```

---

## 13. Batching & Performance

### Security Batching (large universes)

```python
import math
import time
import pandas as pd
from xbbg import blp

def batch_bdp(tickers: list, flds: list, batch_size: int = 500) -> pd.DataFrame:
    """Pull bdp in batches — Bloomberg limit ~1000 securities per request."""
    results = []
    n_batches = math.ceil(len(tickers) / batch_size)
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"Batch {batch_num}/{n_batches}: {len(batch)} securities")
        try:
            data = blp.bdp(batch, flds)
            results.append(data)
        except Exception as exc:
            print(f"  Batch {batch_num} failed: {exc}")
            time.sleep(2 ** batch_num)   # exponential backoff
    return pd.concat(results) if results else pd.DataFrame()


def batch_bdh(ticker: str, flds, start: str, end: str,
              chunk_months: int = 12) -> pd.DataFrame:
    """Chunk long historical pulls by date to avoid timeouts."""
    from dateutil.relativedelta import relativedelta  # pip install python-dateutil
    chunks = []
    cur = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    while cur < end_ts:
        chunk_end = min(cur + relativedelta(months=chunk_months), end_ts)
        data = blp.bdh(ticker, flds,
                       start_date=cur.strftime('%Y-%m-%d'),
                       end_date=chunk_end.strftime('%Y-%m-%d'))
        chunks.append(data)
        cur = chunk_end
    return pd.concat(chunks).sort_index() if chunks else pd.DataFrame()
```

### Concurrent Requests (asyncio)

```python
import asyncio
import pandas as pd
from xbbg import blp

async def parallel_bdp(universe: list[str], flds: list[str],
                       batch_size: int = 200) -> pd.DataFrame:
    """Concurrent bdp using asyncio.gather — fastest for large universes."""
    batches = [universe[i:i+batch_size] for i in range(0, len(universe), batch_size)]
    tasks = [blp.abdp(batch, flds) for batch in batches]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Filter out exceptions
    valid = [r for r in results if isinstance(r, pd.DataFrame)]
    return pd.concat(valid) if valid else pd.DataFrame()

# Usage
universe = ['AAPL US Equity', 'MSFT US Equity', ...]  # thousands of tickers
df = asyncio.run(parallel_bdp(universe, ['PX_LAST', 'PE_RATIO']))
```

### ThreadPoolExecutor (v0.x compatible)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from xbbg import blp

def fetch_ticker_bdh(ticker, flds, start, end):
    return ticker, blp.bdh(ticker, flds, start, end)

def parallel_bdh(tickers, flds, start, end, max_workers=4):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_ticker_bdh, t, flds, start, end): t
                   for t in tickers}
        for future in as_completed(futures):
            ticker, data = future.result()
            results[ticker] = data
    return results
```

---

## 14. Caching Strategy

```python
import os
import pandas as pd
from pathlib import Path
import joblib
from xbbg import blp

# --- Pattern 1: joblib.Memory (recommended for reference data) ---
from joblib import Memory
cache_dir = Path('C:/data/bbg_cache')
memory = Memory(cache_dir, verbose=0)

@memory.cache
def cached_bdp(tickers_tuple: tuple, flds_tuple: tuple) -> pd.DataFrame:
    return blp.bdp(list(tickers_tuple), list(flds_tuple))

# Usage (must use hashable args for joblib)
data = cached_bdp(
    ('AAPL US Equity', 'MSFT US Equity'),
    ('PX_LAST', 'PE_RATIO')
)

# --- Pattern 2: Parquet for historical data ---
def load_or_fetch_bdh(ticker, flds, start, end, cache_dir='C:/data/bbg'):
    cache_file = Path(cache_dir) / f"{ticker.replace(' ', '_')}_{start}_{end}.parquet"
    if cache_file.exists():
        return pd.read_parquet(cache_file)
    df = blp.bdh(ticker, flds, start, end)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_file)
    return df

# --- Pattern 3: Large universe → chunk to Parquet incrementally ---
def incremental_universe_bdh(tickers, flds, start, end, out_dir='C:/data/bbg',
                              batch_size=50):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    all_files = []
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        fname = out / f"batch_{i//batch_size:04d}.parquet"
        if not fname.exists():
            df = blp.bdh(batch, flds, start, end)
            df.to_parquet(fname)
        all_files.append(fname)
    return pd.concat([pd.read_parquet(f) for f in all_files])

# --- Pattern 4: xbbg built-in bdib cache ---
# bdib() automatically caches as Parquet — no extra code needed
# Set BBG_ROOT before import to control location
os.environ['BBG_ROOT'] = 'D:/data/bbg'
```

---

## 15. Error Handling

```python
import time
import logging
from xbbg import blp

logger = logging.getLogger('xbbg')
logging.basicConfig(level=logging.INFO)

# Enable xbbg debug logging for troubleshooting
# logging.getLogger('xbbg').setLevel(logging.DEBUG)

# --- Error taxonomy ---
# ConnectionError / OSError      → Bloomberg Terminal not running
# ValueError                     → Invalid ticker format, unknown field name
# PermissionError / entitlement  → No Bloomberg licence for this data
# TimeoutError                   → Request took too long (increase timeout)
# Returns empty DataFrame        → Ticker not found, no data for date range,
#                                   or timeout (especially for bdtick)

# --- Pattern 1: Retry with exponential backoff ---
def bbg_with_retry(fn, *args, max_retries=3, base_delay=1.0, **kwargs):
    """Retry any Bloomberg call with exponential backoff."""
    for attempt in range(max_retries):
        try:
            result = fn(*args, **kwargs)
            if result is not None and not (hasattr(result, 'empty') and result.empty):
                return result
        except (ConnectionError, OSError) as exc:
            logger.warning(f"Connection error (attempt {attempt+1}): {exc}")
        except Exception as exc:
            msg = str(exc).lower()
            if 'entitlement' in msg or 'permission' in msg:
                raise   # non-retryable
            logger.warning(f"Bloomberg error (attempt {attempt+1}): {exc}")
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            logger.info(f"Retrying in {delay:.1f}s...")
            time.sleep(delay)
    raise RuntimeError(f"Bloomberg call failed after {max_retries} retries")

# Usage
prices = bbg_with_retry(blp.bdp, 'AAPL US Equity', 'PX_LAST')

# --- Pattern 2: Per-security fallback ---
def safe_batch_bdp(tickers, flds):
    try:
        return blp.bdp(tickers, flds), []
    except Exception:
        results, failures = [], []
        for t in tickers:
            try:
                results.append(blp.bdp(t, flds))
            except Exception as exc:
                failures.append((t, str(exc)))
        return (pd.concat(results) if results else pd.DataFrame()), failures

# --- Pattern 3: Empty DataFrame guard ---
def validate_response(df, context=""):
    if df is None or (hasattr(df, 'empty') and df.empty):
        raise ValueError(f"Bloomberg returned empty response for: {context}")
    return df

data = validate_response(blp.bdp('AAPL US Equity', 'PX_LAST'), 'AAPL price')

# --- Pattern 4: Field availability check ---
def check_fields(tickers, flds):
    """Verify fields are available before batch pull."""
    sample = blp.bdp(tickers[0], flds)
    unavailable = sample.columns[sample.iloc[0].isna()].tolist()
    if unavailable:
        logger.warning(f"Fields not available for {tickers[0]}: {unavailable}")
    return [f for f in flds if f not in unavailable]
```

### Common Error → Fix Guide
| Symptom | Likely Cause | Fix |
|---|---|---|
| Empty DataFrame | Terminal not running | Start Bloomberg Terminal |
| Empty DataFrame | Wrong ticker format | Use `AAPL US Equity` not `AAPL` |
| Empty DataFrame | No entitlement | Check Bloomberg subscription |
| Empty DataFrame | bdtick timeout | Add `timeout=5000` parameter |
| `ConnectionError` | blpapi not connecting | Check localhost:8194, restart terminal |
| `ValueError` | Unknown field | Use `blp.fieldSearch('keyword')` to find field |
| NaN everywhere | Holiday / non-trading day | Adjust date range |
| Stale data | Real-time data on weekend | Use `PX_LAST` not `LAST_PRICE_RT` |

---

## 16. Smart Bloomberg Dispatcher — `bbg()`

A single-entry-point function that auto-routes to the correct xbbg call, auto-chunks,
auto-flattens MultiIndex, and auto-retries. Use this as the canonical template in all recipes.

```python
import math
import time
import logging
import pandas as pd
from typing import Union
from xbbg import blp

logger = logging.getLogger(__name__)


def bbg(
    tickers: Union[str, list],
    flds: Union[str, list],
    start_date: str = None,
    end_date: str = None,
    per: str = 'D',
    fill: str = 'P',
    adjust: str = None,
    batch_size: int = 400,
    max_retries: int = 3,
    flat: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Smart Bloomberg Dispatcher.

    Auto-routes:
      - start_date provided → bdh() (historical time series)
      - no start_date       → bdp() (point-in-time reference)

    Features:
      - Auto-batches tickers in chunks of `batch_size`
      - Auto-flattens MultiIndex (single-field bdh → date × ticker DataFrame)
      - Auto-retries with exponential backoff
      - Pass-through kwargs to underlying xbbg function

    Args:
        tickers:    Single ticker string or list of tickers.
        flds:       Single field string or list of fields.
        start_date: If provided, calls bdh(); otherwise calls bdp().
        end_date:   End date for bdh() (default: today).
        per:        Periodicity for bdh() — 'D','W','M','Q','Y'.
        fill:       Fill method for bdh() — 'P','B','F','A'.
        adjust:     Adjustment for bdh() — 'all','dvd','split',None.
        batch_size: Max tickers per Bloomberg request.
        max_retries: Retry attempts on failure.
        flat:       Flatten single-field bdh MultiIndex → date × ticker.
        **kwargs:   Passed through to blp.bdp() or blp.bdh().

    Returns:
        pd.DataFrame: Clean, flat DataFrame ready for analysis.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    if isinstance(flds, str):
        flds = [flds]

    single_field = len(flds) == 1

    def _call(batch):
        for attempt in range(max_retries):
            try:
                if start_date is not None:
                    kw = dict(Per=per, Fill=fill)
                    if adjust:
                        kw['adjust'] = adjust
                    kw.update(kwargs)
                    return blp.bdh(batch, flds,
                                   start_date=start_date,
                                   end_date=end_date or pd.Timestamp.today().strftime('%Y-%m-%d'),
                                   **kw)
                else:
                    return blp.bdp(batch, flds, **kwargs)
            except Exception as exc:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt
                logger.warning(f"Bloomberg error (attempt {attempt+1}): {exc}. Retrying in {wait}s.")
                time.sleep(wait)

    # Batch and collect
    chunks = [tickers[i:i+batch_size] for i in range(0, len(tickers), batch_size)]
    results = [_call(chunk) for chunk in chunks]
    df = pd.concat(results)

    # Flatten MultiIndex for single-field bdh
    if start_date is not None and single_field and flat:
        try:
            df = df.droplevel(1, axis=1)
            df.columns.name = None
        except Exception:
            pass  # already flat or different structure

    return df


# Usage examples
# --- Reference snapshot ---
prices = bbg(['AAPL US Equity', 'MSFT US Equity'], 'PX_LAST')

# --- Adjusted daily history ---
hist = bbg(['AAPL US Equity', 'MSFT US Equity'], 'px_last',
           start_date='2020-01-01', end_date='2024-12-31', adjust='all')
# Returns: clean date × ticker DataFrame (no MultiIndex)

# --- Large universe factor pull ---
universe = [f'{t} US Equity' for t in ['AAPL', 'MSFT', 'GOOGL', 'AMZN']]  # hundreds
factors = bbg(universe, ['PE_RATIO', 'EV_EBITDA', 'BOOK_VAL_PER_SH'])

# --- Monthly with forward fill ---
monthly = bbg('SPX Index', 'PX_LAST',
              start_date='2010-01-01', end_date='2024-12-31',
              per='M', fill='P')
```

---

## 17. Trading Recipes

### Recipe 1: Build a Backtesting Universe

```python
# requires Bloomberg terminal
import pandas as pd
from xbbg import blp

def build_sp500_universe(as_of_date: str = None) -> pd.DataFrame:
    """Pull S&P 500 members + key fields as of a date."""
    if as_of_date:
        members_df = blp.bds('SPX Index', 'INDX_MWEIGHT_HIST',
                             END_DATE_OVERRIDE=as_of_date.replace('-', ''))
    else:
        members_df = blp.bds('SPX Index', 'INDX_MWEIGHT')

    # Extract tickers and weights
    members_df = members_df.reset_index(drop=True)
    tickers = members_df['member_ticker_and_exchange_code'].str.strip().tolist()
    weights = members_df.set_index('member_ticker_and_exchange_code').get(
        'percentage_weight', None)

    # Pull fundamentals in batch
    fundamentals = bbg(tickers, ['GICS_SECTOR_NAME', 'CUR_MKT_CAP', 'PX_LAST'])

    if weights is not None:
        fundamentals['weight'] = fundamentals.index.map(weights)

    return fundamentals.sort_values('cur_mkt_cap', ascending=False)

# Usage
universe = build_sp500_universe(as_of_date='2024-01-01')
print(f"Universe size: {len(universe)}")
```

### Recipe 2: Factor Data Download (Cross-Sectional)

```python
# requires Bloomberg terminal
import pandas as pd
import numpy as np
from xbbg import blp

FACTOR_FIELDS = [
    'PE_RATIO',            # Value
    'EV_EBITDA',           # Value
    'PX_TO_BOOK_RATIO',    # Value
    'RETURN_1YR',          # Momentum
    'VOLATILITY_90D',      # Risk
    'CUR_MKT_CAP',         # Size
    'SHORT_INT_PCT_OF_FLOAT_RT',  # Short interest
    'EARN_PER_SH',         # Quality
    'RETURN_ON_EQUITY',    # Quality
]

def factor_snapshot(tickers: list) -> pd.DataFrame:
    """Pull all factor fields for a universe."""
    raw = bbg(tickers, FACTOR_FIELDS, batch_size=300)

    # Convert to numeric
    for col in raw.columns:
        raw[col] = pd.to_numeric(raw[col], errors='coerce')

    # Z-score each factor cross-sectionally
    scores = raw.apply(lambda col: (col - col.mean()) / col.std())
    scores.columns = [f"{c}_z" for c in scores.columns]

    return pd.concat([raw, scores], axis=1)

# Usage
universe_tickers = ['AAPL US Equity', 'MSFT US Equity', 'GOOGL US Equity']
factors = factor_snapshot(universe_tickers)
```

### Recipe 3: Earnings Calendar

```python
# requires Bloomberg terminal
import pandas as pd
from xbbg import blp

def earnings_calendar(tickers: list) -> pd.DataFrame:
    """Pull next earnings dates and consensus estimates."""
    # Reference: next earnings date
    ref_fields = ['EARN_ANN_DT', 'BEST_EPS', 'BEST_EPS_SURP_PCT']
    ref = bbg(tickers, ref_fields)

    # Historical earnings surprises (bds)
    history = []
    for ticker in tickers[:10]:  # limit for example
        try:
            hist = blp.bds(ticker, 'EARN_ANN_DT_HIST_WITH_EPS')
            hist['ticker'] = ticker
            history.append(hist)
        except Exception:
            pass

    calendar = ref.copy()
    if history:
        hist_df = pd.concat(history)
        # Compute historical beat rate
        beat_rate = (
            hist_df.groupby('ticker')
            .apply(lambda g: (g.get('eps_surprise_pct', 0) > 0).mean())
        )
        calendar['hist_beat_rate'] = calendar.index.map(beat_rate)

    return calendar.sort_values('earn_ann_dt')

# Usage
earnings = earnings_calendar(['AAPL US Equity', 'MSFT US Equity', 'AMZN US Equity'])
```

### Recipe 4: Yield Curve Construction

```python
# requires Bloomberg terminal
import pandas as pd
from xbbg import blp

CURVE_TENORS = {
    '1M': 'USGG1M Index',  '3M': 'USGG3M Index',
    '6M': 'USGG6M Index',  '1Y': 'USGG1YR Index',
    '2Y': 'USGG2YR Index', '3Y': 'USGG3YR Index',
    '5Y': 'USGG5YR Index', '7Y': 'USGG7YR Index',
    '10Y': 'USGG10YR Index', '20Y': 'USGG20YR Index',
    '30Y': 'USGG30YR Index',
}

def build_yield_curve(as_of_date: str = None) -> pd.DataFrame:
    """Build US Treasury yield curve (current or historical)."""
    tickers = list(CURVE_TENORS.values())
    labels  = list(CURVE_TENORS.keys())

    if as_of_date:
        # Historical: use bdh with single date
        raw = blp.bdh(tickers, 'PX_LAST',
                      start_date=as_of_date, end_date=as_of_date)
        curve = raw.iloc[0]
        curve.index = [CURVE_TENORS.get(t, t) for t in curve.index]
    else:
        raw = blp.bdp(tickers, 'PX_LAST')
        curve = raw['px_last']

    result = pd.DataFrame({'tenor': labels, 'yield': curve.values})
    result['slope_2_10'] = (
        result.loc[result.tenor == '10Y', 'yield'].iloc[0] -
        result.loc[result.tenor == '2Y',  'yield'].iloc[0]
    )
    return result

curve = build_yield_curve()
print(f"10Y yield: {curve.loc[curve.tenor=='10Y','yield'].iloc[0]:.2f}%")
print(f"2s10s slope: {curve['slope_2_10'].iloc[0]:.1f}bps")
```

### Recipe 5: Options Chain Pull

```python
# requires Bloomberg terminal
import pandas as pd
from xbbg import blp
from xbbg.ext import option_greeks

def options_chain(underlying: str, expiry_dt: str) -> pd.DataFrame:
    """
    Pull full option chain for an underlying and expiry.

    Args:
        underlying: e.g. 'AAPL US Equity'
        expiry_dt:  e.g. '20250117'
    """
    # Get chain tickers
    chain = blp.bds(underlying, 'OPT_CHAIN', Expiry_Dt=expiry_dt)
    if chain.empty:
        raise ValueError(f"No options chain for {underlying} expiry {expiry_dt}")

    option_tickers = chain.values.flatten().tolist()

    # Reference data
    ref_fields = ['OPT_STRIKE_PX', 'OPT_PUT_CALL', 'OPT_EXPIRE_DT',
                  'PX_BID', 'PX_ASK', 'PX_MID', 'OPEN_INT',
                  'IVOL_MID', 'DELTA_MID_RT', 'GAMMA_MID_RT',
                  'THETA_MID_RT', 'VEGA_MID_RT']
    chain_data = bbg(option_tickers, ref_fields, batch_size=200)

    # Separate calls and puts
    chain_data['opt_put_call'] = chain_data['opt_put_call'].str.strip()
    calls = chain_data[chain_data['opt_put_call'] == 'Call'].copy()
    puts  = chain_data[chain_data['opt_put_call'] == 'Put'].copy()

    for df in [calls, puts]:
        df['mid'] = (df['px_bid'] + df['px_ask']) / 2
        df['spread'] = df['px_ask'] - df['px_bid']
        df['spread_pct'] = df['spread'] / df['mid'].replace(0, float('nan'))

    return pd.concat([calls, puts]).sort_values(['opt_put_call', 'opt_strike_px'])

# Usage
chain = options_chain('AAPL US Equity', expiry_dt='20250117')
print(chain[['opt_strike_px', 'opt_put_call', 'px_mid', 'ivol_mid', 'delta_mid_rt']])
```

### Recipe 6: FX Spot & Forward Ladder

```python
# requires Bloomberg terminal
import pandas as pd
from xbbg import blp

FX_PAIRS = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDCAD']
TENORS = ['1W', '1M', '2M', '3M', '6M', '9M', '1Y', '2Y']

def fx_forward_ladder(pairs: list = None, tenors: list = None) -> pd.DataFrame:
    """
    Build FX forward ladder for a list of pairs.

    Returns: MultiIndex DataFrame (tenor, pair) × (spot, fwd_bid, fwd_ask, fwd_mid)
    """
    pairs = pairs or FX_PAIRS
    tenors = tenors or TENORS

    # Spot rates
    spot_tickers = [f"{p} Curncy" for p in pairs]
    spot = blp.bdp(spot_tickers, ['BID', 'ASK'])
    spot['mid'] = (spot['bid'] + spot['ask']) / 2

    # Forward ladder
    rows = []
    for tenor in tenors:
        fwd_tickers = [f"{p}{tenor} Curncy" for p in pairs]
        fwds = blp.bdp(fwd_tickers, ['BID', 'ASK'])
        fwds['mid'] = (fwds['bid'] + fwds['ask']) / 2
        fwds['tenor'] = tenor
        # Clean ticker index back to pair format
        fwds.index = fwds.index.str.replace(tenor, '', regex=False)
        rows.append(fwds)

    fwd_df = pd.concat(rows)
    fwd_df = fwd_df.reset_index().rename(columns={'index': 'pair'})
    fwd_df = fwd_df.merge(
        spot[['mid']].rename(columns={'mid': 'spot'}),
        left_on='pair', right_index=True
    )
    fwd_df['forward_pts'] = fwd_df['mid'] - fwd_df['spot']

    return fwd_df.pivot(index='tenor', columns='pair', values='mid')

# Usage
ladder = fx_forward_ladder()
print(ladder)
```

---

## 18. MockBlp Testing Harness

Use `MockBlp` to test Bloomberg-dependent code without a live terminal.
All methods mirror xbbg's exact return signatures.

```python
# tests/mock_blp.py  (or inline in test files)
import pandas as pd
import numpy as np
from unittest.mock import patch
from contextlib import contextmanager


class MockBlp:
    """
    Mock Bloomberg API that mirrors xbbg.blp return signatures.
    Use with patch('xbbg.blp.bdp', MockBlp().bdp) etc.
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def bdp(self, tickers, flds, **kwargs) -> pd.DataFrame:
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(flds, str):
            flds = [flds]
        data = {}
        for fld in flds:
            fld_l = fld.lower()
            if 'px' in fld_l or 'price' in fld_l or 'last' in fld_l:
                data[fld_l] = self.rng.uniform(50, 500, len(tickers))
            elif 'pe' in fld_l or 'ratio' in fld_l or 'ebitda' in fld_l:
                data[fld_l] = self.rng.uniform(5, 40, len(tickers))
            elif 'mkt_cap' in fld_l or 'cap' in fld_l:
                data[fld_l] = self.rng.uniform(10_000, 3_000_000, len(tickers))
            elif 'vol' in fld_l:
                data[fld_l] = self.rng.uniform(0.1, 0.6, len(tickers))
            else:
                data[fld_l] = self.rng.uniform(0, 100, len(tickers))
        return pd.DataFrame(data, index=tickers)

    def bdh(self, tickers, flds, start_date, end_date=None,
            Per='D', **kwargs) -> pd.DataFrame:
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(flds, str):
            flds = [flds]
        dates = pd.bdate_range(start_date, end_date or pd.Timestamp.today())
        cols = pd.MultiIndex.from_product([tickers, [f.lower() for f in flds]])
        data = self.rng.uniform(50, 500, (len(dates), len(cols)))
        return pd.DataFrame(data, index=dates, columns=cols)

    def bds(self, ticker, fld, **kwargs) -> pd.DataFrame:
        fld_l = fld.lower()
        if 'indx_member' in fld_l or 'member' in fld_l:
            tickers = [f"TICK{i:02d} US Equity" for i in range(10)]
            return pd.DataFrame({
                'member_ticker_and_exchange_code': tickers,
                'percentage_weight': np.ones(10) * 10.0
            }, index=[ticker] * 10)
        if 'dvd' in fld_l or 'dividend' in fld_l:
            dates = pd.bdate_range('2023-01-01', periods=4, freq='Q')
            return pd.DataFrame({
                'declared_date': dates,
                'ex_date': dates + pd.Timedelta(days=15),
                'dividend_amount': self.rng.uniform(0.2, 0.8, 4),
                'dividend_frequency': ['Quarter'] * 4,
            }, index=[ticker] * 4)
        return pd.DataFrame({'value': [1.0, 2.0, 3.0]}, index=[ticker] * 3)

    def bdib(self, ticker, dt, interval=1, **kwargs) -> pd.DataFrame:
        tz = 'America/New_York'
        times = pd.date_range(f"{dt} 09:30", f"{dt} 16:00",
                              freq=f"{interval}min", tz=tz)
        n = len(times)
        base = self.rng.uniform(150, 200, n)
        cols = pd.MultiIndex.from_tuples(
            [(ticker, c) for c in ['open', 'high', 'low', 'close', 'volume', 'num_trds']]
        )
        data = np.column_stack([
            base, base * 1.002, base * 0.998, base * 1.001,
            self.rng.integers(1000, 100000, n),
            self.rng.integers(10, 500, n)
        ])
        return pd.DataFrame(data, index=times, columns=cols)

    def beqs(self, screen, **kwargs) -> pd.DataFrame:
        tickers = [f"MOCK{i:02d} US Equity" for i in range(20)]
        return pd.DataFrame({'id': tickers}, index=tickers)

    @contextmanager
    def patch_blp(self):
        """Context manager to patch all blp functions at once."""
        mock = self
        with patch('xbbg.blp.bdp', mock.bdp), \
             patch('xbbg.blp.bdh', mock.bdh), \
             patch('xbbg.blp.bds', mock.bds), \
             patch('xbbg.blp.bdib', mock.bdib), \
             patch('xbbg.blp.beqs', mock.beqs):
            yield mock


# Usage in tests:
# mock = MockBlp()
# with mock.patch_blp():
#     result = my_bloomberg_function()
#     assert not result.empty
```

---

## 19. Utilities

### Futures Contract Resolution
```python
from xbbg import blp

# Resolve generic ticker to active specific contract
blp.fut_ticker('ES1 Index', '2024-01-15', freq='ME')   # → 'ESH24 Index'
blp.fut_ticker('CL1 Comdty', '2024-01-15', freq='ME')  # → 'CLG24 Comdty'

# Volume-based active contract selection
blp.active_futures('ESA Index', '2024-01-15')           # → 'ESH24 Index'

# Month codes: F=Jan G=Feb H=Mar J=Apr K=May M=Jun N=Jul Q=Aug U=Sep V=Oct X=Nov Z=Dec
```

### Currency Conversion
```python
from xbbg import blp

# Fetch in local currency, convert to USD
hist_local = blp.bdh('BMW GR Equity', 'PX_LAST', '2024-01-01', '2024-12-31')
hist_usd = blp.adjust_ccy(hist_local, ccy='USD')
```

### Dividend & Turnover
```python
from xbbg import blp

# Dividend history
blp.dividend(['AAPL US Equity', 'MSFT US Equity'],
             start_date='2024-01-01', end_date='2024-12-31')

# Earnings by geography
blp.earning('AMD US Equity', by='Geo', Eqy_Fund_Year=2023, Number_Of_Periods=2)

# Trading volume/turnover (currency-normalised)
blp.turnover(['AAPL US Equity', 'MSFT US Equity'],
             start_date='2024-01-01', end_date='2024-01-10', ccy='USD')
```

### CDX Resolution
```python
from xbbg import blp

blp.cdx_ticker('CDX IG CDSI GEN 5Y Corp', '2024-01-15')  # → specific series
blp.active_cdx('CDX IG CDSI GEN 5Y Corp', '2024-01-15', lookback_days=10)
```

---

## 20. Top 10 Gotchas & Anti-Patterns

### 1. Wrong ticker format
```python
# WRONG
blp.bdp('AAPL', 'PX_LAST')          # Missing exchange + yellow key
blp.bdp('AAPL US', 'PX_LAST')       # Missing yellow key

# CORRECT
blp.bdp('AAPL US Equity', 'PX_LAST')
```

### 2. Using bdhd() instead of bdib() for intraday
```python
# WRONG (v0.x legacy name — does not exist in current xbbg)
blp.bdhd('AAPL US Equity', dt='2024-01-15')

# CORRECT
blp.bdib('AAPL US Equity', dt='2024-01-15')
```

### 3. Forgetting to flatten MultiIndex in bdh
```python
# WRONG: iterating raw MultiIndex
df = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], 'px_last', start, end)
returns = df.pct_change()   # Works but columns are confusing MultiIndex

# CORRECT: flatten first
prices = df.droplevel(1, axis=1)
returns = prices.pct_change()
```

### 4. Single-ticker bdh returns date-indexed (not MultiIndex)
```python
# Single ticker: DatetimeIndex × fields (NO MultiIndex on columns)
df = blp.bdh('AAPL US Equity', ['px_last', 'volume'], start, end)
df.columns   # Index(['px_last', 'volume'], dtype='object')

# Multiple tickers: MultiIndex columns (ticker, field)
df = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], ['px_last', 'volume'], start, end)
df.columns   # MultiIndex([('AAPL US Equity', 'px_last'), ...])
```

### 5. Empty DataFrame ≠ Error (bdp/bdh silently return empty on bad ticker)
```python
# Bad ticker returns empty DataFrame, not an exception
result = blp.bdp('FAKE TICKER Equity', 'PX_LAST')
result.empty   # True — no exception raised!

# Always check
if result.empty:
    raise ValueError("Ticker not found or no entitlement")
```

### 6. N/A fields not NaN by default
```python
# Bloomberg N/A can come through as the string 'N/A' in some versions
result = blp.bdp(tickers, flds)
result = result.replace('N/A', float('nan'))   # explicit coerce
result = result.apply(pd.to_numeric, errors='coerce')  # or bulk numeric cast
```

### 7. Single-looping securities instead of batching
```python
# WRONG: extremely slow, each call opens/closes session
for ticker in universe:
    data[ticker] = blp.bdp(ticker, flds)  # 500 API calls!

# CORRECT: batch in one call
data = blp.bdp(universe, flds)  # 1 API call
```

### 8. Not adjusting for corporate actions in backtests
```python
# WRONG: raw prices — contains splits and dividend gaps
prices = blp.bdh('AAPL US Equity', 'PX_LAST', '2010-01-01', '2024-12-31')

# CORRECT: fully adjusted
prices = blp.bdh('AAPL US Equity', 'PX_LAST', '2010-01-01', '2024-12-31',
                 adjust='all')
```

### 9. Using real-time fields in bdh (stale/wrong data)
```python
# WRONG: RT fields don't work in historical mode
blp.bdh('AAPL US Equity', 'LAST_PRICE_RT', '2024-01-01', '2024-12-31')

# CORRECT: use historical field equivalents
blp.bdh('AAPL US Equity', 'PX_LAST', '2024-01-01', '2024-12-31')
```

### 10. Not pinning xbbg version in production
```python
# WRONG: unpinned install can break on next xbbg release
pip install xbbg

# CORRECT: pin version and track breaking changes
pip install "xbbg==1.0.0a1"    # or latest stable 0.7.x

# At runtime, always log version:
import xbbg
import logging
logging.getLogger(__name__).info(f"xbbg version: {xbbg.__version__}")
```

---

## 21. Field Discovery Workflow

```python
from xbbg import blp

# Step 1: search by keyword
# --- v1.x only ---
blp.fieldSearch('vwap')           # v1.x only
blp.fieldSearch('earnings yield') # v1.x only
blp.fieldInfo(['EQY_WEIGHTED_AVG_PX', 'VWAP_VOLUME'])  # v1.x only
blp.bflds(fields=['DUR_MID', 'MODIFIED_DURATION_ASK'])  # v1.x only

# --- v0.x alternative: use Bloomberg Terminal UI ---
# FLDS<GO>                       → search all fields
# {TICKER}<EQUITY> FLDS          → fields available for a specific security
# FLDS {KEYWORD}                 → keyword search in terminal

# Step 2: test field on a single security before batch (works in all versions)
test = blp.bdp('AAPL US Equity', ['MY_FIELD'])
if test.empty or test.isna().all().all():
    print("Field not available for this security type")

# Step 3: look up field in references/field-reference.md (curated, version-agnostic)
```

---

## Quick Patterns Reference

```python
# --- Most common patterns ---

# Today's prices for a universe
prices = blp.bdp(universe, 'PX_LAST')

# 1yr adjusted daily close, multiple securities, flat DataFrame
prices = bbg(universe, 'px_last', start_date='2024-01-01', adjust='all')

# S&P 500 current members + weights
members = blp.bds('SPX Index', 'INDX_MWEIGHT')

# Historical S&P 500 membership (point-in-time)
hist_members = blp.bds('SPX Index', 'INDX_MWEIGHT_HIST',
                        END_DATE_OVERRIDE='20230101')

# US yield curve (current)
tenors = ['USGG2YR Index', 'USGG5YR Index', 'USGG10YR Index', 'USGG30YR Index']
curve = blp.bdp(tenors, 'PX_LAST')

# Intraday 5-min bars (with caching)
bars = blp.bdib('AAPL US Equity', dt='2024-01-15', interval=5)

# VWAP for a date
vwap = blp.bdp('AAPL US Equity', 'EQY_WEIGHTED_AVG_PX', VWAP_Dt='20240115')

# Dividend history
divs = blp.bds('AAPL US Equity', 'DVD_Hist_All',
               DVD_Start_Dt='20230101', DVD_End_Dt='20231231')

# Equity screen → universe
screen_tickers = blp.beqs(screen='MyScreen')

# Futures front contract
front = blp.fut_ticker('ES1 Index', '2024-01-15', freq='ME')

# FI yield to maturity
ytm = blp.bdp('T 4.5 5/15/38 Govt', 'YLD_YTM_MID')

# Bond analytics via YAS
analytics = blp.yas('T 4.5 5/15/38 Govt', ['YAS_BOND_YLD', 'YAS_MOD_DUR', 'YAS_ASW_SPREAD'])

# Find a field by keyword (v1.x only — use FLDS<GO> in Bloomberg terminal for v0.x)
blp.fieldSearch('free float')   # v1.x only

# Check exchange timezone (v1.x only)
tz = blp.exchange_tz('BHP AU Equity')  # → 'Australia/Sydney'  # v1.x only
```

---

## 22. Data Pipeline Validation

**Mandate:** Any Bloomberg data pulled for **quant modeling, backtests, factors, or ML** must pass through `data_validation.validate()` after shape normalization. Do not feed raw `bdp`/`bdh`/`bdib` output into downstream models without this step.

- **Bloomberg-specific playbook** (output mapping, presets, `validated_bbg`, anti-patterns): `references/data-pipeline-validation.md`
- **Full validation spec** (domains, errors, `skip_validation`): `../ml-algo-trading/references/data-validation.md`

**Quick start** (`validated_bbg` + `EQUITY_CONFIG` are defined in `references/data-pipeline-validation.md`; they wrap Section 16 `bbg()`):

```python
# EQUITY_CONFIG, validated_bbg, bbg — see references/data-pipeline-validation.md + Section 16
validated = validated_bbg(tickers, "px_last", start_date="2020-01-01", adjust="all", config=EQUITY_CONFIG)
clean_df = validated.df
```

| xbbg pattern | Typical `ValidationConfig` preset | Notes |
|---|---|---|
| `bdh` equities / ETFs daily | `EQUITY_CONFIG` (see reference) | Use `adjust='all'` for return-based work |
| `bdh` rates / FI yields, spreads | `CREDIT_CONFIG` | Set `secondary_source_df` when reconciling vs another vendor |
| Macro / slow-moving indices | `MACRO_CONFIG` | Wider gap tolerance for `macro` class |
| `bdh` FX spot / forwards | `FX_CONFIG` | Align calendar with session if not XNYS |
| `bdib` / `bdtick` intraday | Custom or `skip_validation=True` | Default gates are EOD-oriented; aggregate or tune config |
| `bdp` snapshot only | One-row panel + validate or schema-only pre-check | `validate()` needs a `DatetimeIndex` — see reference |

