---
rubric_name: generic_task_anchor
domain_confidence: low
composite_formula: weighted_arithmetic_mean_with_hard_gates
composite_direction: higher
trip_wire_enabled: true
iso_generated_at: "2026-04-29T11:20:00-04:00"
criteria:
  - name: correctness
    weight: 0.35
    threshold: 0.75
    hard_gate: false
    definition: "Output produces the result the task description asks for, on the inputs the task description names."
    what_9_of_10_looks_like: "Every stated requirement in the task description maps to a verifiable element in the output; no requirement is silently dropped or partially addressed."
    gameability_note: "Could be gamed by hard-coding for known inputs or by selectively quoting the task description back at the user. Counter: hold-out inputs the task description did not enumerate, or use an LLM judge that has access to the original task and not just the output."
  - name: completeness
    weight: 0.25
    threshold: 0.7
    hard_gate: false
    definition: "All elements of the task are addressed, not just the most prominent ones; secondary asks are not omitted."
    what_9_of_10_looks_like: "If the task asks for 'A, B, and C', the output addresses all three; if it asks for 'consider X', X is visibly considered (even if briefly)."
    gameability_note: "Could be gamed by adding shallow placeholder sections for every task element. Counter: pair with `clarity` (below) which penalizes filler."
  - name: clarity
    weight: 0.25
    threshold: 0.7
    hard_gate: false
    definition: "A reader unfamiliar with the task can verify the output's correctness without re-reading multiple times."
    what_9_of_10_looks_like: "Output is structured (sections, bullets, or labeled fields where appropriate); jargon is defined or avoided; the output's own organization mirrors the task's structure."
    gameability_note: "Could be gamed by adding superficial structure (headings without content, bullets that pad). Counter: an LLM judge should ask 'does removing this structure lose information?' and penalize when the answer is no."
  - name: efficiency
    weight: 0.15
    threshold: 0.6
    hard_gate: false
    definition: "Output is no longer than necessary to satisfy the task; runtime to produce the output is reasonable for the task's complexity."
    what_9_of_10_looks_like: "No obvious bloat (repeated content, unnecessary preambles, summary-of-the-summary tails); if the task implies a runtime budget, it is honored within reason."
    gameability_note: "Could be gamed by extreme terseness that drops content the task required. Counter: this criterion is bottom-weighted (0.15) so terseness cannot win at the expense of correctness or completeness."
  - name: regression_trip_wire
    weight: 0
    threshold: 0
    hard_gate: true
    definition: "Catastrophic-output detector: empty output, NaN/error tokens, runaway runtime, or fundamentally malformed structure."
    what_9_of_10_looks_like: "Never fires on valid outputs; always fires on degenerate ones (empty file, model-artifact tokens like '<|endoftext|>' leaking through, infinite-loop runs, output that no parser can interpret as the requested format)."
    gameability_note: "Not a quality criterion; pure failure detector. Always include this in generic-task rubrics — by definition, the skill does not know the domain well, so degenerate outputs are more likely than in domain-specific anchors."
    checks:
      - empty_output
      - nan_or_error
      - runtime_exceeded
      - structure_invalid
---

# Generic Task Anchor Rubric

> **Fallback rubric used when no domain-specific anchor matches with high confidence.** This anchor's `domain_confidence` is set to `low` to signal that the resulting RUBRIC.md is a generative draft rather than a domain-tested template. The skill prepends a "no reference rubric matched closely — proceed with extra scrutiny" banner when generating from this anchor.

## When to use this anchor

Use as a last resort when the task description does not match any of the high-confidence anchors:
- `trading-strategy.md`
- `code-quality.md`
- `writing.md`
- `ml-eval.md`

This anchor's criteria (correctness, completeness, clarity, efficiency) are deliberately abstract — they apply to almost any task, but they cannot encode domain-specific failure modes. **The user should treat the resulting rubric as a starting point and tighten it to their task before running an unattended /auto researcher loop.**

## Adversarial Reviewer Persona

A skeptical first-time user who has never seen this task before. They ask: "Does this output do what was asked, completely, clearly, and without obvious waste?" They have no domain context to fall back on, so they evaluate the output on its own terms. Used only when scorer is in `llm_judge` mode.

## Anti-pattern Warnings

- **False confidence from a generic rubric.** The most dangerous failure mode here is the user trusting a generic-task rubric as if it were domain-specific. The skill MUST surface the "low confidence — proceed with extra scrutiny" banner whenever this anchor is used; do not soften this language.
- **Goodhart on completeness.** Without `clarity` and `efficiency` as counterweights, the agent will pad outputs with shallow coverage of every task element. The 0.25 / 0.25 / 0.15 distribution exists to keep this in check.
- **Domain-specific failure modes invisible.** This rubric does not catch failures unique to a domain (test-set leakage in ML, gross-Sharpe optimization in trading, hallucinated citations in writing). When the user runs against this anchor, the skill should explicitly warn about the missing domain-specific protections.
- **Trip-wire is more important here, not less.** Because the rest of the rubric is abstract, the trip-wire's deterministic checks for empty/NaN/runtime/structure failures provide a disproportionate share of the safety net. Disabling the trip-wire on a generic-task rubric is especially dangerous.

## Scorer Implementation Notes

- **Mode:** `llm_judge` is the default — without domain-specific deterministic checks, the LLM judge is the only practical scorer. Use N=3 averaging with `temperature=0`.
- **Inputs the scorer expects:** a single output artifact (file or stdout capture) and the original task description (passed to the LLM judge as context).
- **The adversarial persona above** is generic by design; consider tightening it for the specific task before kicking off a long /auto researcher run.
- **Strongly consider replacing this anchor** with a custom rubric tuned to the task before any unattended loop. The `low` `domain_confidence` value is the skill's signal to the user that this is a starting point, not a destination.
