# Bloomberg Field Reference
<!-- Last verified: xbbg 1.0.0a1 / xbbg 0.7.x | March 2026 -->
<!-- Usage: blp.bdp(ticker, 'FIELD_NAME') or blp.bdh(ticker, 'FIELD_NAME', ...) -->
<!-- Note: Field names are case-insensitive in xbbg; Bloomberg normalises to lowercase in output -->

---

## Equity Fields

### Price & Market Data
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `PX_LAST` | Last price / close | ✅ | ✅ | Most common price field |
| `PX_BID` | Best bid | ✅ | ✅ | Real-time during session |
| `PX_ASK` | Best ask | ✅ | ✅ | Real-time during session |
| `PX_MID` | Mid price | ✅ | ✅ | (bid+ask)/2 |
| `PX_OPEN` | Open price | ✅ | ✅ | |
| `PX_HIGH` | Day high | ✅ | ✅ | |
| `PX_LOW` | Day low | ✅ | ✅ | |
| `PX_VOLUME` | Day volume (shares) | ✅ | ✅ | Also: `VOLUME` |
| `PX_SETTLE` | Settlement price | ✅ | ✅ | Futures/options |
| `PX_TURNOVER` | Turnover value (local ccy) | ✅ | ✅ | |
| `EQY_WEIGHTED_AVG_PX` | VWAP | ✅ | — | Requires `VWAP_Dt` override |
| `HIGH_52WEEK` | 52-week high | ✅ | — | |
| `LOW_52WEEK` | 52-week low | ✅ | — | |
| `RETURN_1D` | 1-day total return | ✅ | ✅ | |
| `RETURN_YTD` | YTD total return | ✅ | ✅ | |
| `RETURN_1YR` | 1-year total return | ✅ | ✅ | |
| `RETURN_3YR` | 3-year total return | ✅ | ✅ | |

### Valuation / Fundamentals
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `PE_RATIO` | Trailing P/E ratio | ✅ | ✅ | TTM earnings |
| `EQY_P_E_RATIO_FORWARD` | Forward P/E | ✅ | ✅ | Next-12-month consensus |
| `PX_TO_BOOK_RATIO` | Price-to-book | ✅ | ✅ | |
| `PX_TO_SALES_RATIO` | Price-to-sales | ✅ | ✅ | |
| `PX_TO_FREE_CASH_FLOW` | Price-to-FCF | ✅ | ✅ | |
| `EV_EBITDA` | EV/EBITDA | ✅ | ✅ | |
| `EV_SALES` | EV/Sales | ✅ | ✅ | |
| `EQY_DVD_YLD_IND` | Indicated dividend yield | ✅ | ✅ | |
| `EQY_DVD_YLD_12M` | Trailing 12M dividend yield | ✅ | ✅ | |
| `EQY_DVD_PER_SH` | Dividend per share (annual) | ✅ | ✅ | |
| `BOOK_VAL_PER_SH` | Book value per share | ✅ | ✅ | |
| `EARN_PER_SH` | EPS (basic, trailing) | ✅ | ✅ | |
| `EARN_PER_SH_NEXT_YR` | EPS next year (consensus) | ✅ | ✅ | |
| `BEST_EPS` | Best EPS estimate | ✅ | ✅ | IBES consensus |
| `BEST_PE_RATIO` | Best forward P/E | ✅ | ✅ | |
| `BEST_EV_EBITDA` | Best EV/EBITDA estimate | ✅ | ✅ | |
| `SALES_REV_TURN` | Revenue (TTM) | ✅ | ✅ | |
| `EBITDA` | EBITDA (TTM) | ✅ | ✅ | |
| `CF_FREE_CASH_FLOW` | Free cash flow | ✅ | ✅ | |
| `RETURN_ON_EQUITY` | ROE | ✅ | ✅ | |
| `RETURN_COM_EQY` | Return on common equity | ✅ | ✅ | |
| `GROSS_MARGIN` | Gross margin % | ✅ | ✅ | |
| `OPER_MARGIN` | Operating margin % | ✅ | ✅ | |
| `NET_MARGIN` | Net margin % | ✅ | ✅ | |

### Size / Float / Ownership
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `CUR_MKT_CAP` | Market cap (USD millions) | ✅ | ✅ | |
| `EQY_FLOAT` | Float (shares) | ✅ | — | |
| `EQY_SH_OUT` | Shares outstanding | ✅ | ✅ | |
| `EQY_FREE_FLOAT_PCT` | Free float % | ✅ | — | |
| `SHORT_INT` | Short interest (shares) | ✅ | ✅ | |
| `SHORT_INT_RATIO` | Short interest ratio (days to cover) | ✅ | ✅ | |
| `SHORT_INT_PCT_OF_FLOAT_RT` | Short interest % of float | ✅ | ✅ | |

