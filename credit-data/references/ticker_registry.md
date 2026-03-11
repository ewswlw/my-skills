# Credit Data — Ticker Registry

Authoritative alias and ticker reference for the `CreditData` skill.
Source of truth: `credit_data.py` → `INSTRUMENT_REGISTRY` + `ALIAS_MAP`.

Cross-reference: `Market Data Pipeline/fetch_data.py` → `DEFAULT_PRICE_MAPPING`,
`DEFAULT_ER_YTD_MAPPING`.

---

## OAS Spreads — CAD IG (field: `INDEX_OAS_TSY_BP`)

| Column Name | Bloomberg Ticker | Description | Key Aliases |
|---|---|---|---|
| `cad_oas` | `I05510CA Index` | CAD IG All Sectors | `cad ig`, `cad credit`, `cad spreads`, `canadian credit`, `cad oas` |
| `cad_short_oas` | `I34227CA Index` | CAD IG Short (1-5Y) | `cad short`, `cad short ig`, `cad 1-5` |
| `cad_long_oas` | `I34229CA Index` | CAD IG Long (10Y+) | `cad long`, `cad long ig`, `cad 10+` |
| `cad_credit_spreads_fins` | `I05523CA Index` | CAD IG Financials | `cad fins`, `cad financials`, `canadian financials` |
| `cad_credit_spreads_non_fins_ex_uts` | `I05520CA Index` | CAD IG Non-Fins ex Utilities | `cad non fins`, `cad industrials`, `non fins ex utils` |
| `cad_credit_spreads_uts` | `I05517CA Index` | CAD IG Utilities | `cad uts`, `cad utilities`, `canadian utilities` |
| `cad_credit_spreads_a_credits` | `I05515CA Index` | CAD IG A-rated | `cad a`, `cad single a`, `cad a credits`, `a credits` |
| `cad_credit_spreads_bbb_credits` | `I05516CA Index` | CAD IG BBB-rated | `cad bbb`, `cad triple b`, `cad bbb credits`, `bbb credits` |
| `cad_credit_spreads_provs` | `I34069CA Index` | CAD Provinces | `cad provs`, `canadian provinces`, `provincial spreads`, `provs` |
| `cad_credit_spreads_provs_longs` | `I34336CA Index` | CAD Provinces Long | `cad provs long`, `long provincials`, `long provs` |

---

## OAS Spreads — US (field: `INDEX_OAS_TSY_BP`)

| Column Name | Bloomberg Ticker | Description | Key Aliases |
|---|---|---|---|
| `us_ig_oas` | `LUACTRUU Index` | US IG Bloomberg US Agg Corp | `us ig`, `us investment grade`, `luac`, `luactruu`, `american ig` |
| `us_hy_oas` | `LF98TRUU Index` | US HY Bloomberg US HY | `us hy`, `us high yield`, `lf98`, `lf98truu`, `junk spreads` |

---

## CDX Spreads (field: `ROLL_ADJUSTED_MID_PRICE`)

> ⚠ CDX instruments use `ROLL_ADJUSTED_MID_PRICE`, not `INDEX_OAS_TSY_BP`.
> Field selection is automatic — no manual override needed.

| Column Name | Bloomberg Ticker | Description | Key Aliases |
|---|---|---|---|
| `cdx_ig` | `IBOXUMAE MKIT Curncy` | CDX IG (roll-adjusted) | `cdx ig`, `cdx investment grade`, `ibox ig`, `iboxumae` |
| `cdx_hy` | `IBOXHYSE MKIT Curncy` | CDX HY (roll-adjusted) | `cdx hy`, `cdx high yield`, `ibox hy`, `iboxhyse` |

---

## CDX Total Return Indices (field: `PX_LAST`)

These are Bloomberg-published cumulative return indices. No YTD conversion needed.

| Column Name | Bloomberg Ticker | Description | Key Aliases |
|---|---|---|---|
| `cdx_ig_er` | `ERIXCDIG Index` | CDX IG Excess Return Index | `cdx ig er`, `cdx ig er index`, `erix`, `erixcdig` |
| `cdx_hy_er` | `UISYMH5S Index` | CDX HY Excess Return Index | `cdx hy er`, `cdx hy er index`, `uisymh5s` |

---

## ER YTD → Chain-Linked Index (field: `INDEX_EXCESS_RETURN_YTD`)

> ★ Bloomberg returns year-to-date % return. `CreditData` automatically
> converts these to chain-linked cumulative indices (base 100).
> Output column names get an `_index` suffix.

### CAD ER

| Input Column | Output Column | Bloomberg Ticker | Description | Key Aliases |
|---|---|---|---|---|
| `cad_ig_er` | `cad_ig_er_index` | `I05510CA Index` | CAD IG ER | `cad er`, `cad ig er`, `cad excess return`, `cad er index` |
| `cad_ig_short_er` | `cad_ig_short_er_index` | `I34227CA Index` | CAD IG Short ER | `cad short er`, `cad short excess return` |
| `cad_ig_long_er` | `cad_ig_long_er_index` | `I34229CA Index` | CAD IG Long ER | `cad long er`, `cad long excess return` |
| `cad_credit_spreads_provs_er` | `cad_credit_spreads_provs_er_index` | `I34069CA Index` | CAD Provinces ER | `cad provs er`, `provincial er` |
| `cad_credit_spreads_provs_longs_er` | `cad_credit_spreads_provs_longs_er_index` | `I34336CA Index` | CAD Provinces Long ER | `cad provs long er`, `long provs er` |

### US ER

| Input Column | Output Column | Bloomberg Ticker | Description | Key Aliases |
|---|---|---|---|---|
| `us_ig_er` | `us_ig_er_index` | `LUACTRUU Index` | US IG ER | `us ig er`, `us ig excess return`, `us ig er index` |
| `us_hy_er` | `us_hy_er_index` | `LF98TRUU Index` | US HY ER | `us hy er`, `us hy excess return`, `us hy er index` |

---

## Ambiguity Resolution Rules

The alias map matches **longest phrase first**. This prevents short aliases
from incorrectly capturing more specific requests:

| Ambiguous phrase | Correct resolution | Why |
|---|---|---|
| `cad ig er` | `cad_ig_er` | "cad ig er" (9 chars) beats "cad ig" (6 chars) |
| `cad long er` | `cad_ig_long_er` | "cad long er" beats "cad long" |
| `cad short er` | `cad_ig_short_er` | "cad short er" beats "cad short" |
| `cad provs long er` | `cad_credit_spreads_provs_longs_er` | most specific wins |

---

## Bloomberg Field Summary

| Field | Used For |
|---|---|
| `INDEX_OAS_TSY_BP` | All CAD IG and US IG/HY OAS spreads |
| `ROLL_ADJUSTED_MID_PRICE` | CDX IG and CDX HY spreads |
| `PX_LAST` | CDX ER total return indices |
| `INDEX_EXCESS_RETURN_YTD` | CAD IG and US IG/HY ER (converted to index) |

---

## Known Bad Dates

| Date | Column | Action | Note |
|---|---|---|---|
| 2005-11-15 | `cad_oas` | replace with prior day | Bloomberg data error |
| 2005-11-15 | `cad_credit_spreads_non_fins_ex_uts` | replace with prior day | Bloomberg data error |
| 2005-11-15 | `cad_credit_spreads_bbb_credits` | replace with prior day | Bloomberg data error |
| 2005-11-15 | `cad_ig_er_index` | replace with prior day | Bloomberg data error |

*Source: `Market Data Pipeline/fetch_data.py` → `DEFAULT_BAD_DATES`*
