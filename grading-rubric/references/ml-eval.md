---
rubric_name: ml_eval_anchor
domain_confidence: high
composite_formula: weighted_arithmetic_mean_with_hard_gates
composite_direction: higher
trip_wire_enabled: true
iso_generated_at: "2026-04-29T11:20:00-04:00"
criteria:
  - name: accuracy
    weight: 0.35
    threshold: 0.75
    hard_gate: false
    definition: "Headline performance metric on a held-out test set (accuracy, F1, AUC, or task-appropriate equivalent)."
    what_9_of_10_looks_like: "Above the published baseline for the task by a meaningful margin (e.g., 3 percent absolute accuracy or 0.05 AUC); test set was sealed from training and validation."
    gameability_note: "Trivially gamed by training on the test set, by overfitting to a specific split, or by tuning hyperparameters using test-set feedback. Counter: enforce strict three-way split (train / val / sealed-test) and verify the test set hash is unchanged across iterations."
  - name: calibration
    weight: 0.20
    threshold: 0.7
    hard_gate: false
    definition: "Predicted probabilities match observed frequencies — when the model says 70 percent, it is right 70 percent of the time."
    what_9_of_10_looks_like: "Expected Calibration Error (ECE) below 0.05 across 10 probability bins; reliability diagram is close to the diagonal; calibration is checked on the same sealed test set as accuracy."
    gameability_note: "Easy to optimize away by post-hoc Platt scaling or isotonic regression on the test set itself. Counter: the calibration fit must be done on validation, not test."
  - name: fairness_parity
    weight: 0.20
    threshold: 0.65
    hard_gate: false
    definition: "Performance does not collapse on any documented data slice (demographic, geographic, temporal, or other domain-relevant subgroup)."
    what_9_of_10_looks_like: "No slice has accuracy below 80 percent of the global accuracy; slices are defined a priori before training, not carved out post hoc; minimum slice size enforced."
    gameability_note: "Easy to game by defining slices coarsely or by ignoring slices the model does poorly on. Counter: slice definitions are version-controlled alongside the rubric and cannot be changed without a comment in the experiment log."
  - name: inference_latency
    weight: 0.15
    threshold: 0.7
    hard_gate: false
    definition: "p95 inference time per sample, on the production-target hardware, within the application's latency budget."
    what_9_of_10_looks_like: "p95 latency below 80 percent of the SLA budget; p99 under 100 percent; measured on a representative batch and on cold-start where applicable."
    gameability_note: "Could be gamed by measuring on warm cache or unrealistic batch sizes. Counter: latency benchmark script is fixed and version-controlled; cold/warm split is mandatory."
  - name: training_reproducibility
    weight: 0.10
    threshold: 0.7
    hard_gate: false
    definition: "Re-running training with the same code and seed produces a model whose test-set metrics match the original within tolerance."
    what_9_of_10_looks_like: "Two independent training runs with the same seed produce test-set accuracy within 0.5 percent of each other; non-determinism (CUDA, dropout) is controlled or documented."
    gameability_note: "Could be gamed by reporting only one of many trial runs. Counter: scorer should run training twice (or read pre-computed dual-seed outputs) and check the delta — not just trust a single number."
  - name: regression_trip_wire
    weight: 0
    threshold: 0
    hard_gate: true
    definition: "Catastrophic-output detector: empty predictions file, NaN/inf in metrics, runaway training time, or invalid model schema."
    what_9_of_10_looks_like: "Never fires on valid runs; always fires on degenerate ones (zero predictions, NaN-poisoned loss, training that exceeds 10x baseline wall-clock, missing required output columns)."
    gameability_note: "Not a quality criterion; pure failure detector. Especially valuable here because ML training failures often produce silently bad outputs (NaN-spiked losses, near-trivial models) that score poorly but in ways the agent might rationalize."
    checks:
      - empty_output
      - nan_or_error
      - runtime_exceeded
      - structure_invalid
---

# ML Evaluation Anchor Rubric

> Reference rubric for evaluating supervised classification or regression model iterations. Used by `grading-rubric` as a high-confidence anchor when the user's task involves model training, hyperparameter tuning, or feature-engineering loops. **Do not use verbatim — adapt to the specific task type, baseline, and SLA.**

## When to use this anchor

Match against this anchor when the user's task description contains signals like:
- Training a classification or regression model
- Hyperparameter optimization (grid search, Bayesian, evolutionary)
- Feature engineering or selection loops
- Model deployment readiness checks

## Adversarial Reviewer Persona

An ML engineer about to merge the model into production. They distrust headline metrics, look hard at the train/val/test split discipline, demand calibration before deployment, and won't ship a model whose worst-slice accuracy is unknown. They've been burned by latency surprises in production and want cold-start numbers. Used only when scorer is in `llm_judge` mode (typically not — most criteria here are deterministic).

## Anti-pattern Warnings

- **Test-set leakage.** The single most common failure mode in ML loops. The `accuracy` criterion above is meaningless if the test set was used for hyperparameter tuning or model selection. Enforce a sealed test set, hash-checked at every iteration, opened only for final scoring.
- **Calibration on test.** Post-hoc calibration (Platt, isotonic) fitted on the test set inflates calibration scores while leaking. The calibration fit must use validation data; the test set is for measurement only.
- **Slice cherry-picking.** Defining fairness slices after seeing model errors is a guaranteed way to find slices the model does well on. Slice definitions must be frozen before training.
- **Single-seed reporting.** A model that scores 88 percent on seed 42 and 81 percent on seed 43 is not an 88-percent model. The `training_reproducibility` criterion is intentionally low-weighted (0.10) so it does not crowd out accuracy, but its threshold (0.7) is firm.
- **Goodhart on accuracy.** Accuracy alone reliably produces models that fail on edge cases. The `fairness_parity` criterion is the structural counterweight; weight it high enough to bite (0.20) but not so high it dominates (which would over-credit models that are uniformly mediocre).

## Scorer Implementation Notes

- **Mode:** `deterministic` for all criteria — every metric here has a well-defined numerical computation. `llm_judge` mode is not appropriate for ML evaluation.
- **Inputs the scorer expects:** a predictions file (per-row predicted label or probability), a ground-truth file (held-out test set labels), a slice-definition file (precomputed slice membership per row), and a latency benchmark output (per-sample wall-clock times). All under `outputs_dir`.
- **Test-set hash check:** the scorer should compute a content hash of the test-set file and compare to a stored expected hash; mismatch fires the trip-wire (`structure_invalid` check).
- **Seed-comparison logic** for `training_reproducibility`: read predictions from two seed runs (e.g., `predictions_seed_a.csv`, `predictions_seed_b.csv`); if only one is present, score this criterion as 0 with a stderr warning.
