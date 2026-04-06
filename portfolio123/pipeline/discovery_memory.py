"""JSONL discovery log, search policy, DNA fingerprinting."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from . import config

MEMORY_PATH: Path = config.MEMORY_PATH

KNOWN_FAMILIES = [
    "momentum",
    "mean_reversion",
    "volatility",
    "carry",
    "liquidity",
    "sentiment",
    "flow",
    "structural",
    "cross_asset",
    "yield_curve",
]


def log_discovery(
    hypothesis: str,
    factor_expression: str,
    reasoning_trace: dict[str, Any],
    screening_result: dict[str, Any],
    oos_result: dict[str, Any] | None = None,
    failure_mode: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Append one discovery record to JSONL."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "hypothesis": hypothesis,
        "factor_expression": factor_expression,
        "reasoning_trace": reasoning_trace,
        "screening": {
            "t_stat": screening_result.get("t_stat"),
            "ic": screening_result.get("ic"),
            "passed": screening_result.get("passed", False),
        },
        "oos": oos_result,
        "failure_mode": failure_mode,
        "tags": tags or [],
        "status": "passed"
        if (oos_result and oos_result.get("sharpe", 0) > 0)
        else "failed",
    }
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_memory() -> list[dict[str, Any]]:
    """Load all discovery records."""
    if not MEMORY_PATH.exists():
        return []
    records: list[dict[str, Any]] = []
    with open(MEMORY_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def suggest_next_action(
    memory: list[dict[str, Any]] | None = None,
    max_exploit_streak: int = 3,
) -> dict[str, Any]:
    """Explore vs exploit suggestion from discovery memory."""
    memory = memory if memory is not None else load_memory()
    if not memory:
        return {"action": "explore", "reason": "empty memory", "candidates": []}

    recent = memory[-max_exploit_streak:]
    recent_tags = [set(r.get("tags", [])) for r in recent]

    if len(recent) >= max_exploit_streak:
        common_tags = recent_tags[0].copy()
        for tags in recent_tags[1:]:
            common_tags &= tags
        if common_tags:
            return {
                "action": "explore",
                "reason": f"last {max_exploit_streak} cycles share tag family {common_tags}",
                "candidates": _suggest_unexplored_families(memory),
            }

    near_misses = [
        r
        for r in memory
        if not r.get("screening", {}).get("passed")
        and r.get("screening", {}).get("t_stat") is not None
        and abs(r["screening"]["t_stat"]) > 2.0
    ]
    if near_misses:
        return {
            "action": "exploit",
            "reason": f"{len(near_misses)} near-miss factors",
            "candidates": near_misses[-3:],
        }

    recent_5 = memory[-5:]
    if len(recent_5) >= 5 and all(r.get("status") == "failed" for r in recent_5):
        return {
            "action": "explore",
            "reason": "last 5 discoveries failed",
            "candidates": [],
        }

    return {"action": "explore", "reason": "default", "candidates": []}


def _suggest_unexplored_families(memory: list[dict[str, Any]]) -> list[str]:
    all_tags: set[str] = set()
    for r in memory:
        all_tags.update(r.get("tags", []))
    return [f for f in KNOWN_FAMILIES if f not in all_tags]


def compute_search_priors(memory: list[dict[str, Any]] | None = None) -> dict[str, float]:
    """Tag family success rates."""
    memory = memory if memory is not None else load_memory()
    success: dict[str, list[bool]] = {f: [] for f in KNOWN_FAMILIES}
    for r in memory:
        passed = r.get("screening", {}).get("passed", False)
        for t in r.get("tags", []):
            if t in success:
                success[t].append(bool(passed))
    return {
        k: (sum(v) / len(v) if v else 0.0) for k, v in success.items()
    }


def log_dna_fingerprint(
    ranking_config: list[str],
    universe: str,
    metrics: dict[str, Any],
    rebal_freq: str = "Every 4 Weeks",
    positions: int = 20,
) -> dict[str, Any]:
    """Strategy DNA record (learnings.md schema)."""
    dna = {
        "dna_id": f"DNA-{datetime.now().strftime('%Y%m%d')}-{len(load_memory()):03d}",
        "ranking_config": ranking_config,
        "universe": universe,
        "rebal_freq": rebal_freq,
        "positions": positions,
        "sharpe": metrics.get("sharpe"),
        "annualized_return": metrics.get("annualized_return"),
        "max_drawdown": metrics.get("max_drawdown"),
        "regime_notes": metrics.get("regime_notes"),
    }
    log_discovery(
        hypothesis="DNA fingerprint",
        factor_expression=str(ranking_config),
        reasoning_trace={},
        screening_result={"t_stat": 0, "ic": 0, "passed": True},
        oos_result=metrics,
        tags=["dna"],
    )
    return dna
