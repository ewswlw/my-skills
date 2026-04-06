"""Discovery memory JSONL."""

import json
from pathlib import Path

import pipeline.discovery_memory as dm
from pipeline.discovery_memory import log_discovery, load_memory, suggest_next_action


def test_log_and_load_roundtrip(tmp_path: Path, monkeypatch) -> None:
    mp = tmp_path / "m.jsonl"
    monkeypatch.setattr(dm, "MEMORY_PATH", mp)
    rec = log_discovery(
        hypothesis="h",
        factor_expression="x",
        reasoning_trace={},
        screening_result={"t_stat": 4.0, "ic": 0.1, "passed": True},
        tags=["momentum"],
    )
    assert mp.is_file()
    loaded = load_memory()
    assert len(loaded) == 1
    assert loaded[0]["hypothesis"] == "h"


def test_suggest_explore_empty() -> None:
    s = suggest_next_action([])
    assert s["action"] == "explore"
