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
