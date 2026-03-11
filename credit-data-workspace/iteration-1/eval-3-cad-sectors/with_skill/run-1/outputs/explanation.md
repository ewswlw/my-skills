# Explanation — CAD IG Sector Spreads

## What the code does

Uses the `CreditData` skill to fetch all six CAD IG sector OAS spreads in a
single `fetch()` call. `CreditData` internally maps each natural-language token
to its Bloomberg ticker and field, calls `blp.bdh()` for each, and outer-joins
the results into one DataFrame with a shared DatetimeIndex.

## Instruments fetched

| Token       | Column returned                        | Bloomberg ticker  |
|-------------|----------------------------------------|-------------------|
| `cad fins`  | `cad_credit_spreads_fins`              | `I05523CA Index`  |
| `cad non fins` | `cad_credit_spreads_non_fins_ex_uts` | `I05520CA Index` |
| `cad uts`   | `cad_credit_spreads_uts`               | `I05517CA Index`  |
| `cad a`     | `cad_credit_spreads_a_credits`         | `I05515CA Index`  |
| `cad bbb`   | `cad_credit_spreads_bbb_credits`       | `I05516CA Index`  |
| `cad provs` | `cad_credit_spreads_provs`             | `I34069CA Index`  |

All fields: `INDEX_OAS_TSY_BP` (OAS vs. Treasuries, in basis points).

## Key parameters

- `start_date="2010-01-01"` — full decade-plus of daily history
- `periodicity="D"` — daily data
- `fill="ffill"` — forward-fills non-trading days (weekends, holidays)

## Output

A single `pd.DataFrame` with ~3,900+ rows × 6 OAS columns, indexed by
`DatetimeIndex`. Columns are named as above. Data quality fixes (e.g. the
2005-11-15 bad date for `cad_credit_spreads_non_fins_ex_uts` and
`cad_credit_spreads_bbb_credits`) are applied automatically by `CreditData`.

## Approach rationale

The single `cd.fetch(...)` call is the idiomatic pattern from the skill —
it avoids multiple round trips to Bloomberg and guarantees a properly
aligned, merged DataFrame. No manual `pd.concat` or join is needed.
