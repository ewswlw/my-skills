"""Evaluator for ML tuning template."""
import argparse

import numpy as np

from shinka.core import run_shinka_eval


def get_kwargs(run_idx: int) -> dict:
    return {"random_seed": int(np.random.randint(0, 1_000_000_000))}


def aggregate_fn(results: list) -> dict:
    scores = [r[0] for r in results]
    texts = [r[1] for r in results if len(r) > 1]
    return {
        "combined_score": float(np.mean(scores)),
        "public": {"mean_accuracy": float(np.mean(scores)), "std_accuracy": float(np.std(scores))},
        "private": {},
        "extra_data": {},
        "text_feedback": "; ".join(t for t in texts if t),
    }


def validate_fn(result):
    score = result[0]
    if not isinstance(score, (int, float)):
        return False, f"Expected numeric accuracy, got {type(score)}"
    if not 0.0 <= score <= 1.0:
        return False, f"Accuracy {score} outside [0, 1] range"
    return True, None


def main(program_path: str, results_dir: str):
    metrics, correct, err = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_experiment",
        num_runs=5,
        get_experiment_kwargs=get_kwargs,
        aggregate_metrics_fn=aggregate_fn,
        validate_fn=validate_fn,
    )
    if not correct:
        raise RuntimeError(err or "Evaluation failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program_path", required=True)
    parser.add_argument("--results_dir", required=True)
    args = parser.parse_args()
    main(program_path=args.program_path, results_dir=args.results_dir)
