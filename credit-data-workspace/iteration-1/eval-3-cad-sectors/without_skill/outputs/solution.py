"""
CAD IG Sector Spread Comparison
================================
Fetches daily OAS spreads for Canadian Investment Grade sector indices
from Bloomberg via xbbg (blp.bdh), merging into a single DataFrame.

Sectors covered:
  - CAD IG Financials
  - CAD IG Non-Financials
  - CAD IG Utilities
  - CAD IG A-rated
  - CAD IG BBB-rated
  - Canadian Provinces

Bloomberg index family: BofA Merrill Lynch (BAML) Canadian Fixed Income Indices
OAS field: OAS_SPREAD
"""

import pandas as pd
from xbbg import blp


# ---------------------------------------------------------------------------
# Ticker definitions
# ---------------------------------------------------------------------------
# Primary tickers use BofA Merrill Lynch (BAML) Canadian IG index series.
# Alternatives are provided as comments for validation on your Bloomberg terminal.
#
# Naming convention reference:
#   C0A0  = CAD Investment Grade Corporate (all ratings, all sectors)
#   C3A0  = CAD IG A-rated (A1/A2/A3)
#   C4A0  = CAD IG BBB-rated (BBB1/BBB2/BBB3)
#   Sector sub-indices append a 2-letter sector code to the base.
#
# For provinces, BAML tracks quasi-government / sub-sovereign issues.

TICKERS: dict[str, str] = {
    # Broad CAD IG (reference / sanity check)
    "CAD_IG_All":      "C0A0 Index",

    # Sector breakdown
    "CAD_IG_Fins":     "C0FN Index",   # Financials  — alt: CGFN Index, CAIG1FN Index
    "CAD_IG_NonFins":  "C0NF Index",   # Non-Financials — alt: C0NC Index, CAIG1NF Index
    "CAD_IG_Utils":    "C0UT Index",   # Utilities — alt: C0U0 Index, CAIG1UT Index

    # Rating breakdown
    "CAD_IG_A":        "C3A0 Index",   # A-rated (A1/A2/A3) — alt: C0A2 Index (AA+A combined)
    "CAD_IG_BBB":      "C4A0 Index",   # BBB-rated — alt: C0B0 Index

    # Provinces (quasi-sovereign / sub-sovereign)
    "CAD_Provinces":   "CGPV Index",   # Canadian Provincial — alt: C0P0 Index, CAGV Index
}

# Bloomberg field for Option-Adjusted Spread (basis points)
OAS_FIELD = "OAS_SPREAD"

# Alternative field if OAS_SPREAD not available on a given index
FALLBACK_FIELD = "SPREAD_TO_WORST"

# Date range
START_DATE = "2010-01-01"
END_DATE = pd.Timestamp.today().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Helper: fetch one series, fall back to alternative field on failure
# ---------------------------------------------------------------------------

def fetch_oas(
    ticker: str,
    name: str,
    start: str,
    end: str,
    field: str = OAS_FIELD,
    fallback: str = FALLBACK_FIELD,
) -> pd.Series:
    """
    Fetch a single OAS spread series from Bloomberg via blp.bdh.

    Tries `field` first; if the result is empty, retries with `fallback`.

    Args:
        ticker:   Bloomberg ticker string (e.g. 'C0A0 Index').
        name:     Label for the returned Series.
        start:    Start date string 'YYYY-MM-DD'.
        end:      End date string 'YYYY-MM-DD'.
        field:    Primary Bloomberg field (default OAS_SPREAD).
        fallback: Secondary field if primary returns nothing.

    Returns:
        pd.Series with a DatetimeIndex, named `name`. Empty on total failure.

    Raises:
        Does not raise; prints warnings instead so partial results are preserved.
    """
    for fld in (field, fallback):
        try:
            raw = blp.bdh(
                tickers=ticker,
                flds=fld,
                start_date=start,
                end_date=end,
                Per="D",          # daily
                Fill="P",         # use previous value for non-trading days
                CshAdjNormal=False,
            )
            if raw is None or raw.empty:
                print(f"[WARN] {name} ({ticker}) field={fld} returned empty — trying fallback.")
                continue
            # blp.bdh returns MultiIndex columns: (ticker, field)
            # Flatten to a plain Series
            series = raw.iloc[:, 0].rename(name)
            series.index = pd.to_datetime(series.index)
            print(f"[OK]   {name} ({ticker}) via {fld}: {len(series)} observations")
            return series
        except Exception as exc:
            print(f"[ERROR] {name} ({ticker}) field={fld}: {exc}")

    print(f"[SKIP] {name} ({ticker}): all fields failed; filling with NaN.")
    return pd.Series(dtype=float, name=name)


# ---------------------------------------------------------------------------
# Main fetch loop
# ---------------------------------------------------------------------------

def build_cad_ig_spreads(
    tickers: dict[str, str] = TICKERS,
    start: str = START_DATE,
    end: str = END_DATE,
) -> pd.DataFrame:
    """
    Fetch daily OAS spreads for all CAD IG sector indices and merge into a
    single wide DataFrame.

    Args:
        tickers: Mapping of {column_name: bloomberg_ticker}.
        start:   Start date 'YYYY-MM-DD'.
        end:     End date 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame with DatetimeIndex and one column per sector.
        Columns are in bps (basis points), e.g. 120.5 = 120.5 bps OAS.
    """
    series_list: list[pd.Series] = []

    for name, ticker in tickers.items():
        s = fetch_oas(ticker=ticker, name=name, start=start, end=end)
        series_list.append(s)

    if not series_list:
        raise RuntimeError("No data fetched — check Bloomberg connection and tickers.")

    df = pd.concat(series_list, axis=1)
    df.index.name = "date"
    df = df.sort_index()

    # Forward-fill up to 5 days to bridge weekends / holidays
    df = df.ffill(limit=5)

    print(f"\n=== CAD IG Sector Spreads ===")
    print(f"Date range : {df.index.min().date()} → {df.index.max().date()}")
    print(f"Shape      : {df.shape}")
    print(f"Columns    : {list(df.columns)}")
    print(f"\nLatest values (bps):\n{df.iloc[-1].to_string()}")
    print(f"\nMissing %:\n{(df.isna().mean() * 100).round(1).to_string()}")

    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    spreads = build_cad_ig_spreads()

    # Optional: save to CSV
    output_path = "cad_ig_sector_spreads.csv"
    spreads.to_csv(output_path)
    print(f"\nSaved to {output_path}")

    # Optional: quick correlation check
    print(f"\nCorrelation matrix (pairwise complete obs):\n")
    print(spreads.corr(method="pearson").round(3).to_string())
