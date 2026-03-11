# Project Constitution
## Project Identity
- **Skill:** `ml-algo-trading` — ML Algorithmic Trading Toolkit
- **Location:** `C:\Users\Eddy\.claude\skills\ml-algo-trading\`

## Technology Stack
- Python >= 3.11, < 3.15 (via `.venv/` managed by UV)
- Core libraries: pandas, numpy, statsmodels, scikit-learn, lightgbm, xgboost, vectorbt, shap, hmmlearn
- All execution: `uv run python script.py`

## Project Structure
- `SKILL.md` — main skill entrypoint; 9-step pipeline + reference table
- `references/` — implementation reference files loaded on demand by agents
  - `regime-philosophy.md` — regime axiom, detection code, failure diagnostics, live monitoring
  - `predictability-analysis.md` — entropy suite, Hurst, BDS, Predictability Score 0–100, agent exec spec
  - `feature-engineering.md` — fractional differentiation, alpha factors, information-driven bars
  - `labeling-weighting.md` — triple-barrier method, meta-labeling, sample weights
  - `model-selection.md` — model comparison matrix, GBM grids, SHAP, purged CV tuning
  - `validation-backtesting.md` — PurgedKFold, walk-forward, PSR, DSR, Kelly, drawdown analysis
  - `strategy-improvement.md` — Section A: binary filter testing; Section B: GA optimization; Section C → see eda-ml-practices.md
  - `eda-ml-practices.md` — EDA methodology, 17-point output format, ML trading best practices, validation checklist
  - `portfolio-construction.md` — HRP, MVO comparison, strategy allocation, rebalancing, performance optimization
  - `advanced-techniques.md` — LSTM, CNN, NLP, RL, regime detection code, block bootstrap

## Executable Commands
- Install: `uv add pandas numpy statsmodels scikit-learn lightgbm xgboost vectorbt shap hmmlearn`
- Run: `uv run python script.py`
- Test: `uv run pytest`

## Hard Boundaries
- **Never modify vault source files** in `Prompts & Instructions/algo trading/` — they are read-only references
- **Never create new pipeline steps in SKILL.md** without explicit user approval
- **Never duplicate Python implementations** — if code exists in a reference file, reference it; don't copy it to another file
- **Skill reference wins over vault** on code conflicts — existing implementations are already production-tested
- **CONFIG objects in reference files are spec templates** — function signature defaults take precedence in actual code
- **`validate_strategy()` is a convenience reference only** — not a production function; label it as such
- **Never commit secrets** (API keys, credentials, `.env` files)
- **Encoding:** all file I/O must specify `encoding='utf-8'` explicitly
