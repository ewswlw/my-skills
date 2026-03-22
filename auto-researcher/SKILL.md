---
name: auto-researcher
description: >-
  Runs autonomous experiment loops on any project with a numeric metric—edit code, run eval, keep or revert, append-only log, git checkpointing. Use when the user says /auto researcher, autoresearch, overnight experiments, iterative optimization with keep/revert, PROGRAM.md experiment config, or domain-agnostic hyperparameter / code search loops.
---

# Auto Researcher (`/auto researcher`)

Self-contained protocol for **autonomous research**: propose a change → checkpoint in git → run evaluation → extract a metric → keep or revert → append one row to `EXPERIMENT_LOG.md` → repeat. No dependency on any external template repo—only the user’s project, git, and shell.

## Triggers

- Explicit: `/auto researcher`, “auto researcher”, “autoresearch-style loop”
- Implicit: overnight experiments, iterative code search with a metric, “keep/revert until the metric improves”

## Hard rules (non-negotiable)

1. **Never** edit `PROGRAM.md` (human-owned). Only read and re-read it each loop iteration.
2. **Never** delete or rewrite existing rows in `EXPERIMENT_LOG.md`. **Append only** new table rows and new `## Session Report` sections.
3. **Only** modify files listed under `editable_files` in `PROGRAM.md`.
4. **Never** `git push --force`, rebase experiments onto rewritten history, or delete remote branches as part of this skill.
5. All experiment and revert commits use **`git commit --no-verify`** so pre-commit hooks do not block the loop.
6. Skill instructions are **domain-agnostic**—do not assume ML, Python, or a specific framework unless `PROGRAM.md` says so.

---

## 1. Parse `PROGRAM.md`

- Expect **YAML frontmatter** between `---` lines, then a markdown body (context, backlog, ideas).
- Required frontmatter keys:
  - `goal` (string)
  - `editable_files` (list of strings, repo-relative paths)
  - `run_command` (string, shell command as the user would run it)
  - `metric_name` (string, for documentation / log column naming)
  - `metric_direction`: `"higher"` or `"lower"`
  - `metric_source`: one of `stdout_pattern`, `results_file`, `eval_command`
- Optional keys (defaults in parentheses):
  - `metric_pattern` (string regex, **required** if `metric_source` is `stdout_pattern`)
  - `metric_file` (path, **required** if `results_file`)
  - `metric_key` (string, optional for JSON files—if omitted, file must be a single float or plain number)
  - `eval_command` (**required** if `metric_source` is `eval_command`)
  - `min_delta` (number, default `0`)
  - `time_budget` (seconds, optional—if set, enforce timeout on `run_command` and on `eval_command` when used)
  - `max_experiments` (integer, default `50`) — max **new** experiment iterations **in this invocation** (each iteration appends one log row)
  - `max_consecutive_failures` (integer, default `5`) — consecutive `reverted` or `crashed` rows; resets to `0` after any `kept`

If parsing fails or any required key is missing, **halt** and list what is missing. Copy the template from `references/program-template.md` in this skill folder if the user needs a starter.

---

## 2. Session initialization (run once per invocation unless resuming mid-spec)

Execute in order:

1. **Locate** `PROGRAM.md` at the **project root** (the workspace folder the user indicated). If missing: halt with:  
   `No PROGRAM.md found in project root. Create one using the template in the auto-researcher skill (references/program-template.md).`
2. **Parse and validate** frontmatter (section 1). If invalid: halt with missing fields list.
3. **Verify** every path in `editable_files` exists. If not: halt with:  
   `editable_files references non-existent file: <path>`
