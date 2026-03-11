# Approach Explanation — CAD IG OAS Baseline Solution

## Data Fetch Strategy

The solution uses `xbbg.blp.bdh` to pull daily OAS (Option-Adjusted Spread) data from 2018-01-01 to today. Rather than hard-coding a single ticker, it defines an ordered list of seven candidate ticker/field combinations — starting with `IBXXCAIG Index` (iBoxx CAD IG) and falling back through Bloomberg Barclays variants (`LUACTRUU Index`, `I05511CA Index`, `BCACIG Index`) and spread-to-worst fields if OAS is unavailable. This fallback chain is necessary because Bloomberg index availability varies by terminal license. The fetch uses `Per="D"` (daily), `Fill="P"` (prior value carry for non-trading days), and `Days="A"` (all calendar days, letting Bloomberg filter to trading days naturally). Column names are flattened from xbbg's default MultiIndex output before the series is returned.

## Historical Context & Statistics

Once the spread series is loaded, four statistical layers are computed. First, a **multi-window historical context table** calculates min/P25/median/mean/P75/max, plus a percentile rank and z-score for the current reading vs each window (1Y, 3Y, 5Y, and full history since 2018). The z-score drives a qualitative signal: "EXTREMELY TIGHT" (z < −2), "TIGHT" (z < −1), "SLIGHTLY TIGHT", "FAIR VALUE" (|z| ≤ 0.5), "SLIGHTLY WIDE", "WIDE" (z > 1), "EXTREMELY WIDE" (z > 2). Second, a **recent moves table** shows the absolute basis-point change vs 1W, 1M, 3M, 6M, YTD, 1Y, 3Y, and 5Y ago. Third, a **regime distribution** buckets the full history into four quantile bands and shows how many trading days the market has spent in each, with the current regime highlighted. Fourth, a **50-day vs 200-day moving average** comparison gives a simple trend signal.

## Design Decisions & Limitations

The solution is intentionally self-contained with no custom classes or skill frameworks — just `xbbg`, `pandas`, `numpy`, and `scipy`. Output is printed to console with `tabulate` for readability, and the user is optionally prompted to save four CSVs. The main limitation is that it requires a live Bloomberg terminal connection; without one, all candidates will fail. The fallback list covers the most common Bloomberg CAD IG index permissioning scenarios but cannot be exhaustive — users on non-standard Bloomberg subscriptions may need to identify their specific index ticker manually using `BDP("IBXXCAIG Index", "LONG_COMP_NAME")` or the SRCH function in the terminal.
