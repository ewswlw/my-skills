# Project Constitution

## Technology Stack
- Python >=3.11, <3.15 (via uv)
- p123api 2.2.0+ (Portfolio123 Python wrapper)
- Cursor IDE browser MCP tools (cursor-ide-browser)
- XML (ElementTree) for ranking system construction
- CSV/JSON for data persistence

## Project Structure
- `SKILL.md` — Core skill instructions, decision tree, workflow entry points (~200 lines)
- `api-reference.md` — Complete p123api endpoint reference, auth, credits, error handling
- `browser-workflows.md` — Login, strategy creation, AI Factor training, snapshot-verify pattern
- `ranking-templates.md` — 5 XML templates, XML validation checklist, factor discovery protocol
- `strategy-templates.md` — 3 strategy configs, buy/sell rule library, pipeline definitions
- `factor-quickref.md` — Curated ~50 most-used factors by category
- `ai-factor-guide.md` — Full ML workflow, 16 hyperparameter presets, 4 validation methods, evaluation diagnostics
- `andreas-reference.md` — Himmelreich methodology, robustness-first philosophy, ensemble design
- `learnings.md` — Continual learning journal, strategy DNA fingerprints, auto-update targets

## Data Output Convention
- All CSV/JSON exports saved to `./p123-output/` relative to workspace root
- Naming pattern: `{operation}_{timestamp}.{csv|json}` (e.g., `screen_backtest_20260312_143022.csv`)

## Executable Commands
- API auth test: `uv run python -c "import p123api; c = p123api.Client(api_id='$P123_API_ID', api_key='$P123_API_KEY'); print(c.data_prices('SPY', start='2024-01-01', end='2024-01-01'))"`
- Install client: `uv add p123api`
- Credit check: `uv run python -c "import p123api, os; c = p123api.Client(api_id=os.environ['P123_API_ID'], api_key=os.environ['P123_API_KEY']); r = c.data_prices('SPY', start='2024-01-01', end='2024-01-01'); print(f'Credits remaining: {r.get(\"quotaRemaining\", \"unknown\")}')"` 

## Hard Boundaries
- Never commit live strategy rebalances — research only
- Never store API keys or login credentials in skill files
- Never create P123 resources without the "agent" name prefix
- Never auto-update reference files without 3+ confirmations (or 1 high-confidence discovery)
- Never remove entries from reference files without user confirmation
- Never exceed 20 parameter combinations per optimization batch without explicit user override
- Never hold a browser session open during AI Factor training execution (async pattern only)
- SKILL.md must remain under 500 lines
