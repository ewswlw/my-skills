"""
Validate RUBRIC.md for the grading-rubric skill.

Parses YAML frontmatter and runs structural checks. Exits 0 on valid, 1 if any
check fails. All failures are printed to stderr in one pass — the validator
never short-circuits on the first error.

Used by the skill's Stage C self-validation step, by anchor-rubric definition-of-done
in U3, and may be invoked manually:

    uv run python scripts/validate_rubric.py path/to/RUBRIC.md
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


REQUIRED_TOP_LEVEL = (
    "rubric_name",
    "domain_confidence",
    "composite_formula",
    "composite_direction",
    "trip_wire_enabled",
    "iso_generated_at",
    "criteria",
)

REQUIRED_CRITERION_FIELDS = (
    "name",
    "definition",
    "what_9_of_10_looks_like",
    "weight",
    "threshold",
    "gameability_note",
)

VALID_TRIP_WIRE_CHECKS = {
    "empty_output",
    "nan_or_error",
    "runtime_exceeded",
    "structure_invalid",
}

WEIGHT_SUM_TOLERANCE = 0.001
TRIP_WIRE_NAME = "regression_trip_wire"


def parse_rubric_md(path: Path) -> dict[str, Any]:
    """Load RUBRIC.md and return its YAML frontmatter as a dict.

    The body after the closing `---` is preserved under the `_body` key for
    callers that want to render or inspect the human-readable section, but
    validation operates only on the YAML frontmatter (single source of truth).
    """
    # `utf-8-sig` transparently strips a leading BOM if one is present (common
    # when the file was authored in an editor that defaults to UTF-8-with-BOM,
    # e.g., Windows PowerShell `Set-Content -Encoding utf8`). Without this, a
    # BOM character lands before the `---` and the frontmatter check fails for
    # files that are otherwise perfectly valid.
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if not text.lstrip().startswith("---"):
        raise ValueError("RUBRIC.md must start with YAML frontmatter (---).")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("RUBRIC.md frontmatter not closed (missing second ---).")
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required: install with `uv sync` from the grading-rubric/ folder."
        )
    front = yaml.safe_load(parts[1]) or {}
    if not isinstance(front, dict):
        raise ValueError("RUBRIC.md frontmatter must be a YAML mapping.")
    out = dict(front)
    out["_body"] = parts[2].lstrip("\n")
    return out


def _is_in_unit_interval(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0.0 <= float(x) <= 1.0


def _validate_criterion(c: Any, idx: int) -> list[str]:
    """Per-criterion field checks. Returns a list of error strings."""
    errs: list[str] = []
    label = f"criteria[{idx}]"
    if not isinstance(c, dict):
        return [f"{label}: each criterion must be a YAML mapping."]
    name = c.get("name")
    if isinstance(name, str) and name.strip():
        label = f"criteria[{idx}] '{name}'"
    for field in REQUIRED_CRITERION_FIELDS:
        if field not in c:
            errs.append(f"{label}: missing required field '{field}'.")
            continue
        val = c[field]
        if field in ("weight", "threshold"):
            if not _is_in_unit_interval(val):
                errs.append(f"{label}: '{field}' must be a number in [0, 1] (got {val!r}).")
        elif field in ("definition", "what_9_of_10_looks_like", "gameability_note", "name"):
            if not isinstance(val, str) or not val.strip():
                errs.append(f"{label}: '{field}' must be a non-empty string.")
    if "hard_gate" in c and not isinstance(c["hard_gate"], bool):
        errs.append(f"{label}: 'hard_gate' must be a boolean if present.")
    if c.get("hard_gate") is True and c.get("name") != TRIP_WIRE_NAME:
        # Non-trip-wire hard gates need a documented fail reason.
        fr = c.get("fail_reason")
        if not isinstance(fr, str) or not fr.strip():
            errs.append(
                f"{label}: 'hard_gate: true' requires a non-empty 'fail_reason' "
                "field documenting what failure means."
            )
    return errs


def _validate_trip_wire(criteria: list[dict], trip_wire_enabled: bool) -> list[str]:
    """Trip-wire presence and structure checks."""
    errs: list[str] = []
    trip_wires = [c for c in criteria if isinstance(c, dict) and c.get("name") == TRIP_WIRE_NAME]
    if trip_wire_enabled:
        if not trip_wires:
            errs.append(
                f"trip_wire_enabled is true but no '{TRIP_WIRE_NAME}' criterion is present."
            )
            return errs
        if len(trip_wires) > 1:
            errs.append(f"more than one '{TRIP_WIRE_NAME}' criterion defined; only one allowed.")
        tw = trip_wires[0]
        if tw.get("weight") != 0:
            errs.append(f"'{TRIP_WIRE_NAME}': weight must be 0 (got {tw.get('weight')!r}).")
        if tw.get("hard_gate") is not True:
            errs.append(f"'{TRIP_WIRE_NAME}': hard_gate must be true.")
        checks = tw.get("checks")
        if not isinstance(checks, list) or not checks:
            errs.append(
                f"'{TRIP_WIRE_NAME}': 'checks' must be a non-empty list (subset of "
                f"{sorted(VALID_TRIP_WIRE_CHECKS)})."
            )
        else:
            unknown = [c for c in checks if c not in VALID_TRIP_WIRE_CHECKS]
            if unknown:
                errs.append(
                    f"'{TRIP_WIRE_NAME}': unknown check(s) {unknown}; valid checks are "
                    f"{sorted(VALID_TRIP_WIRE_CHECKS)}."
                )
    # If trip_wire_enabled is false, presence is allowed but ignored — no check.
    return errs


def validate_rubric(cfg: dict[str, Any]) -> list[str]:
    """Return a list of human-readable errors; empty if valid."""
    errors: list[str] = []

    # 1. Required top-level fields.
    for key in REQUIRED_TOP_LEVEL:
        if key not in cfg:
            errors.append(f"missing required top-level field: '{key}'.")

    # Bail early only on absence of the criteria array — without it, per-criterion
    # checks have no meaningful work to do.
    criteria = cfg.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        if "criteria" in cfg:
            errors.append("'criteria' must be a non-empty list.")
        return errors

    # 2. Top-level value checks (only run when the field is present so we don't
    # double-report missing fields).
    if "domain_confidence" in cfg and cfg["domain_confidence"] not in ("high", "medium", "low"):
        errors.append(
            f"domain_confidence must be one of high|medium|low (got {cfg['domain_confidence']!r})."
        )
    if "composite_direction" in cfg and cfg["composite_direction"] != "higher":
        errors.append(
            f"composite_direction must be 'higher' (got {cfg['composite_direction']!r}). "
            "The grading-rubric skill enforces a single composite direction so /auto researcher's "
            "metric_direction is unambiguous."
        )
    if "trip_wire_enabled" in cfg and not isinstance(cfg["trip_wire_enabled"], bool):
        errors.append("trip_wire_enabled must be a boolean.")
    if "iso_generated_at" in cfg:
        ts = cfg["iso_generated_at"]
        # YAML auto-parses ISO 8601 to datetime; accept either str or datetime here.
        if not isinstance(ts, (str, datetime)):
            errors.append("iso_generated_at must be an ISO 8601 string or YAML datetime.")
        elif isinstance(ts, str):
            try:
                datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"iso_generated_at is not a valid ISO 8601 string (got {ts!r}).")

    # 3. Per-criterion checks.
    for idx, c in enumerate(criteria):
        errors.extend(_validate_criterion(c, idx))

    # 4. Duplicate name check.
    names = [c.get("name") for c in criteria if isinstance(c, dict)]
    seen: set[str] = set()
    dups: list[str] = []
    for n in names:
        if not isinstance(n, str):
            continue
        if n in seen and n not in dups:
            dups.append(n)
        seen.add(n)
    for d in dups:
        errors.append(f"duplicate criterion name: '{d}'.")

    # 5. Weight-sum check across non-hard-gate, non-trip-wire criteria.
    weighted = [
        c
        for c in criteria
        if isinstance(c, dict)
        and not c.get("hard_gate", False)
        and c.get("name") != TRIP_WIRE_NAME
        and isinstance(c.get("weight"), (int, float))
        and not isinstance(c.get("weight"), bool)
    ]
    if weighted:
        total = sum(float(c["weight"]) for c in weighted)
        if abs(total - 1.0) > WEIGHT_SUM_TOLERANCE:
            errors.append(
                f"weights of non-hard-gate criteria sum to {total:.4f}, expected 1.0 "
                f"(±{WEIGHT_SUM_TOLERANCE}). Adjust the weights so they sum to 1.0."
            )

    # 6. Trip-wire structural checks.
    if "trip_wire_enabled" in cfg and isinstance(cfg["trip_wire_enabled"], bool):
        errors.extend(_validate_trip_wire(criteria, cfg["trip_wire_enabled"]))

    return errors


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate RUBRIC.md for grading-rubric.")
    p.add_argument(
        "rubric",
        type=Path,
        nargs="?",
        default=Path("RUBRIC.md"),
        help="Path to RUBRIC.md (default: ./RUBRIC.md)",
    )
    args = p.parse_args(argv)

    try:
        cfg = parse_rubric_md(args.rubric)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    errs = validate_rubric(cfg)
    if errs:
        print(f"RUBRIC.md validation failed ({len(errs)} error(s)):", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_criteria = len(cfg.get("criteria", []))
    print(f"OK: RUBRIC.md is valid ({n_criteria} criteria, "
          f"domain_confidence={cfg.get('domain_confidence')}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
