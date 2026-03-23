# P123 Fundamental Data Reference

**Exhaustive catalog:** The Obsidian vault note `file dump/Portfolio123/Portfolio123 Syntax Dictionary.md` mirrors the full platform lookup (hundreds of entries by category). Use it—or `doc_detail.jsp?factor=NAME`—when a pre-built name is not in this file or [factor-quickref.md](../factor-quickref.md).

All fundamental items follow the same pattern:

```
FunctionName(offset, periodType [, NAHandling])
```
- **offset**: 0=most recent, 1=one period back, ... (0-20 for QTR, 0-10 for ANN)
- **periodType**: `QTR` (quarterly), `ANN` (annual), `TTM` (trailing 12 months)
- **NAHandling**: `FALLBACK` (default), `KEEPNA`, `ZERONA`

Each item also generates pre-built factors (no parentheses): see Pattern Guide at bottom.

---

## Balance Sheet — Current Assets

| Function | Description |
|----------|-------------|
| `Cash(offset, type)` | Cash only |
| `CashEquiv(offset, type)` | Cash and equivalents (cash + short-term investments) |
| `Recvbl(offset, type)` | Accounts receivable (net of allowances) |
| `Inventory(offset, type)` | Inventories |
| `AstCurOther(offset, type)` | Other current assets |
| `AstCur(offset, type)` | Total current assets |
| `PrepaidExp(offset, type)` | Prepaid expenses |

## Balance Sheet — Non-Current Assets

| Function | Description |
|----------|-------------|
| `GrossPlant(offset, type)` | Gross property, plant & equipment |
| `AccumDep(offset, type)` | Accumulated depreciation |
| `NetPlant(offset, type)` | Net PP&E (GrossPlant - AccumDep) |
| `Goodwill(offset, type)` | Goodwill |
| `AstIntan(offset, type)` | Intangible assets |
| `AstNonCurOther(offset, type)` | Other non-current assets |
| `EquityInvest(offset, type)` | Equity investments |
| `AstTot(offset, type)` | **Total assets** |

## Balance Sheet — Current Liabilities

| Function | Description |
|----------|-------------|
| `Payables(offset, type)` | Accounts payable |
| `AccruedExp(offset, type)` | Accrued expenses |
| `LiabCurOther(offset, type)` | Other current liabilities |
| `LiabCur(offset, type)` | Total current liabilities |

## Balance Sheet — Non-Current Liabilities

| Function | Description |
|----------|-------------|
| `LTDebt(offset, type)` | Long-term debt |
| `TotDebt(offset, type)` | Total debt (current + long-term) |
| `CapLease(offset, type)` | Capital lease obligations |
| `DefTaxInvCr(offset, type)` | Deferred taxes & investment credits |
| `LiabTot(offset, type)` | **Total liabilities** |

## Balance Sheet — Shareholders' Equity

| Function | Description |
|----------|-------------|
| `ComEq(offset, type)` | Common equity |
| `BookVal(offset, type)` | Book value |
| `RetainedEarn(offset, type)` | Retained earnings |
| `PrefEq(offset, type)` | Preferred equity |
| `CapSurplus(offset, type)` | Capital surplus (additional paid-in capital) |
| `NonConInt(offset, type)` | Non-controlling interest |

## Balance Sheet — Shares

| Function | Description |
|----------|-------------|
| `ShOut(offset, type)` | Common shares outstanding |
| `ShOutDil(offset, type)` | Fully diluted shares |
| `ShOutMR` | Most recent shares outstanding |

## Derived Balance Sheet

| Function | Description |
|----------|-------------|
| `WorkCap(offset, type)` | Working capital (AstCur - LiabCur) |
| `NetDebt(offset, type)` | Net debt (TotDebt - CashEquiv) |
| `TangBV(offset, type)` | Tangible book value (BookVal - Goodwill - AstIntan) |

---

## Income Statement

| Function | Description |
|----------|-------------|
| `Sales(offset, type)` | **Revenue / Net sales** |
| `COGS(offset, type)` | Cost of goods sold (GAAP) |
| `GrProfit(offset, type)` | Gross profit (GAAP) |
| `SGA(offset, type)` | Selling, general & administrative |
| `RandD(offset, type)` | Research & development |
| `OpInc(offset, type)` | **Operating income** |
| `EBIT(offset, type)` | Earnings before interest and taxes |
| `EBITDA(offset, type)` | EBITDA |
| `IntExp(offset, type)` | Interest expense |
| `PreTaxInc(offset, type)` | Pre-tax income |
| `IncomeTax(offset, type)` | Income tax expense |
| `NetInc(offset, type)` | **Net income** |
| `NetIncBXor(offset, type)` | Net income before extraordinary items |
| `NetIncCommon(offset, type)` | Net income available to common |
| `EPS(offset, type)` | Earnings per share |
| `EPSDil(offset, type)` | Diluted EPS |
| `DPS(offset, type)` | Dividends per share |
| `DepAmort(offset, type)` | Depreciation & amortization |
| `Amort(offset, type)` | Amortization of intangibles |
| `FFO(offset, type)` | Funds from operations (REITs) |
| `StockComp(offset, type)` | Stock-based compensation |
| `PrefDiv(offset, type)` | Preferred dividends |

