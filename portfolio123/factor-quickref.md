# Portfolio123 Factor Quick Reference

~50 most-used factors by category. Validate via doc_detail.jsp before use. Full reference: vault file dump/Portfolio123/Portfolio123 Syntax Dictionary.md

## Valuation (Lower = Better)

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| PEExclXorTTM | P/E ratio, TTM, ex-items | Not #PE or PERatio |
| Pr2SalesTTM | Price-to-Sales TTM | Pr = Price |
| Pr2BookQ | Price-to-Book, quarterly | Prc2Book() is function form |
| Prc2Book() | Price-to-Book | Use in formulas |
| FCFYield | FCF / Market Cap | Clean cash yield |
| Pr2CashFlTTM | Price-to-Cash Flow TTM | |
| Pr2FrCashFlTTM | Price-to-Free Cash Flow TTM | |
| EV2EBITDA | Enterprise Value / EBITDA | |
| PEGRatio | P/E to Growth | |

## Quality (Higher = Better)

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| ROE%TTM | Return on Equity TTM | % in name |
| ROA%TTM | Return on Assets TTM | |
| FCFYield | Free cash flow yield | Also valuation |
| Operating Income % Chg PYQ | OI growth YoY | |
| GrossMargin%TTM | Gross margin % | |
| OperMargin%TTM | Operating margin % | |
| NetMargin%TTM | Net margin % | |
| FCFTTM | Free cash flow TTM | Raw number |
| OperCashFlQ | Operating cash flow, quarter | |
| CapExQ | Capital expenditure, quarter | FCF ≈ OperCashFlQ - CapExQ |

## Growth (Higher = Better)

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| SalesGr%TTM | Sales growth TTM | % in name |
| SalesGr%PYQ | Sales growth YoY quarter | |
| SalesGr%5Y | Sales growth 5Y | |
| EPSExclXorGr%TTM | EPS growth TTM | |
| EPSExclXorGr%PYQ | EPS growth YoY quarter | |
| EPSExclXorGr%5Y | EPS growth 5Y | |
| Operating Income % Chg TTM | OI growth TTM | |

## Momentum (Higher = Better)

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| Momentum(252) | 1-year price momentum | Bars = trading days |
| Momentum(126) | 6-month momentum | |
| Momentum(63) | 3-month momentum | |
| Momentum(20) | 20-day momentum | |
| Ret1Y%Chg | 1-year total return % | Use for TAA; TotRet(252) fails |
| 3MoRet3MoAgo | 3-month return 3 months ago | Quarterly momentum |
| 3MoRet6MoAgo | 3-month return 6 months ago | |

## Technical

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| ATR(bars) | Average True Range | ATR(14,0) typical |
| ATRN(bars) | ATR as % of price | |
| BBUpper(50,1.75,CTR) | Bollinger Band upper | In LoopSum for sell rules |
| BBLower(50,1.75,CTR) | Bollinger Band lower | |
| AvgDailyTot(20) | 20-day avg volume | Liquidity filter |
| AvgVol(noBars) | Average volume | |
| Close(0) | Current close | Price filter |
| Vol10DAvg | 10-day avg volume (millions) | |

## Estimates / Sentiment

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| AvgRec | Average recommendation 1-5 | |
| AvgRec4WkAgo | Avg rec 4 weeks ago | |
| AvgRec13WkAgo | Avg rec 13 weeks ago | |
| EPSRevis4Wk | EPS revision 4-week | |
| SalesRevis4Wk | Sales revision 4-week | |

## Strategy / Position

| P123 Name | Description | Pitfall |
|-----------|-------------|---------|
| rank | Current ranking (1-100) | In buy/sell rules |
| rankprev(1) | Rank previous period | Rank momentum: rank > rankprev(1)+10 |
| RankPos | Rank position | RankPos > 50 = sell when drops |
| gainpct | Gain % since purchase | |
| benchpct | Benchmark return % | gainpct - benchpct for relative |
| mktcap | Market cap | In millions |
| si%float | Short interest % of float | |

## Naming Conventions

- **Pr** = Price (Pr2SalesTTM, Pr2BookQ)
- **TTM, PYQ, PQ, 5Y** = Period suffixes
- **%** in name (ROE%TTM, SalesGr%TTM)
- **Gr** = Growth (SalesGr, EPSExclXorGr)

## Discovery

Always validate: https://www.portfolio123.com/doc/doc_detail.jsp?factor=[FACTOR_NAME]
