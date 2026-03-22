# RecessionALERT Data Dictionary

Distilled from `Guides/RecessAlert_Complete_Encyclopedia.md` and `Guides/RecessAlert_TimeSeries_Encyclopedia.md`. For full prose and methodology, read those files in the vault.

---

## File: CMHI_DATA.xlsx

Composite Market Health Index: breadth, momentum, volume, and macro inputs standardized and combined.

### Sheet: DAILY

| Column | Range / type | Meaning | Trading use |
|--------|----------------|---------|-------------|
| DATE | datetime | Trading day | Index |
| SP500 | float | S&P 500 price | Benchmark when SPXT unavailable |
| DIFF | See note below | Diffusion: in **weekly** sheets often integer 0–7; **daily** sheet may differ by export—verify against your file | Position sizing; fast regime |
| CMHI | about -1 to +1 | Equal-weight average of standardized components | Primary bull/bear filter |

### Sheet: WEEKLY (and MONTHLY — same columns, lower frequency)

| Column | Meaning | Trading use |
|--------|---------|---------------|
| NEW-HI | Net new highs breadth, standardized | Breadth divergence vs price |
| RISING | % names in uptrends, standardized | Participation |
| ROC | SPX rate-of-change oscillator, standardized | Momentum (noisier) |
| MAC | MA crossover oscillator, standardized | Trend confirmation |
| NET VOL | Net advancing volume, standardized | Liquidity / conviction |
| WLEI | Weekly leading economic index, standardized | Macro lead |
| SEASON | Seasonality factor, standardized | Calendar filter |
| DIFF | 0–7 diffusion count | DIFF/7 sizing; hard breadth count |
| CMHI | Composite | Regime |
| MEAN | Long-run regression mean of CMHI (~+0.3) | De-trend reference |
| SP-500 | Weekly/monthly SPX | Benchmark |
| CMHI-2 | CMHI minus MEAN | Bear warning earlier than raw CMHI |
| CMHI-3 | Alternative de-trended CMHI | Cross-check |

**Note:** Long-run mean of CMHI is about +0.3, not zero—bulls are longer than bears.

**CMHI-2 / CMHI-3:** Present on **WEEKLY** and **MONTHLY** sheets of `CMHI_DATA.xlsx`, not on the **DAILY** sheet. The reference `load_cmhi()` reads **DAILY** only (SP500, DIFF, CMHI). Strategies that gate on **CMHI-2** must load weekly/monthly CMHI or extend the loader—see `signal-hierarchy.md`.

---

## File: MonthlyData (4).xlsx

### Sheet: DATA (main monthly panel)

Wide sheet: NBER, SuperIndex, diffusion, RFE ensemble, many model columns, normalized block.

**Representative columns (names vary slightly by export):**

| Group | Examples | Meaning |
|-------|----------|---------|
| NBER | NBER | NBER recession months (label) |
| SuperIndex | CO-INCIDENT, LEADING, LEADING PROB | Current vs leading economy; recession probability |
| Diffusion | DIFF, DIFF CALL, SYN CALL, SYND, HEAD WND, ANXIOUS | Multi-indicator stress |
| RFE | RFE-6, … | Binary: ≥6 of 15 models flag recession |
| Models | NBER MODEL, GDP/I MODEL, Labor Index, USMLEI V2, WLEI2, USHMI, USLONG, RAVI, CMHI-II | Component and external models |
| Normalized | SUPERIDX, SUPER-COIX, …, AVG | Z-style panel for comparison |

**Trading use:** RFE-6 = hard risk-off for many strategies; LEADING / LEADING PROB for macro turns; normalized block for composite scoring.

### Sheet: RFE VARIANTS

| Column | Meaning |
|--------|---------|
| Unnamed: 0 (renamed DATE in code) | Month date |
| RFE-5 … RFE-15 | Binary ensemble triggers at different model counts |

**Loader in reference code:** `RFE-6` from this sheet for `load_recession`.

### Sheet: RAVI

Valuation / forward-return context. **Warning:** columns like 1YR FC, 2YR FC, … are **forward** returns—**do not** use as live trading inputs (lookahead). Use levels and SIGNAL per methodology in Guides.

### Sheet: WORLD

World Leading Economic Index and related—monthly macro context.

### Sheet: WEEKLY DATA

