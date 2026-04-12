"""Extract top-k performing programs from a ShinkaEvolve run.

Produces a Markdown context bundle with scores, code, and text feedback.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect best programs from a Shinka run")
    parser.add_argument("--results-dir", required=True, help="Path to run results directory or DB")
    parser.add_argument("--k", type=int, default=5, help="Number of top programs (default: 5)")
    parser.add_argument("--max-code-chars", type=int, default=4000, help="Per-program code truncation")
    parser.add_argument("--min-generation", type=int, default=None, help="Optional lower bound on generation")
    parser.add_argument("--out", default=None, help="Output markdown path")
    parser.add_argument("--include-feedback", action="store_true", default=True)
    parser.add_argument("--no-include-feedback", dest="include_feedback", action="store_false")
    args = parser.parse_args()

    results_dir = Path(args.results_dir).resolve()
    out_path = Path(args.out) if args.out else results_dir / "shinka_inspect_context.md"

    try:
        from shinka.utils import load_programs_to_df
    except ImportError:
        print("ERROR: shinka not installed. Run: uv pip install shinka-evolve", file=sys.stderr)
        return 1

    try:
        df = load_programs_to_df(str(results_dir))
    except Exception as e:
        print(f"ERROR: Failed to load programs: {e}", file=sys.stderr)
        return 1

    if df.empty:
        print("WARNING: No programs found in results directory.", file=sys.stderr)
        return 1

    if args.min_generation is not None and "generation" in df.columns:
        df = df[df["generation"] >= args.min_generation]

    correct_df = df[df["correct"] == True] if "correct" in df.columns else df  # noqa: E712
    source_df = correct_df if not correct_df.empty else df
    fallback = correct_df.empty

    if "combined_score" in source_df.columns:
        source_df = source_df.sort_values("combined_score", ascending=False)

    top_k = source_df.head(args.k)

    lines = ["# Shinka Inspect: Top Programs\n"]
    if fallback:
        lines.append("> **Note**: No correct programs found. Showing top by score (may include failures).\n")

    lines.append(f"**Results**: `{results_dir}`  ")
    lines.append(f"**Programs shown**: {len(top_k)} of {len(df)}\n")

    lines.append("## Ranking\n")
    lines.append("| Rank | Generation | Score | Correct |")
    lines.append("|------|-----------|-------|---------|")

    for i, (_, row) in enumerate(top_k.iterrows(), 1):
        gen = row.get("generation", "?")
        score = row.get("combined_score", "?")
        correct = row.get("correct", "?")
        lines.append(f"| {i} | {gen} | {score} | {correct} |")

    lines.append("")

    for i, (_, row) in enumerate(top_k.iterrows(), 1):
        lines.append(f"## Program #{i}\n")
        score = row.get("combined_score", "?")
        gen = row.get("generation", "?")
        lines.append(f"**Score**: {score} | **Generation**: {gen}\n")

        if args.include_feedback and "text_feedback" in row and row["text_feedback"]:
            lines.append(f"**Feedback**: {str(row['text_feedback'])[:500]}\n")

        code = str(row.get("code", ""))
        if len(code) > args.max_code_chars:
            code = code[: args.max_code_chars] + "\n# ... truncated ..."
        lines.append(f"```python\n{code}\n```\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Context bundle written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
