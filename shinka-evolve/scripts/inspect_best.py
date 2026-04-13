"""
Post-evolution tearsheet: find the best evolved program and print metrics.

Usage:
    uv run python inspect_best.py --results_dir results/trading_evo

Reads metrics.json files from the results directory, finds the highest
combined_score, and prints a plain-text summary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def find_best(results_dir: Path) -> dict | None:
    best_score = float("-inf")
    best_metrics = None

    for mf in sorted(results_dir.rglob("metrics.json")):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        score = data.get("combined_score")
        if score is not None and float(score) > best_score:
            best_score = float(score)
            best_metrics = data
            best_metrics["_source_file"] = str(mf)

    return best_metrics


def print_tearsheet(m: dict) -> None:
    pub = m.get("public", {})
    print("=" * 60)
    print("  BEST EVOLVED STRATEGY — TEARSHEET")
    print("=" * 60)
    print(f"  Source:          {m.get('_source_file', 'N/A')}")
    print(f"  Policy:          {pub.get('policy_name', 'N/A')}")
    print(f"  Combined Score:  {m.get('combined_score', 0):.4f}")
    print("-" * 60)
    print(f"  Train Sharpe:    {pub.get('train_sharpe', 0):.4f}")
    print(f"  Test Sharpe:     {pub.get('test_sharpe', 0):.4f}")
    print(f"  Train Max DD:    {pub.get('train_max_dd', 0):.4f}")
    print(f"  Test Max DD:     {pub.get('test_max_dd', 0):.4f}")
    print(f"  Mean Turnover:   {pub.get('mean_turnover', 0):.6f}")
    print("=" * 60)

    gap = pub.get("train_sharpe", 0) - pub.get("test_sharpe", 0)
    if gap > 1.0:
        print("  WARNING: Train-test Sharpe gap > 1.0 — possible overfitting")
    if pub.get("train_max_dd", 0) < -0.20:
        print("  WARNING: Train max drawdown exceeds 20%")


def main() -> None:
    p = argparse.ArgumentParser(description="Inspect best ShinkaEvolve result")
    p.add_argument("--results_dir", type=str, required=True)
    args = p.parse_args()

    rd = Path(args.results_dir)
    if not rd.exists():
        print(f"Results directory not found: {rd}")
        return

    best = find_best(rd)
    if best is None:
        print("No metrics.json files found in results directory.")
        return

    print_tearsheet(best)


if __name__ == "__main__":
    main()
