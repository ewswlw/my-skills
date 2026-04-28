"""
Semantic chart, brand, and logo helpers for YTM / Credit Investing.
Loads from tokens.json (same directory) — no third-party dependencies.
"""
from __future__ import annotations

import json
from pathlib import Path

_TOKENS = Path(__file__).with_name("tokens.json")
_ASSETS = (_TOKENS.parent.parent / "assets").resolve()


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
        "chart.panel_alt": str(c.get("panel_alt", "")),
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
    accent = c.get("accent", {})
    if isinstance(accent, dict):
        for k, v in accent.items():
            out[f"chart.accent.{k}"] = str(v)
    return out


def series_hex_list() -> list[str]:
    """Series colors 1-4 in order (for cycler or Plotly)."""
    t = _load()
    s = t.get("chart", {}).get("series", {})
    return [str(s[str(i)]) for i in range(1, 5) if str(i) in s]


def get_brand_colors() -> dict[str, str]:
    """
    Return the YTM brand palette (navy stack, blue, gold, divider) and the
    accent-line roles used by KPI cards and section headers (DESIGN.md §6.3).
    Keys are flat semantic names: 'brand.navy', 'brand.gold',
    'accent.line_primary', 'surface.default', etc.
    """
    t = _load()
    color = t.get("color", {})
    out: dict[str, str] = {}
    for group in ("brand", "accent", "surface", "text"):
        sub = color.get(group, {})
        if isinstance(sub, dict):
            for k, v in sub.items():
                out[f"{group}.{k}"] = str(v)
    return out


def get_logo_assets() -> dict[str, object]:
    """
    Return resolved logo paths and the sizing rules from ``tokens.json``.
    Paths are absolute and point at files shipped under ``../assets/``.
    """
    t = _load()
    logo = t.get("logo", {})
    horiz_name = str(logo.get("preferred_horizontal", "ytm_logo_horizontal.png"))
    icon_name = str(logo.get("preferred_icon", "ytm_icon_192.png"))
    return {
        "horizontal_path": _ASSETS / horiz_name,
        "icon_path": _ASSETS / icon_name,
        "horizontal_full_path": _ASSETS / "ytm_logo_horizontal_full.png",
        "icon_full_path": _ASSETS / "ytm_icon_full.png",
        "min_height_px": int(logo.get("min_height_px", 28)),
        "default_dashboard_height_px": int(
            logo.get("default_dashboard_height_px", 40)
        ),
        "placement_default": str(logo.get("placement_default", "top-left")),
        "assets_dir": _ASSETS,
    }


CHART: dict[str, str] = get_chart_colors()
BRAND: dict[str, str] = get_brand_colors()

__all__ = [
    "get_tokens",
    "get_chart_colors",
    "series_hex_list",
    "get_brand_colors",
    "get_logo_assets",
    "CHART",
    "BRAND",
    "_TOKENS",
    "_ASSETS",
]
