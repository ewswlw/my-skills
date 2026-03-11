# Project Constitution — Credit Data Skill

## Technology Stack
- Python >=3.11, <3.15
- xbbg (Bloomberg Terminal bridge)
- pandas >=2.0
- numpy >=1.26
- uv (package manager and runner)

## Project Structure
- `credit_data.py` — `CreditData` class: all fetch, resolve, context, and save logic
- `SKILL.md` — Cursor agent skill instructions and trigger keywords
- `references/ticker_registry.md` — human-readable alias and ticker documentation

## Executable Commands
- Run fetch: `uv run python credit_data.py "cad ig"`
- Run context: `uv run python credit_data.py --context "cad ig"`
- Fetch all: `uv run python credit_data.py --all --out output.csv`
- Run tests: `uv run pytest tests/` (if tests exist)

## Hard Boundaries
- Never import from `Market Data Pipeline/fetch_data.py` — `credit_data.py` is standalone
- Never commit Bloomberg credentials or API keys
- Never use bare `python` — always `uv run python`
- Never replace the ER chain-linking algorithm with `.cumprod()` — the year-by-year
  algorithm in `_convert_er_to_index()` must remain identical to `fetch_data.py`
- Never change the `INSTRUMENT_REGISTRY` column names — downstream code depends on them
- Bloomberg Terminal must be open before any `blp.bdh()` call — never silently swallow
  Bloomberg connection errors; always surface a clear message
