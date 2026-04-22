# Reference responses — manual “hand run” of `evals/evals.json` prompts

These are **gold-standard** style answers an agent should give when **`ml-algo-trading`** is in context. Use them to grade or diff model outputs.

Generated: 2026-04-22

---

## Eval 1 — `pipeline-hypothesis-dsr-trace`

**User prompt (summary):** Weekly L/S, 40 factors, kept |t|>2.5, walk-forward “looks good,” wants go-live and DSR / n_trials with only 3 LGBM seeds.

### Reference response

**Short answer: you are not ready to go live on that evidence alone, and n_trials is almost certainly not “3.”**

1. **Screening gate** — The skill’s mandatory hurdle is **|t|>3.0** on the univariate IC test before a factor **enters the model** (unless you document a **pre-registered** exception with extra penalties). Dropping the bar to 2.5 **widens the factor zoo** and **increases** the multiple-testing load that **Deflated Sharpe (DSR)** is meant to penalize. You should **re-run screening** at 3.0 or **justify** the lower bar and **increase** `n_trials` to reflect the **extra** mining.

2. **n_trials for DSR** — `n_trials` is the **count of independent strategy / specification trials** that **could have** produced the result you are reporting, including: number of **factors** tried or selected from a larger pool, **lookback** grids, **lag** exploration, **GA** evals, **seeds** only if you **chose the best** seed ex post. **Three random seeds** are a tiny part of the story if you also **tuned** 40 factors × multiple lookbacks. A honest lower bound is often:  
   `(# factor variants actually tested) × (relevant grid dimensions) × (seeds or restarts you cherry-picked from)`.  
   If you **only** ever trained **one** final feature set and **only** compared 3 seeds with **no** other search, state that **explicitly** — but **40** “candidates” usually implies **more** than 3 trials unless selection was **fully** blinded and **pre-registered**.

3. **PSR then DSR** — On **walk-forward OOS** returns: **Probabilistic Sharpe (PSR) > 0.95** first. Then **DSR > 0.95** with the **declared** `n_trials`. If DSR fails, the edge may be **snooped**.

4. **Go-live** — “Walk-forward looks good” must pass the **overfitting prevention checklist** (regime coverage, OOS vs IS, **net-of-cost**, crisis windows, **random** label test, etc.). A CSV path alone does not replace that narrative.

5. **Action items** — Re-screen at |t|>3; **reconcile** n_trials with full search history; compute **PSR/DSR** on **OOS** blocks; add **turnover and costs**; do **not** treat **IS** Sharpe as evidence.

**Expectations check:** mentions PSR/DSR and n_trials; challenges 2.5 vs 3; does not green-light on WF + 3 seeds alone.

---

## Eval 2 — `lead-lag-granger-heatmap`

**User prompt (summary):** Heatmap over 20 sector ETFs, oil → energy 6d lag, full-sample Granger p=0.03, no theory, wants “strongest lag” code.

### Reference response

**I should not just hand you production signal code off a heatmap with no economic story** — that is **exactly** the failure mode the skill’s **lead-lag** reference and Step 1 **element 5** are written to block.

1. **Hypothesis** — “Strongest lag from a **grid**” is **not** a hypothesis. You need a **transmission** sketch (e.g. **which** oil proxy vs which **constituent** **economics**, **ETF** **NAV/roll** vs **spot**, who is **slow** to reprice). **Pre-register** **direction** (X→Y) and a **small** set of lags **tied to that story**, or you must count **all** (pair × τ × direction) in **n_trials** for **DSR**.

2. **Stats** — **Full-sample** Granger **p<0.05** is **insufficient**. Require **rolling** Granger and **OOS** stability; reject if “significant **IS**, dead **OOS**.” Oil vs energy equity also has **ETF/roll** and **beta** **contemporaneous** **components** — see **hedging vs positioning** in the skill: you may be fitting **hedge** **ratios**, not **tradeable** **timing**.

3. **Code** — I can show **illustrative** **pandas/statsmos** for **log-return** **cross-corr** and `grangercausalitytests` with **Y first, X second** in the 2-column array — but label it **research** only until **transmission** + **rolling** **validation** pass.

4. **Discovery memory** — Log **rejected** (pair, τ) in **strategy-improvement** Section C so the next session does not **re-fish** the same heatmap.

**Expectations check:** rejects no-theory; mentions rolling, n_trials, instrument risk; not code-only.

---

## Eval 3 — `predictability-gate-bivariate`

**User prompt (summary):** Univariate **predictability** on target ETF **=15** (<20 STOP) but VIX→SPY **Granger** significant; PM says must STOP.

### Reference response

**The PM’s “score < 20 = STOP” is the right default for a *univariate* model of *Y alone*, but it is not automatically the end for a *pre-specified* *bivariate timing* *hypothesis*.**

1. **Footnote** — `predictability-analysis.md` **Bivariate / conditional** **footnote** and `lead-lag-predictive-inclusion.md` **Section 6**: **Y** can look **nearly** **unpredictable** **marginally** while **lagged** **VIX** still adds **information** in a **Granger** sense (predictive **inclusion** — **not** **economic** **causation**; **VIX/SPX** **mechanics** are **tangled**).

2. **Not a free pass** — You still need **PIT** **labels**, **purged** **CV**, **walk-forward**, **PSR/DSR** with **honest** `n_trials` (how many **VIX** **specs** / **lags** you tried). **VIX** **derived** from **SPX** **options** — interpret as **tight** **economic** **claim** and **stability** **checks**, not **magic** **alpha**.

3. **Decision** — You may **proceed** to **bivariate** **validation** **without** **contradicting** the univariate **STOP** for **Y-only** **forecasting**; you **do not** **overrule** the **score** with a **single** full-sample **Granger** **F-test** alone.

**Expectations check:** bivariate exception explained; OOS/DSR discipline repeated.

---

## How to use

- Compare model outputs to these sections for **substance**, not **verbatim** wording.
- For **CI**: simple string checks on **expectations** in `evals.json` or lightweight **LLM** grader per **skill-creator** `grading.json` format.
