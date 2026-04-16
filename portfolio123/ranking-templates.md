# Portfolio123 Ranking System Templates

5 XML templates, validation checklist, factor discovery protocol, universe creation patterns.

## XML Validation Checklist

- [ ] Every node has unique `Name` attribute
- [ ] Every node has `RankType` ("Higher" or "Lower")
- [ ] StockFormula nodes have `Scope="Universe"`
- [ ] Weights in composite sum to exactly 100
- [ ] Use `<StockFormula>` not `<StockFactor>`
- [ ] Label starts with `agent`

## Factor Discovery Protocol

**Always use:** https://www.portfolio123.com/doc/doc_detail.jsp?factor=[FACTOR_NAME]

1. Navigate to doc_detail.jsp with factor name
2. Extract exact prebuilt ratio/function name
3. Use exact name in XML
4. Test one factor at a time

**Never guess.** Wrong: #PE, Prc2FCFY. Right: PEExclXorTTM, FCFYield.

## Template 1: Value

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_value_root" Weight="100" Label="agent value combo" RankType="Higher">
    <StockFormula Name="pe" RankType="Lower" Scope="Universe" Weight="33" Label="P/E TTM">
      <Formula>PEExclXorTTM</Formula>
    </StockFormula>
    <StockFormula Name="pb" RankType="Lower" Scope="Universe" Weight="33" Label="Price/Book">
      <Formula>Prc2Book()</Formula>
    </StockFormula>
    <StockFormula Name="ps" RankType="Lower" Scope="Universe" Weight="34" Label="Price/Sales">
      <Formula>Pr2SalesTTM</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

## Template 2: Momentum

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_momentum_root" Weight="100" Label="agent momentum combo" RankType="Higher">
    <StockFormula Name="mom_1y" RankType="Higher" Scope="Universe" Weight="50" Label="1Y Momentum">
      <Formula>Momentum(252)</Formula>
    </StockFormula>
    <StockFormula Name="mom_6m" RankType="Higher" Scope="Universe" Weight="50" Label="6M Momentum">
      <Formula>Momentum(126)</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

## Template 3: Quality

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_quality_root" Weight="100" Label="agent quality combo" RankType="Higher">
    <StockFormula Name="roe" RankType="Higher" Scope="Universe" Weight="33" Label="ROE">
      <Formula>ROE%TTM</Formula>
    </StockFormula>
    <StockFormula Name="roa" RankType="Higher" Scope="Universe" Weight="33" Label="ROA">
      <Formula>ROA%TTM</Formula>
    </StockFormula>
    <StockFormula Name="fcf" RankType="Higher" Scope="Universe" Weight="34" Label="FCF Yield">
      <Formula>FCFYield</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

## Template 4: Growth

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_growth_root" Weight="100" Label="agent growth combo" RankType="Higher">
    <StockFormula Name="sales_gr" RankType="Higher" Scope="Universe" Weight="50" Label="Sales Growth">
      <Formula>SalesGr%TTM</Formula>
    </StockFormula>
    <StockFormula Name="eps_gr" RankType="Higher" Scope="Universe" Weight="50" Label="EPS Growth">
      <Formula>EPSExclXorGr%TTM</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

## Template 5: AI Factor

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_ai_root" Weight="100" Label="agent AI Factor Ranking" RankType="Higher">
    <StockFormula Name="ai_validation" RankType="Higher" Scope="Universe" Weight="100" Label="AI Factor - Validation">
      <Formula>FRank(AIFactorValidation("AI Factor Name", "Model Name"))</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

Replace "AI Factor Name" and "Model Name" with exact names (case-sensitive). Enable "Save Predictions" during validation first.

## Template 6: Multifactor Composite (Value + Technical Momentum + Fundamental Momentum)

