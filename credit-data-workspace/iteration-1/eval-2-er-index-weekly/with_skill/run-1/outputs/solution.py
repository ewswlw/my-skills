"""
US IG and US HY Excess Return Indices — Weekly, Base 100
=========================================================
Pulls Bloomberg excess return (ER) data for US Investment Grade (LUACTRUU)
and US High Yield (LF98TRUU) from January 2015 to today, on a weekly
frequency. Converts Bloomberg's YTD % return field to a chain-linked
cumulative index (base = 100 at first data point) and saves to CSV.

Requirements:
    - Bloomberg Terminal open and connected
    - uv add xbbg pandas numpy   (or pip install xbbg pandas numpy)

Usage:
    uv run python solution.py
"""

import sys
from pathlib import Path

# ── Skill import ──────────────────────────────────────────────────────────────
sys.path.insert(0, r"C:\Users\Eddy\.claude\skills\credit-data")
from credit_data import CreditData

# ── Output path ───────────────────────────────────────────────────────────────
OUTPUT_CSV = Path(r"C:\Users\Eddy\.claude\skills\credit-data-workspace"
                  r"\iteration-1\eval-2-er-index-weekly\with_skill\outputs"
                  r"\us_ig_hy_er_weekly.csv")

# ── Fetch ─────────────────────────────────────────────────────────────────────
cd = CreditData(
    start_date="2015-01-01",
    end_date=None,        # today
    periodicity="W",      # weekly
    fill="ffill",
)

df = cd.fetch("us ig er and us hy er")
# Returned columns:
#   us_ig_er_index  — chain-linked cumulative ER index, base=100 at 2015-01-01
#   us_hy_er_index  — chain-linked cumulative ER index, base=100 at 2015-01-01

# ── Save ──────────────────────────────────────────────────────────────────────
cd.save(df, str(OUTPUT_CSV))

# ── Quick preview ─────────────────────────────────────────────────────────────
print(f"Rows: {len(df)}")
print(f"Date range: {df.index[0].date()} → {df.index[-1].date()}")
print(f"Columns: {df.columns.tolist()}")
print()
print(df.head(10).to_string())
print("...")
print(df.tail(5).to_string())
print(f"\nSaved → {OUTPUT_CSV}")
