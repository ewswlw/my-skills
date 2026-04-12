"""Evaluator for creative generation template."""
import argparse

import numpy as np

from shinka.core import run_shinka_eval


def get_kwargs(run_idx: int) -> dict:
    return {
        "random_seed": int(np.random.randint(0, 1_000_000_000)),
        "theme": "art science nature beauty chaos",
    }


def aggregate_fn(results: list) -> dict:
    scores = [r[0] for r in results]
    texts = [r[1] for r in results if len(r) > 1 and r[1]]
    return {
        "combined_score": float(np.mean(scores)),
        "public": {"mean_quality": float(np.mean(scores))},
        "private": {},
        "extra_data": {"sample_outputs": texts[:3]},
        "text_feedback": texts[0] if texts else "",
    }


def validate_fn(result):
    if not isinstance(result[0], (int, float)):
        return False, f"Expected numeric score, got {type(result[0])}"
    return True, None


def main(program_path: str, results_dir: str):
    metrics, correct, err = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_experiment",
        num_runs=3,
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
