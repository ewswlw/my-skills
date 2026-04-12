# ShinkaEvolve Configuration Reference

Full parameter tables for `EvolutionConfig`, `DatabaseConfig`, and `LocalJobConfig`.
Read this file when you need to customize a run beyond the defaults in `scripts/shinka.yaml`.

## EvolutionConfig

| Key | Default | Type | Description |
|-----|---------|------|-------------|
| `task_sys_msg` | "You are an expert optimization..." | `str?` | System message guiding mutation LLMs |
| `patch_types` | `["diff","full","cross"]` | `list[str]` | Patch mutation formats |
| `patch_type_probs` | `[0.6, 0.3, 0.1]` | `list[float]` | Sampling probabilities per patch type |
| `num_generations` | 50 | `int` | Evolution generations |
| `max_patch_resamples` | 3 | `int` | Max resamples on patch failure |
| `max_patch_attempts` | 1 | `int` | Max attempts per patch |
| `language` | `"python"` | `str` | Target language |
| `llm_models` | `["gemini-2.5-flash-preview","gemini-2.5-pro-preview"]` | `list[str]` | Mutation LLMs (Gemini-only) |
| `llm_dynamic_selection` | `"ucb"` | `str?` | Model selection: "ucb", "epsilon_greedy", null |
| `llm_dynamic_selection_kwargs` | `{"cost_aware_coef": 0.5}` | `dict` | Selection kwargs |
| `llm_kwargs` | `{"temperatures":[0.0,0.5,1.0],"max_tokens":16384}` | `dict` | LLM call kwargs |
| `meta_rec_interval` | 10 | `int?` | Generations between meta-recommendations |
| `meta_llm_models` | null | `list[str]?` | Meta-recommendation LLMs (null = disabled) |
| `meta_max_recommendations` | 5 | `int` | Max meta-recommendations per interval |
| `embedding_model` | null | `str?` | **Set to null for Gemini-only** |
| `init_program_path` | `"initial.py"` | `str?` | Path to starting solution |
| `results_dir` | null | `str?` | Output dir (auto-generated if null) |
| `max_api_costs` | 5.0 | `float?` | **Budget cap in USD** |
| `code_embed_sim_threshold` | 0.99 | `float` | Dedup threshold (N/A when embedding=null) |
| `use_text_feedback` | false | `bool` | Include text feedback in evolution context |
| `inspiration_sort_order` | `"ascending"` | `str` | Inspiration ordering |
| `evolve_prompts` | false | `bool` | Enable meta-prompt evolution |
| `prompt_archive_size` | 10 | `int` | System-prompt archive size |

## DatabaseConfig

| Key | Default | Type | Description |
|-----|---------|------|-------------|
| `db_path` | null | `str?` | SQLite path (auto if null) |
| `num_islands` | 2 | `int` | Evolution islands |
| `archive_size` | 40 | `int` | Global archive cap |
| `elite_selection_ratio` | 0.3 | `float` | Elite proportion for inspiration |
| `num_archive_inspirations` | 1 | `int` | Archive programs for inspiration |
| `num_top_k_inspirations` | 1 | `int` | Top-k programs for inspiration |
| `migration_interval` | 10 | `int` | Generations between migrations |
| `migration_rate` | 0.0 | `float` | Population proportion to migrate |
| `island_elitism` | true | `bool` | Keep best on original island |
| `parent_selection_strategy` | `"weighted"` | `str` | "weighted", "power_law", "beam_search" |
| `archive_selection_strategy` | `"fitness"` | `str` | "fitness" or "crowding" |
| `archive_criteria` | `{"combined_score": 1.0}` | `dict` | Weighted ranking criteria |

## LocalJobConfig

| Key | Default | Type | Description |
|-----|---------|------|-------------|
| `eval_program_path` | `"evaluate.py"` | `str?` | Evaluation script path |
| `extra_cmd_args` | `{}` | `dict` | Additional CLI args |
| `time` | null | `str?` | Time limit |
| `conda_env` | null | `str?` | Conda env (mutually exclusive with activate_script) |
| `activate_script` | null | `str?` | Env activation script |

## CLI Quick Reference (PowerShell)

```powershell
# Set API key from skill .env
$env:GOOGLE_API_KEY = "YOUR_KEY_HERE"

# Check models
shinka_models --verbose

# Launch with CLI
shinka_run `
  --task-dir .\my_task `
  --results_dir .\results `
  --num_generations 50 `
  --set "evo.llm_models=[""gemini-2.5-flash-preview"",""gemini-2.5-pro-preview""]" `
  --set "evo.embedding_model=null" `
  --set "evo.max_api_costs=5.0" `
  --max-evaluation-jobs 2 `
  --max-proposal-jobs 2

# Inspect results
uv run python scripts/inspect_best.py --results-dir .\results --k 5

# WebUI
shinka_visualize --port 8888 --open
```
