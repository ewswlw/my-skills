---
name: vectorbt-tearsheet
description: >
  Build a tables-only performance tearsheet using vectorbt and tabulate. Generates up to 14 plain-text tables covering portfolio stats, returns, trades, risk metrics, drawdowns, and more. Use when the user asks for a "vectorbt tearsheet", "portfolio tearsheet", "performance tables", or a detailed, text-based backtest report from a `vbt.Portfolio` object.
---

# Vectorbt Tearsheet Builder

This skill guides the creation of a reusable, tables-only tearsheet from a `vbt.Portfolio` object. It produces up to 14 plain-text tables using `tabulate` for clean, readable output.

**Key Constraints:**
- **No charts or plots**: The output is strictly tables-only.
- **`tabulate` for output**: Ensures clean, plain-text tables that are never truncated.
- **Open-source `vectorbt`**: Does not require `vectorbt pro`.

## Core Workflow

1.  **Install Dependencies**: Install `vectorbt`, `tabulate`, and `quantstats`.
2.  **Structure the Project**: Create a `tearsheet.py` module for the core logic.
3.  **Implement the Tearsheet**: Build the `generate_tearsheet` function, creating each of the 14 tables listed in the **Table Summary** below.
4.  **Handle Edge Cases**: Implement logic to gracefully handle scenarios like no trades or a missing benchmark.
5.  **Validate**: Test the tearsheet against the test specifications.

---

## 1. Install Dependencies

Install the required libraries into the system environment.

```bash
uv add vectorbt tabulate pandas numpy quantstats
```

---

## 2. Structure the Project

Organize the code into a module for reusability. Create the project folder alongside your strategy code — typically inside the vault's Coding Projects directory:

```
C:\Users\Eddy\Documents\Obsidian Vault\Coding Projects\[your-strategy]\
├── tearsheet.py          # Core tearsheet module (all logic)
└── run_tearsheet.py      # Example script to run the tearsheet
```

Run with:
```bash
uv run python run_tearsheet.py
```

---

## 3. Implement the Tearsheet

Create the main `generate_tearsheet` function in `tearsheet.py`. The goal is to produce a series of formatted text tables.

### Table Summary

Your implementation must generate the following 14 tables. For a detailed breakdown of which metrics are native to `vectorbt` and which require custom computation, you **MUST** read `references/api-reference.md` and `references/custom-metrics.md` in this skill's folder.

1.  **Portfolio Stats**: Overall performance metrics.
2.  **Returns Stats**: In-depth return analysis.
3.  **Trades Stats**: Statistics on individual trades.
4.  **Risk & Benchmark Metrics**: Alpha, Beta, CVaR, etc.
5.  **Drawdowns Stats**: Analysis of portfolio drawdowns.
6.  **Signals Stats**: Statistics on the entry signals.
7.  **Trade-by-Trade Log**: A detailed log of every trade.
8.  **Period Returns**: MTD, YTD, 1Y, 3Y, etc.
9.  **Extremes**: Best/worst day, month, and year.
10. **Drawdown Details**: Avg drawdown, recovery factor, etc.
11. **Win Rate Breakdown**: Win rates by day, month, quarter, year.
12. **Monthly Returns Grid**: A pivot table of monthly returns.
13. **Top 5 Drawdown Episodes**: Details on the 5 worst drawdowns.
14. **Rolling Performance**: Rolling Sharpe, Sortino, and Volatility.

### Plain Text Formatting

Use the `tabulate` library with `tablefmt="simple"` for all tables. Format data as follows:
-   **Percentages**: `f"{value:.2%}"` (e.g., `"12.48%"`)
-   **Ratios**: `f"{value:.2f}"` (e.g., `"1.61"`)
-   **Currency**: `f"${value:,.2f}"` (e.g., `"$10,672.16"`)

---

## 4. Handling Edge Cases

Your `generate_tearsheet` function must be robust.

-   **If `benchmark_rets` is `None`**: Omit the "Benchmark" column from all tables.
-   **If `pf.trades.count` is 0**: Gracefully skip trade-related tables (3, 7, 11) and print a message like "No trades were executed."
-   **If data history is too short**: For period returns (Table 8), display `"N/A"` for any period longer than the available data.

---

## 5. Validate

Before delivering the tearsheet, ensure it is robust by testing it against various scenarios. The `references/test-spec.md` file in this skill's folder provides a detailed list of test cases to consider.

---

## Windows/Cursor Compatibility Notes

- Install command changed: `uv add` replaces `sudo uv pip install --system`.
- Project structure path changed from `/home/ubuntu/your-project/` to a relative `your-project/` directory.
- All reference file paths changed to relative form: `references/[file].md` in this skill's folder.
- Run the tearsheet with: `uv run python tearsheet.py`
