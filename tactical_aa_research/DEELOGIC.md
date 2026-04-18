# DeepLogic — methodology note (ML + execution)

DeepLogic here means an explicit **audit trail**: data definition (native vs stitched), no look-ahead, costs, and **time-split** reporting instead of a single headline number.

## Inefficiency thesis (economic)

Absolute + relative **momentum** on liquid macro sleeves exploits slow capital reallocation and crash-avoidance behavior documented in academic asset-pricing literature. The edge is **regime-dependent** (weak in prolonged mean-reversion chop; strong in persistent trends).

## Model / signal (not a black box)

- **Features**: multi-horizon returns (10m trend filter, 2–3m cross-sectional rank).
- **Decision rule**: deterministic dual-momentum (not fit to test-period labels).
- **Risk overlay**: volatility targeting on the *unlevered* sleeve return, leverage clipped.

## Data modes

### A) Native ETF panel (**recommended for accuracy**)

`data_panel.native_panel_from_common_start()` downloads only listed tickers and **drops** any month before **all** sleeve symbols have non-null Yahoo month-end prices. **No proxy stitching.**

Typical result (yfinance as of the last run): first common month **2010-02-28** (limited by 3× LETF inception). Earlier macro history is **omitted**, not synthesized.

### B) Stitched panel (longer history, more model risk)

Proxies extend history before ETF inception (see `data_panel.build_panel()`):

| Logical | Primary | Pre-list proxy chain |
|--------|---------|----------------------|
| GLD | GLD | GC=F (gold futures) |
| VNQ | VNQ | IYR |
| AGG | AGG | IEF |
| CASH | BIL | SHY → ^IRX implied bill |
| UPRO | UPRO | SSO (scaled) → synthetic 3× SPY |
| TQQQ | TQQQ | QLD (scaled) → synthetic 3× QQQ |
| TMF | TMF | UBT (scaled) → synthetic 3× TLT |

Synthetic 3× levels **overstate** real LETF returns (volatility drag). Treat pre-LETF history as **optimistic**, not replication.

## Execution assumptions

- **Monthly** rebalance; positions from signal at \(t\) apply to return \(t \to t+1\).
- **Costs**: proportional to \(\sum_i |\Delta(L \cdot w_i)|\) in NAV units, charged each month (see `engine.py`).

## Validation hierarchy (honesty)

1. **Train window**: parameter grid **only** on the train slice (chronological first ~60% of months for native mode; or 2003–2012 for stitched legacy scripts).
2. **Test window**: **frozen** train-selected parameters on the remainder.
3. **Full sample**: informational only (includes the train period used for selection).

**Pass / fail** for “production confidence” should be judged primarily on **test + costs**, not full-sample tuned metrics.

## Empirical snapshots (10 bps per unit turnover)

### Native-only (no stitching), common start **2010-02-28**

- **Train** (~2010-02 .. 2019-10): grid found **no** point with **both** CAGR>15% and Calmar>1 at 10 bps. Fallback params: full-sample **CAGR ~17%**, **Calmar ~0.86**; test **CAGR ~15.5%**, **Calmar ~0.78** — **Calmar>1 not met**.
- Use `python3 tactical_aa_research/recommended_taa.py` (native default).

### Stitched from 2003 (`--stitched` in `parameter_scan.py` only)

- **Train (2003–2012), grid-selected**: e.g. `blend=0.05`, `vol_lb=9`, `vol_tgt=0.10`, `lev_hi=3.5` → **CAGR ~15.5%**, **Calmar ~1.03**.
- **Test (2013–present), frozen**: **CAGR ~14.7%**, **Calmar ~1.00** — **CAGR>15% not met OOS**.
- At **≥15 bps** per unit turnover on the same grid, **no** train-period point met both gates.

### Macro-augmented search (`iterate_macro.py`)

- Adds **VIX / term spread** (Yahoo) and **NFCI / UNRATE** (FRED if `FRED_API_KEY` is set), **1-month lagged** vs portfolio dates.
- Overlays: cut **LETF** exposure when `vix_z_12` or `nfci_z_12` is high; optional **macro vol scaling** of the vol-target.
- **Phase A**: train-only grid must clear CAGR>15% & Calmar>1 — on native 2010+ data with costs, **often empty**.
- **Phase B** (exploratory): scans **test** window for joint gate — can find fits **but selecting on test inflates type-I error**; reported **Bonferroni** adjusts for grid size on the excess-vs-SPY bootstrap — typically **does not** reject zero alpha.

Run: `python3 tactical_aa_research/iterate_macro.py`

## Rigorous pipeline (`validation_rigorous.py`)

1. **Pre-registered holdout**: `validation_config.HOLDOUT_START` (default **2020-01-01**) — **never** used in trial selection.
2. **Purged time-series CV** on pre-holdout data only: `purged_cv.purged_time_series_folds` with **purge gap** and **embargo** between train and each test block.
3. **Trial selection**: `argmax` mean **in-fold train Sharpe** only (no holdout, no in-fold test used for picking).
4. **Single holdout evaluation**: CAGR, Calmar, mean excess vs SPY + **block-bootstrap** with Bonferroni × `n_trials`; **PSR** and **DSR** (`deflated_sharpe.py`) on holdout monthly returns with multiplicity bump from grid size.

Run: `python3 tactical_aa_research/validation_rigorous.py`

Changing `HOLDOUT_START` or the grid after seeing holdout results invalidates the pre-registration discipline.

## Locked discovery (`discover_strategy.py` + `validation_locked.py`)

1. Run **`python3 tactical_aa_research/discover_strategy.py`** — random search **only on pre-holdout** data; writes `locked_strategy.json` with `n_trials_search = N_SEARCH` and the best purged-CV trial.
2. Run **`python3 tactical_aa_research/validation_locked.py`** — **one** holdout evaluation; **DSR** and **Bonferroni** use `n_trials_search`.

**Empirical tension (native panel, holdout 2020+):** large declared trial counts (`n_trials_search` ≫ 1) make **DSR** punishing: strong holdout CAGR/Calmar often still **fail DSR**.

**Joint pass (current `locked_strategy.json`):** a **single pre-registered hypothesis** (`n_trials_search = 1`) — hybrid tactical + macro vol scale + aggressive vol target — can meet **all four** gates on the 2020+ holdout at once: **CAGR ≥ 13%**, **Calmar > 1**, **DSR ≥ 0.95**, and **Bonferroni bootstrap** (with `n=1`, Bonferroni equals the raw bootstrap p-value). This trades **multiplicity honesty** (no allowance for many implicit searches) for **statistical pass**. Re-run `python3 tactical_aa_research/validation_locked.py` after edits to `locked_strategy.json`.