4. **Git working tree**: run `git status --porcelain`. If non-empty: run `git stash push -u -m "autoresearch: stash before session"` (or equivalent), then tell the user: `Stashed uncommitted changes before autoresearch session.`
5. **Git repo**: if `.git` is missing, run `git init`. If it fails, print the error and halt.
6. **Baseline capture**:
   - If **no** `EXPERIMENT_LOG.md` **or** log has no data rows yet (see §8 resume):
     - Stage all `editable_files` (and only those needed for a consistent baseline): `git add -- <paths>`
     - Commit if there is anything to commit: `git commit --no-verify -m "[autoresearch] baseline"` (skip if empty and nothing to commit—then create empty commit only if required for tag; prefer committing real files)
     - Tag: `git tag -f autoresearch/baseline` (force move tag if re-baselining in a fresh repo—**only** when starting a **new** log; see resume rules)
   - If **resuming** with existing log: **do not** recreate or move `autoresearch/baseline` unless the user explicitly asked for a full reset. If the tag is missing, warn: `Tag autoresearch/baseline not found; continuing from EXPERIMENT_LOG.md state only.`
7. **Baseline metric**: run `run_command` once (with timeout if `time_budget` set—§5). Capture stdout+stderr. If exit code ≠ 0: halt with:  
   `Baseline evaluation failed. Fix your run_command and try again.` and include command output.  
   Extract metric (§4). If extraction fails (NaN, no match, etc.), treat as baseline failure and halt with output.
   - Store as `baseline_metric` and `global_best` (initialized to extracted value; for “lower” better, smaller is better; for “higher”, larger is better).
8. **Experiment log**:
   - If `EXPERIMENT_LOG.md` missing or empty table: create file with header per §7, **no data rows yet**.
   - If resuming: parse §8; set `next_id`, `global_best`, `next_parent_id`, `consecutive_failures` from log. If table is malformed: halt with:  
     `EXPERIMENT_LOG.md appears corrupted. Fix or delete it and restart.`
9. **max_experiments == 0**: halt immediately after baseline; append session report (§9) with zero experiments.

---

## 3. Core experiment loop (each iteration)

Let `N = next_id` (increment after each row). Let `metric_before = global_best` at the **start** of this iteration (the value you are trying to beat).

1. **Hot-reload** `PROGRAM.md` (re-parse YAML + body).
2. **Read** entire `EXPERIMENT_LOG.md` (mandatory context for proposal rules).
3. **Propose** one hypothesis (1–2 sentences) **before** editing. Rules:
   - Do **not** repeat a prior `hypothesis` or `diff_summary` (exact or near-duplicate).
   - Prefer **small** targeted edits before large rewrites.
   - If **≥ 3** consecutive `reverted` or `crashed` rows with the same *theme* (same area of code), **pivot** to a different approach.
   - Obey `constraints` from frontmatter and any new constraints in the body.
4. **Edit** only `editable_files`.
5. **Checkpoint (before run):**  
   `git add -- <editable_files>`  
   `git commit --no-verify -m "[autoresearch] experiment #N: <short hypothesis>"`  
   If there is nothing to commit (no diff), do not run eval—treat as failed proposal: skip or amend hypothesis (do not append a duplicate empty experiment; fix the workflow).
6. **Execute** `run_command` with optional timeout (§5). Collect exit code and combined stdout/stderr.
7. **Exit code**: if ≠ 0 → **crash** path (§3 step 9–10): no metric, revert.
8. **Extract metric** (§4). On failure → **crash**.
9. **Compare** using `min_delta`:
   - `metric_direction: higher` → **KEEP** iff `metric_after >= global_best + min_delta`
   - `metric_direction: lower` → **KEEP** iff `metric_after <= global_best - min_delta`
   - Else → **REVERT**
10. **Keep**: set `global_best = metric_after`. Next iteration’s default parent is this experiment’s `id` (child edge in genealogy).
11. **Revert or crash**:
    - `git checkout HEAD~1 -- <editable_files>` then  
      `git commit --no-verify -m "[autoresearch] revert experiment #N"`  
    - Next iteration’s `parent_id` = **this row’s `parent_id`** (sibling branch), not this experiment’s id.
    - For crash: leave `metric_after` and `delta` as `—` in the log table (markdown em dash or empty cell per user style—**be consistent** within a file).
