# Project Constitution

## Technology Stack

- Python >=3.11, <3.15 (managed by UV)
- UV for virtual environments, dependency resolution, and lockfiles
- Hatchling as build backend
- Bloomberg Python API (`blpapi`) from `https://blpapi.bloomberg.com/repository/releases/python/simple`
- All other packages from PyPI

## Project Structure

```
<TARGET_DIR>/
├── pyproject.toml          # Generated from canonical list embedded in skill
├── <snake_name>/
│   └── __init__.py         # Minimal hatchling package stub
├── main.py                 # Entry-point scratch file
├── .gitignore              # Created if absent
├── .python-version         # Carries requires-python range
└── .venv/                  # Created by uv sync
```

## Executable Commands

- Sync runtime deps: `uv sync`
- Sync all extras: `uv sync --all-extras`
- Run Python: `uv run python script.py`
- Add a package: `uv add <package>`
- Health check: invoke skill with "check my UV env" or "env health check"

## Hard Boundaries

- Never use bare `python` or bare `pip` — always `uv run` / `uv add`
- Never hardcode personal file paths in the skill instructions
- Never read from the Bond-RV-App source at runtime — dependency list is embedded in the skill
- Never omit `[tool.uv.sources]` + `[[tool.uv.index]]` when `blpapi` is a dependency
- Always double-quote paths in all PowerShell commands (paths may contain spaces)
- Never commit `.venv/`, `uv.lock`, or any secrets to version control
- Update mode must diff only `[project].dependencies` — never silently overwrite user-added sections
