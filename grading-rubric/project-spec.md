<project_specification>

  <project_name>grading-rubric</project_name>

  <overview>
    A meta-skill that generates the optimal scoring rubric for any iterative-validation loop — primarily to feed `/auto-researcher` (which requires a single numeric metric) and `/recursive-refine` (which uses per-criterion thresholds). Given a free-text task description and optional file paths, the skill infers the domain via reasoning, generates 3–10 weighted criteria scored on `[0, 1]` with per-criterion pass thresholds and optional hard gates, validates the rubric, and emits three artifacts: `RUBRIC.md` (human-readable spec, dual-use for both downstream skills), `scorer.py` (runnable composite computer with auto-included degeneracy trip-wire), and `PROGRAM.fragment.md` (paste-ready `/auto-researcher` block with compatibility comment). Success is measured by whether the rubric (a) passes lightweight structural validation, (b) produces sane composite scores on synthetic best/worst dry-run inputs (best ≥ 0.7, worst ≤ 0.3), and (c) is robust against gameability and silent-failure modes that would corrupt overnight optimization loops.
  </overview>

  <technology_stack>
    Markdown (skill definition + outputs); Python 3.11+ (scorer template, validator CLI; **stdlib only in scorer** for portability); YAML (skill frontmatter + PROGRAM.fragment); `uv` (validator runner). No new runtime dependencies imposed on user projects.
  </technology_stack>

  <assumptions>
    - User invokes the skill explicitly via `/grading-rubric`, `grading rubric`, or `scoring rubric` — explicit triggers only, no implicit firing.
    - User's project may or may not have an existing `PROGRAM.md`; the skill writes only `RUBRIC.md`, `scorer.py`, and `PROGRAM.fragment.md` (a paste-ready snippet, never a full `PROGRAM.md`).
    - User is responsible for the actual experiment workflow (`editable_files`, `run_command`, baseline) — the rubric covers metric definition only.
    - When the scorer uses an LLM judge, the user has API access available in the eval environment.
    - `/auto-researcher`'s PROGRAM.md schema (as defined in its `SKILL.md` §3 and `references/program-template.md`) is the integration contract.
    - Each invocation is stateless except for honoring overwrite-prompts on existing files.
  </assumptions>

  <out_of_scope>
    - Generating PROGRAM.md `goal`, `editable_files`, or `run_command` (user owns these).
    - Running the iterative loop itself (that is `/auto-researcher`'s job).
    - Persistent state across invocations.
    - Post-hoc analysis of `EXPERIMENT_LOG.md` after the loop finishes.
    - Hardcoded keyword routing per domain — the skill is universal-scope, reasoning-driven.
    - Domain-specific defaults beyond the 5 anchor reference rubrics.
    - Implicit / aggressive triggering on adjacent phrases like "design an evaluation" without an explicit rubric/scoring keyword.
  </out_of_scope>

  <core_features>

    <feature name="Domain-aware rubric generation">
      As a user running an iterative loop, I want to describe my task in natural language and receive a domain-appropriate rubric so I do not have to design metrics from scratch. **Acceptance:** skill produces 3–10 weighted criteria each with `name` (unique), `definition`, `what_9_of_10_looks_like`, `weight` (criteria weights sum to 1.0 ±0.001 excluding the trip-wire), `threshold` (float in `[0, 1]`), `hard_gate` (bool, default `false`), and `gameability_note` ("cheapest shortcut that would game this criterion").
    </feature>

    <feature name="Single-float composite for /auto-researcher">
      As a user feeding the rubric into `/auto-researcher`, I need a deterministic single-float metric in `[0, 1]` where higher is better, regardless of underlying task semantics. **Acceptance:** `scorer.py` outputs `composite: <float>` to stdout; composite = (weighted arithmetic mean of criterion scores) × (product of hard-gate multipliers, each `0` or `1`); composite is always in `[0, 1]`; `metric_direction` is always `higher` in the emitted PROGRAM fragment.
    </feature>

    <feature name="Per-criterion thresholds for /recursive-refine">
      As a user feeding the same rubric into `/recursive-refine`, I need per-criterion PASS/FAIL thresholds so the skill can drive its iterate-until-passes loop. **Acceptance:** every criterion in `RUBRIC.md` carries an explicit threshold value; the same `RUBRIC.md` is consumed by both downstream skills with no transformation needed.
    </feature>

    <feature name="Adversarial persona derivation">
      As a user with an LLM-judge scorer, I want the rubric to ship with a derived adversarial reviewer persona so the LLM judge has a concrete role to play. **Acceptance:** every `RUBRIC.md` contains an "Adversarial Reviewer Persona" section; persona is task-specific; section is present even when scorer is deterministic (in which case it is documented as "ignored unless using LLM judge mode").
    </feature>

    <feature name="Trip-wire criterion (auto-included)">
      As a user running an overnight `/auto-researcher` loop, I want degenerate outputs (empty / NaN / stack traces / runtime > 10× baseline) auto-detected and flagged as hard-gate failures so the agent does not optimize toward shortcuts that defeat the rubric's intent. **Acceptance:** every generated rubric includes a `regression_trip_wire` criterion (`weight: 0`, `hard_gate: true`); `scorer.py` implements all four checks; user can disable per-invocation via a single flag in `RUBRIC.md` if explicitly desired (with a warning emitted).
    </feature>

    <feature name="Hard-gate failures surface as 'crashed' rows">
      As a user reading `EXPERIMENT_LOG.md`, I want hard-gate failures visibly distinguishable from low scores. **Acceptance:** when any hard gate fails, `scorer.py` exits with non-zero status AND prints `GATE_FAILED: <gate_name>: <reason>` to stderr; `/auto-researcher` records this as a `crashed` row, not as a `kept` / `reverted` row with `composite: 0.0`.
    </feature>

    <feature name="LLM-judge averaging">
      As a user whose scorer uses an LLM judge, I want composite jitter minimized so `/auto-researcher`'s keep/revert decisions track real signal. **Acceptance:** `scorer.py` auto-averages `N=3` LLM-judge calls per criterion when LLM-judge mode is selected; `PROGRAM.fragment.md` recommends `min_delta ≥ estimated stddev` with a stub for the user to fill in after a calibration run; `temperature=0` and a fixed seed are templated where supported by the chosen LLM API.
    </feature>

    <feature name="Per-criterion gameability articulation">
      As a user trusting the rubric to drive an unattended optimizer, I want each criterion to name its own cheapest shortcut so I (or the skill) can either redesign the criterion or add a counter-criterion. **Acceptance:** every criterion in `RUBRIC.md` has a non-empty `gameability_note`; the skill suggests a counter-criterion or threshold tweak whenever a shortcut is identified that would score ≥7/10 without genuinely satisfying the criterion's intent.
    </feature>

    <feature name="Self-validation before delivery">
      As a user trusting the rubric before kicking off an overnight loop, I want structural defects caught upfront. **Acceptance:** skill runs `scripts/validate_rubric.py` before declaring done; checks include weights summing to `1.0` (±`0.001` tolerance, excluding trip-wire), every criterion has a threshold in `[0, 1]`, no duplicate criterion names, every `hard_gate` criterion has a documented fail reason, every criterion has a non-empty `gameability_note`. Failures abort delivery with clear, actionable error messages.
    </feature>

    <feature name="Synthetic dry-run sanity test">
      As a user about to invest hours in a `/auto-researcher` run, I want proof the scorer actually computes meaningful composites on best- vs worst-case inputs. **Acceptance:** skill generates two synthetic outputs (best-case and worst-case for the inferred task), runs `scorer.py` on each, and shows the user both composite values; user is warned if best-case composite < `0.7` or worst-case > `0.3` (suggesting weak rubric discrimination) and offered the chance to revise.
    </feature>

    <feature name="Domain-confidence banner">
      As a user in a domain not covered by the 5 anchor examples, I want a clear warning rather than false confidence. **Acceptance:** `RUBRIC.md` header includes a `Domain Confidence: high|medium|low` line; when `low` (no reference rubric matched closely), a "no reference rubric matched — proceed with extra scrutiny" banner is prepended above the criteria table.
    </feature>

    <feature name="Anti-pattern flagging">
      As a user designing a metric, I want common pitfalls surfaced inline. **Acceptance:** `RUBRIC.md` includes an "Anti-pattern Warnings" section that flags Goodhart-law risks, gameable criteria, missing penalty terms, and any criterion lacking a deterministic fallback when the rubric will be used with `/auto-researcher`.
    </feature>

    <feature name="Compatibility-aware PROGRAM fragment">
      As a user pasting the fragment into `/auto-researcher`'s PROGRAM.md, I want compatibility verified. **Acceptance:** `PROGRAM.fragment.md` begins with `# Compatible with auto-researcher SKILL.md §3 contract as of <ISO date>`; skill reads `C:\Users\Eddy\.claude\skills\auto-researcher\references\program-template.md` at runtime when available and emits a warning if any required field is missing or any new field is present.
    </feature>

    <feature name="Safe overwrite handling">
      As a user iterating on the rubric, I do not want to lose prior work. **Acceptance:** if `RUBRIC.md`, `scorer.py`, or `PROGRAM.fragment.md` already exists at the target location, the skill prompts the user with three options: overwrite, write to versioned filename (`RUBRIC.v2.md`, `scorer.v2.py`, `PROGRAM.fragment.v2.md`), or cancel.
    </feature>

  </core_features>

  <database_schema>
    Not a database schema in the traditional sense — this skill writes flat-file artifacts and maintains no persistent state. The "schema" is the structure of each generated file, formalized below using the template's `<table>` pattern.

    <table name="RUBRIC.md">
      YAML frontmatter: `rubric_name STRING NOT NULL`; `domain_confidence ENUM[high|medium|low] NOT NULL`; `composite_formula STRING DEFAULT "weighted_arithmetic_mean_with_hard_gates"`; `composite_direction ENUM[higher] NOT NULL DEFAULT "higher"`; `iso_generated_at ISO8601`; `trip_wire_enabled BOOL DEFAULT true`. Markdown sections: Domain-Confidence Banner (only when `low`); Adversarial Reviewer Persona (always); Criteria Table (`name STRING UNIQUE`, `definition STRING`, `what_9_of_10_looks_like STRING`, `weight FLOAT [0, 1]` (sums to 1.0 excluding trip-wire), `threshold FLOAT [0, 1]`, `hard_gate BOOL DEFAULT false`, `gameability_note STRING NOT NULL`); auto-included `regression_trip_wire` row (`weight=0`, `hard_gate=true`, four checks documented); Anti-pattern Warnings; Scorer Implementation Notes.
    </table>

    <table name="scorer.py">
      Inputs: `outputs_dir PATH` (required, conventionally `./results/` or user-specified), `baseline_dir PATH` (optional, only required if trip-wire runtime ratio is enabled). Outputs: stdout `composite: FLOAT [0, 1]` on success; stderr `GATE_FAILED: <gate_name>: <reason>` on hard-gate failure. Exit codes: `0` = success (compute composite, possibly low but valid); non-zero = hard-gate failure (mapped to `/auto-researcher` `crashed` row). Implementation: stdlib only; LLM-judge mode auto-averages `N=3` calls per criterion with `temperature=0`.
    </table>

    <table name="PROGRAM.fragment.md">
      Header: `# Compatible with auto-researcher SKILL.md §3 contract as of <ISO date>`. YAML keys: `metric_name STRING NOT NULL`; `metric_direction ENUM[higher] NOT NULL`; `metric_source ENUM[eval_command] DEFAULT "eval_command"`; `eval_command STRING DEFAULT "python scorer.py"`; `min_delta FLOAT` (placeholder with calibration guidance — `≥ estimated scorer stddev` for LLM-judge mode, `0.001` default for deterministic).
    </table>
  </database_schema>

  <api_endpoints_summary>
    Not applicable — skills do not expose APIs. The interfaces are:
    <endpoint>SKILL_INVOCATION — triggered by user phrases `/grading-rubric`, `grading rubric`, `scoring rubric`</endpoint>
    <endpoint>FILE_OUTPUTS — `RUBRIC.md`, `scorer.py`, `PROGRAM.fragment.md` written to user's project root (or override path)</endpoint>
    <endpoint>VALIDATOR_CLI — `uv run python scripts/validate_rubric.py <path-to-RUBRIC.md>` — exit code `0` = valid, non-zero = errors printed to stderr</endpoint>
    <endpoint>SCORER_CLI — `python scorer.py` (in user's project) — exit `0` + `composite: <float>` to stdout = success; non-zero exit + `GATE_FAILED: <reason>` to stderr = hard-gate failure</endpoint>
  </api_endpoints_summary>

  <implementation_steps>
    1. Scaffold skill folder `C:\Users\Eddy\.claude\skills\grading-rubric\` with `SKILL.md`, `references/`, `scripts/`, `assets/`, `evals/`.
    2. Write `SKILL.md` v1: trigger-tuned YAML frontmatter (description loaded with phrases per Phase 2 Q2 batch a) + workflow body covering Stages A (analyze) → B (generate) → C (self-validate) → D (dry-run) → E (emit). Body ≤500 lines; longer detail goes into `references/`.
    3. Build 5 anchor reference rubrics in `references/`: `trading-strategy.md`, `code-quality.md`, `writing.md`, `ml-eval.md`, `generic-task.md`. Each is a worked example with all data-shape fields populated, including `gameability_note` per criterion.
    4. Build `assets/scorer.py.template`: parameterized Python (stdlib only) that reads outputs, computes weighted mean × hard-gate multiplier, averages `N=3` for LLM-judge mode (`temperature=0`), implements `regression_trip_wire` checks (empty / NaN / runtime > 10× baseline / structure invalid), prints `composite: <float>`, exits non-zero with stderr reason on hard-gate failure.
    5. Build `assets/PROGRAM.fragment.md.template`: ready-to-paste snippet with `# Compatible with auto-researcher SKILL.md §3 as of <ISO date>` header, `metric_source: eval_command` pointing at `scorer.py`, `min_delta` placeholder with calibration guidance for LLM-judge vs deterministic modes.
    6. Build `scripts/validate_rubric.py`: weights sum to `1.0` (±`0.001`, excluding trip-wire), every criterion has threshold in `[0, 1]`, no duplicate names, every `hard_gate` criterion has a documented fail reason, every criterion has a non-empty `gameability_note`. `uv`-runnable.
    7. Document gameability + adversarial persona + anti-pattern + domain-confidence logic inline in `SKILL.md` as part of the generation workflow (Stage B).
    8. Document dry-run sanity workflow in `SKILL.md` (Stage D): synthesize best/worst outputs, run `scorer.py` on both, display composites, warn if best < `0.7` or worst > `0.3`.
    9. Write `evals/evals.json` with 3 realistic test prompts: (a) "design a rubric for an `/auto-researcher` loop optimizing a momentum trading strategy on SPY," (b) "scoring rubric for a code-refactor loop targeting readability of a Python module," (c) "rubric for iteratively improving a 1-page research summary on a macro topic." Add assertions covering: weights sum check, trip-wire presence, `scorer.py` runs without error on synthetic input, `RUBRIC.md` contains required sections (frontmatter, persona, criteria table, anti-patterns, scorer implementation notes).
    10. Run `/skill-creator` eval workflow: spawn 3 with-skill + 3 baseline subagents in parallel, capture timing data on completion, grade via assertions, aggregate benchmark, launch `eval-viewer/generate_review.py` for human review, iterate based on feedback until user is satisfied; then optionally package via `scripts/package_skill.py`.
  </implementation_steps>

  <success_criteria>

    <functional>
      - Skill triggers on explicit user phrases (`/grading-rubric`, `grading rubric`, `scoring rubric`) with high reliability (≥90% on a held-out trigger eval if the description-optimization step is run).
      - Generated `RUBRIC.md` passes `validate_rubric.py` for 100% of tested invocations.
      - Generated `scorer.py` runs without errors on synthetic inputs for 100% of tested invocations.
      - Composite output is always in `[0, 1]`, higher-is-better, regardless of domain.
      - Hard-gate failures always exit non-zero with stderr reason — never silent zero.
      - `regression_trip_wire` criterion is present in 100% of generated rubrics unless explicitly disabled.
      - `PROGRAM.fragment.md` always includes the auto-researcher compatibility comment.
    </functional>

    <ux>
      - Single-mode operation: skill auto-decides interview depth based on confidence; user is asked at most 3 clarifying questions in low-confidence cases.
      - Files written to user's project root by default, with overwrite protection (overwrite / versioned / cancel).
      - Domain-confidence banner makes capability honest and visible.
      - Anti-pattern + gameability warnings surface inline in `RUBRIC.md`, not buried in references.
      - On dry-run failure (best < `0.7` or worst > `0.3`), user is offered the chance to revise before files are finalized.
    </ux>

    <technical>
      - `SKILL.md` ≤500 lines; reference files cover detail.
      - `scorer.py.template` uses Python stdlib only (no extra installs in user projects).
      - `scripts/validate_rubric.py` is `uv`-runnable.
      - `PROGRAM.fragment.md` includes auto-researcher compatibility comment AND the skill performs a runtime read of `program-template.md` when present.
      - Self-validation and dry-run gates block delivery on failure with actionable error messages.
      - 5 anchor reference rubrics each cover all data-shape fields and serve as concrete worked examples (not defaults).
    </technical>

  </success_criteria>

</project_specification>
