---
name: grading-rubric
description: >-
  Generates an optimal scoring rubric (criteria + thresholds + scorer.py + PROGRAM.md fragment) for any iterative-validation loop — primarily to feed `/auto researcher` (which requires a single numeric metric) and `/recursive-refine` (which uses per-criterion thresholds). Use when the user invokes /grading-rubric, says "grading rubric" or "scoring rubric", asks for a rubric to drive an /auto researcher loop, asks for a rubric for /recursive-refine, or describes designing a metric for an autonomous keep/revert / overnight optimization loop. Emits three artifacts: RUBRIC.md (dual-use spec), scorer.py (stdlib runnable composite computer with auto-included degeneracy trip-wire), and PROGRAM.fragment.md (paste-ready /auto researcher block). Do NOT trigger for grading student work, course rubrics, performance reviews, or general evaluation requests unrelated to iterative-loop validation.
---

# Grading Rubric (`/grading-rubric`)

Self-contained protocol for **rubric generation**: infer the user's domain from the task description → draft 3–10 weighted criteria with per-criterion thresholds and gameability notes → derive an adversarial reviewer persona → self-validate the rubric → dry-run the scorer on synthetic best/worst inputs → emit three artifacts to the user's project root. Designed so the same RUBRIC.md feeds both `/auto researcher` (composite single-float) and `/recursive-refine` (per-criterion thresholds) with no transformation.

## Triggers

- **Explicit:** `/grading-rubric`, "grading rubric", "scoring rubric"
- **Implicit (only with iterative-loop context):** "rubric for /auto researcher", "metric design for keep/revert", "scoring rubric for /recursive-refine"
- **Do not trigger** for: course/student grading, employee performance rubrics, generic "design an evaluation" requests without iterative-loop context, or any rubric for a one-shot human review.

## Hard rules (non-negotiable)

1. **Composite is always in `[0, 1]`, higher is better.** No exceptions, no per-rubric direction. The skill is unambiguous about this so /auto researcher's `metric_direction: higher` is unambiguous.
2. **Hard-gate failures exit non-zero with `GATE_FAILED: <name>: <reason>` to stderr** — never silent zero. /auto researcher records crashes visibly in `EXPERIMENT_LOG.md`.
3. **Auto-include `regression_trip_wire`** in every emitted rubric unless the user explicitly disables it for that invocation (warn loudly when disabled).
4. **Run `scripts/validate_rubric.py` before delivery.** If it fails, abort delivery with the validator's error output.
5. **Run synthetic best/worst dry-run before delivery.** If discrimination is weak (best < 0.7 or worst > 0.3), warn the user and offer to revise before emitting files.
6. **`PROGRAM.fragment.md` carries the `# Compatible with auto-researcher SKILL.md §3 contract as of <ISO date>` header** every time, no exceptions.
7. **Honor overwrite protection.** If `RUBRIC.md`, `scorer.py`, or `PROGRAM.fragment.md` exists in the target dir, prompt the user with overwrite / versioned filename / cancel.
8. **No domain-specific defaults.** The 5 anchor rubrics in `references/` are *anchors* (worked examples), not defaults — adapt them, never copy-paste.

---

## Stage A: Analyze

Goal: classify the user's domain and pick a confidence level. Three questions, answered in order:

1. **What is the primary domain?** (e.g., systematic trading, code refactoring, professional writing, ML model evaluation, generic task)
2. **What does the user's pipeline produce?** (file types, structure, runtime budget — needed for trip-wire setup)
3. **Will the scorer be deterministic or LLM-judge?** Deterministic when criteria reduce to numbers a Python script can compute (Sharpe, accuracy, latency, line counts, test exit codes). LLM-judge when criteria require subjective judgment (readability, persuasiveness, naming quality).

### Set `domain_confidence`

| Confidence | When to assign | Behavior |
|---|---|---|
| `high` | Task description matches one of the 5 anchor rubrics closely (trading-strategy, code-quality, writing, ml-eval) | Use that anchor as the structural template; adapt criteria + weights to the task |
| `medium` | Domain is recognizable but doesn't match any anchor cleanly (e.g., infrastructure config tuning, prompt engineering loop) | Build criteria from first principles using the spec's data shape; reference the closest anchor for style guidance |
| `low` | Domain is unfamiliar OR the task description is too vague to classify | Use `references/generic-task.md` as the anchor; emit the "no reference rubric matched closely — proceed with extra scrutiny" banner in the RUBRIC.md header |

### Ask up to 3 clarifying questions only when confidence is low