Weekly SuperIndex (`WEEK`, `WLIr`, `WLInr`, etc.). **Stale after ~2015** in many exports; reference implementation prefers **WeeklyData (2).xlsx → WEEKLY LEI's** for current SUPERINDEX.

### Sheet: INPUTS

Model performance stats (lead times, CoV, false positives)—metadata, not time series for trading.

---

## File: OPTIMUM_DATA.xlsx

### Sheet: OPTIMUM

| Column | Meaning | Values / notes |
|--------|---------|----------------|
| DATE | Day | Index |
| OPT-1 … OPT-5 | Sub-models | Binary / discrete signals per RA methodology |
| OPT-CMHI | OPTIMUM × CMHI style macro | Regime |
| STM, STM-PRO | Seasonality timing | Seasonal risk on/off |
| DIFFN | Diffusion count across OPT models | Conviction breadth |
| TRADE | Master action | Typically -1, 0, 1, 2 = short, cash, long, leveraged long |

**Warning:** OPTIMUM models are **in-sample optimized**; treat OOS performance with skepticism and strict validation.

---

## File: WeeklyData (2).xlsx

### Sheet: WEEKLY LEI's

| Column | Meaning |
|--------|---------|
| DATE | Week end |
| WLEI2, ECRI | Leading indices |
| SUPER | Renamed to SUPERINDEX in code—**preferred** current weekly SuperIndex |

### Sheet: SP500 BREADTH DATA

Many columns: **MTLV2**, **SIGS**, **DCOM**, **VIX**, **%>50DMA**, **%200DMA**, S1–S12, ZBT BUY, ALIX, VMCOS, etc. Chart-tab mapping is in the Complete Encyclopedia Part 6.

### Sheet: TRENDEX PROB MODELS

| Column | Meaning |
|--------|---------|
| TDIFF | Trendex differential (stops / trend strength) |
| NET P | Net probability-style score |
| TOP, BOT | Multi-factor top/bottom scores |
| FAST/MED/SLOW | Stop or horizon variants (per export) |

### Sheet: GEN-2 PROB MODELS

**P(TOP)** and **P(BOT)** at multiple horizons (column names like `P(TOP).1`, `P(BOT).1` for medium term). Probabilities 0–1.

### Sheet: SP500 MF PROB MODEL

| Column | Meaning |
|--------|---------|
| NET AVG, NET TOP3 | Combined probability scores |
| BIGBOT, BIGTOP | Rare high-conviction bottom/top flags |
| NET DIFF | Spread between top and bottom pressure |

---

## Data quality warnings (mandatory)

1. **Survivorship:** Breadth uses current S&P 500 constituents—long-horizon breadth has mild survivorship bias.
2. **RAVI forward columns:** Future return columns are hindsight—never feed them as same-day features.
3. **Gen-2 revisions:** Near-term probabilities can revise for a few days—document if you simulate point-in-time.
4. **OPTIMUM / STM:** In-sample optimization—use holdout, walk-forward, and DSR.
5. **Monthly WEEKLY DATA vs WEEKLY LEI's:** Use **WeeklyData** for up-to-date SUPERINDEX join in `load_recession`.

---

## Quick column → loader mapping (reference implementation)

| Loader | Source file / sheet | Key outputs |
|--------|---------------------|-------------|
| `load_cmhi` | CMHI_DATA / DAILY | SP500, DIFF, CMHI |
| `load_recession` | MonthlyData / RFE VARIANTS + WeeklyData / WEEKLY LEI's (+ optional WEEKLY DATA for WLIr) | RFE-6, SUPERINDEX, WLIr |
| `load_breadth_extended` | WeeklyData / SP500 BREADTH DATA | MTLV2, SIGS, DCOM, VIX, %>50DMA |
| `load_trendex` | WeeklyData / TRENDEX PROB MODELS | TDIFF, NET P, TOP, BOT |
| `load_gen2` | WeeklyData / GEN-2 PROB MODELS | P(TOP)*, P(BOT)* |
| `load_mf_prob` | WeeklyData / SP500 MF PROB MODEL | NET AVG, NET TOP3, BIGBOT, BIGTOP, NET DIFF |
| `load_optimum` | OPTIMUM_DATA / OPTIMUM | TRADE, DIFFN, OPT-CMHI, STM |

See `loaders-and-merge.md` for merge order and pitfalls.
