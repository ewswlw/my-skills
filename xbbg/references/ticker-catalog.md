# Bloomberg Ticker Catalog
<!-- Last verified: March 2026 -->
<!-- Companion to ticker-formats.md (format rules) — this file answers "which specific tickers exist and do they work?" -->

> **Scope:** US and Canadian asset classes. Commodity and global fixed income indices included where they serve as standard benchmarks. Pre-1990 data availability is noted throughout — this catalog originated from research into long-history data for backtesting.
>
> **Companion files:** `ticker-formats.md` (how to construct tickers) · `field-reference.md` (what fields to request)

---

## 1. Equity Indices

```python
# Canonical usage — price history
blp.bdh('SPX Index', 'PX_LAST', '1990-01-01', '2024-12-31')

# Total return history (use TR ticker directly)
blp.bdh('SPXT Index', 'PX_LAST', '1990-01-01', '2024-12-31')
```

### US Broad Market

| Ticker | Index Name | Inception | BBG Data From | Notes |
|---|---|---|---|---|
| `INDU Index` | Dow Jones Industrial Average | 1896 | ~1896 | 30 blue-chip stocks; oldest US index |
| `SPX Index` | S&P 500 | 1957 | ~1957 | Primary US large-cap benchmark |
| `NYA Index` | NYSE Composite | 1966 | 1966 | All NYSE-listed stocks |
| `CCMP Index` | NASDAQ Composite | 1971 | 1971 | All NASDAQ stocks; tech-heavy |
| `W5000 Index` | Wilshire 5000 Total Market | 1974 | ~1970 | Broadest US equity index |
| `RIY Index` | Russell 1000 | 1984 | ~1984 | Top 1,000 by market cap (~92% of Russell 3000) |
| `RTY Index` | Russell 2000 | 1984 | **1978-12-31** | Small-cap benchmark; back-tested before launch |
| `RAY Index` | Russell 3000 | 1984 | ~1984 | ~98% of investable US equity market |
| `NDX Index` | NASDAQ-100 | 1985 | 1985 | 100 largest non-financial NASDAQ stocks |
| `RLG Index` | Russell 1000 Growth | 1987 | ~1987 | First growth style index |
| `RLV Index` | Russell 1000 Value | 1987 | ~1987 | First value style index |

### Canada Equity Indices

| Ticker | Index Name | Inception | BBG Data From | Notes |
|---|---|---|---|---|
| `SPTSX Index` | S&P/TSX Composite | 1977 | ~1977 | Headline Canadian benchmark; ~70% of TSX market cap |

> **Excluded (post-1990 launch):** S&P MidCap 400 (1991), S&P SmallCap 600 (1994), `SPTSX60 Index` (1998), all GICS sector indices (`S5FINL Index`, `S5INFT Index`, etc. — GICS created 1999; no reliable pre-1990 history).

### US Equity Total Return Tickers (Bloomberg-Validated)

Confirmed via `bdh()` — start dates are Bloomberg's actual available history.

| Price Index | Total Return Ticker | Index Name | BBG Data From |
|---|---|---|---|
| `INDU Index` | `DJITR Index` | DJIA Total Return | **1987-09-30** |
| `SPX Index` | `SPXT Index` | S&P 500 Total Return | **1989-09-11** |
| `NYA Index` | `NYATR Index` | NYSE Composite Total Return | 2012-02-21 |
| `CCMP Index` | `XCMP Index` | NASDAQ Composite Total Return | 2003-09-25 |
| `W5000 Index` | `W5000TR Index` | Wilshire 5000 Total Return | **1970-12-31** |
| `RIY Index` | `RUITR Index` | Russell 1000 Total Return | 1995-06-01 |
| `RTY Index` | `RUTTR Index` | Russell 2000 Total Return | 1995-06-01 |
| `NDX Index` | `XNDX Index` | NASDAQ-100 Total Return | 1999-03-04 |

**Confirmed NODATA** — returned empty DataFrame on Bloomberg; do not use:

| Ticker | Description |
|---|---|
| `RUATR Index` / `RAYTR Index` | Russell 3000 Total Return (both variants) |
| `RLGTR Index` / `RLVTR Index` | Russell 1000 Growth/Value Total Return |
| `SPTSXCATR Index` / `TRGSPTSE Index` | S&P/TSX Composite Total Return (both variants) |
| `W5000FLT Index` | Wilshire 5000 Float-Adj Total Return |

