"""
CAD IG OAS Spreads — Historical Pull + Spread Context
======================================================
Pulls daily CAD IG OAS spreads from 2018-01-01 to today using the CreditData
skill, then produces a comprehensive spread intelligence report including
percentiles, z-scores, and regime labels vs both full history and the 2018+
window.

Prerequisites:
  - Bloomberg Terminal open and connected
  - uv add xbbg pandas numpy
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, r"C:\Users\Eddy\.claude\skills\credit-data")
from credit_data import CreditData  # noqa: E402

import numpy as np
import pandas as pd


# ── 1. Fetch CAD IG OAS daily from 2018 ──────────────────────────────────────

cd = CreditData(
    start_date="2018-01-01",
    end_date=None,       # today
    periodicity="D",
    fill="ffill",
)

df = cd.fetch("cad ig")
# Resulting DataFrame: single column  cad_oas  (bps), DatetimeIndex

print("=" * 60)
print("CAD IG OAS — Daily Spreads (2018-01-01 to today)")
print("=" * 60)
print(f"Rows fetched : {len(df):,}")
print(f"Date range   : {df.index[0].date()}  →  {df.index[-1].date()}")
print(f"Missing obs  : {df['cad_oas'].isna().sum()}")
print()
print(df.tail(10).to_string())
print()


# ── 2. Built-in spread intelligence via context() ────────────────────────────
# context() uses the full Bloomberg history (back to 2002) for percentile/
# z-score calculations so the regime label reflects the complete cycle.

print("=" * 60)
print("Spread Intelligence (full-history context)")
print("=" * 60)
print(cd.context("cad ig"))
print()


# ── 3. Manual statistics over the 2018–today window ──────────────────────────
# Users often want to know "vs post-GFC history" or "vs this cycle".
# We compute a second set of stats anchored to our 2018 fetch window.

series = df["cad_oas"].dropna()
current = float(series.iloc[-1])

mean_2018   = series.mean()
std_2018    = series.std(ddof=1)
pctile_2018 = float(pd.Series(series).rank(pct=True).iloc[-1]) * 100
z_2018      = (current - mean_2018) / std_2018

# 1-year (252 trading days) rolling stats
window_1y = series.tail(252)
mean_1y   = window_1y.mean()
std_1y    = window_1y.std(ddof=1)
z_1y      = (current - mean_1y) / std_1y

# Full-sample stats (same window since we only fetched from 2018)
hi   = series.max()
lo   = series.min()
hi_d = series.idxmax().date()
lo_d = series.idxmin().date()

# 52-week range
rng_52w = series.tail(252)
hi_52   = rng_52w.max()
lo_52   = rng_52w.min()
pos_52  = (current - lo_52) / (hi_52 - lo_52) * 100 if hi_52 != lo_52 else 50.0

# Regime label (same thresholds as context())
def regime(pctile: float) -> str:
    if pctile < 35:
        return "TIGHT"
    elif pctile < 65:
        return "FAIR"
    elif pctile < 85:
        return "WIDE"
    else:
        return "DISTRESSED"

regime_2018 = regime(pctile_2018)

# ASCII bar (10-char)
bar_len = round(pos_52 / 10)
bar     = "█" * bar_len + "░" * (10 - bar_len)

print("=" * 60)
print(f"CAD IG OAS — 2018+ Window Statistics  ({date.today()})")
print("=" * 60)
print(f"  Current spread    :  {current:.1f} bps")
print(f"  2018+ Mean        :  {mean_2018:.1f} bps")
print(f"  2018+ Std Dev     :  {std_2018:.1f} bps")
print(f"  2018+ Percentile  :  {pctile_2018:.0f}th")
print(f"  Z-Score (2018+)   :  {z_2018:+.2f}σ")
print(f"  Z-Score (1Y)      :  {z_1y:+.2f}σ")
print(f"  Regime (2018+)    :  {regime_2018}")
print()
print(f"  All-Time High     :  {hi:.1f} bps  ({hi_d})")
print(f"  All-Time Low      :  {lo:.1f} bps  ({lo_d})")
print()
print(f"  52-Week Range     :  {lo_52:.0f}–{hi_52:.0f} bps   {bar}  {pos_52:.0f}%")
print()


# ── 4. Year-by-year summary table ─────────────────────────────────────────────

print("=" * 60)
print("Year-by-Year Summary (mean / min / max / end bps)")
print("=" * 60)
annual = (
    series
    .to_frame()
    .assign(year=lambda x: x.index.year)
    .groupby("year")["cad_oas"]
    .agg(mean="mean", low="min", high="max", end="last")
    .round(1)
)
print(annual.to_string())
print()


# ── 5. Percentile table (cross-sectional thresholds) ─────────────────────────

print("=" * 60)
print("Spread Distribution (2018+ Percentiles)")
print("=" * 60)
for p in [5, 10, 25, 50, 75, 90, 95]:
    val = np.percentile(series, p)
    marker = "  ◄ current" if abs(val - current) == min(
        abs(np.percentile(series, q) - current) for q in [5, 10, 25, 50, 75, 90, 95]
    ) else ""
    print(f"  {p:2d}th pctile : {val:6.1f} bps{marker}")
print(f"\n  Current      : {current:6.1f} bps  →  {pctile_2018:.0f}th pctile  ({z_2018:+.2f}σ)")
print()


# ── 6. Optional save ──────────────────────────────────────────────────────────

save_path = (
    Path(r"C:\Users\Eddy\Documents\Obsidian Vault\Market Data Pipeline")
    / "processed market data"
    / "cad_ig_oas_2018.csv"
)
cd.save(df, str(save_path))
print(f"Saved → {save_path}")
