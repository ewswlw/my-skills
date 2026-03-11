# Credit Data Skill

Provides Bloomberg credit market spread and return series data via the
`CreditData` class in `credit_data.py`. Translates natural language queries
into fetch calls, auto-selects the correct Bloomberg field per instrument,
and delivers clean DataFrames ready for analysis.

---

## Trigger Keywords

Use this skill when the user's message contains any of:

**Slash command:** `/credit data`, `/credit-data`

**Spread / OAS keywords:**
`oas`, `spreads`, `sprds`, `credit spreads`, `spread data`, `ig spreads`,
`hy spreads`, `credit oas`, `option adjusted spread`

**Index / instrument keywords:**
`cad ig`, `cad credit`, `canadian credit`, `cad oas`, `cad short`, `cad long`,
`cad fins`, `cad financials`, `cad non fins`, `cad industrials`, `cad uts`,
`cad utilities`, `cad a`, `cad bbb`, `cad provs`, `cad provinces`,
`us ig`, `us hy`, `us investment grade`, `us high yield`, `luactruu`, `lf98`,
`cdx ig`, `cdx hy`, `cdx spread`, `iboxumae`, `iboxhyse`

**Return / ER keywords:**
`er index`, `excess return`, `er series`, `return series`, `cad er`, `us ig er`,
`us hy er`, `cdx ig er`, `cdx hy er`, `cad ig er`, `cad short er`, `cad long er`,
`cad provs er`, `return index`, `ytd return`, `excess return index`

**General credit research:**
`credit data`, `credit market data`, `fetch credit`, `pull credit data`,
`get spreads`, `get oas`, `bloomberg credit`, `credit time series`

---

## Prerequisites

Bloomberg Terminal must be **open and connected** before any fetch call.

```bash
# Install dependencies (run once in the project virtual environment)
uv add xbbg pandas numpy
```

---

## Python Module Location

```
C:\Users\Eddy\.claude\skills\credit-data\credit_data.py
```

Import pattern:
```python
import sys
sys.path.insert(0, r"C:\Users\Eddy\.claude\skills\credit-data")
from credit_data import CreditData
```

---

## Core API

```python
cd = CreditData(
    start_date="2002-11-01",   # default — full history
    end_date=None,             # default — today
    periodicity="D",           # "D" | "W" | "M"
    fill="ffill",              # "ffill" | "bfill" | None
)

# Single or multi-series — natural language
df = cd.fetch("cad ig")
df = cd.fetch("us ig and us hy")
df = cd.fetch("cad ig, cad bbb, cad fins")
df = cd.fetch("cdx ig")

# Date and frequency overrides
df = cd.fetch("cad ig", start_date="2020-01-01", periodicity="W")

# ER → chain-linked cumulative index (auto-conversion, no extra steps)
df = cd.fetch("cad ig er")           # returns col: cad_ig_er_index
df = cd.fetch("us hy er")            # returns col: us_hy_er_index
df = cd.fetch("cdx ig er")           # PX_LAST — already a level index

# Fetch everything
df = cd.fetch_all()
df = cd.fetch("all credit data")

# Spread intelligence context
print(cd.context("cad ig"))
print(cd.context("us hy"))

# Save
cd.save(df, "path/to/output.csv")   # UTF-8, creates dirs if needed
```

---

## Instrument Quick Reference