---

## 2. Economic & Macro Time Series

> **Ticker format:** `MNEMONIC Index` — economic series always use the `Index` yellow key.
> **Usage:** These are time series — always use `bdh()`. Current/latest value: `bdp(ticker, 'PX_LAST')`.
> **Suffixes:** `YOY` = year-over-year · `MOM` = month-over-month · `QOQ` = quarter-over-quarter · `SA` = seasonally adjusted · `NSA` = not seasonally adjusted · `SAAR` = seasonally adjusted annual rate.

```python
# Pull a macro series — always bdh(), field is PX_LAST
blp.bdh('USURTOT Index', 'PX_LAST', '1990-01-01', '2024-12-31', Per='M', Fill='P')

# Multiple macro series together
blp.bdh(
    ['CPI YOY Index', 'USURTOT Index', 'NAPMPMI Index'],
    'PX_LAST', '2000-01-01', '2024-12-31', Per='M', Fill='P'
)
```

### US Economic Indicators

| Category | Ticker | Name | Freq | ~Data From |
|---|---|---|---|---|
| **GDP** | `GDPC% QoQ Index` | GDP QoQ % Change SAAR | Quarterly | ~1947 |
| | `GDP CUR$ Index` | GDP Current Dollars | Quarterly | ~1947 |
| | `EHGDUSY Index` | US Real GDP Annual YoY % | Quarterly | ~1947 |
| **Inflation** | `CPI YOY Index` | CPI YoY % Change | Monthly | ~1947 |
| | `CPURNSA Index` | CPI Urban Consumers NSA | Monthly | ~1947 |
| | `PPI YOY Index` | PPI YoY % Change | Monthly | ~1940s |
| | `PCE CYOY Index` | Core PCE Price Index YoY SA | Monthly | ~1959 |
| | `PCE CMOM Index` | Core PCE Price Index MoM SA | Monthly | ~1959 |
| **Labor** | `USURTOT Index` | U-3 Unemployment Rate | Monthly | ~1948 |
| | `NFP TCH Index` | Non-Farm Payrolls MoM Change | Monthly | ~1939 |
| | `USPARTIC Index` | Labor Force Participation Rate | Monthly | ~1948 |
| | `INJCJC Index` | Initial Jobless Claims | Weekly | ~1967 |
| **Consumer** | `RSTAMOM Index` | Retail Sales MoM % Change | Monthly | ~1992 |
| | `CONCCONF Index` | Conference Board Consumer Confidence | Monthly | ~1967 |
| | `PCE CRCH Index` | PCE Nominal Dollars MoM SA | Monthly | ~1959 |
| **Production** | `IP YOY Index` | Industrial Production YoY % | Monthly | ~1919 |
| | `CAPUTL Index` | Capacity Utilization | Monthly | ~1967 |
| | `IPMGCHNG Index` | IP Manufacturing MoM SA | Monthly | ~1919 |
| | `CPTICHNG Index` | Capacity Utilization % of Total | Monthly | ~1967 |
| **Manufacturing** | `NAPMPMI Index` | ISM Manufacturing PMI | Monthly | ~1948 |
| | `DGNOCHNG Index` | Durable Goods New Orders MoM SA | Monthly | ~1992 |
| | `DGNOXTCH Index` | Durable Goods ex-Transportation MoM SA | Monthly | ~1992 |
| **Services** | `NPMISERV Index` | ISM Non-Manufacturing (Services) PMI | Monthly | ~1997 |
| **Trade** | `USTBTOT Index` | Trade Balance | Monthly | ~1960s |
| **Housing** | `NHSPSTOT Index` | Housing Starts | Monthly | ~1959 |
| | `NHSPATOT Index` | Building Permits Total | Monthly | ~1960 |
| | `ETSLTOTL Index` | NAR Existing Home Sales SAAR | Monthly | ~1968 |
| | `ETSLMOM Index` | Existing Home Sales MoM SA | Monthly | ~1968 |
| | `ETSLMP Index` | NAR Existing Home Sales Median Price NSA | Monthly | ~1968 |
| | `SPCSUSAY Index` | S&P/Case-Shiller US Home Price NSA | Monthly | ~1987 |
| **Credit** | `CICRTOT Index` | Fed Consumer Credit Total Net Change SA | Monthly | ~1943 |
| **Fiscal** | `FDDSSD Index` | US Treasury Budget Deficit/Surplus NSA | Monthly | ~1940s |
| **Rates** | `FEDL01 Index` | Fed Funds Target Rate (Upper Bound) | Daily | ~1954 |
| | `USGG10YR Index` | US 10-Year Government Yield | Daily | ~1962 |
| **Business Cycle** | `LEI CHNG Index` | Conference Board US Leading Index | Monthly | ~1959 |

