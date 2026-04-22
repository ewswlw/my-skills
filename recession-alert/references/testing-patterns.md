# Testing Patterns and TDD

Aligned with embedded tests in `spx_timing_strategy.py` (`--test`, `--menu 12-22`) and `project-constitution.md` (tests for merge/P&L-affecting code).

---

## Test categories

| # | Category | What to assert |
|---|----------|----------------|
| 1 | **Schema / loader** | File exists; sheet exists; required columns present; dates parse; index monotonic |
| 2 | **Merge invariants** | Business-day index; after `ffill`, no lookahead from future *file* rows (spot-check known dates); duplicate dates handled; panel ends at last valid price row |
| 3 | **Features** | No `inf`; NaNs handled per project rules; z-scores finite after warmup |
| 4 | **Rule positions** | Binary or bounded outputs; **RFE-6 hard gate** forces flat when enforced; CMHI/TDIFF thresholds |
| 5 | **Backtest math** | CAGR, MDD, alpha vs benchmark on synthetic series with known answer |
| 6 | **ML / labels** | PurgedKFold no overlap; meta-labels no lookahead; walk-forward embargo |
| 7 | **Freshness** | Last CMHI / SUPERINDEX date within tolerance (integration) |

---

## Naming and placement

- **Pytest:** `tests/test_<module>_<behavior>.py` when using a `tests/` folder.
- **Embedded (legacy):** `_t_<concern>()` functions registered in a test runner menu.
- Pattern: **`test_<function>_<property>`** or **`_t_<property>`**.

---

## Minimal pytest-style templates

**Loader/schema:**

```python
def test_load_cmhi_required_columns(tmp_path):
    # Use fixture copy of small Excel snippet or mock pd.read_excel
    ...
```

**Merge invariant:**

```python
def test_ffill_uses_prior_row_only():
    # Construct weekly series with jump on known Wednesday; assert daily Thu/Fri
    # equal Wednesday value until next week
    ...
```

**Backtest alpha (synthetic):**

```python
def test_alpha_two_percent_excess():
    # Benchmark flat 0; strategy +2% annualized synthetic → alpha ~ 0.02
    ...
```

---

## Validation gates (research quality)

| Gate | Typical threshold | Failure means |
|------|-------------------|---------------|
| Holdout | Last 20% OOS | Tune only on train portion |
| OOS degradation | Train metric vs test &lt; ~20% drop | Possible overfit |
| DSR | Below project threshold (e.g. **&lt; 0.95** in reference code) | Low DSR ⇒ multiple-testing / snooping suspicion—**higher** DSR is better |
| Parameter robustness | Perturb thresholds ±20% | Strategy fragile |

Constants like `HOLDOUT_PCT`, `DSR_THRESHOLD` live in `spx_timing_strategy.py` config—override per project in config YAML.

---

## TDD workflow rule

For **new** loaders, merge changes, features, or position logic:

1. **Write the failing test** (schema error, wrong CAGR, gate not firing).
2. Implement the minimum code to pass.
3. Refactor only with tests green.

Skip TDD only for exploratory notebooks—**promote** notebook logic to modules with tests before relying on capital allocation conclusions.

---

## Running tests (reference project)

```bash
uv run python "Coding Projects/Recession Alert/spx_timing_strategy.py" --test
```

Or menu groups `--menu 13`–`22` for focused suites. Prefer **`uv run`** per vault rules.

---

## Suggested checklist before “strategy works” claims

- [ ] Schema validation passes on current Raw Data (skill `raw-data/*.xlsx` and/or vault `Coding Projects/Recession Alert/Raw Data/`, depending on which paths the code loads)
- [ ] Merged panel start date matches **max overlap** or explicit user start
- [ ] Benchmark column aligned with strategy returns (lag, total return)
- [ ] At least one **integration** test: load → merge → one backtest metric on toy data
- [ ] If ML: purged CV + holdout documented with trial count for DSR
