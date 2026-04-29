---
rubric_name: writing_anchor
domain_confidence: high
composite_formula: weighted_arithmetic_mean_with_hard_gates
composite_direction: higher
trip_wire_enabled: true
iso_generated_at: "2026-04-29T11:20:00-04:00"
criteria:
  - name: specificity
    weight: 0.30
    threshold: 0.7
    hard_gate: false
    definition: "Concrete claims with named entities, numbers, and time horizons rather than abstract generalities."
    what_9_of_10_looks_like: "Every paragraph contains at least one named entity (company, instrument, central bank, country) and at least one quantitative anchor (percent, basis points, dollar amount, date). No paragraph is entirely composed of abstract nouns."
    gameability_note: "Could be gamed by stuffing in random numbers or dropping ticker symbols without explanatory weight. Counter: pair with `sourcing` criterion below — every quantitative claim should be either sourced or explicitly framed as estimate/expectation."
  - name: sourcing
    weight: 0.30
    threshold: 0.7
    hard_gate: false
    definition: "Quantitative claims and non-obvious assertions are attributed to a named source or marked as the author's view."
    what_9_of_10_looks_like: "Every figure carries a parenthetical source (e.g., '(Fed dot plot, March 2026)') or a citation marker; assertions of opinion are flagged with 'we expect / our view'; no orphan statistics."
    gameability_note: "Could be gamed by inventing plausible-looking citations the user cannot easily verify. Counter: in /recursive-refine mode, the adversarial reviewer is instructed to spot-check at least one citation per paragraph."
  - name: structural_clarity
    weight: 0.20
    threshold: 0.7
    hard_gate: false
    definition: "Reader can scan the document in 30 seconds and extract the thesis, the supporting evidence, and the recommendation."
    what_9_of_10_looks_like: "Headline thesis at the top; bolded subheads for each section; a one-paragraph summary or bulleted takeaways at the end; no paragraph longer than 6 lines on a standard PDF render."
    gameability_note: "Could be gamed by adding decorative headings that don't reflect content shifts. Counter: structural review should ask 'does each subhead's body actually deliver what the subhead promises?'"
  - name: non_hedginess
    weight: 0.20
    threshold: 0.7
    hard_gate: false
    definition: "Author commits to a directional view rather than enumerating possibilities. Hedge language is bounded and intentional."
    what_9_of_10_looks_like: "Clear 'we expect / our view is / we recommend' statements; hedge words ('possibly', 'could', 'may', 'likely') used at most twice per page; no closing paragraph that retreats from the headline thesis."
    gameability_note: "Could be gamed by stripping all hedges, producing overconfident bad writing. Counter: this criterion is bottom-weighted (0.20) and the adversarial persona below is instructed to flag overclaiming as a separate problem."
  - name: regression_trip_wire
    weight: 0
    threshold: 0
    hard_gate: true
    definition: "Catastrophic-output detector: empty document, hallucinated tokens (raw model artifacts), runaway runtime, or broken markdown structure."
    what_9_of_10_looks_like: "Never fires on valid drafts; always fires on degenerate ones (zero-word output, '<|endoftext|>' tokens leaking through, infinite hedging-loop, broken markdown that won't render)."
    gameability_note: "Not a quality criterion; pure failure detector. Especially valuable for LLM-driven refinement loops where degenerate outputs are common failure modes."
    checks:
      - empty_output
      - nan_or_error
      - structure_invalid
---

# Writing / Research Summary Anchor Rubric

> Reference rubric for refining short-form research, IC memos, market commentary, or any 1-page persuasive writing where a decision-maker is the audience. Used by `grading-rubric` as a high-confidence anchor for `/recursive-refine` workflows on professional writing. **Do not use verbatim — adapt criteria, weights, and adversarial persona to the audience.**

## When to use this anchor

Match against this anchor when the user's task description contains signals like:
- Refining a research summary, IC memo, or investor letter
- Improving a 1-page macro / equity / credit note
- Tightening exec comms (status updates, post-mortems for execs)
- Rewriting marketing copy for a sophisticated B2B audience

## Adversarial Reviewer Persona

A buy-side portfolio manager with 90 seconds before their next call. They scan the document for the thesis, the key numbers, and the recommendation. They mistrust hedge words, generic claims, and unsourced figures. They will accept a wrong-but-clear view over a hedged-but-vague one (because the wrong view is debatable; the vague one is unfalsifiable). Used only when scorer is in `llm_judge` mode.

## Anti-pattern Warnings

- **Specificity-without-sourcing trap.** An LLM-judge optimizer will quickly discover that adding numbers raises the `specificity` score. Without `sourcing` as a paired criterion, those numbers will be invented. Keep both criteria — they are co-dependent.
- **Hedge-stripping overcorrection.** Removing all hedges produces overconfident writing that the adversarial reviewer will also penalize. The `non_hedginess` criterion is intentionally bottom-weighted to avoid an overshoot dynamic.
- **Goodhart on length.** If the scorer measures word count or paragraph count, the optimizer learns to pad. Keep length out of the rubric; let `structural_clarity` and the implicit page-budget guide the model.
- **Citation hallucination.** The adversarial reviewer must spot-check citations. If they cannot (e.g., in fully-automated mode), `sourcing`'s LLM-judge prompt should explicitly demand the citations be plausible-and-verifiable, not just present.

## Scorer Implementation Notes

- **Mode:** `llm_judge` is required — every criterion above involves judgment a deterministic scorer cannot make. Average N=3 with `temperature=0`.
- **Inputs the scorer expects:** a single markdown or plain-text file containing the refined draft, readable from `outputs_dir`.
- **The adversarial persona above** should be passed verbatim into the LLM-judge system prompt as the reviewer's role.
- **For `/recursive-refine` integration:** the per-criterion `threshold` values drive the loop's pass/fail decision. The composite is also computed (for /auto researcher), but `/recursive-refine` cares more about per-criterion thresholds.