### Canada Economic Indicators

| Category | Ticker | Name | Freq | ~Data From |
|---|---|---|---|---|
| **GDP** | `GDPMOM% Index` | Canada GDP MoM % Change | Monthly | ~1961 |
| | `GDP..YOY Index` | Canada GDP YoY % Change | Quarterly | ~1961 |
| | `EHGDCAY Index` | Canada Real GDP Annual YoY % | Annual | ~1961 |
| **Inflation** | `CACPIYOY Index` | Canada CPI YoY % Change | Monthly | ~1914 |
| | `CACPI Index` | Canada CPI NSA | Monthly | ~1914 |
| | `CAPPIYOY Index` | Canada PPI YoY % Change | Monthly | ~1956 |
| | `CACPCMOM Index` | Canada Core CPI MoM SA | Monthly | ~1984 |
| **Labor** | `CANUEMPR Index` | Canada Unemployment Rate | Monthly | ~1976 |
| | `CANLPAR Index` | Labor Force Participation Rate | Monthly | ~1976 |
| | `CALPPROD Index` | Canada Labor Productivity QoQ SA | Quarterly | ~1981 |
| **Consumer** | `CARSL%MOM Index` | Canada Retail Sales MoM % Change | Monthly | ~1991 |
| | `BNCCCONI Index` | Bloomberg Nanos Consumer Confidence | Weekly | ~2008 |
| **Production** | `CACAPUTL Index` | Canada Industrial Capacity Utilization | Quarterly | ~1987 |
| **Manufacturing** | `CAMFCHNG Index` | Canada Manufacturing Sales MoM SA | Monthly | ~1992 |
| **Business Surveys** | `IVEPMA Index` | Ivey Purchasing Managers Index | Monthly | ~1948 |
| **Trade** | `CATRTOTL Index` | Canada Trade Balance | Monthly | ~1971 |
| **Housing** | `CAHSTARTS Index` | Housing Starts (Annualized) | Monthly | ~1948 |
| | `CAHOMOM Index` | Canada Building Permits MoM % SA | Monthly | ~1950s |
| **Rates** | `BOCLTVR Index` | Bank of Canada Target Rate | Daily | ~1996 |
| | `GCAN10YR Index` | Canada 10-Year Government Yield | Daily | ~1990s |

### Bloomberg Terminal Functions for Economic Data

| Function | Description |
|---|---|
| `ECST` | World Economic Statistics — browse by country and category |
| `WECO` | Economic Calendars by Country — upcoming data releases |
| `ECFC` | Economic Forecasts — consensus forecasts |
| `ECMX` | Global Economic Matrix — compare indicators across countries |

---

## 3. Commodities & Fixed Income Indices

```python
# Fixed income index — total return series via bdh()
blp.bdh('LBUSTRUU Index', 'PX_LAST', '1990-01-01', '2024-12-31', Per='M', Fill='P')

# Commodity index
blp.bdh('CRYTR Index', 'PX_LAST', '1970-01-01', '2024-12-31')
```

### Commodity Total Return Indices

| Ticker | Index Name | Data From | Notes |
|---|---|---|---|
| `CRYTR Index` | FTSE/CoreCommodity CRB Total Return | **1957** | Only major broad commodity index with pre-1990 history; 19 commodities across energy, agriculture, metals |
| `SPGSCITR Index` | S&P GSCI Total Return | 1991-04-11 | First major investable commodity index; launched post-1990 |
| `BCOM Index` | Bloomberg Commodity Index (price return) | ~1960 (back-filled) | Index created 1998; back-tested data to 1960 but not a live pre-1990 track record |

### US Fixed Income Total Return Indices

