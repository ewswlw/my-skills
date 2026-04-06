# P123 ML integration pipeline

Python package under the Portfolio123 skill: pull point-in-time data via **p123api**, run **PurgedKFold** + LightGBM/ExtraTrees, **PSR/DSR** gates, optional **StockFactor** / **DataSeries** upload, **ranking XML** builders, **discovery_memory** JSONL, and **Chrome CDP** helpers for the logged-in dashboard.

## Setup

1. Copy `.env.example` to `.claude/skills/portfolio123/.env` with `P123_API_ID` and `P123_API_KEY` (never commit `.env`).
2. Optional: `OBSIDIAN_VAULT` or `P123_OUTPUT_DIR` — defaults to `~/Documents/Obsidian Vault/p123-output`.
3. Optional: `CDP_SCRIPT` if `chrome-cdp` is not at `~/.claude/skills/chrome-cdp/scripts/cdp.mjs`.
4. From the Obsidian vault root: `uv sync` (pulls **gplearn** and existing deps).

## Run tests

```powershell
cd $env:USERPROFILE\Documents\Obsidian Vault
$env:PYTHONPATH = "$env:USERPROFILE\.claude\skills\portfolio123"
uv run pytest "$env:USERPROFILE\.claude\skills\portfolio123\tests" -q
```

Or use `pytest.ini` in the skill folder (run pytest with that config).

## CLI

```powershell
$env:PYTHONPATH = "$env:USERPROFILE\.claude\skills\portfolio123"
uv run python -m pipeline.orchestrator train
uv run python -m pipeline.orchestrator validate
uv run python -m pipeline.orchestrator discover
```

(`pull` requires API credentials.)

## Validation tiers

Per **Portfolio123** skill: **screen_backtest** / quick API metrics are **Tier 3** (estimated). Final claims require **native Simulated Strategy** or **Strategy Book** (**Tier 1/2**). This pipeline does not replace P123’s engine.

## Module map

| Module | Role |
|--------|------|
| `config` | Paths, thresholds, CDP script path |
| `data_pull` | `data_universe` batching, credits, license fallback |
| `feature_engineering` | IC screen, FFD, cross-section z |
| `model_training` | `PurgedKFold`, LGBM/ET, SHAP helper |
| `validation` | PSR, DSR, walk-forward, drawdown |
| `factor_upload` | `StockFactor` / `DataSeries` CSV upload |
| `regime_detection` | HMM + `DataSeries` + rule snippets |
| `ranking_builder` | Ranking XML + `agent_` validation |
| `discovery_memory` | JSONL log + explore/exploit hint |
| `cdp_monitor` | `node cdp.mjs` wrappers |
| `orchestrator` | CLI smoke / full loop stub |