Only ask when the answer would change the rubric materially:
- "What does the output of one iteration look like? (a CSV, a markdown file, predictions JSON, a code diff?)"
- "Are there any failure modes the agent must never optimize toward? (e.g., 'don't delete tests', 'don't trade naked options')"
- "Is there a runtime budget per iteration? (used to set the `runtime_exceeded` trip-wire)"

If confidence is high or medium, do not ask — proceed with explicit assumptions surfaced inline in the RUBRIC.md.

---

## Stage B: Generate

This is the core reasoning stage. Each substep is required.

### B1: Draft 3–10 weighted criteria

- **Adaptive count:** simple tasks need 3–4; complex multi-faceted tasks need 6–8; rarely beyond 10 (the LLM judge's reliability degrades and the agent loses focus).
- **Each criterion has the full data shape** (validated by `scripts/validate_rubric.py`):
  - `name` (unique snake_case)
  - `definition` (one sentence)
  - `what_9_of_10_looks_like` (concrete, observable benchmark)
  - `weight` (float in `[0, 1]`; weights of non-hard-gate, non-trip-wire criteria sum to 1.0 ±0.001)
  - `threshold` (float in `[0, 1]`; the per-criterion pass bar for `/recursive-refine`)
  - `hard_gate` (bool, default `false`)
  - `gameability_note` (mandatory — see B3)
  - `fail_reason` (required when `hard_gate: true` and `name != "regression_trip_wire"`)

### B2: Apply Goodhart counter-design

For each criterion, ask: "If the agent perfectly optimized this metric and ignored every other concern, what would it produce?" If the answer is "something genuinely good," the criterion is solid. If the answer is "a degenerate shortcut" (e.g., maximizing Sharpe by ignoring drawdown), either:
- **Add a counter-criterion** that penalizes the shortcut (e.g., `max_drawdown_control` paired with `sharpe_quality`), OR
- **Tighten the criterion's threshold** so the shortcut alone can't earn a passing score, OR
- **Promote to hard_gate** if the shortcut is catastrophic (e.g., `tests_pass` for code refactor loops).

### B3: Articulate the gameability shortcut for every criterion

Write `gameability_note` as the cheapest shortcut the agent could use to score well without genuinely satisfying intent, plus the proposed counter. Examples:
- "Sharpe could be inflated by tuning on the test window. Counter: enforce sealed test set."
- "Readability could be gamed by adding verbose docstrings. Counter: pair with `minimal_diff` weight."
- "Specificity could be gamed by stuffing in random numbers. Counter: pair with `sourcing` requirement."

A criterion without a non-trivial gameability shortcut is suspicious — usually it means the criterion is too vague to game *or* too vague to be useful.

### B4: Auto-include `regression_trip_wire`

Always append the regression_trip_wire criterion (unless the user explicitly disables it):

```yaml
- name: regression_trip_wire
  weight: 0
  threshold: 0
  hard_gate: true
  definition: "Catastrophic-output detector: empty output, NaN/error tokens, runaway runtime, or invalid structure."
  what_9_of_10_looks_like: "Never fires on valid outputs; always fires on degenerate ones."
  gameability_note: "Not a quality criterion; pure failure detector."
  checks:
    - empty_output
    - nan_or_error
    - runtime_exceeded     # requires baseline_runtime_seconds set in scorer.py
    - structure_invalid    # requires expected_format set in scorer.py
```

If the user disables the trip-wire, emit this warning verbatim before delivery: **"Disabling `regression_trip_wire` removes the main defense against the agent discovering degenerate-output shortcuts. Recommended only for short, attended runs."**

### B5: Derive the adversarial reviewer persona

A one-paragraph persona description: who the toughest realistic reviewer of this output would be, what they care about, what they reject. Used by the LLM-judge scorer mode (and ignored when scorer is deterministic, but emitted regardless for documentation). Examples in `references/*.md`.

### B6: Compose anti-pattern warnings

Inline in the rubric body (not buried in references), call out:
- **Goodhart risks** specific to this rubric (e.g., "optimizing Sharpe alone produces strategies that ignore drawdown")
- **Tension between criteria** the agent will be tempted to resolve poorly (e.g., readability vs. minimal-diff)
- **Domain-specific failure modes** that the criteria do not directly catch but the user should know about

### B7: Set `domain_confidence` banner

The RUBRIC.md frontmatter carries `domain_confidence: high | medium | low`. When `low`, prepend a top-of-file banner:

```markdown
> ⚠️ **Domain confidence: LOW.** No reference rubric matched closely. The criteria below
> were generated from first principles. Tighten weights, thresholds, and definitions to
> your specific task before kicking off any unattended /auto researcher loop.
```

---

## Stage C: Self-validate

Run `scripts/validate_rubric.py` against the draft RUBRIC.md (write it to a temp location first):

```bash
uv run python scripts/validate_rubric.py <temp-RUBRIC.md>
```

Validator checks (each runs in one pass; all errors reported together):
- Required top-level fields present and well-typed
- Weights of non-hard-gate, non-trip-wire criteria sum to 1.0 ±0.001
- Every criterion has `name`, `definition`, `what_9_of_10_looks_like`, `weight in [0,1]`, `threshold in [0,1]`, `gameability_note`
- No duplicate criterion names
- Hard-gate criteria carry `fail_reason`
- `regression_trip_wire` (when enabled) has `weight: 0`, `hard_gate: true`, and `checks` from the valid set

If the validator fails, **do not deliver**. Fix the rubric and re-run. If validation fails twice consecutively, surface the validator output to the user and ask for guidance — do not silently emit a broken rubric.

---

## Stage D: Dry-run sanity test

The validator confirms the rubric's *structure*. The dry-run confirms the rubric's *discrimination* — that it actually distinguishes good outputs from bad.

### D1: Synthesize best-case and worst-case outputs

Generate two synthetic outputs the user's pipeline plausibly *could* produce:
- **Best case:** the kind of output that should score near 1.0 across all criteria (a clean, complete, on-spec result)
- **Worst case:** the kind of output that should score near 0.0 (empty, malformed, or obviously-bad)

Examples:
- Trading: best = realistic equity curve with Sharpe 2.0, Max DD 8%; worst = empty CSV
- Code refactor: best = clean diff with all tests passing; worst = empty file
- Writing: best = a 1-page draft with concrete claims and citations; worst = empty markdown
- ML eval: best = predictions matching ground truth at 95% accuracy; worst = predictions all NaN

### D2: Render the scorer for both modes (briefly) and run on both inputs

Render `assets/scorer.py.template` (see Stage E for substitution mechanics) into a temp `scorer.py`, set up a temp `outputs/` dir with each synthetic case, and run.

### D3: Warn on weak discrimination

| Result | Interpretation | Action |
|---|---|---|
| best ≥ 0.7 AND worst ≤ 0.3 | Healthy discrimination | Proceed to Stage E |
| best < 0.7 | Even the best case doesn't score well — criteria are too strict or `what_9_of_10_looks_like` benchmarks are unrealistic | Warn user, propose loosening thresholds or recalibrating benchmarks, offer to revise |
| worst > 0.3 | Even degenerate output scores too well — criteria are too loose or trip-wire is catching the issue (which is fine, but means the *non-trip-wire* criteria don't discriminate) | Warn user, propose tightening thresholds or adding hard gates, offer to revise |
| Both | Rubric does not discriminate at all | Strong warning; do not deliver without explicit user override |

For LLM-judge mode, dry-run is expensive (each criterion costs N=3 API calls × 2 synthetic cases). Offer to skip dry-run with explicit user opt-out and a recommendation to calibrate `min_delta` post-deployment instead.

---

## Stage E: Emit

Three artifacts written to the user's project root (or `--output-dir <path>` if specified).

### E1: Render the artifacts

Read templates and perform substitution:

1. **`RUBRIC.md`** — write directly with the validated YAML frontmatter + body sections (banner if low confidence, persona, criteria summary table regenerated from YAML, anti-patterns, scorer notes).

2. **`scorer.py`** — read `assets/scorer.py.template`, then:
   - **Strip the unused mode block** line-by-line. Markers `# === BEGIN MODE: deterministic ===` … `# === END MODE: deterministic ===` and the corresponding `llm_judge` markers delimit the two branches. Drop the entire unused block AND the marker lines themselves.
   - **Substitute placeholders** via `string.Template.safe_substitute()` with these keys:
     - `rubric_name`, `mode`, `iso_generated_at`
     - `trip_wire_enabled_python` ("True" or "False" — Python literal)
     - `baseline_runtime_seconds_or_none` ("None" or a float literal like "1.5")
     - `main_output_filename`, `expected_format` ("text" or "json")
     - `criteria_python_literal` (use `repr(criteria_list)` to produce a clean Python list-of-dicts literal)
     - `llm_model_default` (only used in llm_judge mode; "gpt-4o-mini" is a safe default placeholder)
     - `adversarial_persona` (the Stage B5 persona text)

3. **`PROGRAM.fragment.md`** — read `assets/PROGRAM.fragment.md.template` and substitute via `string.Template.safe_substitute()`:
   - `iso_date` (date only, e.g., "2026-04-29")
   - `iso_generated_at`, `rubric_name`, `mode`, `main_output_filename`
   - `min_delta_value`: `"0.001"` for deterministic, `"0.05"` for llm_judge (placeholder)
   - `min_delta_calibration_note`: short rationale for deterministic; explicit "CALIBRATION REQUIRED" instructions for llm_judge

### E2: Schema-drift sentinel

Before writing `PROGRAM.fragment.md`, attempt to read `auto-researcher/references/program-template.md` (one directory up from this skill folder, then over to `auto-researcher/`). If found, scan for any required-field name in the auto-researcher PROGRAM.md schema that does NOT appear in the fragment template's documented user-owned-fields section; if any is missing, emit a stderr warning: **"⚠️ auto-researcher schema may have drifted. New required field detected: `<name>`. Update the grading-rubric skill or fix manually."** Always emit the fragment regardless — never block on drift detection.

### E3: Overwrite handling

For each of the three target files, before writing:
- If the file does not exist, write it.
- If the file exists, prompt the user with three options:
  1. **Overwrite** the existing file
  2. **Write to versioned filename** (`RUBRIC.v2.md`, `scorer.v2.py`, `PROGRAM.fragment.v2.md`)
  3. **Cancel** this artifact (write the others)

Never silently overwrite.

### E4: Final confirmation

Print to the user:
- The three artifact paths
- The rubric's `domain_confidence` value
- The chosen scorer mode (deterministic or llm_judge)
- The `min_delta` calibration recommendation (especially for llm_judge — the user must run scorer 5x and recalibrate)
- A reminder that the trip-wire's `BASELINE_RUNTIME_SECONDS` is `None` until the user runs once and updates it

---

## Anchor reference index

Read the matching anchor at Stage A when the domain is identified. These are *worked examples*, not defaults.

| Anchor | Domain |
|---|---|
| `references/trading-strategy.md` | Systematic trading strategy backtesting |
| `references/code-quality.md` | Python code refactoring for readability |
| `references/writing.md` | Short-form professional writing (research, IC memos) |
| `references/ml-eval.md` | Supervised model training/evaluation |
| `references/generic-task.md` | Domain-agnostic fallback (used when confidence is low) |

Each anchor demonstrates the full data shape — including a populated `gameability_note` for every criterion, an adversarial persona, anti-pattern warnings, and scorer implementation notes. The `code-quality.md` anchor includes a worked-example non-trip-wire `hard_gate` criterion (`tests_pass`); use it as the model for any rubric that needs a behavioral-correctness gate.

## Output specification

After Stage E, the user's project root contains:

```
<user_project>/
├── RUBRIC.md              # YAML frontmatter (single source of truth) + markdown body
├── scorer.py              # stdlib-only, runnable, prints `composite: <float>`
└── PROGRAM.fragment.md    # paste-ready /auto researcher fragment
```

The user is responsible for adding `goal`, `editable_files`, `run_command`, and any optional fields to their actual `PROGRAM.md`. The fragment documents this clearly.

## Validation tooling

- `scripts/validate_rubric.py` — structural validator, runs in one pass, reports all errors. Used by Stage C.
- `pyproject.toml` — declares PyYAML for the validator (the validator is `uv`-runnable; the user-facing `scorer.py` remains stdlib-only).

## Implementation notes for the agent running this skill

- **Order of mode-block stripping vs. placeholder substitution:** strip the unused mode block FIRST, then substitute placeholders. The unused block contains placeholders relevant only to the other mode (e.g., `${adversarial_persona}` lives only in the llm_judge block).
- **`criteria_python_literal` formatting:** use `repr(list_of_dicts)`. Python's repr produces a clean, parseable literal. Do NOT use `json.dumps` — the scorer uses `True`/`False`/`None` (Python literals), not `true`/`false`/`null`.
- **`adversarial_persona` substitution:** the persona may contain newlines or quote characters. `string.Template.safe_substitute()` handles this correctly because the value is interpolated as-is into a triple-quoted Python string in the template.
- **Cross-platform file paths:** when writing output paths in messages to the user, use forward slashes — they work on both Windows and Unix shells.
- **Be explicit about what the user owns vs. what this skill owns:** the skill emits `RUBRIC.md`, `scorer.py`, `PROGRAM.fragment.md`. The user owns `PROGRAM.md` itself, the `run_command`, and the `editable_files`. Conflating these confuses /auto researcher's mental model.
