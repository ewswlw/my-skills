"""
Validate PROGRAM.md for the auto-researcher skill.

Parse YAML frontmatter, check required keys, and extract metrics (stdout / file).
Used by tests and optionally run manually: ``uv run python scripts/validate_program.py path/to/PROGRAM.md``.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


REQUIRED_KEYS = frozenset(
    {
        "goal",
        "editable_files",
        "run_command",
        "metric_name",
        "metric_direction",
        "metric_source",
    }
)


def parse_program_md(path: Path) -> dict[str, Any]:
    """Load PROGRAM.md; return frontmatter dict + body text under key ``_body``."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip().startswith("---"):
        raise ValueError("PROGRAM.md must start with YAML frontmatter (---).")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("PROGRAM.md frontmatter not closed (missing second ---).")
    if yaml is None:
        raise RuntimeError("PyYAML is required: pip install pyyaml or uv sync.")
    front = yaml.safe_load(parts[1]) or {}
    if not isinstance(front, dict):
        raise ValueError("PROGRAM.md frontmatter must be a YAML mapping.")
    body = parts[2].lstrip("\n")
    out = dict(front)
    out["_body"] = body
    return out


def validate_config(cfg: dict[str, Any], project_root: Path) -> list[str]:
    """Return a list of human-readable errors; empty if valid."""
    errors: list[str] = []
    for key in REQUIRED_KEYS:
        if key not in cfg or cfg[key] in (None, "", []):
            errors.append(f"missing or empty required field: {key}")

    if errors:
        return errors

    direction = cfg.get("metric_direction")
    if direction not in ("higher", "lower"):
        errors.append('metric_direction must be "higher" or "lower".')

    source = cfg.get("metric_source")
    if source not in ("stdout_pattern", "results_file", "eval_command"):
        errors.append(
            "metric_source must be stdout_pattern, results_file, or eval_command."
        )

    files = cfg.get("editable_files")
    if not isinstance(files, list) or not files:
        errors.append("editable_files must be a non-empty list of paths.")
    elif isinstance(files, list):
        for f in files:
            if not isinstance(f, str) or not f.strip():
                errors.append("each editable_files entry must be a non-empty string.")
                break
            p = project_root / f
            if not p.is_file():
                errors.append(f"editable_files references non-existent file: {f}")

    if source == "stdout_pattern":
        pat = cfg.get("metric_pattern")
        if not pat or not isinstance(pat, str):
            errors.append("metric_pattern is required when metric_source is stdout_pattern.")
        else:
            try:
                rx = re.compile(pat)
            except re.error as e:
                errors.append(f"metric_pattern is not a valid regex: {e}")
            else:
                if rx.groups < 1:
                    errors.append("metric_pattern must contain at least one capture group.")

    if source == "results_file":
        mf = cfg.get("metric_file")
        if not mf or not isinstance(mf, str):
            errors.append("metric_file is required when metric_source is results_file.")

    if source == "eval_command":
        ev = cfg.get("eval_command")
        if not ev or not isinstance(ev, str):
            errors.append("eval_command is required when metric_source is eval_command.")

    for opt in ("min_delta", "max_experiments", "max_consecutive_failures", "time_budget"):
        if opt in cfg and cfg[opt] is not None:
            if not isinstance(cfg[opt], (int, float)):
                errors.append(f"{opt} must be a number if set.")

    return errors


def extract_metric_stdout(text: str, pattern: str) -> float | None:
    """
    Apply regex; last match wins. First capture group must be a float.
    Returns None if no valid finite float.
    """
    try:
        rx = re.compile(pattern)
    except re.error:
        return None
    matches = list(rx.finditer(text))
    if not matches:
        return None
    last = matches[-1]
    if not last.groups():
        return None
    try:
        val = float(last.group(1))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(val):
        return None
    return val


def extract_metric_file(path: Path, metric_key: str | None) -> float | None:
    """Read results file: JSON with optional key, or plain float string."""
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return None
    if metric_key:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict) or metric_key not in data:
            return None
        try:
            val = float(data[metric_key])
        except (TypeError, ValueError):
            return None
    else:
        try:
            val = float(raw)
        except ValueError:
            return None
    if not math.isfinite(val):
        return None
    return val


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate PROGRAM.md for auto-researcher.")
    p.add_argument(
        "program",
        type=Path,
        nargs="?",
        default=Path("PROGRAM.md"),
        help="Path to PROGRAM.md (default: ./PROGRAM.md)",
    )
    p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root for resolving editable_files (default: parent of PROGRAM.md)",
    )
    args = p.parse_args(argv)
    root = args.root or args.program.parent
    try:
        cfg = parse_program_md(args.program)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    errs = validate_config(cfg, root)
    if errs:
        print("PROGRAM.md validation failed:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: PROGRAM.md is valid.")
    print(f"  goal: {cfg.get('goal', '')[:80]}...")
    print(f"  metric: {cfg.get('metric_name')} ({cfg.get('metric_direction')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
