# tactical_aa_research

Tactical asset allocation research stack with:

- native ETF panel construction,
- momentum + macro overlays,
- transaction-cost-aware backtests,
- purged CV and holdout validation,
- probabilistic/deflated Sharpe diagnostics.

## Environment setup

From repository root:

```bash
python3 -m pip install -r tactical_aa_research/requirements.txt
```

## Core validation commands

Run from repository root:

```bash
python3 tactical_aa_research/validation_locked.py
python3 tactical_aa_research/validation_rigorous.py
```

## Automated tests

```bash
pytest tactical_aa_research/tests -q
```

## Iterative discovery workflow

```bash
python3 tactical_aa_research/discover_strategy.py
python3 tactical_aa_research/validation_locked.py
```

Optional broader seeded search:

```bash
python3 tactical_aa_research/joint_pass_search.py
python3 tactical_aa_research/validation_locked.py
```

## No-portfolio-leverage policy (default)

The current search/validation scripts default to:

- `portfolio_leverage_allowed = false`
- `portfolio_leverage_cap = 1.0`

This means portfolio NAV is never scaled above 1x. Leveraged ETFs can still appear
as holdings when selected by momentum logic, but the portfolio-level leverage scalar
is disabled.

Example no-leverage seeded search:

```bash
python3 tactical_aa_research/joint_pass_search.py --draws-per-seed 1 --seeds-tried-max 1200 --min-cagr 0.13 --min-calmar 1.0 --dsr-min 0.95
python3 tactical_aa_research/validation_locked.py
```

## Notes

- Holdout boundary is defined in `validation_config.py` (`HOLDOUT_START`).
- Validation gates are sourced from `locked_strategy.json` when present.
- Data are downloaded from Yahoo at runtime; results can drift as upstream history updates.