12. **Append** one **new** table row (§7). Set `delta = metric_after - metric_before` when numeric; else `—`.
13. **Genealogy**: set `parent_id` for this row:
    - First experiment after fresh baseline: `parent_id = 0` unless resuming dictates otherwise (§8).
    - If previous row was **kept**: this row’s `parent_id` = previous experiment’s `id`.
    - If previous row was **reverted/crashed**: this row’s `parent_id` = **same** `parent_id` as the reverted/crashed row (sibling).
14. **Counters**: increment `experiments_this_session`. On revert/crash, increment `consecutive_failures`; on keep, reset `consecutive_failures` to 0.
15. **Halt** if `consecutive_failures >= max_consecutive_failures` OR `experiments_this_session >= max_experiments` → go to §9.
16. **Repeat** from step 1.

**Note:** `metric_before` in the log is the **global_best at iteration start**, per spec.

### Genealogy state machine (`parent_id`)

Maintain `pending_parent_id` across iterations (resume: initialize from last row—see below).

- Before the first experiment of a **new** log: `pending_parent_id = 0`.
- For experiment with id `N` and row `parent_id = pending_parent_id`:
  - If **kept**: set `pending_parent_id = N` (next experiment is a **child** of `N`).
  - If **reverted** or **crashed**: set `pending_parent_id = parent_id` of this row (next experiment is a **sibling** of `N`, same parent).

On **resume**, set `pending_parent_id` from the last log row: if last row was **kept**, `pending_parent_id = last.id`; if **reverted/crashed**, `pending_parent_id = last.parent_id`.

---

## 4. Metric extraction

**Sanity:** After parsing a float `x`, if `math.isnan(x)` or not `math.isfinite(x)` → **crash**.

### A. `stdout_pattern`

- Concatenate stdout + stderr as one string.
- Apply `metric_pattern` regex with **exactly one capturing group** for the float.
- **All** matches → take the **last** match (final line wins).
- Zero matches → **crash**.

### B. `results_file`

- After `run_command` succeeds, read `metric_file` (text, UTF-8, `errors=replace`).
- If JSON object and `metric_key` set: `float(data[metric_key])`.
- If file is a single number (strip whitespace) → that float.
- If missing or unparsable → **crash**.

### C. `eval_command`

- Run `eval_command` after `run_command` (same cwd as project root unless user specified otherwise in command).
- Exit ≠ 0 → **crash**.
- Parse stdout for a single float (strip; last line or whole string—prefer **last** float token if multiple).
- Timeout: apply `time_budget` if set.

---

## 5. Timeouts

- **Unix:** `timeout <seconds> <run_command>` (or `gtimeout` on macOS with coreutils).
- **Windows PowerShell:**  
  `$p = Start-Process -FilePath ... -PassThru -NoNewWindow -Wait;` use `-Wait` with a job timeout pattern, or run `python -c` wrapper—**simplest portable**: document using `python scripts/run_with_timeout.py` if the user needs cross-platform; **default** recommendation: user wraps their command in a script that exits within budget.  
- **Practical default for the agent:** if `time_budget` set, prefer **GNU timeout** on Git Bash/WSL; on native Windows cmd, use `powershell` `Start-Process` with timeout or `chcp` + external `timeout.exe` **only** for simple commands.

*(Minimum requirement: honor `time_budget` when the environment provides a clear timeout primitive; if impossible, warn the user once and run unbounded.)*

---

## 6. Git discipline

- Experiment commit message: `[autoresearch] experiment #N: <hypothesis short>`
- Revert message: `[autoresearch] revert experiment #N`
- Recover baseline: `git diff autoresearch/baseline -- <files>` or `git checkout autoresearch/baseline -- <files>`

---

## 7. `EXPERIMENT_LOG.md` format

Use a **single markdown table** with columns:

`| id | parent_id | hypothesis | diff_summary | metric_before | metric_after | delta | status | timestamp |`

- `status`: `kept` | `reverted` | `crashed`
- `timestamp`: ISO-like local time string
- **Append-only** for rows. Never edit prior rows.

---

## 8. Resume from existing log