### Classification / Identifiers
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `SECURITY_NAME` | Full security name | ✅ | — | |
| `GICS_SECTOR_NAME` | GICS sector | ✅ | — | |
| `GICS_INDUSTRY_NAME` | GICS industry | ✅ | — | |
| `GICS_INDUSTRY_GROUP_NAME` | GICS industry group | ✅ | — | |
| `GICS_SUB_INDUSTRY_NAME` | GICS sub-industry | ✅ | — | |
| `BICS_LEVEL_1_SECTOR_NAME` | BICS level-1 sector | ✅ | — | Bloomberg classification |
| `COUNTRY_ISO` | Country ISO-2 code | ✅ | — | |
| `EXCH_CODE` | Exchange code | ✅ | — | e.g. `UN`, `UW`, `LN` |
| `ID_ISIN` | ISIN | ✅ | — | |
| `ID_CUSIP` | CUSIP | ✅ | — | |
| `ID_SEDOL1` | SEDOL | ✅ | — | |
| `ID_BB_GLOBAL` | FIGI (Bloomberg Global ID) | ✅ | — | |
| `CRNCY` | Currency | ✅ | — | |

### Risk / Technical
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `VOLATILITY_30D` | 30-day historical vol (annualised) | ✅ | ✅ | |
| `VOLATILITY_90D` | 90-day historical vol | ✅ | ✅ | |
| `VOLATILITY_260D` | 260-day historical vol | ✅ | ✅ | |
| `BETA_ADJUSTED_OVERRIDABLE` | Adjusted beta (vs S&P 500) | ✅ | ✅ | |
| `BETA_RAW_OVERRIDABLE` | Raw beta (vs S&P 500) | ✅ | ✅ | Use `EQY_BETA_ADJ_OVERRIDABLE` override |
| `RSI_14D` | 14-day RSI | ✅ | ✅ | |
| `TOT_DEBT_TO_TOT_EQY` | Debt/Equity | ✅ | ✅ | |
| `TOT_DEBT_TO_TOT_ASSET` | Debt/Assets | ✅ | ✅ | |

### Index / Bulk Reference (bds only)
| Field | Description | Function | Notes |
|---|---|---|---|
| `INDX_MEMBERS` | Index members (tickers) | `bds` | Returns DataFrame with `member_ticker_and_exchange_code` |
| `INDX_MWEIGHT` | Index member weights | `bds` | Returns weight% per constituent |
| `INDX_MWEIGHT_HIST` | Historical member weights | `bds` | Requires `END_DATE_OVERRIDE` override |
| `DVD_HIST_ALL` | Full dividend history | `bds` | Use `DVD_Start_Dt` / `DVD_End_Dt` overrides |
| `CSHD_HISTORY_SPLITS` | Split history | `bds` | |
| `EARN_ANN_DT_HIST_WITH_EPS` | Earnings announcement dates + EPS | `bds` | Quarterly calendar |

---

## Fixed Income Fields

### Price & Yield
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `PX_LAST` | Clean last price (% of par) | ✅ | ✅ | Standard price field |
| `PX_BID` | Clean bid price | ✅ | ✅ | |
| `PX_ASK` | Clean ask price | ✅ | ✅ | |
| `PX_MID` | Clean mid price | ✅ | ✅ | |
| `PX_DIRTY_MID` | Dirty mid price (incl. accrued) | ✅ | ✅ | |
| `YLD_YTM_MID` | Yield to maturity (mid) | ✅ | ✅ | Most common yield |
| `YLD_YTM_BID` | Yield to maturity (bid) | ✅ | ✅ | |
| `YLD_YTM_ASK` | Yield to maturity (ask) | ✅ | ✅ | |
| `YLD_YTC_MID` | Yield to call (mid) | ✅ | ✅ | Callable bonds |
| `YLD_YTW_MID` | Yield to worst (mid) | ✅ | ✅ | Min of YTM, YTC |
| `YAS_BOND_YLD` | YAS yield | ✅ | ✅ | Via `blp.yas()` |
| `YAS_BOND_PX` | YAS price | ✅ | ✅ | Via `blp.yas()` |
| `ACCRUED_INT` | Accrued interest | ✅ | ✅ | Per $100 face |

### Spread Analytics
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `YAS_ASW_SPREAD` | Asset swap spread (bps) | ✅ | ✅ | Via `blp.yas()` |
| `YAS_ISPREAD_TO_GOVT` | I-spread to government (bps) | ✅ | ✅ | |
| `YAS_ZSPREAD_TO_GOVT` | Z-spread to government (bps) | ✅ | ✅ | |
| `OAS_SPREAD_ASK` | OAS (ask side, bps) | ✅ | ✅ | Option-adjusted spread |
| `CDS_SPREAD_5YR` | 5-year CDS spread (bps) | ✅ | ✅ | |
| `CUR_YIELD_MID` | Current yield (mid) | ✅ | ✅ | Coupon / clean price |

