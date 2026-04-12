# Project Constitution

## Technology Stack
- Python 3.11 (shinka-evolve v0.0.4+ from PyPI, import as `import shinka`)
- UV package manager (`uv pip install shinka-evolve`)
- Google Gemini API via `google-genai`:
  - Mutation LLMs: `gemini-2.5-flash-preview` (volume) + `gemini-2.5-pro-preview` (quality)
  - Embeddings: disabled (`embedding_model: null`) — Levenshtein distance for code dedup
  - Temperature diversity: `[0.0, 0.5, 1.0]` (default, maintained)
- Hydra 1.3.2 (configuration management, bundled with shinka)
- Windows 10 + PowerShell (primary shell)

## Project Structure
- `SKILL.md` - Unified skill: setup, convert, run, inspect workflows
- `.env` - Gemini API key (`GOOGLE_API_KEY=...`)
- `reference.md` - Full EvolutionConfig, DatabaseConfig, JobConfig parameter tables
- `scripts/smoke_test.py` - Pre-flight evaluator validation
- `scripts/inspect_best.py` - Top-k program extraction to Markdown
- `scripts/run_evo.py` - Evolution launcher template
- `scripts/shinka.yaml` - Default YAML config (Gemini-only, 50 gens, 2 islands)
- `scripts/templates/` - 4 task scaffolds: algorithm, data processing, ML tuning, creative

## Executable Commands (PowerShell)
- Install: `uv pip install shinka-evolve`
- Smoke test: `uv run python scripts/smoke_test.py --program_path initial.py --results_dir .\smoke_results`
- Model check: `shinka_models --verbose`
- Set API key: `$env:GOOGLE_API_KEY = (Get-Content "$env:USERPROFILE\.claude\skills\shinka-evolve\.env" | Select-String "GOOGLE_API_KEY=(.+)" | ForEach-Object { $_.Matches.Groups[1].Value })`
- Launch evolution: `shinka_run --task-dir <dir> --results_dir .\results --num_generations 50`
- Inspect results: `uv run python scripts/inspect_best.py --results-dir .\results --k 5`
- WebUI (optional): `shinka_visualize --port 8888 --open`

## Hard Boundaries
- NEVER commit `.env` files or expose API keys in SKILL.md, scripts, or agent output
- NEVER launch evolution without a passing smoke test (metrics.json with numeric `combined_score` + correct.json with `correct: true`)
- NEVER skip the `shinka_models` pre-flight check — model names change; verify before every run
- NEVER exceed $5 USD per evolution run (enforce via `evo.max_api_costs=5.0`)
- NEVER auto-continue evolution batches without human confirmation (default policy)
- NEVER modify files outside the task directory during evolution (workspace `.venv` is shared for installs only)
- NEVER assume `.env` in the skill folder is auto-discovered by shinka — always set `$env:GOOGLE_API_KEY` or copy `.env` to task CWD before launching
- Embedding model MUST be `null` (no OpenAI dependency); dedup uses Levenshtein distance
- PowerShell string escaping: use `--set "evo.llm_models=[""gemini-2.5-flash-preview"",""gemini-2.5-pro-preview""]"` (double-quote escaping, not single quotes)
