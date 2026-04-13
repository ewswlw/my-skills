# Project Constitution

## Technology Stack
- Python >=3.10, <3.15
- `shinka-evolve` >=0.0.4 (PyPI; `import shinka`)
- numpy >=1.24, pandas >=2.0
- yfinance (optional data fallback)
- uv (package manager)

## Project Structure
- `SKILL.md` — Main skill instructions (triggers, workflow, agent behavior)
- `reference.md` — Full `evaluate.py` + `initial.py` templates with inline comments
- `scripts/inspect_best.py` — Post-evolution tearsheet utility
- `.env.example` — API key environment variable template

## Executable Commands
- Install: `uv add shinka-evolve numpy pandas yfinance`
- Run evolution: `shinka_run --task-dir <task_dir> --results_dir <out> --num_generations 50 --max-evaluation-jobs 2`
- Inspect results: `uv run python scripts/inspect_best.py --results_dir <out>`

## Hard Boundaries
- **NEVER** store API keys in SKILL.md, reference.md, or any committed file
- **NEVER** print, log, or echo API keys in terminal output or results files
- **NEVER** remove the `max_api_costs` cap without explicit user confirmation
- **NEVER** use test/OOS data inside `combined_score` (train metrics only for fitness)
- **NEVER** create skills in `~/.cursor/skills-cursor/` (reserved for Cursor internals)
- **NEVER** modify the user's existing backtest code outside the designated task directory
