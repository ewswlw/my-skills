"""Tests for scripts/validate_program.py (PROGRAM.md parsing and metric helpers)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from validate_program import (
    extract_metric_file,
    extract_metric_stdout,
    parse_program_md,
    validate_config,
)


def test_parse_program_md_ok(tmp_path: Path) -> None:
    p = tmp_path / "PROGRAM.md"
    p.write_text(
        """---
goal: "x"
editable_files:
  - a.txt
run_command: "echo"
metric_name: m
metric_direction: lower
metric_source: stdout_pattern
metric_pattern: 'm:\\s*([\\d.]+)'
---
Body here.
""",
        encoding="utf-8",
    )
    (tmp_path / "a.txt").write_text("hi", encoding="utf-8")
    cfg = parse_program_md(p)
    assert cfg["goal"] == "x"
    assert cfg["editable_files"] == ["a.txt"]
    assert "Body here." in cfg["_body"]


def test_validate_config_missing_key(tmp_path: Path) -> None:
    cfg = {"goal": "g"}
    errs = validate_config(cfg, tmp_path)
    assert any("required field" in e for e in errs)


def test_validate_config_editable_missing_file(tmp_path: Path) -> None:
    cfg = {
        "goal": "g",
        "editable_files": ["nope.txt"],
        "run_command": "echo",
        "metric_name": "m",
        "metric_direction": "lower",
        "metric_source": "stdout_pattern",
        "metric_pattern": r"(\d+\.?\d*)",
    }
    errs = validate_config(cfg, tmp_path)
    assert any("non-existent" in e for e in errs)


def test_validate_config_stdout_ok(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("x", encoding="utf-8")
    cfg = {
        "goal": "g",
        "editable_files": ["a.txt"],
        "run_command": "echo",
        "metric_name": "m",
        "metric_direction": "higher",
        "metric_source": "stdout_pattern",
        "metric_pattern": r"score:\s*([\d.]+)",
    }
    assert validate_config(cfg, tmp_path) == []


def test_extract_metric_stdout_last_match() -> None:
    text = "noise\nval_loss: 9.0\nval_loss: 2.5\n"
    v = extract_metric_stdout(text, r"val_loss:\s*([\d.]+)")
    assert v == 2.5


def test_extract_metric_stdout_no_match() -> None:
    assert extract_metric_stdout("no", r"x:\s*([\d.]+)") is None


def test_extract_metric_file_plain(tmp_path: Path) -> None:
    p = tmp_path / "out.txt"
    p.write_text("3.14\n", encoding="utf-8")
    assert extract_metric_file(p, None) == pytest.approx(3.14)


def test_extract_metric_file_json(tmp_path: Path) -> None:
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"score": 1.25}), encoding="utf-8")
    assert extract_metric_file(p, "score") == pytest.approx(1.25)


def test_main_cli_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import validate_program as vp

    prog = tmp_path / "PROGRAM.md"
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    prog.write_text(
        """---
goal: "goal text here"
editable_files:
  - a.txt
run_command: "python -c print(1)"
metric_name: score
metric_direction: lower
metric_source: stdout_pattern
metric_pattern: "([0-9]+)"
---
""",
        encoding="utf-8",
    )
    rc = vp.main([str(prog), "--root", str(tmp_path)])
    assert rc == 0
