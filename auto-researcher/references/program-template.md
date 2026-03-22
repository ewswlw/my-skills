# PROGRAM.md template (Auto Researcher)

Copy this file to your **project root** as `PROGRAM.md`. Fill in YAML frontmatter between the `---` lines; use the markdown body for free-form context, backlog, and ideas.

```yaml
---
# === Required ===

# What you are trying to achieve (one sentence).
goal: "Describe the optimization or research goal"

# Repo-relative paths the agent may edit. All must exist before starting.
editable_files:
  - path/to/editable_file.py
  # - another_file.ext

# Shell command to run evaluation (cwd = project root). Must exit 0 on success.
run_command: "uv run python train.py"

# Name for logs / documentation (does not change parsing by itself).
metric_name: "val_loss"

# "higher" = larger metric is better; "lower" = smaller is better.
metric_direction: "lower"

# One of: stdout_pattern | results_file | eval_command
metric_source: "stdout_pattern"

# --- If metric_source is stdout_pattern (required) ---
# Regex with EXACTLY ONE capture group that captures a float. Last match wins.
metric_pattern: "val_loss:\\s*([\\d.]+)"

# --- If metric_source is results_file (required) ---
# metric_file: "results.json"
# metric_key: "score"   # omit if the file is a single plain number

# --- If metric_source is eval_command (required) ---
# eval_command: "uv run python eval.py --json-out results.json"

# === Optional ===

# Minimum improvement required to KEEP (same units as metric). Default 0.
min_delta: 0.001

# Wall-clock seconds for run_command (and eval_command if applicable). Omit for no timeout.
# time_budget: 300

# Max NEW experiment iterations in this agent invocation (each adds one log row).
max_experiments: 50

# Stop after this many consecutive reverted + crashed rows (resets on any kept).
max_consecutive_failures: 5

# Hard rules the agent must not violate (strings).
constraints:
  - "Do not delete tests/"
  - "Keep public API stable unless the goal says otherwise"
---

## Context

Describe the codebase, what the metric means, and any traps (nondeterminism, flaky tests).

## Ideas backlog (optional)

- Hypothesis ideas you want explored first
- Areas that are off-limits beyond `constraints`

```

## Field reference

| Field | Required | Notes |
|-------|----------|--------|
| `goal` | Yes | Drives hypotheses |
| `editable_files` | Yes | Allowlist only |
| `run_command` | Yes | Exit 0 required for success |
| `metric_name` | Yes | Documentation |
| `metric_direction` | Yes | `higher` or `lower` |
| `metric_source` | Yes | See SKILL.md §4 |
| `metric_pattern` | If stdout | One capture group; last match wins |
| `metric_file` | If results_file | Path after `run_command` |
| `metric_key` | Optional | For JSON; omit for plain float file |
| `eval_command` | If eval_command | Runs after `run_command` |
| `min_delta` | No | Default `0` |
| `time_budget` | No | Seconds |
| `max_experiments` | No | Default `50` |
| `max_consecutive_failures` | No | Default `5` |
| `constraints` | No | List of strings |

## Output files (agent-managed)

- `EXPERIMENT_LOG.md` — append-only table + optional session reports (do not hand-edit rows).

## Related

- Full protocol: `SKILL.md` in the `auto-researcher` skill folder
- Specification: `project-spec.md` in the same folder
