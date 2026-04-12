---
name: shinka-evolve
description: "Run LLM-driven evolutionary code optimization using ShinkaEvolve. Covers full lifecycle: scaffold new tasks (shinka-setup), convert existing code (shinka-convert), run evolution batches (shinka-run), and inspect top results (shinka-inspect). Trigger on: shinka, ShinkaEvolve, evolve code, optimize algorithm, evolutionary search, LLM mutation, program evolution, code evolution."
---

# ShinkaEvolve — Unified Agent Skill

Combine LLMs with evolutionary algorithms to optimize code. This skill covers the full lifecycle: setup, convert, run, and inspect.

## Workflow Router

Determine which workflow applies:

| Situation | Workflow | Jump to |
|-----------|----------|---------|
| New task from a description, no existing code | **Setup** | [Setup Workflow](#setup-workflow) |
| Existing codebase to optimize | **Convert** | [Convert Workflow](#convert-workflow) |
| `evaluate.py` + `initial.py` already exist | **Run** | [Run Workflow](#run-workflow) |
| Evolution completed, need results | **Inspect** | [Inspect Workflow](#inspect-workflow) |

## Pre-flight (Required Before Any Run)

Before launching evolution, **always** execute these checks:

```powershell
# 1. Set API key (load from skill .env)
$skillEnv = "$env:USERPROFILE\.claude\skills\shinka-evolve\.env"
$env:GOOGLE_API_KEY = (Get-Content $skillEnv | Select-String "GOOGLE_API_KEY=(.+)" | ForEach-Object { $_.Matches.Groups[1].Value })

# 2. Verify shinka is installed
uv run python -c "import shinka; print(shinka.__version__)"
# If missing: uv pip install shinka-evolve

# 3. Verify models are available
shinka_models --verbose
# Confirm gemini-2.5-flash-preview and gemini-2.5-pro-preview appear in llm list

# 4. Smoke test the task
uv run python "$env:USERPROFILE\.claude\skills\shinka-evolve\scripts\smoke_test.py" --task-dir .
```

If any check fails, fix it before proceeding. Do NOT launch evolution with a failing smoke test.

---

## Setup Workflow

Create a new ShinkaEvolve task from a natural-language description.

### Inputs needed
- Task description + success criteria
- What to optimize (the "evolve region")
- Evaluation metric(s) and scoring direction (higher = better)
- Number of eval runs / seeds

### Steps

1. **Choose a template** from `scripts/templates/`:
   - `algorithm_optimization/` — pure algorithm improvement
   - `data_processing/` — pipeline throughput + quality
   - `ml_tuning/` — model training/inference accuracy
   - `creative_generation/` — novelty + quality scoring

2. **Copy template** to the task directory:
   ```powershell
   $skillDir = "$env:USERPROFILE\.claude\skills\shinka-evolve"
   Copy-Item -Recurse "$skillDir\scripts\templates\algorithm_optimization\*" .\my_task\
   ```

3. **Edit `initial.py`**: Replace the code inside `EVOLVE-BLOCK-START` / `EVOLVE-BLOCK-END` with your algorithm. Keep evolve markers tight — only code the LLM should mutate.

4. **Edit `evaluate.py`**: Customize `get_kwargs`, `aggregate_fn`, and `validate_fn` for your task. Ensure `combined_score` is numeric and higher = better.

5. **Copy config and .env** to task directory:
   ```powershell
   Copy-Item "$skillDir\scripts\shinka.yaml" .\my_task\
   Copy-Item "$skillDir\.env" .\my_task\
   ```

6. **Run smoke test**:
   ```powershell
   uv run python "$skillDir\scripts\smoke_test.py" --task-dir .\my_task
   ```
   Pass criteria: `metrics.json` has numeric `combined_score`, `correct.json` has `correct: true`.

7. **Ask user**: Run evolution manually, or proceed to [Run Workflow](#run-workflow)?

### Template: initial.py (Python)
```python
import random

# EVOLVE-BLOCK-START
def advanced_algo():
    # LLMs will mutate this region
    return 0.0, ""
# EVOLVE-BLOCK-END

def run_experiment(random_seed: int | None = None, **kwargs):
    """Entry point called by evaluator."""
    if random_seed is not None:
        random.seed(random_seed)
    return advanced_algo()
```

### Template: evaluate.py
```python
from shinka.core import run_shinka_eval

def main(program_path: str, results_dir: str):
    metrics, correct, err = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_experiment",
        num_runs=3,
        get_experiment_kwargs=get_kwargs,
        aggregate_metrics_fn=aggregate_fn,
        validate_fn=validate_fn,
    )
```

---

## Convert Workflow

Turn existing code into a Shinka-ready task directory.

### Steps

1. **Inspect the codebase**: Identify language, entrypoints, and the function/region to optimize.

2. **Create sidecar directory**: `.\shinka_task\` — copy only the minimal runnable snapshot.
   ```powershell
   New-Item -ItemType Directory -Force .\shinka_task
   ```

3. **Create `initial.py`** in the sidecar: Extract the target code, wrap it with `EVOLVE-BLOCK-START` / `EVOLVE-BLOCK-END` markers, and expose a `run_experiment(**kwargs)` entry point.

4. **Create `evaluate.py`**: Use the Python module path (preferred) or subprocess path for non-Python code.

5. **Copy config files**:
   ```powershell
   $skillDir = "$env:USERPROFILE\.claude\skills\shinka-evolve"
   Copy-Item "$skillDir\scripts\shinka.yaml" .\shinka_task\
   Copy-Item "$skillDir\.env" .\shinka_task\
   ```

6. **Smoke test**:
   ```powershell
   uv run python "$skillDir\scripts\smoke_test.py" --task-dir .\shinka_task
   ```

7. **Ask user**: Proceed to [Run Workflow](#run-workflow)?

### Conversion rules
- Keep evolve region tight — don't make the whole project mutable
- Preserve correctness checks outside the evolve region
- Python: prefer `run_shinka_eval` path over subprocess
- Non-Python: use subprocess in `evaluate.py`, write `metrics.json` + `correct.json`

---

## Run Workflow

Launch async evolution batches with human-in-the-loop control.

### Before first batch
1. Confirm task directory has `evaluate.py` + `initial.py`
2. Run [Pre-flight](#pre-flight-required-before-any-run) checks
3. Confirm run config with user:
   - Generation count (default: 50)
   - Budget cap (default: $5)
   - Models (default: gemini-2.5-flash-preview + gemini-2.5-pro-preview)
   - Concurrency (default: 2 eval / 2 proposal)

### Launch

```powershell
shinka_run `
  --task-dir .\my_task `
  --results_dir .\my_task\results `
  --num_generations 50 `
  --set "evo.llm_models=[""gemini-2.5-flash-preview"",""gemini-2.5-pro-preview""]" `
  --set "evo.embedding_model=null" `
  --set "evo.max_api_costs=5.0" `
  --set "db.num_islands=2" `
  --max-evaluation-jobs 2 `
  --max-proposal-jobs 2 `
  --max-db-workers 4
```

For long/multiline system prompts, use a config file instead of shell escaping:
```powershell
shinka_run `
  --task-dir .\my_task `
  --config-fname shinka.yaml `
  --results_dir .\my_task\results `
  --num_generations 50
```

### Between batches (required)
1. Summarize results from the finished batch (scores, improvements, failures)
2. Ask user: "What new directions should we push next batch? Include algorithm ideas, constraints, and failure modes to avoid."
3. Turn feedback into a revised `evo.task_sys_msg` for the next batch
4. Keep the same `--results_dir` for continuation batches
5. Do NOT start the next batch until user confirms

### After final batch
Proceed to [Inspect Workflow](#inspect-workflow).

### Optional: WebUI monitoring
```powershell
shinka_visualize --port 8888 --open
```

---

## Inspect Workflow

Extract top programs from a completed run.

### Steps

1. Confirm results exist:
   ```powershell
   Get-ChildItem .\my_task\results
   ```

2. Generate context bundle:
   ```powershell
   $skillDir = "$env:USERPROFILE\.claude\skills\shinka-evolve"
   uv run python "$skillDir\scripts\inspect_best.py" `
     --results-dir .\my_task\results `
     --k 5
   ```

3. Read and present the output:
   ```powershell
   Get-Content .\my_task\results\shinka_inspect_context.md
   ```

4. Summarize top programs for the user with scores, key code changes, and text feedback.

### Tuning knobs
- `--k 8` — more programs
- `--max-code-chars 5000` — longer code snippets
- `--min-generation 10` — skip early generations
- `--no-include-feedback` — omit text feedback

---

## Quick Install

```powershell
uv pip install shinka-evolve
uv run python -c "import shinka; print(shinka.__version__)"
```

## Additional resources
- Full config parameter tables: [reference.md](reference.md)
- Repo and docs: https://github.com/SakanaAI/ShinkaEvolve
- Getting started guide: https://sakanaai.github.io/ShinkaEvolve/getting_started/

## Notes
- Higher `combined_score` = better performance (maximization)
- Model names are subject to Google renaming — always verify via `shinka_models`
- Budget cap (`max_api_costs`) stops new proposals at the cap; in-flight jobs finish
- Evolve markers: `# EVOLVE-BLOCK-START` / `# EVOLVE-BLOCK-END` (Python)
- `.env` propagation: shinka reads CWD/.env, NOT the skill folder — always copy or set env var