| User says | Column returned | Bloomberg ticker | Field |
|---|---|---|---|
| `cad ig` | `cad_oas` | `I05510CA Index` | `INDEX_OAS_TSY_BP` |
| `cad short` | `cad_short_oas` | `I34227CA Index` | `INDEX_OAS_TSY_BP` |
| `cad long` | `cad_long_oas` | `I34229CA Index` | `INDEX_OAS_TSY_BP` |
| `cad fins` | `cad_credit_spreads_fins` | `I05523CA Index` | `INDEX_OAS_TSY_BP` |
| `cad non fins` | `cad_credit_spreads_non_fins_ex_uts` | `I05520CA Index` | `INDEX_OAS_TSY_BP` |
| `cad uts` | `cad_credit_spreads_uts` | `I05517CA Index` | `INDEX_OAS_TSY_BP` |
| `cad a` | `cad_credit_spreads_a_credits` | `I05515CA Index` | `INDEX_OAS_TSY_BP` |
| `cad bbb` | `cad_credit_spreads_bbb_credits` | `I05516CA Index` | `INDEX_OAS_TSY_BP` |
| `cad provs` | `cad_credit_spreads_provs` | `I34069CA Index` | `INDEX_OAS_TSY_BP` |
| `cad provs long` | `cad_credit_spreads_provs_longs` | `I34336CA Index` | `INDEX_OAS_TSY_BP` |
| `us ig` | `us_ig_oas` | `LUACTRUU Index` | `INDEX_OAS_TSY_BP` |
| `us hy` | `us_hy_oas` | `LF98TRUU Index` | `INDEX_OAS_TSY_BP` |
| `cdx ig` | `cdx_ig` | `IBOXUMAE MKIT Curncy` | `ROLL_ADJUSTED_MID_PRICE` ⚠ |
| `cdx hy` | `cdx_hy` | `IBOXHYSE MKIT Curncy` | `ROLL_ADJUSTED_MID_PRICE` ⚠ |
| `cdx ig er` | `cdx_ig_er` | `ERIXCDIG Index` | `PX_LAST` |
| `cdx hy er` | `cdx_hy_er` | `UISYMH5S Index` | `PX_LAST` |
| `cad ig er` | `cad_ig_er_index` ★ | `I05510CA Index` | `INDEX_EXCESS_RETURN_YTD` |
| `cad short er` | `cad_ig_short_er_index` ★ | `I34227CA Index` | `INDEX_EXCESS_RETURN_YTD` |
| `cad long er` | `cad_ig_long_er_index` ★ | `I34229CA Index` | `INDEX_EXCESS_RETURN_YTD` |
| `cad provs er` | `cad_credit_spreads_provs_er_index` ★ | `I34069CA Index` | `INDEX_EXCESS_RETURN_YTD` |
| `cad provs long er` | `cad_credit_spreads_provs_longs_er_index` ★ | `I34336CA Index` | `INDEX_EXCESS_RETURN_YTD` |
| `us ig er` | `us_ig_er_index` ★ | `LUACTRUU Index` | `INDEX_EXCESS_RETURN_YTD` |
| `us hy er` | `us_hy_er_index` ★ | `LF98TRUU Index` | `INDEX_EXCESS_RETURN_YTD` |

**⚠ CDX note:** CDX instruments use `ROLL_ADJUSTED_MID_PRICE` — roll-adjusted
spread mid price, not OAS. Field selection is automatic. `context()` works for
CDX spreads. `context()` does **not** work for `cdx_ig_er` / `cdx_hy_er`
(PX_LAST indices) — use `fetch()` for those.

**★ ER note:** Bloomberg `INDEX_EXCESS_RETURN_YTD` is a year-to-date % return.
`CreditData` automatically converts it to a chain-linked cumulative index
(base=100 at the first data point) using the year-by-year algorithm from
`Market Data Pipeline/fetch_data.py`. The output DataFrame column is renamed
`<input_column>_index` (e.g. `cad_ig_er` → `cad_ig_er_index`).
`context()` does **not** support ER instruments — use `fetch()` for ER data.

---

## Known Bad Dates (auto-corrected)

These data quality issues are corrected automatically on every fetch:

| Date | Column | Action |
|---|---|---|
| 2005-11-15 | `cad_oas` | replace with prior day |
| 2005-11-15 | `cad_credit_spreads_non_fins_ex_uts` | replace with prior day |
| 2005-11-15 | `cad_credit_spreads_bbb_credits` | replace with prior day |
| 2005-11-15 | `cad_ig_er_index` | replace with prior day |

---

## `context()` — Spread Intelligence

When the user asks *"where are spreads?"*, *"how tight is CAD IG?"*, or any
spread-level question, call `cd.context(query)` instead of just `cd.fetch()`:

```python
print(cd.context("cad ig"))
```

Output format:
```
CAD IG All Sectors  (I05510CA Index)
──────────────────────────────────────────────────────────
  Current:              124.0 bps
  Full-History Pctile:   34th
  5-Year Pctile:         28th
  Z-Score (5Y):          -0.82
  52-Week Range:  98–167 bps   ████░░░░░░ 40%
  Regime:               TIGHT
```

