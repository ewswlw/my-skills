"""
Bloomberg US IG and US HY Excess Return Indices — Weekly Base-100 Index
========================================================================
Pulls Bloomberg Barclays US IG and US HY excess return series from
January 2015 to today, resamples to weekly frequency, and outputs a
cumulative base-100 index to CSV.

Bloomberg tickers used:
  LUACEXUU Index  — Bloomberg US Corporate Investment Grade Excess Return Index
  LF98EXUU Index  — Bloomberg US High Yield Excess Return Index

Strategy
--------
1. Attempt to pull raw index levels via PX_LAST (preferred — avoids YTD
   reset logic entirely). Values are then rebased to 100 at first date.
2. If PX_LAST returns YTD-style percentages (common for some delivery modes),
   fall back to EXCESS_RETURN_YTD and chain year-by-year into a continuous
   cumulative index.

Usage
-----
    uv run python solution.py [--output path/to/output.csv]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from xbbg import blp


# ── Configuration ─────────────────────────────────────────────────────────────

START_DATE = "2015-01-01"
END_DATE = pd.Timestamp.today().strftime("%Y-%m-%d")

DEFAULT_OUTPUT = Path("er_index_weekly.csv")

# Bloomberg Barclays excess return index tickers (unhedged USD)
TICKERS: dict[str, str] = {
    "US_IG_ER": "LUACEXUU Index",  # Bloomberg US Corporate IG Excess Return
    "US_HY_ER": "LF98EXUU Index",  # Bloomberg US HY Excess Return
}

# Alternative / fallback tickers to try if primaries fail
ALT_TICKERS: dict[str, list[str]] = {
    "US_IG_ER": [
        "LUACEXUU Index",   # Bloomberg Barclays US Corp IG ER (primary)
        "LF94EXUU Index",   # Bloomberg Barclays US Credit ER
        "C0A0 Index",       # ICE BofA US Corporate Index — use PX_LAST
    ],
    "US_HY_ER": [
        "LF98EXUU Index",   # Bloomberg Barclays US HY ER (primary)
        "H0A0 Index",       # ICE BofA US HY Master II Index — use PX_LAST
    ],
}


# ── Bloomberg helpers ──────────────────────────────────────────────────────────

def _flatten_bdh(raw: pd.DataFrame, tickers: dict[str, str]) -> pd.DataFrame:
    """
    Flatten xbbg bdh output and rename columns from Bloomberg tickers
    to human-readable labels.

    xbbg returns a MultiIndex (ticker, field) unless a single field is
    requested, in which case columns may already be flat tickers.

    Args:
        raw: DataFrame returned by blp.bdh
        tickers: mapping label -> Bloomberg ticker string

    Returns:
        DataFrame with columns renamed to labels
    """
    if raw.empty:
        return raw

    if isinstance(raw.columns, pd.MultiIndex):
        # Drop the field level — we only requested one field
        raw.columns = raw.columns.get_level_values(0)

    reverse_map = {v: k for k, v in tickers.items()}
    return raw.rename(columns=reverse_map)


def fetch_index_levels(
    tickers: dict[str, str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """
    Pull index levels (PX_LAST) from Bloomberg for each ticker.

    Args:
        tickers: label -> Bloomberg ticker
        start: start date YYYY-MM-DD
        end: end date YYYY-MM-DD

    Returns:
        DataFrame of daily index levels, columns = labels

    Raises:
        ValueError: if Bloomberg returns empty data
    """
    raw = blp.bdh(
        tickers=list(tickers.values()),
        flds=["PX_LAST"],
        start_date=start,
        end_date=end,
    )
    df = _flatten_bdh(raw, tickers)

    if df.empty:
        raise ValueError("blp.bdh returned empty DataFrame for PX_LAST")

    return df


def fetch_ytd_excess_returns(
    tickers: dict[str, str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """
    Pull EXCESS_RETURN_YTD percentage field from Bloomberg.

    Args:
        tickers: label -> Bloomberg ticker
        start: start date YYYY-MM-DD
        end: end date YYYY-MM-DD

    Returns:
        DataFrame of YTD excess return percentages, columns = labels

    Raises:
        ValueError: if Bloomberg returns empty data
    """
    raw = blp.bdh(
        tickers=list(tickers.values()),
        flds=["EXCESS_RETURN_YTD"],
        start_date=start,
        end_date=end,
    )
    df = _flatten_bdh(raw, tickers)

    if df.empty:
        raise ValueError("blp.bdh returned empty DataFrame for EXCESS_RETURN_YTD")

    return df


# ── Index construction ─────────────────────────────────────────────────────────

def rebase_to_100(series: pd.Series) -> pd.Series:
    """
    Rebase a continuous price series so the first non-NaN value equals 100.

    Args:
        series: price or index level series

    Returns:
        Rebased series, first value = 100.0
    """
    series = series.dropna()
    if series.empty:
        return series
    return series / series.iloc[0] * 100.0


def ytd_pct_to_cumulative_index(
    series: pd.Series,
    base: float = 100.0,
) -> pd.Series:
    """
    Convert a YTD-percentage excess return series into a continuous
    cumulative base-100 index.

    Bloomberg's EXCESS_RETURN_YTD resets to 0.0 on the first trading day
    of each calendar year.  To build a cumulative index we chain across
    year boundaries:

        level[t]  = carry_prior_year * (1 + ytd[t] / 100)

    where carry_prior_year is the last index level from the previous year.

    Args:
        series: YTD excess returns as percentages (3.5 means +3.5%)
        base: index value assigned to the day before the first data point

    Returns:
        Continuous cumulative index series with first value near `base`

    Raises:
        ValueError: if series is empty after dropping NaNs
    """
    series = series.dropna().sort_index()
    if series.empty:
        raise ValueError("Series is empty after dropping NaNs")

    result = pd.Series(index=series.index, dtype=float, name=series.name)
    carry = base

    for yr in sorted(series.index.year.unique()):
        mask = series.index.year == yr
        yr_slice = series.loc[mask]

        # Level = prior carry * (1 + ytd_return / 100)
        result.loc[mask] = carry * (1.0 + yr_slice / 100.0)

        # Roll carry forward to last day of this year
        valid = result.loc[mask].dropna()
        if not valid.empty:
            carry = valid.iloc[-1]

    return result


def _looks_like_index_level(series: pd.Series, min_threshold: float = 50.0) -> bool:
    """
    Heuristic: Bloomberg ER index levels are typically 100–2000+.
    YTD percentages are small numbers (e.g. -15 to +30).

    Args:
        series: a column from the BDH result
        min_threshold: values above this are treated as index levels

    Returns:
        True if median absolute value exceeds threshold
    """
    med = series.dropna().abs().median()
    return bool(med > min_threshold)


# ── Resampling ─────────────────────────────────────────────────────────────────

def resample_weekly_friday(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily index levels to weekly frequency, taking the last
    available observation each week (week ending Friday).

    Args:
        df: daily DataFrame with DatetimeIndex

    Returns:
        Weekly DataFrame, index = Friday dates
    """
    return df.resample("W-FRI").last().dropna(how="all")


