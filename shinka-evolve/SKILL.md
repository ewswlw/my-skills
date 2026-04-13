---
name: shinka-evolve
description: >-
  Scaffold and run SakanaAI ShinkaEvolve (shinka-evolve) to evolve algorithmic
  trading strategies via LLM + evolutionary search. Creates evaluate.py with
  run_shinka_eval and initial.py with EVOLVE-BLOCK, configures Gemini API key,
  sets combined_score fitness (Sharpe, drawdown, turnover penalties), and runs
  shinka_run. Use when the user mentions ShinkaEvolve, shinka-evolve, shinka_run,
  evolving a trading strategy, LLM program evolution for alpha, open-ended
  optimization of signal logic, mutating backtest code, or evolutionary
  algorithm design for systematic trading. Also use when user asks to optimize
  a signal function, evolve position sizing, or auto-improve a backtest.
---

# ShinkaEvolve for Algorithmic Trading

Evolve trading signal code using LLM mutations + evolutionary search.
Upstream: https://github.com/SakanaAI/ShinkaEvolve

## Prerequisites

1. **Python >=3.10** with `uv` package manager
2. **Gemini API key** in environment (see [API Key Setup](#api-key-setup))
3. A Python project with a venv or uv-managed environment

## API Key Setup

The Gemini API key **must** be an environment variable. **NEVER** store it in
files, print it, log it, or echo it in terminal output.

```powershell
# Windows PowerShell (session)
$env:GEMINI_API_KEY = "your-key-here"

# Windows permanent (user scope)
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key-here", "User")
```

```bash
# Linux/macOS
export GEMINI_API_KEY="your-key-here"
```

Or use a `.env` file in the project root (never commit it):

```
GEMINI_API_KEY=your-key-here
```

See `.env.example` in this skill folder for the template.

## Agent Workflow

When the user triggers this skill, follow these steps **in order**:

### Step 1: Check environment

```python
# Verify shinka is installed
import importlib.util
if not importlib.util.find_spec("shinka"):
    # Install it
    # uv add shinka-evolve numpy pandas yfinance
    pass

# Verify API key
import os
assert os.environ.get("GEMINI_API_KEY"), "Set GEMINI_API_KEY env var first"
```

If `shinka` is missing, install via `uv add shinka-evolve numpy pandas yfinance`.
If `GEMINI_API_KEY` is not set, stop and tell the user how to set it (see above).

### Step 2: Create task directory

Create a folder in the user's project (e.g. `shinka_trading_task/`) containing:

| File | Source |
|------|--------|
| `evaluate.py` | Adapt from template in [reference.md](reference.md) § evaluate.py |
| `initial.py` | Adapt from template in [reference.md](reference.md) § initial.py |

Read `reference.md` in this skill folder for the **full templates** with inline
comments. Adapt to the user's data (ticker, date range, features).

### Step 3: Configure evolution

Default config (override per user request):

| Parameter | Default | Notes |
|-----------|---------|-------|
| `num_generations` | 50 | Quick test: 20; thorough: 100+ |
| `max_evaluation_jobs` | 2 | Parallel local evaluations |
| `max_proposal_jobs` | 2 | Parallel LLM proposals |
| `max_api_costs` | 5.0 | USD budget cap; **warn if user removes** |
| `llm_models` | `["gemini-2.0-flash"]` | Adjust to user's available models |
| `fee_bps` | 1.0 | Transaction cost in basis points |
| `train_split` | 0.7 | 70% train / 30% test chronological |

### Step 4: Run evolution

```bash
shinka_run \
    --task-dir shinka_trading_task \
    --results_dir results/trading_evo \
    --num_generations 50 \
    --max-evaluation-jobs 2
```

Or use the Python API:

```python
from shinka.core import ShinkaEvolveRunner, EvolutionConfig
from shinka.database import DatabaseConfig
from shinka.launch import LocalJobConfig

job = LocalJobConfig(
    eval_program_path="evaluate.py",
    activate_script=".venv/Scripts/activate",  # Windows
)
runner = ShinkaEvolveRunner(
    evo_config=EvolutionConfig(
        init_program_path="initial.py",
        llm_models=["gemini-2.0-flash"],
        max_api_costs=5.0,
    ),
    job_config=job,
    db_config=DatabaseConfig(),
    max_evaluation_jobs=2,
    max_proposal_jobs=2,
    max_db_workers=2,
)
runner.run()
```

On Linux/macOS change `activate_script` to `.venv/bin/activate`.

### Step 5: Inspect results

After evolution completes, run the bundled inspection script:

```bash
uv run python path/to/this/skill/scripts/inspect_best.py \
    --results_dir results/trading_evo
```

Or just read the best program from `results/trading_evo/` and re-run it on the
test set to print a tearsheet.

## Fitness Design

`combined_score` in `aggregate_metrics_fn` (higher = better):

```
combined_score = train_sharpe
               + 0.15 * test_sharpe
               - 0.05 * mean_turnover * 100
               - 0.25 * max(0, -train_max_dd)
               - 0.50 * max(0, train_sharpe - test_sharpe - 1.0)
```

The last term is a **train-test gap penalty**: if train Sharpe exceeds test
Sharpe by more than 1.0, the score is penalized, discouraging overfitting.

## Validation Rules

`validate_fn` rejects candidates that:
- Return NaN or non-finite Sharpe
- Have fewer than 20 train data points
- Crash or raise exceptions during evaluation

## Data Fallback Order

1. **User-provided CSV** (preferred)
2. **yfinance** download for a given ticker + date range
3. **Synthetic random walk** (deterministic seed, works offline)

## Key Constraints

- **NEVER** store, print, log, or echo API keys
- **NEVER** remove `max_api_costs` without explicit user confirmation
- **NEVER** use test data inside `combined_score` as the primary metric
- **ALWAYS** apply `shift(1)` to positions before computing returns (no lookahead)
- **ALWAYS** include transaction costs in simulated PnL
- Pin `shinka-evolve>=0.0.4` in requirements

## Upgrade Paths (document for user, don't implement by default)

- Walk-forward or purged k-fold CV instead of simple 70/30
- Slippage model (spread + market impact) instead of flat bps
- Multi-asset / portfolio-level evolution
- Ensemble of multiple LLM providers (Gemini + OpenAI)

## References

- Full code templates: [reference.md](reference.md)
- Post-evolution script: [scripts/inspect_best.py](scripts/inspect_best.py)
- API key template: [.env.example](.env.example)
- Upstream docs: https://sakanaai.github.io/ShinkaEvolve/getting_started/
- Upstream repo: https://github.com/SakanaAI/ShinkaEvolve
