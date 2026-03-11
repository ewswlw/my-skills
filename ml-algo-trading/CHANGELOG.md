# Changelog — ml-algo-trading Skill

---

## 2026-03-10 15:50 ET — Vault Integration

Integrated 7 Obsidian vault algo-trading documents (`Prompts & Instructions/algo trading/`)
into the skill's reference files using surgical synthesis. Only content unique to the vault
and absent from existing skill refs was added. Existing Python implementations were preserved
unchanged. Vault source files were not modified.

### Modified Files

**`references/regime-philosophy.md`**
- Added "What Shifts Across Regimes" summary table (means, variances, autocorrelations,
  correlations, factor loadings with trading implications)
- Added expanded "Asset & Timeframe Adaptations" table with detection difficulty column
  and universal truth note

**`references/predictability-analysis.md`**
- Added "Agent Execution Spec" section at top: annotated CONFIG template (marked as spec
  template only; function defaults take precedence), 10-step execution order, markdown
  report output template
- Expanded decision rules table from 8 to 10 conditions (added: score 20–40 with no
  regime variation = STOP; score > 80 = verify data integrity)

**`references/validation-backtesting.md`**
- Added "Drawdown Analysis" section with `calculate_drawdown()` and `time_under_water()`
  implementations (with type hints and docstrings)
- Added `validate_strategy()` convenience composite (annotated as convenience reference
  only, not a production function)

**`references/strategy-improvement.md`**
- Extended Section B (GA Optimization) with: GA edge case handling (market anomalies,
  data quality, computational efficiency), GA success criteria checklist, GA output
  documentation requirements
- Updated "See Also" to reference `eda-ml-practices.md`

**`references/portfolio-construction.md`**
- Added "Performance Optimization" section with: NumPy/Pandas vectorization patterns
  (loop vs vectorized comparison), `mp_pandas_obj()` atoms-and-molecules multiprocessing
  function (López de Prado pattern), `PortfolioManager` convenience class,
  performance optimization rules summary table

**`SKILL.md`**
- Updated Reference Files table: expanded all row descriptions to name new sections
  explicitly; added `eda-ml-practices.md` as a new row (10 reference files total)

### New Files

**`references/eda-ml-practices.md`** *(new)*
- EDA statistical techniques (8 methods: bootstrap CIs, multiple testing, purged CV,
  Monte Carlo, walk-forward, crisis stress tests, cross-asset robustness, live-execution
  replication)
- 17-point required EDA output format
- ML trading best practices (8 items)
- ML trading pitfalls table (5 items with fixes)
- Four-phase validation checklist (pre-development, development, validation, documentation)

**`project-spec.md`** *(new)*
- Full project specification for this integration work

**`project-constitution.md`** *(new)*
- Immutable technology stack, project structure, hard boundaries for the skill

### Vault Source Files Referenced (read-only, not modified)
- `Regime-Dependent Market Philosophy.md`
- `Time Series Predictability Analysis.md`
- `Cross-Validation & Performance Metrics.md`
- `Strategy Validation and Improvement Guide.md`
- `Genetic Algorithm Backtesting System.md`
- `Portfolio Construction & Implementation.md`
- `Trading Strategy Development Index.md`
