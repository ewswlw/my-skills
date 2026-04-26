"""
Semantic chart + panel colors for YTM / Credit Investing.
Loads from tokens.json (same directory) — no third-party dependencies.
"""
from __future__ import annotations

import json
from pathlib import Path

_TOKENS = Path(__file__).with_name("tokens.json")


def _load() -> dict:
    if not _TOKENS.is_file():
        raise FileNotFoundError(
            f"tokens.json not found next to chart_palette.py: {_TOKENS}"
        )
    with _TOKENS.open(encoding="utf-8") as f:
        return json.load(f)


def get_tokens() -> dict:
    """Return the full token document."""
    return _load()


def get_chart_colors() -> dict[str, str]:
    """
    Flatten chart-related keys to semantic names (chart.series.1, ...).
    Map series 1-4 in order for a typical Matplotlib `axes.prop_cycler` or
    manual z-order; see ``tokens.json`` under ``chart.series``.
    """
    t = _load()
    c = t.get("chart", {})
    s = c.get("series", {})
    out: dict[str, str] = {
        "chart.panel": str(c.get("panel", "")),
        "chart.grid": str(c.get("grid", "")),
        "chart.axis": str(c.get("axis", "")),
    }
    leg = c.get("legend", {})
    if isinstance(leg, dict):
        out["chart.legend"] = str(leg.get("color", ""))
    tick = c.get("tick", {})
    if isinstance(tick, dict):
        out["chart.tick"] = str(tick.get("color", ""))
    for i in range(1, 5):
        v = s.get(str(i))
        if v is not None:
            out[f"chart.series.{i}"] = str(v)
    tickp = c.get("tick_print", {})
    if isinstance(tickp, dict) and "color" in tickp:
        out["chart.tick_print"] = str(tickp["color"])
    return out


def series_hex_list() -> list[str]:
    """Series colors 1-4 in order (for cycler or Plotly)."""
    t = _load()
    s = t.get("chart", {}).get("series", {})
    return [str(s[str(i)]) for i in range(1, 5) if str(i) in s]


CHART: dict[str, str] = get_chart_colors()

__all__ = ["get_tokens", "get_chart_colors", "series_hex_list", "CHART", "_TOKENS"]