### Risk Metrics
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `DUR_MID` | Modified duration (mid) | ✅ | ✅ | |
| `DUR_ADJ_MID` | Adjusted duration (mid) | ✅ | ✅ | OAS-adjusted |
| `MODIFIED_DURATION_ASK` | Modified duration (ask) | ✅ | ✅ | |
| `CONVEXITY_MID` | Convexity (mid) | ✅ | ✅ | |
| `DV01` | DV01 (per $100 face, bps) | ✅ | ✅ | Dollar value of 1bp |
| `RISK_MID` | Risk (mid, $) | ✅ | ✅ | DV01 × notional |
| `YAS_MOD_DUR` | YAS modified duration | ✅ | ✅ | Via `blp.yas()` |

### Reference Data
| Field | Description | bdp | Notes |
|---|---|---|---|
| `SECURITY_NAME` | Bond description | ✅ | e.g. "Apple Inc 3.25% 2029" |
| `MATURITY` | Maturity date | ✅ | |
| `COUPON` | Coupon rate (%) | ✅ | |
| `COUPON_FREQ` | Coupon frequency | ✅ | S=semi-annual, A=annual |
| `DAY_CNT_DES` | Day count convention | ✅ | e.g. "ACT/360" |
| `ISSUE_DT` | Issue date | ✅ | |
| `FIRST_COUPON_DT` | First coupon date | ✅ | |
| `NEXT_COUPON_DT` | Next coupon date | ✅ | |
| `PREV_COUPON_DT` | Previous coupon date | ✅ | |
| `AMT_OUTSTANDING` | Outstanding amount (face, millions) | ✅ | |
| `CALLABLE` | Is callable (Y/N) | ✅ | |
| `CONVERTIBLE` | Is convertible (Y/N) | ✅ | |
| `ISSUER` | Issuer name | ✅ | |
| `COUNTRY_ISO` | Issuer country ISO-2 | ✅ | |
| `CRNCY` | Settlement currency | ✅ | |
| `RTG_MOODY` | Moody's rating | ✅ | |
| `RTG_SP` | S&P rating | ✅ | |
| `RTG_FITCH` | Fitch rating | ✅ | |
| `NXT_CALL_DT` | Next call date | ✅ | |
| `NXT_CALL_PX` | Next call price | ✅ | |
| `ID_ISIN` | ISIN | ✅ | |
| `ID_CUSIP` | CUSIP (US bonds) | ✅ | |

### Bulk Reference (bds)
| Field | Function | Notes |
|---|---|---|
| `DES_CASH_FLOW` | `bds` | Full coupon + principal cash flow schedule |
| `CALLABLE_INFO` | `bds` | All call dates and prices |
| `DVD_HIST_ALL` | `bds` | Not applicable for bonds; use for prefs |

---

## FX Fields

### Spot & Forward
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `PX_LAST` | Spot rate (last) | ✅ | ✅ | e.g. `EURUSD Curncy` |
| `BID` | Spot bid | ✅ | ✅ | |
| `ASK` | Spot ask | ✅ | ✅ | |
| `MID` | Spot mid | ✅ | ✅ | |
| `PX_HIGH` | Day high | ✅ | ✅ | |
| `PX_LOW` | Day low | ✅ | ✅ | |
| `PX_OPEN` | Open (NY) | ✅ | ✅ | |
| `RATE_CHANGE_1D` | 1-day pip change | ✅ | ✅ | |
| `FWD_BID` | Forward bid (for tenor) | ✅ | — | Use `FWD_TENOR` override |
| `FWD_ASK` | Forward ask (for tenor) | ✅ | — | |
| `FWD_MID` | Forward mid (for tenor) | ✅ | — | |
| `FX_FORWARD_RATE_BID` | Forward outright bid | ✅ | — | Requires date override |
| `FX_FORWARD_RATE_ASK` | Forward outright ask | ✅ | — | |

### Volatility
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `VOLATILITY_30D` | 30D realised vol | ✅ | ✅ | |
| `IVOL_1MO_MID` | 1-month implied vol (ATM) | ✅ | ✅ | |
| `IVOL_3MO_MID` | 3-month implied vol (ATM) | ✅ | ✅ | |
| `IVOL_6MO_MID` | 6-month implied vol (ATM) | ✅ | ✅ | |
| `IVOL_1YR_MID` | 1-year implied vol (ATM) | ✅ | ✅ | |
| `RR25_1MO` | 1M 25-delta risk reversal | ✅ | ✅ | Skew measure |
| `BF25_1MO` | 1M 25-delta butterfly | ✅ | ✅ | Kurtosis measure |

---

## Macro / Index Fields