---

## Cash Flow Statement

### Operating
| Function | Description |
|----------|-------------|
| `OpCashFl(offset, type)` | **Operating cash flow** |
| `ChgAccrIncTax(offset, type)` | Change in accrued income taxes |
| `ChgRecvbl(offset, type)` | Change in receivables |
| `ChgInv(offset, type)` | Change in inventories |
| `ChgOtherWC(offset, type)` | Change in other working capital |

### Investing
| Function | Description |
|----------|-------------|
| `CapEx(offset, type)` | **Capital expenditures** |
| `CashFrInvest(offset, type)` | Cash from investing |
| `Acquis(offset, type)` | Acquisitions |
| `Divest(offset, type)` | Divestitures |
| `OtherInvCF(offset, type)` | Other investing cash flow |

### Financing
| Function | Description |
|----------|-------------|
| `CashFrFin(offset, type)` | Cash from financing |
| `ChangeDebt(offset, type)` | Change in debt |
| `ChangeEq(offset, type)` | Change in equity |
| `EqPurch(offset, type)` | Equity purchased (buybacks) |
| `LTDebtIssued(offset, type)` | Long-term debt issued |
| `LTDebtReduc(offset, type)` | Long-term debt reduction |

### Summary
| Function | Description |
|----------|-------------|
| `CashFl(offset, type)` | Total cash flow |
| `FCF(offset, type)` | **Free cash flow** (OpCashFl - CapEx) |
| `NFCF(offset, type)` | Net free cash flow |
| `NetChgCash(offset, type)` | Net change in cash position |

---

## Key Pre-Built Ratios & Statistics

### Valuation
| Factor | Description |
|--------|-------------|
| `PEExclXorTTM` | **P/E excluding extraordinary items (TTM)** |
| `PEExclXorA` | P/E excluding extraordinary items (Annual) |
| `PEInclXorTTM` | P/E including extraordinary items |
| `Pr2BookQ` | **Price to book (quarterly)** |
| `Pr2SalesTTM` | **Price to sales (TTM)** |
| `Pr2SalesQ` | Price to sales (quarterly) |
| `Pr2CashFlTTM` | Price to cash flow (TTM) |
| `Pr2FCFTTM` | **Price to free cash flow (TTM)** |
| `Pr2TangBVQ` | Price to tangible book value |
| `EVToEBITDATTM` | **EV/EBITDA (TTM)** |
| `EVToEBITTTM` | EV/EBIT (TTM) |
| `EVToSalesTTM` | EV/Sales (TTM) |
| `EVToFCFTTM` | EV/FCF (TTM) |
| `DivYield%TTM` | **Dividend yield (TTM)** |
| `ShrYield%TTM` | Shareholder yield (div + buyback) |
| `EarnYield%TTM` | Earnings yield (inverse of PE) |

### Profitability
| Factor | Description |
|--------|-------------|
| `ROE%TTM` | **Return on equity (TTM)** |
| `ROA%TTM` | **Return on assets (TTM)** |
| `ROIC%TTM` | Return on invested capital |
| `GrMgn%TTM` | **Gross margin (TTM)** |
| `OpMgn%TTM` | **Operating margin (TTM)** |
| `NetMgn%TTM` | Net margin (TTM) |
| `AstTurn(0, TTM)` | Asset turnover |

### Growth
| Factor | Description |
|--------|-------------|
| `SalesGr%TTM` | **Sales growth (TTM vs prior TTM)** |
| `SalesGr%A` | Sales growth (annual) |
| `SalesGr%PYQ` | Sales growth (quarter vs prior year quarter) |
| `EPSGr%TTM` | EPS growth (TTM) |
| `OpIncGr%TTM` | Operating income growth |
| `EBITDAGr%TTM` | EBITDA growth |
| `FCFGr%TTM` | Free cash flow growth |

