"""Config path resolution."""

from pathlib import Path

import pipeline.config as cfg


def test_skill_root_exists() -> None:
    assert cfg.SKILL_ROOT.is_dir()


def test_output_dir_is_path() -> None:
    assert isinstance(cfg.OUTPUT_DIR, Path)


def test_constants() -> None:
    assert cfg.SCREENING_T_THRESHOLD == 3.0
    assert cfg.PSR_THRESHOLD == 0.95
