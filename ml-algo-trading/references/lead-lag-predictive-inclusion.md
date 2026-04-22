# Lead–Lag, Granger Causality, and Predictive Inclusion

This reference extends the main pipeline when the hypothesis involves **cross-series timing** (e.g. macro X → asset Y, commodity → sector equity) or when you need to separate **hedging** from **directional** information. Read together with `regime-philosophy.md`, `feature-engineering.md`, `labeling-weighting.md`, `validation-backtesting.md`, and `strategy-improvement.md` (discovery memory).

---

## 1. Principles

### Contemporaneous comovement vs structural lag

**Contemporaneous correlation** (two series moving together *in the same bar*) is primarily useful for **hedging** and **beta** — it tells you how exposures co-move, not necessarily *where to position next* once both legs have printed.

**Non-zero lag** in the cross-correlation of **returns** (if **economically grounded** and **stable out-of-sample**) can indicate a **transmission delay**: information or shock A is impounded in B only after τ bars. That is a candidate for **timing** or **overlay** alpha, not a substitute for risk management.

### Transmission mechanism (mandatory for tradable claims)

A **statistical** lead (peak |ρ| at τ ≠ 0) is **not** an economic edge until you can state **why** the delay exists (e.g. flow into ETF before single names, earnings revision lag, roll-driven dynamics in a futures proxy). Without a mechanism, treat the lead as **unstable** or **artifact-prone**.

### Regime dependence

Optimal lag **τ** is generally a function of market state — e.g. realized volatility, liquidity, macro trend, positioning. See `regime-philosophy.md`. **Global** or **full-sample** estimates of τ often **mislead**; **rolling** and **regime-indexed** validation are mandatory before promotion.

### From research to execution

Map any approved relationship to a **portfolio process**: **Signal → Position → Risk → Execution**, with explicit rules for activation, strength, horizon, sizing, and **when to disable** (regime drift, lag decay).

---

## 2. Lead–lag procedure (operational)

### Use returns, not prices

Work on **log-returns** (or simple returns), not raw prices, to avoid spurious correlation driven by shared **trends**.

For series A and B:

\[
\rho_\tau = \text{corr}(r_A(t),\, r_B(t+\tau))
\]

Interpretation (by construction of the shift): **τ > 0** means **A leads B** when the shift is applied as in your implementation (always document which series is shifted).

### Minimum observations per lag

Each lag **τ** reduces usable sample size. Enforce a **minimum effective n** per lag (e.g. one trading year of overlapping bars) before treating a correlation as meaningful.

### Optimal-lag matrix asymmetry

For a pair (A, B), compare estimated optimal lags **A→B** vs **B→A**. Pure **contemporaneous** beta-style relationships often look **symmetric**; **directional information flow** can show **asymmetry** (not a hard rule — validate empirically and economically).

### Rolling vs full sample

**Do not** promote a feature based on **full-sample** peak τ alone. Require **rolling** optimal lag and/or **rolling** correlation stability; reject if “significant in-sample, dead or inverted out-of-sample.”

### Illustrative: cross-correlation on returns

```python
import numpy as np
import pandas as pd


def cross_correlation_returns(
    series_a: pd.Series,
    series_b: pd.Series,
    max_lag: int = 10,
    min_obs: int = 252,
) -> pd.Series:
    """
    Cross-correlation of *returns* at lags in [-max_lag, max_lag].
    Aligns shifted A with B: positive lag => A leads B (A shifted back).
    """
    r_a = series_a.dropna()
    r_b = series_b.dropna()
    correlations: dict[int, float] = {}
    for lag in range(-max_lag, max_lag + 1):
        shifted_a = r_a.shift(lag)
        aligned = pd.concat([shifted_a, r_b], axis=1).dropna()
        if len(aligned) < min_obs:
            correlations[lag] = np.nan
        else:
            correlations[lag] = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
    return pd.Series(correlations)
```

---

## 3. Granger causality (operational)

### Definition (predictive inclusion, not economic causation)

**Granger causality** tests whether **lagged values of X** improve the **linear** forecast of **Y**, beyond what **lagged Y alone** provides. It is a **predictive inclusion** statement, not proof of an economic causal mechanism. **Common latent factors** and **structural breaks** can generate false positives.

### statsmodels column order

`statsmodels.tsa.stattools.grangercausalitytests` expects a 2-column array:

- **Column 0** = **target** Y (the series to predict)
- **Column 1** = **predictor** X (lags of X are tested)

**Pre-register** `maxlag` (and avoid testing many maxlag values without counting them in **n_trials** for DSR).