### Quality / Accruals
| Factor | Description |
|--------|-------------|
| `AccrualsTTM` | Accruals (TTM) |
| `Accruals%AstTTM` | Accruals / Total assets |
| `DebtToEqQ` | Debt to equity |
| `CurRatioQ` | Current ratio |
| `QuickRatioQ` | Quick ratio |
| `IntCov%TTM` | Interest coverage |
| `AltmanZ` | Altman Z-score |

### Market / Price
| Factor | Description |
|--------|-------------|
| `MktCap` | **Market capitalization** |
| `EntVal` | Enterprise value |
| `Beta` | Beta (60-month) |
| `AvgDailyTot(N)` | Avg daily dollar volume over N bars |
| `ShortInt%` | Short interest ratio |
| `InsiderBuySell%3Mo` | Insider buy/sell ratio (3 month) |
| `InstOwn%` | Institutional ownership % |

### Estimates
| Factor | Description |
|--------|-------------|
| `EstEPSCQ` | EPS estimate current quarter |
| `EstEPSNQ` | EPS estimate next quarter |
| `EstEPSCY` | EPS estimate current year |
| `EstEPSNY` | EPS estimate next year |
| `EstEPSGr%NQ` | Estimated EPS growth next quarter |
| `EstEPSGr%NY` | Estimated EPS growth next year |
| `NumEstEPSCQ` | Number of analyst estimates CQ |
| `EPSSurprise%CQ` | EPS surprise % current quarter |
| `SumRevisions` | Sum of EPS revisions |
| `EstSalesCY` | Sales estimate current year |
| `EstSalesNY` | Sales estimate next year |
| `AvgRec` | Average analyst recommendation (1-5) |
| `LTGrRt` | Long-term EPS growth rate estimate |

---

## Pre-Built Factor Naming Pattern

For any base function `Item`, P123 auto-generates factors:

| Suffix | Meaning | Example |
|--------|---------|---------|
| `Q` | Most recent quarter | `SalesQ` |
| `A` | Most recent annual | `SalesA` |
| `TTM` | Trailing 12 months | `SalesTTM` |
| `PQ` | Previous quarter | `SalesPQ` |
| `PY` | Previous year | `SalesPY` |
| `PYQ` | Previous year same quarter | `SalesPYQ` |
| `PTM` | Previous trailing 12 months | `SalesPTM` |
| `Gr%TTM` | Growth TTM vs prior TTM | `SalesGr%TTM` |
| `Gr%A` | Growth annual vs prior annual | `SalesGr%A` |
| `Gr%PQ` | Growth QoQ | `SalesGr%PQ` |
| `Gr%PYQ` | Growth Q vs prior year Q (YoY) | `SalesGr%PYQ` |
| `Gr%PQTTM` | Growth in TTM vs prior Q TTM | `SalesGr%PQTTM` |
| `Gr%3Y` | 3-year CAGR | `SalesGr%3Y` |
| `Gr%5Y` | 5-year CAGR | `SalesGr%5Y` |
| `Gr%10Y` | 10-year CAGR | `SalesGr%10Y` |
| `PSA` | Per share (annual) | `SalesPSA` |
| `PSQ` | Per share (quarterly) | `SalesPSQ` |
| `%AssetsA` | As % of assets (annual) | `Sales%AssetsA` |
| `%AssetsQ` | As % of assets (quarterly) | `Sales%AssetsQ` |
| `%SalesA` | As % of sales (annual) | `CapEx%SalesA` |
| `%SalesQ` | As % of sales (quarterly) | `CapEx%SalesQ` |
| `3YAvg` | 3-year average | `Sales3YAvg` |
| `5YAvg` | 5-year average | `Sales5YAvg` |
| `RegGr%ANN` | Regression growth (annual) | `SalesRegGr%ANN` |
| `RegGr%TTM` | Regression growth (TTM) | `SalesRegGr%TTM` |
| `RSD%ANN` | Regression residual std dev (annual) | `SalesRSD%ANN` |
| `RegEstANN` | Regression estimate (annual) | `SalesRegEstANN` |

---

## Company / Classification

| Factor | Description |
|--------|-------------|
| `SectorId` | GICS sector code (10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60) |
| `IndustryId` | GICS industry code (8-digit) |
| `SubIndId` | GICS sub-industry code |
| `ExchCountry` | Exchange country |
| `Country` | Country of domicile |
| `FYEndMonth` | Fiscal year end month |
| `Employees` | Number of employees |
| `CoName("name")` | Match company name (returns TRUE/FALSE) |

**GICS Sectors**: 10=Energy, 15=Materials, 20=Industrials, 25=Consumer Disc, 30=Consumer Staples, 35=Health Care, 40=Financials, 45=Info Tech, 50=Communication, 55=Utilities, 60=Real Estate
