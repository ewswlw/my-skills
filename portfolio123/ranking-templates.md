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