Regime labels:
- `TIGHT` — below 35th full-history percentile
- `FAIR` — 35th–64th percentile
- `WIDE` — 65th–84th percentile
- `DISTRESSED` — 85th percentile and above

Works for OAS and CDX instruments. Not applicable to ER indices (use `fetch()`).

---

## Resolve Without Fetching

To inspect what instruments a query maps to without hitting Bloomberg:

```python
cd = CreditData()
print(cd.resolve("cad ig and us hy"))
# ['cad_oas', 'us_hy_oas']

print(cd.resolve("cad er"))
# ['cad_ig_er']
```

---

## Agent Workflow

When a user requests credit data, the agent should:

1. **Identify trigger** — any keyword above, or `/credit data` slash command.
2. **Identify instruments** — use the table above to map user language to column names.
3. **Identify data type using this decision tree:**

   ```
   Does the user want LEVELS / "where are spreads?" / historical context?
   └── YES → use context(query)   [OAS and CDX instruments only]
       └── Is it an ER instrument (er, excess return, return index)?
           └── YES → DO NOT use context(); use fetch(query) instead.
                     context() will return an error string for ER data.

   Does the user want RAW DATA for analysis / modelling / a DataFrame?
   └── YES → use fetch(query)
       └── ER request? → fetch() auto-converts YTD → cumulative index. No extra steps.

   Does the user want EVERYTHING?
   └── YES → use fetch_all()   or   fetch("all credit data")
   ```

4. **Generate and run code** using the import pattern above.
5. **Handle Bloomberg errors** — if `blp.bdh()` raises, surface the message:
   `"Bloomberg Terminal must be open and connected"` and stop.
6. **Save if requested** — use `cd.save(df, path)`. Path is agent's choice
   unless the user specifies one.

---

## Complete Working Examples

### Example 1 — Single OAS series
```python
import sys
sys.path.insert(0, r"C:\Users\Eddy\.claude\skills\credit-data")
from credit_data import CreditData

cd = CreditData()
df = cd.fetch("cad ig")
print(df.tail())
# cad_oas
# 2025-03-05    122.0
# ...
```

### Example 2 — Multi-series OAS
```python
cd = CreditData(start_date="2020-01-01")
df = cd.fetch("cad ig and us ig")
print(df.columns.tolist())
# ['cad_oas', 'us_ig_oas']
```

### Example 3 — ER cumulative index
```python
cd = CreditData()
df = cd.fetch("cad ig er")
# Column returned: cad_ig_er_index (chain-linked, base=100 at 2002-11-01)
print(df["cad_ig_er_index"].tail())
```

### Example 4 — Weekly CDX spreads
```python
cd = CreditData(periodicity="W", start_date="2018-01-01")
df = cd.fetch("cdx ig and cdx hy")
# cdx_ig uses ROLL_ADJUSTED_MID_PRICE (not OAS) — handled automatically
```

### Example 5 — Spread context
```python
cd = CreditData()
print(cd.context("cad ig"))
print(cd.context("us hy"))
```

### Example 6 — Full dataset
```python
cd = CreditData()
df = cd.fetch_all()
cd.save(df, r"C:\Users\Eddy\Documents\Obsidian Vault\Market Data Pipeline\processed market data\credit_full.csv")
```

### Example 7 — CLI
```bash
# From the skill directory, with Bloomberg Terminal open:
uv run python credit_data.py "cad ig"
uv run python credit_data.py "us ig and us hy" --start 2020-01-01
uv run python credit_data.py "cad ig er" --out output.csv
uv run python credit_data.py --context "cad ig"
uv run python credit_data.py --all --out full_credit.csv
```

---

## Authoritative Source Reference

The Bloomberg ticker/field mappings in `credit_data.py` are sourced from and
should stay in sync with `Market Data Pipeline/fetch_data.py`:

- `DEFAULT_PRICE_MAPPING` → `INSTRUMENT_REGISTRY` (OAS + CDX tickers)
- `DEFAULT_ER_YTD_MAPPING` → `INSTRUMENT_REGISTRY` (ER tickers)
- `DEFAULT_BAD_DATES` → `BAD_DATES`
- `DataPipeline.convert_er_ytd_to_index()` → `CreditData._convert_er_to_index()`

If tickers are added to `fetch_data.py`, add them to `INSTRUMENT_REGISTRY`
and `ALIAS_MAP` in `credit_data.py` as well.
