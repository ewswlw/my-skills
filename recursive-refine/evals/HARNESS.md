# recursive-refine benchmark harness

## Canonical vs baseline (adversarial)

Grading always uses the **canonical** task in each eval’s `prompt` and `expectations` — what a full recursive-refine run should achieve.

**Baseline** runs simulate a **scope-averse or process-constrained user** via `baseline_constraints`. Executors that ignore these constraints produce invalid baselines (treat as benchmark bug and re-run).

| Run type       | Instructions |
|----------------|--------------|
| `with_skill`   | Read `SKILL.md` and satisfy the canonical `prompt` with scorecard + loop. |
| `without_skill`| Apply the same `prompt` **and** obey `baseline_constraints` exactly. |

This separates “model defaults under tight stakeholder rules” from “structured rubric workflow,” and reduces false ties when the base model would otherwise gold-plate.

## Adding an eval

1. Append an object to `evals` in `evals.json` with `id`, `prompt`, `expectations`, and `baseline_constraints`.
2. Write `expectations` so they are checkable from `outputs/` + `transcript.md` / `scorecard.md`.
3. **Stress-test** `baseline_constraints`: a literal reading should make at least one high-value expectation fail without the skill (usually scorecard + length/structure).
4. **Align the bar with the prompt:** if the canonical `prompt` says “keep it concise,” a high minimum word count on `with_skill` can fail despite good output (iteration-3 eval-1). Either lower the floor, remove the word-count check, or tighten the skill to “meet numeric eval thresholds when present.”

## Files

- `evals.json` — source of truth for prompts, expectations, and baseline traps.
- Workspace output: `recursive-refine-workspace/iteration-N/eval-*/{with_skill,without_skill}/run-1/`.
