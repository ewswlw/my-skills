"""
Pre-registered evaluation boundaries — do not tune on holdout.

`HOLDOUT_START` is fixed in code (not chosen from data). All grid search / CV
uses only rows strictly before this date.
"""
from __future__ import annotations

import pandas as pd

# First month-end >= this date is **holdout** (never used in parameter search).
HOLDOUT_START = pd.Timestamp("2020-01-01")
