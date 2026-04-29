---
rubric_name: code_quality_anchor
domain_confidence: high
composite_formula: weighted_arithmetic_mean_with_hard_gates
composite_direction: higher
trip_wire_enabled: true
iso_generated_at: "2026-04-29T11:20:00-04:00"
criteria:
  - name: tests_pass
    weight: 0
    threshold: 1
    hard_gate: true
    fail_reason: "Any test failure indicates the refactor changed behavior the existing test suite is meant to protect; the loop must revert this iteration."
    definition: "Existing project test suite passes after the refactor with no skipped or xfail tests added."
    what_9_of_10_looks_like: "Full test suite green; no @pytest.mark.skip or xfail decorators introduced; test count is unchanged or higher."
    gameability_note: "Could be gamed by deleting failing tests or marking them as skipped. Counter: separate criterion (test_count_preserved) or pre/post test-count diff check, plus this rubric's `minimal_diff` criterion which would penalize test-file deletions."
  - name: readability
    weight: 0.40
    threshold: 0.75
    hard_gate: false
    definition: "How quickly a fellow engineer can understand each function's purpose and flow without external context."
    what_9_of_10_looks_like: "Cyclomatic complexity ≤ 6 per function; descriptive names; no nested conditionals more than 2 deep; comments explain *why* (intent, trade-off) not *what* (which the code already shows)."
    gameability_note: "Could be gamed by adding verbose docstrings and one-line-per-statement formatting that bloats line count without improving comprehension. Counter: pair with `minimal_diff` (below) so growth is penalized; consider a token-density check."
  - name: naming_quality
    weight: 0.20
    threshold: 0.7
    hard_gate: false
    definition: "Identifiers (functions, variables, classes) carry their meaning without abbreviation, hungarian notation, or single-letter names outside narrow loop indices."
    what_9_of_10_looks_like: "Every public name passes the 'a new contributor reads it once and gets it' test; private helpers may be terser; no `data`, `result`, `tmp`, or `obj` as standalone variable names; no Hungarian-style prefixes."
    gameability_note: "Could be gamed by inflating names with redundant qualifiers (`get_user_data_from_database_by_user_id_function`). Counter: maximum-name-length soft check or LLM-judge review."
  - name: structure
    weight: 0.20
    threshold: 0.7
    hard_gate: false
    definition: "Logical organization within the module — related code grouped, dependency direction sensible, no circular imports or cross-cutting helpers buried mid-file."
    what_9_of_10_looks_like: "Public API at the top, private helpers below; constants and types grouped; clear separation between data structures, business logic, and I/O."
    gameability_note: "Could be gamed by reshuffling without behavioral improvement (motion theater). Counter: pair with `minimal_diff` so shuffling for its own sake costs."
  - name: minimal_diff
    weight: 0.20
    threshold: 0.7
    hard_gate: false
    definition: "Surgical changes: only the lines needed for the refactor are touched; unrelated formatting, comment churn, and adjacent rewrites are avoided."
    what_9_of_10_looks_like: "Net line-count change within ±20 percent of original; no formatting-only edits to lines outside the refactor's logical scope; preserved trailing whitespace and existing comment style."
    gameability_note: "Could be gamed by being so minimal the refactor doesn't actually fix anything. Counter: this criterion is bottom-weighted (0.20) so it cannot dominate; readability and structure carry the load."
  - name: regression_trip_wire
    weight: 0
    threshold: 0
    hard_gate: true
    definition: "Catastrophic-output detector: empty file, NaN/error tokens in source, runaway formatter runtime, or syntactically invalid Python."
    what_9_of_10_looks_like: "Never fires on valid refactors; always fires on degenerate ones (zero-byte source files, syntax errors, infinite-loop AST visitors)."
    gameability_note: "Not a quality criterion; pure failure detector. Disabling this risks the agent discovering 'refactor by deletion' as a way to maximize minimal_diff."
    checks:
      - empty_output
      - nan_or_error
      - runtime_exceeded
      - structure_invalid
---

# Code Quality Anchor Rubric

> Reference rubric for Python code refactoring loops targeting readability and maintainability. Used by `grading-rubric` as a high-confidence anchor when the user's task involves restructuring existing code without behavior change. **Do not use verbatim for a real loop — adapt criteria and weights to the codebase.**

## When to use this anchor

Match against this anchor when the user's task description contains signals like:
- Refactoring a Python module for readability or testability
- Reducing cyclomatic complexity or file length
- Renaming variables, extracting helpers, splitting functions
- Improving error handling or naming consistency in a bounded scope

## Adversarial Reviewer Persona

A senior engineer reviewing the refactor PR with the original module open in a side-by-side diff. They ask: "Did this make the code easier for the *next* person to change?" They are skeptical of motion-without-improvement (rearranging chairs), of cleverness for its own sake, and of any change that touches lines outside the stated scope. Used only when scorer is in `llm_judge` mode.

## Anti-pattern Warnings

- **Tests-pass-only optimization.** Without the `tests_pass` hard gate, the agent will discover "delete the failing test" as a winning move. Without the rest of the rubric, it will discover "do nothing, all tests still pass" as winning too. The hard gate is necessary but not sufficient — keep both.
- **Readability vs. minimal-diff tension.** The agent will be tempted to either rewrite huge swaths of code to chase readability or make trivial changes to chase minimal_diff. The 0.40 / 0.20 weighting here biases toward readability while keeping minimal_diff present as a brake.
- **Goodhart on cyclomatic complexity.** If the scorer literally measures CC and weights it heavily, the agent will replace one complex function with three nested helpers to game the per-function metric while making the call graph worse. Keep CC as input to the LLM-judge readability score, not as a standalone numeric criterion.
- **Comment churn.** Refactors often produce comment edits that aren't strictly part of the refactor. The `minimal_diff` criterion catches these; do not relax it without a counterweight.

## Scorer Implementation Notes

- **Mode:** `llm_judge` is preferred for `readability`, `naming_quality`, and `structure` — these are inherently subjective. `tests_pass`, `minimal_diff`, and the trip-wire are deterministic.
- **Inputs the scorer expects:** the refactored source file path and the original (pre-refactor) source file path, both readable from `outputs_dir`. Tests-pass is determined by `pytest` exit code (subprocess call) or a `pytest_exit_code.txt` written by the user's `run_command`.
- **`minimal_diff` is computed deterministically** from `git diff --numstat` (or unified-diff line counts); the scorer should not LLM-judge this.
- **`tests_pass.fail_reason`** must surface in the `GATE_FAILED:` stderr line so the user reading `EXPERIMENT_LOG.md` immediately understands which test broke.
