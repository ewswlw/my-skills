# CAD IG Sector Spreads — Solution Explanation

## Approach

Used `xbbg` (`blp.bdh`) directly to fetch daily OAS spreads from Bloomberg for seven
CAD Investment Grade sector indices, then merged them into a single wide DataFrame.

---

## Index Family

All tickers reference the **BofA Merrill Lynch (BAML)** Canadian Fixed Income index
series. BAML is the dominant benchmark for Canadian IG credit research and is natively
available in Bloomberg with complete OAS history back to the early 2000s.

---

## Tickers Used

| Column | Bloomberg Ticker | Description |
|---|---|---|
| CAD_IG_All | C0A0 Index | Broad CAD IG Corporate (all sectors/ratings) |
| CAD_IG_Fins | C0FN Index | CAD IG Financials |
| CAD_IG_NonFins | C0NF Index | CAD IG Non-Financials |
| CAD_IG_Utils | C0UT Index | CAD IG Utilities |
| CAD_IG_A | C3A0 Index | CAD IG A-rated (A1/A2/A3) |
| CAD_IG_BBB | C4A0 Index | CAD IG BBB-rated |
| CAD_Provinces | CGPV Index | Canadian Provincial (quasi-sovereign) |

Alternatives are documented as inline comments in the code for cases where tickers
need validation (e.g., `CAIG1FN Index`, `C0P0 Index`).

---

## Bloomberg Field

**`OAS_SPREAD`** — Option-Adjusted Spread in basis points. This is the standard
Bloomberg field on BAML fixed income indices. A fallback to `SPREAD_TO_WORST` is
automatically attempted if the primary field returns empty for any ticker.

---

## Key Design Decisions

1. **Per-ticker error isolation** — each ticker fetches independently; failures print
   a warning and return an empty Series rather than crashing the whole pull.
2. **Field fallback** — `OAS_SPREAD` → `SPREAD_TO_WORST` per ticker.
3. **`Fill="P"` (previous)** — Bloomberg carries forward the last valid price on
   non-trading days, which is standard for index data.
4. **Forward-fill (≤5 days)** after concat to bridge any residual gaps from weekends
   or market holidays where Bloomberg doesn't emit a row.
5. **No external dependencies** beyond `xbbg` and `pandas`.

---

## Uncertainty / Caveats

- The sector sub-index tickers (`C0FN`, `C0NF`, `C0UT`) are inferred from BAML naming
  conventions. The exact identifiers should be confirmed by running
  `FLDS OAS_SPREAD` or `DES` on each ticker in the Bloomberg terminal.
- Provincial spread tickers (`CGPV Index`) may map differently depending on the
  Bloomberg subscription; `C0P0 Index` is a documented alternative.
- History depth: most BAML Canadian sub-indices have data from ~2000–2005 onwards;
  the 2010 start date should be safe.