Three equal-weight top-level composites, each internally 1/N. This is the most common real-world multifactor pattern. Validate all factor names via `doc_detail.jsp` before use.

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_value" Weight="33" Label="Value Composite" RankType="Higher">
    <StockFormula Name="fcf_yield" RankType="Higher" Scope="Universe" Weight="17" Label="FCF Yield">
      <Formula>FCFYield</Formula>
    </StockFormula>
    <StockFormula Name="earn_yield" RankType="Higher" Scope="Universe" Weight="17" Label="Earnings Yield">
      <Formula>Eval(IsNA(PEExclXorTTM), 0, 1/PEExclXorTTM)</Formula>
    </StockFormula>
    <StockFormula Name="ebitda_yield" RankType="Lower" Scope="Universe" Weight="17" Label="EV/EBITDA">
      <Formula>EV2EBITDA</Formula>
    </StockFormula>
    <StockFormula Name="pb" RankType="Lower" Scope="Universe" Weight="16" Label="Price/Book">
      <Formula>Prc2Book()</Formula>
    </StockFormula>
    <StockFormula Name="ps" RankType="Lower" Scope="Universe" Weight="16" Label="Price/Sales">
      <Formula>Pr2SalesTTM</Formula>
    </StockFormula>
    <StockFormula Name="fwd_pe" RankType="Lower" Scope="Universe" Weight="17" Label="Forward PE">
      <Formula>Eval(IsNA(ConsEstMean(#EPS,#CY)), PEExclXorTTM, Close(0)/ConsEstMean(#EPS,#CY))</Formula>
    </StockFormula>
  </Composite>
  <Composite Name="agent_tech_mom" Weight="34" Label="Technical Momentum Composite" RankType="Higher">
    <StockFormula Name="mom_12m" RankType="Higher" Scope="Universe" Weight="25" Label="12M Momentum">
      <Formula>Momentum(252)</Formula>
    </StockFormula>
    <StockFormula Name="mom_6m" RankType="Higher" Scope="Universe" Weight="25" Label="6M Momentum">
      <Formula>Momentum(126)</Formula>
    </StockFormula>
    <StockFormula Name="mom_sharpe" RankType="Higher" Scope="Universe" Weight="25" Label="12M Sharpe">
      <Formula>Momentum(252)/Volatility(252)</Formula>
    </StockFormula>
    <StockFormula Name="mom_accel" RankType="Higher" Scope="Universe" Weight="25" Label="Momentum Acceleration">
      <Formula>Momentum(126) - Momentum(252)</Formula>
    </StockFormula>
  </Composite>
  <Composite Name="agent_fund_mom" Weight="33" Label="Fundamental Momentum Composite" RankType="Higher">
    <StockFormula Name="piotrosky" RankType="Higher" Scope="Universe" Weight="25" Label="Piotrosky F-Score">
      <Formula>PiotroskiScore</Formula>
    </StockFormula>
    <StockFormula Name="sales_gr" RankType="Higher" Scope="Universe" Weight="25" Label="Sales Growth TTM">
      <Formula>SalesGr%TTM</Formula>
    </StockFormula>
    <StockFormula Name="fcf_gr" RankType="Higher" Scope="Universe" Weight="25" Label="FCF Growth">
      <Formula>Eval(FCFTTM > 0, FCFTTM / Eval(IsNA(FHist("FCFTTM",4,13)), FCFTTM, Abs(FHist("FCFTTM",4,13))+1) - 1, -1)</Formula>
    </StockFormula>
    <StockFormula Name="eps_revis" RankType="Higher" Scope="Universe" Weight="25" Label="EPS Revision">
      <Formula>EPSRevis4Wk</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

**Design rules (1/N discipline):** Keep top-level siblings at equal weight (33/34/33) unless you have documented, out-of-sample evidence for asymmetry. Deviating from 1/N to pump a backtest is a known overfitting pattern.

## Template 7: Short-Side Ranking

Inverted orientation — higher rank = better short candidate. Use with short-side Strategy; target large, liquid names for borrow availability.

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_short_value" Weight="20" Label="Expensive Value (Short)" RankType="Higher">
    <StockFormula Name="high_pe" RankType="Higher" Scope="Universe" Weight="50" Label="High PE">
      <Formula>PEExclXorTTM</Formula>
    </StockFormula>
    <StockFormula Name="low_fcf_yield" RankType="Lower" Scope="Universe" Weight="50" Label="Low FCF Yield">
      <Formula>FCFYield</Formula>
    </StockFormula>
  </Composite>
  <Composite Name="agent_short_mom" Weight="20" Label="Weak Momentum (Short)" RankType="Higher">
    <StockFormula Name="weak_12m" RankType="Lower" Scope="Universe" Weight="50" Label="Weak 12M Momentum">
      <Formula>Momentum(252)</Formula>
    </StockFormula>
    <StockFormula Name="weak_6m" RankType="Lower" Scope="Universe" Weight="50" Label="Weak 6M Momentum">
      <Formula>Momentum(126)</Formula>
    </StockFormula>
  </Composite>
  <Composite Name="agent_short_fund" Weight="20" Label="Weak Fundamentals (Short)" RankType="Higher">
    <StockFormula Name="low_piotrosky" RankType="Lower" Scope="Universe" Weight="50" Label="Low Piotrosky">
      <Formula>PiotroskiScore</Formula>
    </StockFormula>
    <StockFormula Name="down_revisions" RankType="Lower" Scope="Universe" Weight="50" Label="EPS Revisions Down">
      <Formula>EPSRevis4Wk</Formula>
    </StockFormula>
  </Composite>
  <Composite Name="agent_short_quality" Weight="20" Label="Low Quality (Short)" RankType="Higher">
    <StockFormula Name="low_roe" RankType="Lower" Scope="Universe" Weight="50" Label="Low ROE">
      <Formula>ROE%TTM</Formula>
    </StockFormula>
    <StockFormula Name="low_margin" RankType="Lower" Scope="Universe" Weight="50" Label="Low Gross Margin">
      <Formula>GrossMargin%TTM</Formula>
    </StockFormula>
  </Composite>
  <Composite Name="agent_short_size" Weight="20" Label="Large and Liquid (Short Borrow)" RankType="Higher">
    <StockFormula Name="large_cap" RankType="Higher" Scope="Universe" Weight="50" Label="Large Cap">
      <Formula>MktCap</Formula>
    </StockFormula>
    <StockFormula Name="high_adv" RankType="Higher" Scope="Universe" Weight="50" Label="High Daily Volume">
      <Formula>AvgDailyTot(20)</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

**Notes:**
- Short universe should target the **largest ~1500 stocks** by market cap (~$7B+ in 2020s terms) — borrow is available and cost is low
- Add **~50% ML weight** blended with classic for short side (shorter horizon target variable than long book)
- Add extra liquidity buy rule in Strategy: `AvgDailyTot(20) > 100000`
- Short strategy costs: **1% carry** + variable slippage

## Ranking Sub-Patterns

### Liquidity Composite (as ranking sub-component)

Liquidity can be added as a sub-composite inside a multifactor ranking system (not only as a hard universe filter). This captures relative liquidity preference while the universe filter still sets the minimum floor.

**Key finding:** Standalone liquidity ranking does **not** survive slippage; its value is inside a multifactor blend. When using, also enable **"Force positions into universe"** in the Simulated Strategy settings — this prevents forced sells when a stock temporarily falls out of a liquidity-based universe screen at a check date.

```xml
<Composite Name="agent_liquidity" Weight="10" Label="Liquidity + Size" RankType="Higher">
  <StockFormula Name="adv_rank" RankType="Higher" Scope="Universe" Weight="50" Label="50-Day ADV Rank">
    <Formula>FRank("AvgDailyTot(50)", #All, #Desc)</Formula>
  </StockFormula>
  <StockFormula Name="size_rank" RankType="Higher" Scope="Universe" Weight="50" Label="Market Cap Rank">
    <Formula>FRank("MktCap", #All, #Desc)</Formula>
  </StockFormula>
</Composite>
```

Add this as a sibling composite inside Template 6 (e.g., with 10% weight, reducing each other block to 30/30/30).

### Regional Universe Patterns

Use `Country()` in universe rules to create regional sub-strategies for ML specialization.

```text
// Global (base) — no country filter
// US only
Country("USA")
// Ex-US only
!Country("USA")
```

**Note:** Regional splits (US / Ex-US) typically **hurt** simple multifactor metrics vs. a single global 30-stock strategy — fewer names increases idiosyncratic noise. The primary rationale for splitting is **ML model specialization**: training on a homogeneous regional universe allows the model to learn regional "dialects" of factor behavior more cleanly.

## Universe Creation (Stock)

**API XML structure:**
```xml
<Universe>
  <Rules>
    <Rule><Type>MarketCap</Type><Operator>>=</Operator><Value>1000000000</Value></Rule>
    <Rule><Type>Region</Type><Operator>=</Operator><Value>US</Value></Rule>
    <Rule><Type>AvgDailyTot</Type><Operator>>=</Operator><Value>1000000</Value></Rule>
  </Rules>
</Universe>
```

## Universe Creation (ETF)

Use Ticker function: `Ticker("SPY,EFA,AGG")` — comma-separated, no spaces.

**Templates:** US Large Cap (mktcap >= 10B), US Small Cap (mktcap 300M-2B), Canada (Region=Canada), Easy to Trade (AvgDailyTot >= 100k).

## GUI-First, XML Fallback

Try GUI first. After 2 failures (Add Node timeout, spinner), use raw editor: click "raw editor (no ajax)", paste XML, save.
