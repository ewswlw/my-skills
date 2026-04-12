"""Pre-flight smoke test for ShinkaEvolve task directories.

Runs evaluate.py on initial.<ext> and validates the output schema.
Pass criteria: metrics.json has numeric combined_score, correct.json has correct=true.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test a Shinka task directory")
    parser.add_argument("--task-dir", default=".", help="Task directory (default: CWD)")
    parser.add_argument("--results-dir", default=None, help="Results output dir")
    args = parser.parse_args()

    task_dir = Path(args.task_dir).resolve()
    results_dir = Path(args.results_dir) if args.results_dir else task_dir / "smoke_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    eval_script = task_dir / "evaluate.py"
    initial = None
    for ext in ("py", "jl", "cpp", "cu", "rs", "swift", "json"):
        candidate = task_dir / f"initial.{ext}"
        if candidate.exists():
            initial = candidate
            break

    if not eval_script.exists():
        print(f"FAIL: evaluate.py not found in {task_dir}", file=sys.stderr)
        return 1
    if initial is None:
        print(f"FAIL: No initial.<ext> found in {task_dir}", file=sys.stderr)
        return 1

    print(f"Running: evaluate.py --program_path {initial.name} --results_dir {results_dir}")
    result = subprocess.run(
        [sys.executable, str(eval_script),
         "--program_path", str(initial),
         "--results_dir", str(results_dir)],
        capture_output=True, text=True, timeout=300, cwd=str(task_dir),
    )

    if result.returncode != 0:
        print(f"FAIL: evaluate.py exited with code {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return 1

    metrics_path = results_dir / "metrics.json"
    correct_path = results_dir / "correct.json"

    errors = []
    if not metrics_path.exists():
        errors.append("metrics.json not found in results_dir")
    else:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if "combined_score" not in metrics:
            errors.append("metrics.json missing 'combined_score' key")
        elif not isinstance(metrics["combined_score"], (int, float)):
            errors.append(f"combined_score is {type(metrics['combined_score']).__name__}, expected numeric")

    if not correct_path.exists():
        errors.append("correct.json not found in results_dir")
    else:
        correct = json.loads(correct_path.read_text(encoding="utf-8"))
        if not correct.get("correct", False):
            err_msg = correct.get("error", "unknown error")
            errors.append(f"correct.json reports failure: {err_msg}")

    if errors:
        print("FAIL:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    score = json.loads(metrics_path.read_text(encoding="utf-8"))["combined_score"]
    print(f"PASS: Smoke test succeeded. combined_score = {score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
