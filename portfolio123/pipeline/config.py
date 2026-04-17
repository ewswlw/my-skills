"""Environment, paths, and constants for the P123 ML pipeline."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Skill root: .../portfolio123 — credentials only from this folder’s `.env`
SKILL_ROOT = Path(__file__).resolve().parents[1]
_ENV_PATH = SKILL_ROOT / ".env"
load_dotenv(_ENV_PATH, encoding="utf-8")

P123_API_ID: str | None = os.environ.get("P123_API_ID")
P123_API_KEY: str | None = os.environ.get("P123_API_KEY")
P123_USERNAME: str | None = os.environ.get("P123_USERNAME")
P123_PASSWORD: str | None = os.environ.get("P123_PASSWORD")

# Default vault output (Obsidian vault); override with P123_OUTPUT_DIR
def _default_output_dir() -> Path:
    env = os.environ.get("P123_OUTPUT_DIR")
    if env:
        return Path(env).expanduser().resolve()
    vault = Path(os.environ.get("OBSIDIAN_VAULT", ""))
    if not vault or not vault.is_dir():
        vault = Path.home() / "Documents" / "Obsidian Vault"
    out = vault / "p123-output"
    out.mkdir(parents=True, exist_ok=True)
    return out


OUTPUT_DIR: Path = _default_output_dir()

# Discovery memory JSONL (under pipeline package dir)
MEMORY_PATH: Path = Path(
    os.environ.get("P123_MEMORY_PATH", str(Path(__file__).resolve().parent / "discovery_memory.jsonl"))
)

# Chrome CDP CLI (skill)
_CDP_DEFAULT = Path.home() / ".claude" / "skills" / "chrome-cdp" / "scripts" / "cdp.mjs"
CDP_SCRIPT: Path = Path(os.environ.get("CDP_SCRIPT", str(_CDP_DEFAULT))).resolve()

# Vault root for optional src.data_validation imports
OBSIDIAN_VAULT_ROOT: Path | None = None
_v = os.environ.get("OBSIDIAN_VAULT")
if _v:
    OBSIDIAN_VAULT_ROOT = Path(_v).expanduser().resolve()

# --- ML / validation thresholds (ml-algo-trading + P123 skill) ---
SCREENING_T_THRESHOLD: float = 3.0
PSR_THRESHOLD: float = 0.95
DSR_THRESHOLD: float = 0.95
WALK_FORWARD_MIN_PCT: float = 0.60

# P123 defaults
DEFAULT_UNIVERSE: str = "Prussell3000"
DEFAULT_REBAL_FREQ: str = "Every 4 Weeks"
DEFAULT_BATCH_DATES: int = 50  # data_universe asOfDts per request

# Credit warnings (api-reference)
CREDIT_WARN_80_PCT: int = 8000
CREDIT_WARN_95_PCT: int = 9500
MONTHLY_CREDIT_QUOTA: int = 10000


def ensure_output_dir() -> Path:
    """Create OUTPUT_DIR if missing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
