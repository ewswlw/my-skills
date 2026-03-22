"""Integration-style check: valid PROGRAM.md + files on disk passes validation."""

from __future__ import annotations

from pathlib import Path

from validate_program import parse_program_md, validate_config


def test_mini_project_passes_validation(tmp_path: Path) -> None:
    (tmp_path / "bench.py").write_text(
        'print("score: 10.0")\n', encoding="utf-8"
    )
    prog = tmp_path / "PROGRAM.md"
    prog.write_text(
        """---
goal: "Lower score"
editable_files:
  - bench.py
run_command: "python bench.py"
metric_name: score
metric_direction: lower
metric_source: stdout_pattern
metric_pattern: 'score:\\s*([\\d.]+)'
min_delta: 0.01
max_experiments: 3
---
""",
        encoding="utf-8",
    )
    cfg = parse_program_md(prog)
    errs = validate_config(cfg, tmp_path)
    assert errs == [], errs
