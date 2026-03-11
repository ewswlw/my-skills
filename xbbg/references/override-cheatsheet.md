# Bloomberg Override Cheat Sheet
<!-- Last verified: xbbg 1.0.0a1 | March 2026 -->
<!-- Usage in xbbg: pass as keyword arguments OR as ovrds dict -->
<!-- blp.bdp(ticker, fld, OVERRIDE_NAME='value')  — keyword style -->
<!-- blp.bdp(ticker, fld, ovrds={'OVERRIDE_NAME': 'value'})  — dict style (v0.x) -->
<!-- Note: In xbbg v1, overrides are typically passed as keyword arguments -->

---

## How to Pass Overrides

```python
from xbbg import blp

# Keyword argument style (recommended, v1+)
blp.bdp('AAPL US Equity', 'EQY_WEIGHTED_AVG_PX', VWAP_Dt='20240115')

# Dict-style (works in both v0.x and v1)
blp.bdh('AAPL US Equity', 'PX_LAST', '2024-01-01', '2024-12-31',
        CshAdjNormal=True, CshAdjAbnormal=True, CapChg=True)

# BDS with overrides
blp.bds('AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20230101', DVD_End_Dt='20231231')
```

---

## Equity Overrides

### Price Adjustment (bdh)
| Override | Values | Effect |
|---|---|---|
| `CshAdjNormal` | `True` / `False` | Adjust for regular cash dividends |
| `CshAdjAbnormal` | `True` / `False` | Adjust for special dividends |
| `CapChg` | `True` / `False` | Adjust for stock splits |
| `adjust` | `'all'` / `'dvd'` / `'split'` | xbbg shorthand (v1 shortcut) |

```python
# Fully adjusted prices (most common for backtesting)
blp.bdh('AAPL US Equity', 'PX_LAST', '2020-01-01', '2024-12-31', adjust='all')

# Split-adjusted only
blp.bdh('AAPL US Equity', 'PX_LAST', '2020-01-01', '2024-12-31',
        CapChg=True, CshAdjNormal=False, CshAdjAbnormal=False)
```

### VWAP
| Override | Format | Example |
|---|---|---|
| `VWAP_Dt` | `YYYYMMDD` | `VWAP_Dt='20240115'` |
| `VWAP_START_TIME` | `HH:MM:SS` | `VWAP_START_TIME='09:30:00'` |
| `VWAP_END_TIME` | `HH:MM:SS` | `VWAP_END_TIME='16:00:00'` |

```python
blp.bdp('AAPL US Equity', 'EQY_WEIGHTED_AVG_PX', VWAP_Dt='20240115')
```

### Dividend / Earnings History (bds)
| Override | Format | Example |
|---|---|---|
| `DVD_Start_Dt` | `YYYYMMDD` | `DVD_Start_Dt='20230101'` |
| `DVD_End_Dt` | `YYYYMMDD` | `DVD_End_Dt='20231231'` |
| `Eqy_Fund_Year` | `YYYY` | `Eqy_Fund_Year=2023` |
| `Number_Of_Periods` | `int` | `Number_Of_Periods=4` |

```python
blp.bds('AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20230101', DVD_End_Dt='20231231')
blp.earning('AMD US Equity', by='Geo', Eqy_Fund_Year=2023, Number_Of_Periods=2)
```

### Beta
| Override | Values | Effect |
|---|---|---|
| `EQY_BETA_OVERRIDE_PERIOD` | `'1YR'`, `'2YR'`, `'3YR'` | Lookback period |
| `EQY_BETA_ADJ_OVERRIDABLE` | `'ADJUSTED'`, `'RAW'` | Adjusted vs raw |
| `BETA_INDEX_CODE` | e.g. `'SPX Index'` | Benchmark index |

### Index Members (bds)
| Override | Format | Effect |
|---|---|---|
| `END_DATE_OVERRIDE` | `YYYYMMDD` | Historical membership as of date |

```python
# Current members
blp.bds('SPX Index', 'INDX_MEMBERS')

# Historical members as of a past date
blp.bds('SPX Index', 'INDX_MWEIGHT_HIST', END_DATE_OVERRIDE='20230101')
```

---

## Fixed Income Overrides

### Price Convention
| Override | Values | Effect |
|---|---|---|
| `PRICING_OPTION` | `'PRICING_OPTION_PRICE'` | Price-based (default for most bonds) |
| `PRICING_OPTION` | `'PRICING_OPTION_YIELD'` | Yield-based (give yield, get analytics) |
| `SETTLE_DT` | `YYYYMMDD` | Settlement date override |
| `CALC_TYP_OVRDE` | `'STREET'` / `'TRUE'` | Calculation type |

### Yield Type
| Override | Values | Effect |
|---|---|---|
| `YIELD_TO_CALL_DATES` | `YYYYMMDD` | Yield to specific call date |
| `YLD_COMP_FREQ` | `1`=annual, `2`=semi-annual, `4`=quarterly | Yield compounding frequency |

