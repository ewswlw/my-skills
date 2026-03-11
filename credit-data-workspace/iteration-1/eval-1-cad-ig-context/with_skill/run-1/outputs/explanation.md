# Approach Explanation — CAD IG OAS Pull + Context

## Data Fetch

The solution uses the `CreditData` skill module (`credit_data.py`) to pull daily
CAD IG OAS spreads from Bloomberg ticker `I05510CA Index` using field
`INDEX_OAS_TSY_BP`. The `CreditData` class is initialised with
`start_date="2018-01-01"`, `periodicity="D"`, and `fill="ffill"` so weekends and
holidays are forward-filled automatically. The single `cd.fetch("cad ig")` call
handles Bloomberg API plumbing, bad-date corrections (e.g. 2005-11-15 spike),
and returns a clean `pd.DataFrame` with column `cad_oas`.

## Spread Context — Two Layers

The built-in `cd.context("cad ig")` call surfaces the skill's full-history
percentile (back to 2002), 5-year z-score, 52-week range bar, and regime label
(`TIGHT / FAIR / WIDE / DISTRESSED`) in a single formatted block. On top of
that, the script computes a second set of manual statistics anchored to the 2018+
window: mean, standard deviation, percentile rank, and z-scores on both the 2018+
and 1-year horizons. This gives the user two reference frames — long-run cycle
context from `context()`, and post-2018 / current-cycle context from the manual
stats.

## Output Structure

The script prints five distinct sections: (1) a raw data preview, (2) the
skill's built-in spread intelligence block, (3) manual 2018+ stats with regime
label, (4) a year-by-year summary table (mean/min/max/year-end), and (5) a
cross-sectional percentile table with the current spread marked. It closes by
saving the raw DataFrame to the vault's `processed market data` folder via
`cd.save()`. The code requires only Bloomberg Terminal to be open; all
computation is in-process using `pandas` and `numpy`.
