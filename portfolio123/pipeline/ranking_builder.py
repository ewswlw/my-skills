"""P123 ranking system XML construction and validation."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any
from uuid import uuid4


def build_ranking_xml(
    factors: list[dict[str, Any]],
    composite_label: str | None = None,
) -> str:
    """
    Build RankingSystem XML from factor specs.

    Each factor dict: name, formula, weight (int), lower_is_better (bool), label (optional).
    """
    total_w = sum(int(f["weight"]) for f in factors)
    if total_w != 100:
        raise ValueError(f"Weights must sum to 100, got {total_w}")

    root_name = composite_label or f"agent_composite_{uuid4().hex[:8]}"
    if not root_name.startswith("agent"):
        root_name = f"agent_{root_name}"

    parts = [
        '<RankingSystem RankType="Higher">',
        f'  <Composite Name="{_esc(root_name)}" Weight="100" '
        f'Label="{_esc(root_name)}" RankType="Higher">',
    ]
    for f in factors:
        fname = f["name"]
        direction = "Lower" if f.get("lower_is_better") else "Higher"
        w = int(f["weight"])
        lab = f.get("label", fname)
        if not str(lab).startswith("agent"):
            lab = f"agent_{lab}"
        parts.append(
            f'    <StockFormula Name="{_esc(fname)}" RankType="{direction}" '
            f'Scope="Universe" Weight="{w}" Label="{_esc(lab)}">'
        )
        parts.append(f"      <Formula>{f['formula']}</Formula>")
        parts.append("    </StockFormula>")
    parts.append("  </Composite>")
    parts.append("</RankingSystem>")
    xml = "\n".join(parts)
    validate_xml(xml)
    return xml


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def inject_stock_factor(
    xml_string: str,
    factor_name: str,
    weight: int,
    label: str | None = None,
) -> str:
    """Insert or replace a StockFormula node for FRank(StockFactor(...))."""
    formula = f'FRank(StockFactor("{factor_name}"))'
    node_name = "agent_ml_stockfactor"
    new_block = (
        f'    <StockFormula Name="{_esc(node_name)}" RankType="Higher" '
        f'Scope="Universe" Weight="{weight}" Label="{_esc(label or node_name)}">\n'
        f"      <Formula>{formula}</Formula>\n"
        "    </StockFormula>"
    )
    if "StockFactor" in xml_string and factor_name in xml_string:
        return xml_string
    # Insert before closing Composite
    idx = xml_string.rfind("</Composite>")
    if idx == -1:
        raise ValueError("Invalid XML: no </Composite>")
    return xml_string[:idx] + new_block + "\n" + xml_string[idx:]


def inject_ai_factor(
    xml_string: str,
    ai_factor_name: str,
    model_name: str,
    weight: int,
    label: str | None = None,
) -> str:
    """Insert AIFactorValidation formula node."""
    formula = f'FRank(AIFactorValidation("{ai_factor_name}", "{model_name}"))'
    node_name = "agent_ai_validation"
    new_block = (
        f'    <StockFormula Name="{_esc(node_name)}" RankType="Higher" '
        f'Scope="Universe" Weight="{weight}" Label="{_esc(label or node_name)}">\n'
        f"      <Formula>{formula}</Formula>\n"
        "    </StockFormula>"
    )
    idx = xml_string.rfind("</Composite>")
    if idx == -1:
        raise ValueError("Invalid XML: no </Composite>")
    return xml_string[:idx] + new_block + "\n" + xml_string[idx:]


def validate_xml(xml_string: str) -> None:
    """Ranking-templates checklist: parse XML, weights, agent_ prefix on labels."""
    try:
        ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {e}") from e

    weights = [int(x) for x in re.findall(r'Weight="(\d+)"', xml_string)]
    if weights and sum(weights) != 100:
        # Allow multiple composites — then sum may not be 100 on whole doc
        # Single-composite template: top composite Weight="100" and children sum 100
        composites = re.findall(r"<Composite[^>]*Weight=\"(\d+)\"", xml_string)
        if len(composites) == 1 and composites[0] == "100":
            stock_weights = re.findall(r"<StockFormula[^>]*Weight=\"(\d+)\"", xml_string)
            if stock_weights and sum(int(w) for w in stock_weights) != 100:
                raise ValueError("StockFormula weights must sum to 100")

    if "Label=" in xml_string:
        labs = re.findall(r'Label="([^"]*)"', xml_string)
        for lab in labs:
            if lab and not lab.startswith("agent"):
                raise ValueError(f"Label must start with agent_: {lab}")
