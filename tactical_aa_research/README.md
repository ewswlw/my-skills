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

## Notes

- Holdout boundary is defined in `validation_config.py` (`HOLDOUT_START`).
- Validation gates are sourced from `locked_strategy.json` when present.
- Data are downloaded from Yahoo at runtime; results can drift as upstream history updates.