| Ticker | Index Name | Data From | Notes |
|---|---|---|---|
| `LBUSTRUU Index` | Bloomberg US Aggregate Bond Total Return (USD Unhedged) | **1976-01-01** | Flagship US investment-grade benchmark; covers govt, corporate, MBS; created 1986 with back-fill |
| `LUATTRUU Index` | Bloomberg US Treasury Total Return (USD Unhedged) | **1973** | US dollar fixed-rate nominal Treasury debt, ≥1yr maturity |
| `LF98TRUU Index` | Bloomberg US High Yield Total Return | post-1990 | US HY benchmark |
| `LTR1TRUU Index` | Bloomberg US Treasury 1–5 Year Total Return | post-1990 | Short-duration Treasury sub-index |

### Canada Fixed Income Total Return Indices

| Ticker | Index Name | Data From | Notes |
|---|---|---|---|
| `I05486CA Index` | Bloomberg Canada Aggregate Total Return | **1980** | Benchmark for Canadian investment-grade (govt + corporate) |

> **FTSE Canada Universe Bond Index (1979):** Widely used Canadian IG benchmark but a specific total return ticker is not confirmed available in Bloomberg — verify on terminal via `FLDS`.

### Gold & Precious Metals

> **No gold/precious metals total return indices have pre-1990 data.** COMEX gold futures began 1974-12-31; TR indices require futures markets and were created post-1991.

| Ticker | Index Name | Data From | Notes |
|---|---|---|---|
| `SPGSGCTR Index` | S&P GSCI Gold Total Return | **1991-05-01** | Earliest available gold TR index |
| `SPGSPMTR Index` | S&P GSCI Precious Metals Total Return | **1991-05-01** | Earliest available precious metals TR index |
| `BCOMGCTR Index` | Bloomberg Commodity Gold Subindex TR | 1998 | Part of BCOM launch |
| `BCOMPRTR Index` | Bloomberg Commodity Precious Metals Subindex TR | 1998 | Part of BCOM launch |

**Spot gold (price only — no roll or collateral yield):**

| Source | Data From | Bloomberg Access |
|---|---|---|
| London Gold Fixing | **1919** | `GOLDLNPM Index` (PM fix) |
| COMEX Gold Spot | 1974 | `GC1 Comdty` (front futures) |

---

## 4. Mutual Funds (Pre-1990 Inception)

> **Format:** US-domiciled mutual funds use `TICKER:US` (e.g., `VFINX:US`).
> **Use case:** Long-history asset class proxies for back-testing tactical allocation models.

```python
# Mutual fund NAV history — use bdh() with PX_LAST
blp.bdh('VFINX:US', 'PX_LAST', '1976-01-01', '2024-12-31', adjust='all')
```

| Ticker | Fund Name | Inception | Asset Class |
|---|---|---|---|
| `MITTX:US` | MFS Massachusetts Investors Trust | **1924** | US Large Cap Blend — oldest US mutual fund |
| `PINVX:US` | Putnam Investors Fund | 1925 | US Large Cap Blend |
| `PIODX:US` | Pioneer Fund | 1928 | US Large Cap Blend |
| `DODIX:US` | Dodge & Cox Income Fund | 1928 | US Fixed Income |
| `LOMMX:US` | CGM Mutual Fund | 1929 | US Large Cap Blend |
| `VWELX:US` | Vanguard Wellington Fund | **1929** | Balanced (US Equity/Bond) — 60/40 back-test proxy |
| `OTCFX:US` | T. Rowe Price Small-Cap Stock Fund | 1956 | US Small Cap Growth |
| `VWNDX:US` | Vanguard Windsor Fund | 1958 | US Large Cap Value |
| `FBNDX:US` | Fidelity Investment Grade Bond Fund | 1971 | US Investment Grade Bonds |
| `VFINX:US` | Vanguard 500 Index Fund | **1976** | US Large Cap Index — first index fund |
| `VWIGX:US` | Vanguard International Growth Fund | 1981 | International Large Cap Growth |
| `MIEBX:US` | MFS International Bond Fund | 1986 | Global Bond |
| `MADCX:US` | BlackRock Emerging Markets Fund | 1989 | Emerging Markets Equity |

### Coverage Gaps (No Pre-1990 Funds Available)

| Asset Class | Earliest Available | Notes |
|---|---|---|
| REITs / Real Estate | `CSRSX:US` — 1991 | Cohen & Steers Realty Shares; first dedicated REIT fund |
| High Yield Bonds | `SPHIX:US` — August 1990 | Fidelity High Income; just misses pre-1990 cutoff |
| Commodities | post-2000 | Dedicated commodity mutual funds are a post-2000 innovation |
