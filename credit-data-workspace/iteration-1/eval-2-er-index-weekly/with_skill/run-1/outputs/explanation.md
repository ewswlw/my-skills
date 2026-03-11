# Explanation — US IG & HY ER Index (Weekly, Base 100)

## What the skill provides

The `CreditData` skill wraps Bloomberg `bdh()` calls and maps natural-language
queries to the correct ticker/field pair automatically.

For ER data, Bloomberg publishes `INDEX_EXCESS_RETURN_YTD` — a **year-to-date
percentage return** that resets to zero on January 1 each year. The skill
automatically converts this to a **chain-linked cumulative index** (base = 100
at the first data point) before returning the DataFrame.

## Instruments

| User query    | Bloomberg ticker  | Bloomberg field            | Output column     |
|---------------|-------------------|----------------------------|-------------------|
| `us ig er`    | `LUACTRUU Index`  | `INDEX_EXCESS_RETURN_YTD`  | `us_ig_er_index`  |
| `us hy er`    | `LF98TRUU Index`  | `INDEX_EXCESS_RETURN_YTD`  | `us_hy_er_index`  |

## YTD → Cumulative index conversion

The conversion follows the year-by-year chain-linking algorithm from
`Market Data Pipeline/fetch_data.py`:

1. For each calendar year, extract the YTD return series.
2. Convert YTD % values to daily index levels within the year:
   `level_t = (1 + ytd_t/100)` relative to January 1 of that year.
3. Chain years together by multiplying each year's level by the last
   level of the prior year.
4. Normalise so the **first observation = 100**.

This produces a single, unbroken cumulative performance index across all years.

## Code summary

```python
cd = CreditData(start_date="2015-01-01", periodicity="W")
df = cd.fetch("us ig er and us hy er")
# df columns: us_ig_er_index, us_hy_er_index  (base 100)
cd.save(df, "us_ig_hy_er_weekly.csv")
```

One `fetch()` call handles:
- Ticker / field resolution
- Bloomberg `bdh()` request
- YTD → cumulative index conversion
- Weekly resampling (Friday close via `periodicity="W"`)
- Forward-filling any missing weeks

## Output

`us_ig_hy_er_weekly.csv` — date-indexed, two columns, ~575 weekly rows
(Jan 2015 → today).
