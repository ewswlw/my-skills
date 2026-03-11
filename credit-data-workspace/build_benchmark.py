"""Build benchmark.json from grading.json files, handling UTF-8 BOM."""
import json
import math
from pathlib import Path
from datetime import datetime, timezone

base = Path(r"C:\Users\Eddy\.claude\skills\credit-data-workspace\iteration-1")


def read_json(path):
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return json.loads(raw.decode("utf-8"))


def stats(vals):
    n = len(vals)
    if n == 0:
        return {"mean": 0, "stddev": 0, "min": 0, "max": 0}
    mean = sum(vals) / n
    stddev = math.sqrt(sum((x - mean) ** 2 for x in vals) / (n - 1)) if n > 1 else 0
    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
    }


evals = [
    ("eval-1-cad-ig-context", 1),
    ("eval-2-er-index-weekly", 2),
    ("eval-3-cad-sectors", 3),
]

runs = []
for eval_name, eval_id in evals:
    for cfg in ("with_skill", "without_skill"):
        gf = base / eval_name / cfg / "grading.json"
        g = read_json(gf)
        pr = g["summary"]["pass_rate"]
        passed = g["summary"]["passed"]
        total = g["summary"]["total"]
        print(f"{eval_name} {cfg}: {pr} ({passed}/{total})")
        name = eval_name.replace(f"eval-{eval_id}-", "")
        runs.append({
            "eval_id": eval_id,
            "eval_name": name,
            "configuration": cfg,
            "run_number": 1,
            "result": {
                "pass_rate": pr,
                "passed": passed,
                "failed": total - passed,
                "total": total,
                "time_seconds": 0,
                "tokens": 0,
                "errors": 0,
            },
            "expectations": g.get("expectations", []),
            "notes": [],
        })

ws_rates = [r["result"]["pass_rate"] for r in runs if r["configuration"] == "with_skill"]
ns_rates = [r["result"]["pass_rate"] for r in runs if r["configuration"] == "without_skill"]
ws_stats = stats(ws_rates)
ns_stats = stats(ns_rates)
delta = round(ws_stats["mean"] - ns_stats["mean"], 4)

benchmark = {
    "metadata": {
        "skill_name": "credit-data",
        "skill_path": r"C:\Users\Eddy\.claude\skills\credit-data",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evals_run": [1, 2, 3],
        "runs_per_configuration": 1,
    },
    "runs": runs,
    "run_summary": {
        "with_skill": {
            "pass_rate": ws_stats,
            "time_seconds": {"mean": 0, "stddev": 0, "min": 0, "max": 0},
            "tokens": {"mean": 0, "stddev": 0, "min": 0, "max": 0},
        },
        "without_skill": {
            "pass_rate": ns_stats,
            "time_seconds": {"mean": 0, "stddev": 0, "min": 0, "max": 0},
            "tokens": {"mean": 0, "stddev": 0, "min": 0, "max": 0},
        },
        "delta": {
            "pass_rate": f"+{delta}",
            "time_seconds": "0",
            "tokens": "0",
        },
    },
    "notes": [
        "with_skill 93.3% vs without_skill 73.3% — +20pp improvement across 3 evals",
        "Eval 2 (ER index weekly): with_skill 100% — single fetch() call, auto YTD→index, correct tickers. Baseline used wrong tickers (LUACEXUU vs LUACTRUU/LF98TRUU).",
        "Eval 3 (CAD sectors): with_skill 100% — single fetch(), correct INDEX_OAS_TSY_BP. Baseline used wrong field (OAS_SPREAD) and uncertain BAML tickers.",
        "Eval 1 (CAD IG context): with_skill 80% — CreditData+context() used correctly. Both configs missed uv run python execution command — assertion is weak.",
        "IMPROVEMENT TARGET: Add regime label (TIGHT/FAIR/WIDE/DISTRESSED) assertion to Eval 1.",
        "IMPROVEMENT TARGET: Replace uv run assertion with a more discriminating check (e.g. CreditData class usage).",
    ],
}

out = base / "benchmark.json"
out.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nWrote {out}")
print(f"with_skill mean: {ws_stats['mean']}  |  without_skill mean: {ns_stats['mean']}  |  delta: +{delta}")