### Currency Override
| Override | Values | Effect |
|---|---|---|
| `CRNCY_ADJ_DT` | `YYYYMMDD` | FX rate as of specific date |
| `CRNCY` | `'USD'`, `'EUR'` etc. | Convert output to this currency |

```python
# Get EUR bond yield in USD terms
blp.bdp('DB 3 3/14/25 Corp', ['YLD_YTM_MID', 'PX_LAST'], CRNCY='USD')
```

### Cash Flow Schedule (bds)
| Override | Values | Effect |
|---|---|---|
| `INCLUDE_PRINCIPAL` | `'Y'` / `'N'` | Include/exclude principal payments |
| `SETTLE_DT` | `YYYYMMDD` | Settlement date for accruals |

```python
blp.bds('/isin/US037833AK68', 'DES_CASH_FLOW', SETTLE_DT='20240301')
```

### Callable Bonds
| Override | Values | Effect |
|---|---|---|
| `CALL_DT_OVERRIDE` | `YYYYMMDD` | Compute yield to specific call date |

---

## FX Overrides

### Forward Rates
| Override | Values | Effect |
|---|---|---|
| `FWD_TENOR` | `'1M'`, `'3M'`, `'6M'`, `'1Y'` etc. | Forward tenor |
| `SETTLE_DT` | `YYYYMMDD` | Specific settle date for forward |

```python
# 3-month EUR/USD forward
blp.bdp('EURUSD Curncy', ['FWD_BID', 'FWD_ASK', 'FWD_MID'], FWD_TENOR='3M')
```

---

## Historical Data (bdh) Overrides

### Periodicity
| Override | Values | Effect |
|---|---|---|
| `Per` | `'D'` | Daily (default) |
| `Per` | `'W'` | Weekly |
| `Per` | `'M'` | Monthly |
| `Per` | `'Q'` | Quarterly |
| `Per` | `'Y'` | Yearly (Semi-annual: `'S'`) |
| `Fill` | `'A'` | All calendar days |
| `Fill` | `'B'` | Back-fill missing dates |
| `Fill` | `'F'` | Forward-fill missing dates |
| `Fill` | `'P'` | Previous value carry |
| `Days` | `'A'` | All days including holidays |
| `Days` | `'T'` | Trading days only (default) |
| `Days` | `'W'` | Weekdays |

```python
# Monthly data, carry forward on missing dates
blp.bdh('SPX Index', 'PX_LAST', '2020-01-01', '2024-12-31', Per='M', Fill='P')

# Weekly with all calendar days
blp.bdh('EURUSD Curncy', 'PX_LAST', '2024-01-01', '2024-12-31', Per='W', Days='A')
```

---

## Options Overrides

### Option Chain
| Override | Values | Effect |
|---|---|---|
| `Expiry_Dt` | `YYYYMMDD` | Filter chain to expiry date |
| `OPT_STRIKE_PX_MAX` | `float` | Max strike filter |
| `OPT_STRIKE_PX_MIN` | `float` | Min strike filter |
| `OPT_PUT_CALL` | `'Call'` / `'Put'` | Filter by put or call |

```python
# Get SPX call options expiring Jan 17 2025
blp.bds('SPX Index', 'OPT_CHAIN', Expiry_Dt='20250117', OPT_PUT_CALL='Call')
```

### Implied Vol Surface
| Override | Values | Effect |
|---|---|---|
| `IVOL_SURFACE_DELTA` | `float (0–1)` | Delta slice of vol surface |
| `IVOL_SURFACE_TENOR` | `'1M'`, `'3M'` etc. | Tenor slice |

---

## Common Override Patterns by Task

```python
# --- Backtesting: fully adjusted daily prices ---
prices = blp.bdh(
    tickers, 'PX_LAST',
    start_date='2015-01-01', end_date='2024-12-31',
    adjust='all',        # xbbg v1 shorthand
    Per='D', Days='T'   # trading days only
)

# --- Factor research: point-in-time fundamentals ---
fundamentals = blp.bdp(
    tickers,
    ['PE_RATIO', 'EV_EBITDA', 'BOOK_VAL_PER_SH', 'EARN_PER_SH'],
)

# --- Index composition as of rebalance date ---
members = blp.bds('SPX Index', 'INDX_MWEIGHT_HIST',
                  END_DATE_OVERRIDE='20230901')

# --- Yield curve: 10 UST benchmarks ---
tenors = ['USGG1M', 'USGG3M', 'USGG6M', 'USGG1YR', 'USGG2YR',
          'USGG3YR', 'USGG5YR', 'USGG7YR', 'USGG10YR', 'USGG30YR']
curve = blp.bdp([f'{t} Index' for t in tenors], 'PX_LAST')

# --- Bond pricing from yield ---
blp.yas('T 4.5 5/15/38 Govt', flds='YAS_BOND_PX', yield_=4.8)

# --- FX forward ladder ---
tenors = ['1W', '1M', '2M', '3M', '6M', '9M', '1Y', '2Y']
fwds = {t: blp.bdp('EURUSD Curncy', ['FWD_BID', 'FWD_ASK'], FWD_TENOR=t)
        for t in tenors}
```