# ── Main pipeline ──────────────────────────────────────────────────────────────

def build_er_index(
    tickers: dict[str, str] = TICKERS,
    start: str = START_DATE,
    end: str = END_DATE,
) -> pd.DataFrame:
    """
    Full pipeline: fetch data → build cumulative index → resample weekly.

    Args:
        tickers: mapping label -> Bloomberg ticker
        start: start date YYYY-MM-DD
        end: end date YYYY-MM-DD

    Returns:
        Weekly DataFrame with columns [US_IG_ER, US_HY_ER], base 100 at start
    """
    print(f"[1/3] Fetching Bloomberg data  ({start} → {end})")

    # ── Strategy A: pull raw index levels via PX_LAST ────────────────────────
    try:
        df = fetch_index_levels(tickers, start, end)
        print(f"      PX_LAST returned {len(df)} rows × {df.shape[1]} cols")

        # Sanity-check: do values look like index levels (not YTD pct)?
        level_cols = [
            c for c in df.columns if _looks_like_index_level(df[c])
        ]
        if len(level_cols) < len(df.columns):
            pct_cols = [c for c in df.columns if c not in level_cols]
            print(
                f"      WARNING: {pct_cols} look like YTD %, "
                "will apply chaining for those columns"
            )

        # Build base-100 series
        daily = pd.DataFrame(index=df.index)
        for col in df.columns:
            if col in level_cols:
                daily[col] = rebase_to_100(df[col])
            else:
                daily[col] = ytd_pct_to_cumulative_index(df[col])

    except Exception as exc_a:
        print(f"      PX_LAST failed: {exc_a!r}")
        print("      Falling back to EXCESS_RETURN_YTD ...")

        # ── Strategy B: pull YTD excess return field ─────────────────────────
        ytd_df = fetch_ytd_excess_returns(tickers, start, end)
        print(f"      EXCESS_RETURN_YTD returned {len(ytd_df)} rows")

        daily = pd.DataFrame(index=ytd_df.index)
        for col in ytd_df.columns:
            daily[col] = ytd_pct_to_cumulative_index(ytd_df[col])

    print(f"\n[2/3] Resampling to weekly (W-FRI)  ...")
    weekly = resample_weekly_friday(daily)
    weekly.index.name = "date"
    print(f"      {len(weekly)} weekly observations")

    # Validate no large gaps
    max_gap = weekly.index.to_series().diff().dt.days.max()
    if max_gap and max_gap > 14:
        print(f"      WARNING: max gap between weekly obs = {max_gap:.0f} days")

    print(f"\n[3/3] Final index (tail 5 rows):")
    print(weekly.tail())

    return weekly


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pull US IG / HY excess return indices and save to CSV"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--start",
        default=START_DATE,
        help=f"Start date YYYY-MM-DD (default: {START_DATE})",
    )
    parser.add_argument(
        "--end",
        default=END_DATE,
        help=f"End date YYYY-MM-DD (default: today)",
    )
    args = parser.parse_args(argv)

    weekly = build_er_index(
        tickers=TICKERS,
        start=args.start,
        end=args.end,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    weekly.to_csv(args.output, encoding="utf-8")
    print(f"\nSaved → {args.output.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
