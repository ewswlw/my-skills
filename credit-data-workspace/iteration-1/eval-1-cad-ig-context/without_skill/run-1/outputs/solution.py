"""
CAD IG OAS Spread Fetcher & Historical Context Analyzer
========================================================
Pulls daily Canadian Investment Grade OAS spreads from 2018 to today
using Bloomberg (xbbg), then provides full historical context:
percentile rank, z-score, tight/wide analysis vs rolling windows.

Bloomberg index used:
    IBXXCAIG Index  — iBoxx CAD Investment Grade Index (OAS)
    Fallback candidates tried in order if primary fails:
    - LUACTRUU Index  — Bloomberg CAD IG (OAS field)
    - I05511CA Index  — Bloomberg Barclays CAD IG

Requirements:
    uv add xbbg pandas numpy scipy tabulate
    Active Bloomberg terminal connection required.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd
from scipy import stats

try:
    from xbbg import blp
except ImportError as e:
    sys.exit(
        "xbbg not installed. Run: uv add xbbg\n"
        f"Original error: {e}"
    )

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

START_DATE = "20180101"
END_DATE = date.today().strftime("%Y%m%d")

# Candidate tickers in priority order.
# OAS = Option-Adjusted Spread (in basis points).
CANDIDATES: list[tuple[str, str, str]] = [
    # ticker,                  field,              label
    ("IBXXCAIG Index",         "OAS_SPREAD_BP",    "iBoxx CAD IG OAS"),
    ("IBOXIG Index",           "OAS_SPREAD_BP",    "iBoxx CAD IG OAS (alt1)"),
    ("LUACTRUU Index",         "OAS_BP",           "BBG CAD IG OAS"),
    ("I05511CA Index",         "OAS_BP",           "BBG Barclays CAD IG OAS"),
    ("BCACIG Index",           "OAS_BP",           "BBG CAD IG (BCACIG)"),
    # Spread-to-worst as secondary fallback
    ("IBXXCAIG Index",         "SPREAD_TO_WORST",  "iBoxx CAD IG STW"),
    ("LUACTRUU Index",         "SPREAD_TO_WORST",  "BBG CAD IG STW"),
]

# Look-back windows for rolling statistics (trading days)
LOOKBACK_WINDOWS: dict[str, int] = {
    "1Y":   252,
    "3Y":   756,
    "5Y":   1260,
    "Full": 0,   # 0 = use full available history
}

# Z-score thresholds for qualitative labels
ZSCORE_THRESHOLDS = {
    "extremely tight": -2.0,
    "tight":           -1.0,
    "slightly tight":  -0.5,
    "fair value":       0.5,   # ±0.5 band
    "slightly wide":    1.0,
    "wide":             2.0,
    "extremely wide":   float("inf"),
}


# ---------------------------------------------------------------------------
# Bloomberg data fetch
# ---------------------------------------------------------------------------

def fetch_oas(
    tickers: list[tuple[str, str, str]],
    start: str,
    end: str,
) -> tuple[pd.Series, str]:
    """
    Attempt each candidate ticker/field combo until one returns data.

    Returns:
        series: Daily OAS spread series (bps), indexed by date.
        label:  Human-readable label for the successful ticker.

    Raises:
        RuntimeError if no candidate returns data.
    """
    for ticker, field, label in tickers:
        try:
            raw = blp.bdh(
                tickers=ticker,
                flds=field,
                start_date=start,
                end_date=end,
                Per="D",          # daily
                Fill="P",         # previous value fill for weekends/holidays
                Days="A",         # all calendar days (Bloomberg will skip non-trading)
            )
            if raw is None or raw.empty:
                print(f"  [skip] {ticker} / {field} — no data returned")
                continue

            # xbbg returns MultiIndex columns (ticker, field); flatten
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = ["_".join(col).strip() for col in raw.columns]

            col = raw.columns[0]
            series = raw[col].dropna()

            if len(series) < 50:
                print(
                    f"  [skip] {ticker} / {field} — insufficient rows "
                    f"({len(series)} < 50)"
                )
                continue

            series.index = pd.to_datetime(series.index)
            series.name = "OAS_bps"
            print(f"  [OK]   {ticker} / {field} — {len(series)} rows ({label})")
            return series, label

        except Exception as exc:  # noqa: BLE001
            print(f"  [error] {ticker} / {field} — {exc}")

    raise RuntimeError(
        "All Bloomberg candidates failed. "
        "Verify your Bloomberg connection and index permissions."
    )


# ---------------------------------------------------------------------------
# Statistical context
# ---------------------------------------------------------------------------

def compute_percentile(series: pd.Series, current: float) -> float:
    """Return percentile rank of `current` within `series` (0–100)."""
    return float(stats.percentileofscore(series.dropna().values, current))


def compute_zscore(series: pd.Series, current: float) -> float:
    """Z-score of `current` relative to `series` mean/std."""
    mu = series.mean()
    sigma = series.std(ddof=1)
    if sigma == 0:
        return 0.0
    return (current - mu) / sigma


def label_from_zscore(z: float) -> str:
    """Map z-score to qualitative label."""
    if z < ZSCORE_THRESHOLDS["extremely tight"]:
        return "EXTREMELY TIGHT"
    if z < ZSCORE_THRESHOLDS["tight"]:
        return "TIGHT"
    if z < ZSCORE_THRESHOLDS["slightly tight"]:
        return "SLIGHTLY TIGHT"
    if abs(z) <= ZSCORE_THRESHOLDS["fair value"]:
        return "FAIR VALUE"
    if z < ZSCORE_THRESHOLDS["slightly wide"]:
        return "SLIGHTLY WIDE"
    if z < ZSCORE_THRESHOLDS["wide"]:
        return "WIDE"
    return "EXTREMELY WIDE"


def historical_context(series: pd.Series) -> pd.DataFrame:
    """
    Build a summary DataFrame with stats for each look-back window.

    Columns:
        window, n_obs, min, p25, median, mean, p75, max,
        current, pct_rank, z_score, label
    """
    current_date = series.index.max()
    current_val = float(series.iloc[-1])
    rows: list[dict] = []

    for window_name, n_days in LOOKBACK_WINDOWS.items():
        if n_days == 0:
            subset = series
        else:
            cutoff = current_date - pd.offsets.BDay(n_days)
            subset = series[series.index >= cutoff]

        if subset.empty:
            continue

        pct_rank = compute_percentile(subset, current_val)
        z = compute_zscore(subset, current_val)

        rows.append({
            "Window":         window_name,
            "N Obs":          len(subset),
            "Min (bps)":      round(subset.min(), 1),
            "P25 (bps)":      round(subset.quantile(0.25), 1),
            "Median (bps)":   round(subset.median(), 1),
            "Mean (bps)":     round(subset.mean(), 1),
            "P75 (bps)":      round(subset.quantile(0.75), 1),
            "Max (bps)":      round(subset.max(), 1),
            "Current (bps)":  round(current_val, 1),
            "Pct Rank":       round(pct_rank, 1),
            "Z-Score":        round(z, 2),
            "Signal":         label_from_zscore(z),
        })

    return pd.DataFrame(rows)


def recent_moves(series: pd.Series) -> pd.DataFrame:
    """
    Show spread change over recent horizons vs current level.
    """
    current_val = float(series.iloc[-1])
    horizons = {
        "1W":  5,
        "1M":  21,
        "3M":  63,
        "6M":  126,
        "YTD": None,   # handled separately
        "1Y":  252,
        "3Y":  756,
        "5Y":  1260,
    }
    current_date = series.index.max()
    ytd_start = pd.Timestamp(f"{current_date.year}-01-01")
    rows: list[dict] = []

    for label, n in horizons.items():
        if label == "YTD":
            subset = series[series.index >= ytd_start]
            if subset.empty:
                continue
            past_val = float(subset.iloc[0])
        else:
            cutoff = current_date - pd.offsets.BDay(n)
            subset = series[series.index >= cutoff]
            if subset.empty:
                continue
            past_val = float(subset.iloc[0])

        chg_bps = current_val - past_val
        rows.append({
            "Horizon":        label,
            "Past (bps)":     round(past_val, 1),
            "Current (bps)":  round(current_val, 1),
            "Change (bps)":   round(chg_bps, 1),
            "Direction":      "WIDER" if chg_bps > 0 else "TIGHTER" if chg_bps < 0 else "UNCHANGED",
        })

    return pd.DataFrame(rows)


def regime_analysis(series: pd.Series, n_regimes: int = 4) -> pd.DataFrame:
    """
    Bucket the entire spread history into n quantile regimes and show
    how many trading days the market has spent in each.
    """
    qs = np.linspace(0, 1, n_regimes + 1)
    boundaries = series.quantile(qs).values
    labels_list = []
    for i in range(n_regimes):
        lo = round(boundaries[i], 1)
        hi = round(boundaries[i + 1], 1)
        mask = (
            (series >= boundaries[i]) &
            (series <= boundaries[i + 1] if i == n_regimes - 1 else series < boundaries[i + 1])
        )
        days = mask.sum()
            
        labels_list.append({
            "Regime":         f"Q{i + 1} ({lo}–{hi} bps)",
            "Days":           int(days),
            "% of History":   round(days / len(series) * 100, 1),
            "Current":        "<<< YOU ARE HERE" if (
                float(series.iloc[-1]) >= boundaries[i] and
                float(series.iloc[-1]) < (boundaries[i + 1] + 0.001)
            ) else "",
        })

    return pd.DataFrame(labels_list)


# ---------------------------------------------------------------------------
# Pretty printing helpers
# ---------------------------------------------------------------------------

def print_section(title: str) -> None:
    width = 72
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_df(df: pd.DataFrame) -> None:
    try:
        from tabulate import tabulate
        print(tabulate(df, headers="keys", tablefmt="rounded_outline", showindex=False))
    except ImportError:
        print(df.to_string(index=False))


# ---------------------------------------------------------------------------
# Optional: save outputs
# ---------------------------------------------------------------------------

def save_outputs(
    series: pd.Series,
    context_df: pd.DataFrame,
    moves_df: pd.DataFrame,
    regime_df: pd.DataFrame,
    output_dir: str = ".",
) -> None:
    """
    Persist:
      - cad_ig_oas_daily.csv       — full daily time series
      - cad_ig_oas_context.csv     — historical context table
      - cad_ig_oas_moves.csv       — recent change table
      - cad_ig_oas_regimes.csv     — regime distribution
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    series.to_frame("OAS_bps").to_csv(
        f"{output_dir}/cad_ig_oas_daily.csv",
        encoding="utf-8",
    )
    context_df.to_csv(
        f"{output_dir}/cad_ig_oas_context.csv",
        index=False,
        encoding="utf-8",
    )
    moves_df.to_csv(
        f"{output_dir}/cad_ig_oas_moves.csv",
        index=False,
        encoding="utf-8",
    )
    regime_df.to_csv(
        f"{output_dir}/cad_ig_oas_regimes.csv",
        index=False,
        encoding="utf-8",
    )
    print(f"\nOutputs saved to: {output_dir}/")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("CAD IG OAS SPREAD — Bloomberg Data Fetch")
    print(f"  Date range : {START_DATE} → {END_DATE}")
    print(f"  Candidates : {len(CANDIDATES)} ticker/field combinations")
    print()
    print("Trying Bloomberg candidates...")

    series, label = fetch_oas(CANDIDATES, START_DATE, END_DATE)

    current_val = float(series.iloc[-1])
    current_date = series.index.max().strftime("%Y-%m-%d")

    print_section("CURRENT SPREAD")
    print(f"  Index  : {label}")
    print(f"  Date   : {current_date}")
    print(f"  OAS    : {current_val:.1f} bps")

    print_section("HISTORICAL CONTEXT — Multi-Window Z-Score & Percentile")
    ctx = historical_context(series)
    print_df(ctx)

    print_section("RECENT SPREAD MOVES")
    moves = recent_moves(series)
    print_df(moves)

    print_section("SPREAD REGIME DISTRIBUTION (Full History)")
    regimes = regime_analysis(series, n_regimes=4)
    print_df(regimes)

    # Simple trend: 50-day vs 200-day moving average
    print_section("MOVING AVERAGE CONTEXT")
    ma50 = series.rolling(50).mean().iloc[-1]
    ma200 = series.rolling(200).mean().iloc[-1]
    ma_signal = (
        "SPREAD ABOVE BOTH MAs (WIDENING TREND)"
        if current_val > ma50 and current_val > ma200
        else "SPREAD BELOW BOTH MAs (TIGHTENING TREND)"
        if current_val < ma50 and current_val < ma200
        else "SPREAD BETWEEN 50D AND 200D MA (MIXED)"
    )
    print(f"  50-day  MA : {ma50:.1f} bps  (current vs MA: {current_val - ma50:+.1f} bps)")
    print(f"  200-day MA : {ma200:.1f} bps  (current vs MA: {current_val - ma200:+.1f} bps)")
    print(f"  Signal     : {ma_signal}")

    # Ask user whether to save
    save = input("\nSave outputs to CSV? [y/N]: ").strip().lower()
    if save == "y":
        save_outputs(series, ctx, moves, regimes, output_dir="cad_ig_oas_outputs")


if __name__ == "__main__":
    main()
