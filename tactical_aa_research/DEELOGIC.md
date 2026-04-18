# DeepLogic — methodology note (ML + execution)

DeepLogic here means an explicit **audit trail**: data stitching, no look-ahead, costs, and **time-split** reporting instead of a single headline number.

## Inefficiency thesis (economic)

Absolute + relative **momentum** on liquid macro sleeves exploits slow capital reallocation and crash-avoidance behavior documented in academic asset-pricing literature. The edge is **regime-dependent** (weak in prolonged mean-reversion chop; strong in persistent trends).

## Model / signal (not a black box)

- **Features**: multi-horizon returns (10m trend filter, 2–3m cross-sectional rank).
- **Decision rule**: deterministic dual-momentum (not fit to test-period labels).
- **Risk overlay**: volatility targeting on the *unlevered* sleeve return, leverage clipped.

## Data (stitching)

Proxies extend history before ETF inception (see `data_panel.py`):

| Logical | Primary | Pre-list proxy chain |
|--------|---------|----------------------|
| GLD | GLD | GC=F (gold futures) |
| VNQ | VNQ | IYR |
| AGG | AGG | IEF |
| CASH | BIL | SHY → ^IRX implied bill |
| UPRO | UPRO | SSO (scaled) → synthetic 3× SPY |
| TQQQ | TQQQ | QLD (scaled) → synthetic 3× QQQ |
| TMF | TMF | UBT (scaled) → synthetic 3× TLT |

Synthetic 3× levels are **known to overstate** real LETF returns (volatility drag). Treat pre-LETF history as **upper-bound optimism**, not replication.

## Execution assumptions

- **Monthly** rebalance; positions from signal at \(t\) apply to return \(t \to t+1\).
- **Costs**: proportional to \(\sum_i |\Delta(L \cdot w_i)|\) in NAV units, charged each month (see `engine.py`).

## Validation hierarchy (honesty)

1. **In-sample (2003–2012)**: small parameter grid only on this window (mitigate obvious snooping).
2. **Out-of-sample (2013–present)**: **frozen** train-selected parameters.
3. **Full-sample (2003–present)**: informational only after costs.

**Pass / fail** for “production confidence” should be judged primarily on **OOS + costs**, not full-sample tuned metrics.

## Empirical snapshot (current code, 10 bps per unit turnover)

- **Train (2003–2012), grid-selected**: `blend=0.05`, `vol_lb=9`, `vol_tgt=0.10`, `lev_hi=3.5` → **CAGR ~15.5%**, **Calmar ~1.03**, max DD ~−15%.
- **Test (2013–present), frozen**: **CAGR ~14.7%**, **Calmar ~1.00**, max DD ~−14.7% — **CAGR gate is not met OOS** at the stated cost and split.
- **Full sample (informational)**: **CAGR ~16.0%**, **Calmar ~1.06** (includes the train period used for selection).

At **≥15 bps** per unit turnover on the same grid, **no** train-period point met both CAGR>15% and Calmar>1 in our scan (`parameter_scan.py`).