### Rolling and OOS discipline

Complement a **single** full-sample test with **rolling** window Granger tests and **out-of-sample** decay checks. **Reject** features that pass full-sample but fail **rolling** or **walk-forward** stability (same spirit as strategy failure diagnostics elsewhere in the skill).

### Illustrative: Granger test on returns

```python
from statsmodels.tsa.stattools import grangercausalitytests

# gc_data: column 0 = target (e.g. SPY returns), column 1 = predictor (e.g. VIX returns)
# maxlag = p: joint test on coefficients of X_{t-1}..X_{t-p}
gc_data = ...  # np.ndarray shape (n, 2)
grangercausalitytests(gc_data, maxlag=3)
```

---

## 4. Relationship to the |t|>3 IC screening gate

| Statistic | Typical question |
|-----------|------------------|
| **Granger** | Do lags of **X** improve **linear** forecast of **Y**, given lags of **Y**? |
| **Univariate IC vs forward return** | Does **feature** (often aligned to **predict** next-period target return) **co-move** with forward return in a **ranking** sense? |

They are **not** equivalent. A variable can **Granger-cause** Y but show **weak IC** after scaling or in a specific horizon; conversely, high **IC** can reflect **contemporaneous** structure or **leakage** if misaligned.

**Rule:** **Pre-specify one primary promotion criterion** for the research stage (e.g. IC at a **fixed** alignment implied by the hypothesis). Use the other as a **diagnostic**. **Do not** “require both” and then **cherry-pick** the window where both pass — that is **double p-hacking**.

---

## 5. Multiple testing, n_trials, and discovery memory

### What to count toward n_trials (DSR)

Include every **independent comparison** that **informed** the final feature choice, including:

- Pairs **(A, B)** tested
- Each **lag τ** (or range) explored to **select** τ\*
- Each **maxlag** (Granger) tried to **select** specification
- Hyperparameter grids tied to lead–lag construction

**Bidirectional rule:** If you **explore** both **A→B** and **B→A** (or symmetric ±τ scans) to **decide direction**, count **both directions** in **n_trials**. If the hypothesis **pre-registered** a single direction and you **never** tested the reverse, do not count the untested direction. If you **peeked** at both, count both.

### Discovery memory

Per `strategy-improvement.md` Section C, **log rejected** structures: (pair, τ, window, regime, failure mode: e.g. “rolling Granger p>0.05”, “τ flips sign OOS”). Prevents **repeated heatmap fishing** across sessions.

### Stricter validation paths

For **large** combinatorial searches over pairs and lags, consider **Combinatorial Purged Cross-Validation (CPCV)** and **Probability of Backtest Overfitting (PBO)** — see headings **CPCV** and **PBO** in `validation-backtesting.md`. Do not duplicate full implementations here.

---

## 6. Step 2: Bivariate / conditional predictability

The default **predictability_score** on **Y alone** (see `predictability-analysis.md`) answers: “Is **Y** marginally predictable?”

For **X → Y** timing hypotheses, **Y** can look **weak** on univariate predictability while **incremental** predictability from **X** (conditional on Y’s own lags) is **real**. In that case:

- **Do not STOP** on univariate score **alone** without checking the **bivariate** story (see footnote in `predictability-analysis.md`).
- Use **pre-specified** incremental tests (e.g. **rolling Granger**, **directed** prediction error reduction) with the same **purged / OOS** discipline as the rest of the pipeline.

The univariate pipeline remains the **default** for **single-series** forecasting; bivariate logic is an **extension**, not a bypass of data validation or DSR.

---

## 7. Instrument and data hygiene

### ETF vs spot / underlying

An **ETF** (e.g. commodity tracker) may **not** match **spot** economics: **roll yield**, **contango/backwardation**, **replication** slippage. If the thesis references **spot** but the data are an **ETF**, either **restate the thesis** to the tradable instrument or **reconcile** to a more appropriate series.

### Futures rolls

Rolled futures series embed **contract change** and **term-structure** effects. Lead–lag vs an **equity** may pick up **roll** and **microstructure** as much as “information flow.” **Document** the contract rule and run **sensitivity** where applicable.

Tie to Step 1.5: **reconciliation** and **provenance** in `data-validation.md` (and **Instrument and proxy series** there).

---

## 8. High frequency and the Epps effect

At **intraday** and **tick** resolution, **asynchronous trading** and the **Epps effect** (correlation **deflation** at high frequency) can create **spurious** lead–lag **unless** you use appropriate **sampling, alignment, or** correlation estimators for **asynchronous** data.

