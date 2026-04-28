"""
YTM / Credit Investing — Matplotlib dashboard scaffold (page-level brand).

This fragment is the canonical answer to "build me a YTM dashboard". It
materializes the brand motifs documented in `references/DESIGN.md`:

  * Deep-navy page surface (`color.surface.default`, #162236).
  * Slightly lighter navy chart panels (`chart.panel`, #1c2d42).
  * Official YTM logo placed top-left via OffsetImage (no fabrication).
  * Header bar with title + gold "signature rule" under the title.
  * KPI cards with a 3 px vertical gold accent line on the leading edge.
  * Brand-blue + gold series order, Montserrat (with sensible fallbacks).

Copy this whole file into a working directory and edit the `KPI_CARDS`,
`build_charts`, and `PAGE_TITLE` blocks for your data. The helpers below
(``add_logo``, ``draw_kpi_card``, ``draw_signature_rule``) can also be
imported individually.

Run:

    uv run python matplotlib_dashboard_scaffold.py

Output: ``ytm_dashboard.png`` next to the script.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, OffsetImage
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---------------------------------------------------------------------------
# Skill bootstrap — pull tokens, brand colors, and logo paths from the skill.
# ---------------------------------------------------------------------------
SKILL_REF = Path(r"C:\Users\Eddy\.claude\skills\ytm-branding\references")
if str(SKILL_REF) not in sys.path:
    sys.path.insert(0, str(SKILL_REF))

import chart_palette as cp  # noqa: E402

CHART = cp.get_chart_colors()
BRAND = cp.get_brand_colors()
LOGO = cp.get_logo_assets()
SERIES = cp.series_hex_list()

MPLSTYLE = SKILL_REF / "fragments" / "matplotlib.mplstyle.txt"
plt.style.use(str(MPLSTYLE))

# ---------------------------------------------------------------------------
# Tunables — edit these for your specific dashboard.
# ---------------------------------------------------------------------------
PAGE_TITLE = "Credit Strategy Dashboard"
PAGE_SUBTITLE = "YTM Capital — internal review"
KPI_CARDS = [
    {"value": "+3.42%", "label": "QTD return"},
    {"value": "182 bp", "label": "OAS vs benchmark"},
    {"value": "4.8 yr", "label": "Effective duration"},
    {"value": "BBB", "label": "Avg credit quality"},
]
OUTPUT_FILE = Path(__file__).with_name("ytm_dashboard.png")


# ---------------------------------------------------------------------------
# Brand primitives (reusable).
# ---------------------------------------------------------------------------
def add_logo(
    fig: plt.Figure,
    *,
    height_px: int | None = None,
    pad_px: int = 24,
) -> None:
    """Place the official YTM horizontal logo in the top-left of ``fig``.

    Uses ``logo.preferred_horizontal`` from ``tokens.json``; honors
    ``logo.default_dashboard_height_px`` and ``logo.min_height_px``.
    """
    logo_path: Path = LOGO["horizontal_path"]  # type: ignore[assignment]
    if not logo_path.exists():
        return  # fail-soft: do not fabricate a wordmark
    h_px = int(height_px or LOGO["default_dashboard_height_px"])  # type: ignore[arg-type]
    h_px = max(h_px, int(LOGO["min_height_px"]))  # type: ignore[arg-type]

    img = mpimg.imread(str(logo_path))
    src_h = img.shape[0]
    zoom = h_px / src_h

    box = OffsetImage(img, zoom=zoom, interpolation="hanning")
    anchored = AnchoredOffsetbox(
        loc="upper left",
        child=box,
        pad=0,
        borderpad=pad_px / 72.0,  # borderpad is in fontsize units; ~px at 72 dpi
        frameon=False,
        bbox_to_anchor=(0.0, 1.0),
        bbox_transform=fig.transFigure,
    )
    fig.add_artist(anchored)


def draw_signature_rule(
    fig: plt.Figure,
    *,
    x_fig: float,
    y_fig: float,
    width_fig: float,
    color: str | None = None,
    height_px: int = 2,
) -> None:
    """Draw the gold signature rule beneath the page title (DESIGN.md §6.2)."""
    color = color or BRAND["accent.line_primary"]
    ax = fig.add_axes([x_fig, y_fig, width_fig, height_px / (fig.get_figheight() * fig.dpi)])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(color)
    ax.patch.set_alpha(1.0)


def draw_kpi_card(
    ax: plt.Axes,
    *,
    value: str,
    label: str,
    accent_color: str | None = None,
    card_color: str | None = None,
) -> None:
    """Render a single KPI tile with the YTM vertical-accent motif.

    Use one ``ax`` per KPI (e.g. via ``GridSpec`` or ``subplots(1, n)``).
    """
    accent = accent_color or BRAND["accent.line_primary"]
    card = card_color or BRAND["surface.elevated"]

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(BRAND["surface.default"])  # blend into page

    card_patch = FancyBboxPatch(
        (0.02, 0.05),
        0.96,
        0.90,
        boxstyle="round,pad=0.0,rounding_size=0.04",
        linewidth=0,
        facecolor=card,
        zorder=1,
    )
    ax.add_patch(card_patch)

    rule = Rectangle(
        (0.02, 0.05),
        0.018,
        0.90,
        facecolor=accent,
        linewidth=0,
        zorder=2,
    )
    ax.add_patch(rule)

    ax.text(
        0.10,
        0.62,
        value,
        color=BRAND["text.primary"],
        fontsize=22,
        fontweight=700,
        va="center",
        ha="left",
        zorder=3,
    )
    ax.text(
        0.10,
        0.30,
        " ".join(label.upper()),  # tracked-out feel without a letterspacing prop
        color=BRAND["text.muted"],
        fontsize=8,
        fontweight=500,
        va="center",
        ha="left",
        zorder=3,
    )


# ---------------------------------------------------------------------------
# Demo body — replace with your real charts.
# ---------------------------------------------------------------------------
def build_charts(ax_left: plt.Axes, ax_right: plt.Axes) -> None:
    import numpy as np

    rng = np.random.default_rng(42)
    n = 90
    x = np.arange(n)
    portfolio = 100 + np.cumsum(rng.normal(0.05, 0.6, n))
    benchmark = 100 + np.cumsum(rng.normal(0.03, 0.5, n))

    ax_left.plot(x, portfolio, color=SERIES[0], linewidth=2.0, label="Portfolio")
    ax_left.plot(
        x, benchmark, color=SERIES[1], linewidth=2.0, linestyle="--", label="Benchmark"
    )
    ax_left.set_title("Total return — last 90 sessions", loc="left")
    ax_left.legend(loc="upper left", frameon=False)
    ax_left.axhline(100, color=CHART["chart.accent.rule"], linewidth=1.2, alpha=0.7)

    sectors = ["Banks", "Energy", "Telco", "Utils", "Cons.", "Tech"]
    weights = [28, 18, 14, 12, 16, 12]
    bar_colors = [SERIES[0], SERIES[1], SERIES[2], SERIES[3], SERIES[0], SERIES[1]]
    ax_right.bar(sectors, weights, color=bar_colors, width=0.65)
    ax_right.set_title("Sector weight (%)", loc="left")
    ax_right.set_ylim(0, max(weights) * 1.25)


def build_dashboard() -> Path:
    fig = plt.figure(figsize=(14, 8.5), dpi=120)
    fig.set_facecolor(BRAND["surface.default"])

    # Header text + gold signature rule
    fig.text(
        0.30,
        0.945,
        PAGE_TITLE,
        color=BRAND["text.primary"],
        fontsize=18,
        fontweight=700,
        ha="left",
        va="center",
    )
    fig.text(
        0.30,
        0.910,
        PAGE_SUBTITLE,
        color=BRAND["text.muted"],
        fontsize=10,
        fontweight=500,
        ha="left",
        va="center",
    )
    draw_signature_rule(fig, x_fig=0.30, y_fig=0.890, width_fig=0.10)

    add_logo(fig)

    # KPI strip (top of body)
    n_kpi = len(KPI_CARDS)
    kpi_axes = fig.subplots(
        1,
        n_kpi,
        gridspec_kw={
            "left": 0.04,
            "right": 0.97,
            "top": 0.84,
            "bottom": 0.66,
            "wspace": 0.08,
        },
    )
    if n_kpi == 1:
        kpi_axes = [kpi_axes]
    for ax, kpi in zip(kpi_axes, KPI_CARDS):
        draw_kpi_card(ax, value=kpi["value"], label=kpi["label"])

    # Chart row
    ax_left = fig.add_axes([0.04, 0.10, 0.55, 0.48])
    ax_right = fig.add_axes([0.66, 0.10, 0.31, 0.48])
    for ax in (ax_left, ax_right):
        ax.set_facecolor(CHART["chart.panel"])
    build_charts(ax_left, ax_right)

    fig.savefig(
        OUTPUT_FILE,
        dpi=140,
        facecolor=fig.get_facecolor(),
        bbox_inches=None,
    )
    plt.close(fig)
    return OUTPUT_FILE


if __name__ == "__main__":
    out = build_dashboard()
    print(f"Wrote {out}")