### Index Price Data
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `PX_LAST` | Last level | ✅ | ✅ | e.g. `SPX Index` |
| `PX_OPEN` | Open level | ✅ | ✅ | |
| `PX_HIGH` | High level | ✅ | ✅ | |
| `PX_LOW` | Low level | ✅ | ✅ | |
| `PX_VOLUME` | Volume | ✅ | ✅ | |
| `OPEN_INT` | Open interest | ✅ | ✅ | Futures |
| `HIGH_52WEEK` | 52-week high | ✅ | — | |
| `LOW_52WEEK` | 52-week low | ✅ | — | |
| `RETURN_YTD` | YTD return | ✅ | ✅ | |
| `RETURN_1YR` | 1-year return | ✅ | ✅ | |
| `RETURN_3YR` | 3-year return | ✅ | ✅ | |

### Index Composition (bds)
| Field | Function | Notes |
|---|---|---|
| `INDX_MEMBERS` | `bds` | Returns `member_ticker_and_exchange_code` column |
| `INDX_MWEIGHT` | `bds` | Returns weight% per member |
| `INDX_MWEIGHT_HIST` | `bds` | Historical weights; needs `END_DATE_OVERRIDE` |
| `INDX_NUMOF_MEMBERS` | `bdp` | Count of index members |

### Economic Indicators
| Field | Description | bdp | Notes |
|---|---|---|---|
| `ECO_RELEASE_DT` | Last release date | ✅ | |
| `ECO_FUTURE_RELEASE_DT` | Next scheduled release | ✅ | |
| `ECO_SURVEY_MEDIAN` | Survey median (consensus) | ✅ | |
| `ECO_SURVEY_HIGH` | Survey high | ✅ | |
| `ECO_SURVEY_LOW` | Survey low | ✅ | |
| `ECO_ACTUAL_RELEASE` | Actual released value | ✅ | |
| `LAST_UPDATE_DT` | Last data update date | ✅ | |

### Commodities / Futures
| Field | Description | bdp | bdh | Notes |
|---|---|---|---|---|
| `PX_LAST` | Last / settle price | ✅ | ✅ | |
| `PX_SETTLE` | Settlement price | ✅ | ✅ | |
| `OPEN_INT` | Open interest (contracts) | ✅ | ✅ | |
| `FUT_CUR_GEN_TICKER` | Current generic ticker | ✅ | — | e.g. CL1→CLZ24 |
| `FUT_NEXT_GEN_TICKER` | Next generic ticker | ✅ | — | |
| `LAST_TRADEABLE_DT` | Last trading date | ✅ | — | |
| `FUT_DELIVERABLE_BONDS` | CTD basket for bond futures | ✅ | — | |

---

## Options Fields

### Greeks & Analytics
| Field | Description | bdp | Notes |
|---|---|---|---|
| `DELTA_MID_RT` | Delta (mid, real-time) | ✅ | |
| `GAMMA_MID_RT` | Gamma (mid) | ✅ | |
| `THETA_MID_RT` | Theta (mid, per day) | ✅ | |
| `VEGA_MID_RT` | Vega (mid, per 1% vol) | ✅ | |
| `RHO_MID_RT` | Rho (mid, per 1% rate) | ✅ | |
| `IVOL_MID` | Implied volatility (mid) | ✅ | |
| `IVOL_BID` | Implied volatility (bid) | ✅ | |
| `IVOL_ASK` | Implied volatility (ask) | ✅ | |
| `OPEN_INT` | Open interest | ✅ | |
| `OPT_INTRINSIC_VAL` | Intrinsic value | ✅ | |
| `OPT_TIME_VAL` | Time value | ✅ | |
| `OPT_STRIKE_PX` | Strike price | ✅ | |
| `OPT_EXPIRE_DT` | Expiry date | ✅ | |
| `OPT_PUT_CALL` | Put or Call | ✅ | `Put` or `Call` |
| `OPT_UNDL_TICKER` | Underlying ticker | ✅ | |

### Option Chain (bds)
| Field | Function | Notes |
|---|---|---|
| `OPT_CHAIN` | `bds` | All option tickers for an underlying; use `Expiry_Dt` override |
| `CHAIN_TICKERS` | `bds` | Alternative chain field |

---

## Field Discovery (Runtime)

```python
# Search for fields by keyword
blp.fieldSearch('vwap')          # returns DataFrame with field names + descriptions
blp.fieldSearch('duration')      # find duration fields for FI
blp.fieldSearch('implied vol')   # vol surface fields

# Get metadata for specific fields
blp.fieldInfo(['PX_LAST', 'YLD_YTM_MID', 'DELTA_MID_RT'])

# Unified interface (recommended, v1+)
blp.bflds(search_spec='spread')          # search
blp.bflds(fields=['DUR_MID', 'DV01'])    # info lookup
```
