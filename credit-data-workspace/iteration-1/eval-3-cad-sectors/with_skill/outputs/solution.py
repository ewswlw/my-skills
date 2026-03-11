"""
CAD IG Sector Spreads — all sectors in a single DataFrame, daily from 2010.

Sectors covered:
  - Financials          (cad_credit_spreads_fins)
  - Non-Financials ex-Uts (cad_credit_spreads_non_fins_ex_uts)
  - Utilities           (cad_credit_spreads_uts)
  - A-rated credits     (cad_credit_spreads_a_credits)
  - BBB-rated credits   (cad_credit_spreads_bbb_credits)
  - Provincials         (cad_credit_spreads_provs)
"""

import sys
sys.path.insert(0, r"C:\Users\Eddy\.claude\skills\credit-data")
from credit_data import CreditData

# Instantiate with daily frequency from 2010-01-01
cd = CreditData(
    start_date="2010-01-01",
    periodicity="D",
    fill="ffill",
)

# Fetch all six CAD IG sector spreads in a single call — CreditData merges them
df = cd.fetch("cad fins, cad non fins, cad uts, cad a, cad bbb, cad provs")

# Confirm all six columns are present
expected_cols = [
    "cad_credit_spreads_fins",
    "cad_credit_spreads_non_fins_ex_uts",
    "cad_credit_spreads_uts",
    "cad_credit_spreads_a_credits",
    "cad_credit_spreads_bbb_credits",
    "cad_credit_spreads_provs",
]
assert list(df.columns) == expected_cols, (
    f"Unexpected columns: {df.columns.tolist()}"
)

print(f"Shape: {df.shape}")
print(f"Date range: {df.index[0].date()} → {df.index[-1].date()}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nLatest values (bps):\n{df.tail(1).T.rename(columns={df.index[-1]: 'latest'})}")
print(f"\nSample (last 5 rows):\n{df.tail()}")
