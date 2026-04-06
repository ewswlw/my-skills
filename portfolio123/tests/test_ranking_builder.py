"""Ranking XML."""

import pytest

from pipeline.ranking_builder import build_ranking_xml, validate_xml


def test_build_ranking_xml() -> None:
    xml = build_ranking_xml(
        [
            {
                "name": "pe",
                "formula": "PEExclXorTTM",
                "weight": 50,
                "lower_is_better": True,
                "label": "agent_pe",
            },
            {
                "name": "mom",
                "formula": "Momentum(126)",
                "weight": 50,
                "lower_is_better": False,
                "label": "agent_mom",
            },
        ],
        composite_label="agent_test_combo",
    )
    assert "agent_" in xml
    assert "PEExclXorTTM" in xml
    validate_xml(xml)


def test_validate_xml_rejects_bad_label() -> None:
    bad = """
<RankingSystem RankType="Higher">
  <Composite Name="agent_x" Weight="100" Label="agent_x" RankType="Higher">
    <StockFormula Name="a" RankType="Higher" Scope="Universe" Weight="100" Label="bad">
      <Formula>Momentum(20)</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
"""
    with pytest.raises(ValueError, match="agent_"):
        validate_xml(bad)