**Default stance in this skill:** the main pipeline is **daily+** unless you explicitly add a **microstructure-grade** sub-pipeline. Do **not** copy daily `shift`-based lead–lag code to **tick** data without review.

---

## 9. Optional: transfer entropy (nonlinear directed dependence)

**Granger** is **linear** by construction. **Transfer entropy** and related **information-theoretic** measures can flag **nonlinear** directed dependence (often **stronger in tails** or stress regimes).

- Treat TE as an **optional second screen**, not a required dependency. **Vetted** third-party packages may be used after maintainer review; **no** new package is **required** by the core skill.
- **Permutation / block**-style nulls and **OOS** stability are still mandatory.
- **Count tuning** and **grid search** in TE construction toward **n_trials**.

When **TE is strong and Granger weak (OOS-robust)**: possible **nonlinear** edge — use **different sizing and risk** assumptions than a linear factor. When **Granger is strong and TE weak**: often **linear** spuriousness or **regime-fragile** — validate carefully.

---

## 10. Net-of-cost and promotion

**Predictive** (Granger) is not **profitable** after **costs**. A rough break-even **intuition** for many systematic setups:

> Gross edge scales like **|IC| × σ_target × √breadth**; it must exceed **turnover × cost per unit** **plus** slippage model error.

Promote features using **realistic** costs for the **actual** **traded** universe (large-cap US vs **EM** vs small-cap). Align with **walk-forward** implementation assumptions in `validation-backtesting.md` and `portfolio-construction.md`.

---

## 11. Labels, leakage, and causal alignment (Step 4)

For **lagged** predictors of **Y**:

- **Labels** and **triple-barrier** events must be defined using **only information available at** the **label** time for **Y** (and consistent with PIT in `data-validation.md`).
- A **bad pattern**: “lead–lag in **features**” but **label** or **barrier** construction accidentally uses **future** information from **Y** in the same bar as a **leaked** “signal.”

See `labeling-weighting.md` and Step 4 in the main `SKILL.md`.

---

## 12. Adversarial: naive “bolt-on” failure modes

| Risk | What breaks | Mitigation |
|------|-------------|------------|
| **Contemporaneous mislabeling** | “Alpha” is **hedge** or **beta**, not **timing** | Distinguish **hedging** vs **positioning**; align IC at **horizon** implied by τ; pre-specify **direction** of information flow |
| **Dual-test cherry-pick** | Only report windows where **Granger** and **IC** both “pass” | **One** primary criterion **pre-registered**; other is **diagnostic** |
| **n_trials undercount** | DSR **optimistic** after pair×τ×**maxlag** **search** | Count **all** tests that **informed** the final choice; include **A↔B** if both explored |
| **Full-sample only** | **Regime** inversion OOS; **one** F-test | **Rolling** Granger, **rolling** τ, **walk-forward** |
| **Univariate predictability stop** | Abandon valid **X→Y** when **Y** is **nearly** **white** | **Bivariate** / conditional check (Section 6) |
| **Instrument artifacts** | “Lag” = **ETF** **roll** or **NAV** **mechanics** | **Reconcile** instrument to thesis; document **replication** |
| **HF spurious lead** | **Epps** / **asynchrony** | **Daily+** default; HF needs **dedicated** **alignment** |
| **Linear + nonlinear double-count** | **GBM** finds interactions **not** in **Granger** | **Clear attribution**; stricter **purged** CV; **higher** **n_trials** for **model** **search** |
| **Late cost check** | **IC** **clears** **gross** but **not** **net** | **Net-of-cost** at **feature** or **simulation** **promotion** |
| **TE complexity** | Unstable **estimates** + **tuning** **inflation** | **Optional** **late** **stage**; **permutation**-style **discipline**; **n_trials** |

---

## 13. Production monitoring

Alongside **regime** and **moment** stability (`regime-philosophy.md`), monitor:

- **Lag decay:** rolling |ρ_τ| or **rolling** Granger **p-value** for promoted pairs
- **Stability of τ\*** in **relevant** **regime** **cells**

**Disable** or **down-weight** the signal when pre-specified **stability** criteria fail — same philosophy as **intervention triggers** in regime monitoring.

---

## See also

- `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\regime-philosophy.md` — joint state, **τ** as regime-dependent
- `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\validation-backtesting.md` — DSR, PSR, **CPCV**, **PBO**, walk-forward
- `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\strategy-improvement.md` — discovery memory, **n_trials** for **GA**
- `C:\Users\Eddy\.claude\skills\ml-algo-trading\references\data-validation.md` — **PIT**, **reconciliation**, **instrument** **proxies**