1. Parse all **data** rows (skip header separator).
2. `next_id = max(id) + 1`. If no rows, `next_id = 1`.
3. Among rows with `status == kept`, take the row with **maximum `id`**: its `metric_after` → `global_best`; its `id` → candidate for next `parent_id` for the **next** experiment (the next experiment’s parent should be that id if we are continuing the winning line—**align with genealogy rules in §3**).
4. If **no** `kept` rows: `global_best = baseline_metric` from fresh baseline run; `next_parent_id = 0`.
5. Set `consecutive_failures` from trailing rows: count consecutive `reverted`/`crashed` from the **end** of the table backward until a `kept`.
6. Tell the user: `Resuming from experiment #<next_id-1>, current best: <global_best>` (adjust wording if empty).

---

## 9. Session report (append to `EXPERIMENT_LOG.md`)

When the session ends (halt, limit, or user stop):

```markdown
## Session Report — <timestamp>
- **Baseline score**: <value>
- **Best score**: <value> (experiment #N)
- **Total experiments**: <count this session>
- **Kept / Reverted / Crashed**: <k> / <r> / <c>
- **Win rate**: <k/total * 100>%
- **Top 3 improvements**: ...
- **Winning lineage**: #id → #id → ... (best)
- **Cumulative diff from baseline**: <short natural-language summary; cite `git diff autoresearch/baseline` if available>
- **Marginal improvements** (< 1% relative vs previous global_best): #id, ...
```

**Marginal flag:** For each `kept` row, compute relative improvement vs `metric_before`; if `< 1%`, list under marginal (for both directions, use absolute relative change).

---

## 10. Error handling (agent responses)

| Condition | Response |
|-----------|----------|
| No `PROGRAM.md` | Halt; point to template path in this skill. |
| Missing required YAML keys | Halt; list keys. |
| `editable_files` path missing | Halt; list path. |
| Dirty tree at start | `git stash`; inform user. |
| `git init` fails | Halt; show error. |
| Baseline eval fails | Halt; show output. |
| `run_command` exit ≠ 0 | Crash; revert; log. |
| NaN / Inf metric | Crash; revert; log. |
| No regex match | Crash; revert; log. |
| `results_file` missing | Crash; revert; log. |
| Malformed log on resume | Halt; ask to fix or delete log. |
| Missing `autoresearch/baseline` tag on resume | Warn; continue from log. |
| `max_experiments == 0` | Halt after baseline; session report with 0 experiments. |

---

## 11. Worked example (toy project)

**Goal:** Lower `score` printed by a script.

**`PROGRAM.md`:**

```yaml
---
goal: "Minimize score in bench.py"
editable_files:
  - bench.py
run_command: "python bench.py"
metric_name: score
metric_direction: lower
metric_source: stdout_pattern
metric_pattern: "score:\\s*([\\d.]+)"
min_delta: 0.01
max_experiments: 3
max_consecutive_failures: 5
---
```

**`bench.py` (initial):** prints `score: 10.0` (agent would reduce magic number in file).

**Expected behavior:** Baseline run → log baseline metric → experiments 1..3 each append one row; revert on regression; session report at end.

---

## 12. Files in this skill

- `SKILL.md` — this file
- `references/program-template.md` — copy-paste template for user projects
- `project-spec.md` — full specification
- `project-constitution.md` — hard boundaries
- `scripts/validate_program.py` — optional CLI to validate `PROGRAM.md` (YAML, paths, metric fields)
- `pyproject.toml` + `tests/` — run `uv sync --extra dev` and `uv run pytest` from this folder to verify the validator

**Validate locally:** `uv run python scripts/validate_program.py PROGRAM.md --root .`

---

## Agent checklist before closing the turn

- [ ] Validated `PROGRAM.md` and paths
- [ ] Baseline metric recorded
- [ ] Each experiment: hypothesis stated **before** edit
- [ ] Only `editable_files` changed; `--no-verify` on commits
- [ ] One log row per experiment; append-only
- [ ] Session report appended when stopping
