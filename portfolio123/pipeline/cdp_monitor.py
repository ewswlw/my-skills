"""Subprocess wrappers for chrome-cdp ``cdp.mjs`` — list, eval, screenshots, polling."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import pandas as pd

from . import config


def cdp_cmd(*args: str, timeout: float = 120.0) -> str:
    """Run ``node cdp.mjs <args>``; return stdout text."""
    script = config.CDP_SCRIPT
    if not script.is_file():
        raise FileNotFoundError(
            f"CDP script not found: {script}. Set CDP_SCRIPT or install chrome-cdp skill."
        )
    cmd = ["node", str(script), *args]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"cdp failed ({proc.returncode}): {proc.stderr or proc.stdout}"
        )
    return proc.stdout


def list_tabs() -> list[dict[str, str]]:
    """Parse ``cdp list`` output into {targetId, title, url} rows (best-effort)."""
    out = cdp_cmd("list", timeout=30.0)
    rows: list[dict[str, str]] = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Typical: TARGETPREFIX  Title  url...
        parts = re.split(r"\s{2,}|\t", line, maxsplit=2)
        if len(parts) >= 2:
            tid = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else ""
            url = parts[2].strip() if len(parts) > 2 else ""
            if len(tid) >= 8:
                rows.append({"targetId": tid, "title": title, "url": url})
    return rows


def find_p123_tab() -> str | None:
    """Return targetId prefix for first portfolio123.com tab."""
    for row in list_tabs():
        if "portfolio123.com" in row.get("url", "").lower():
            return row["targetId"][:12]
    return None


def extract_page_data(target_prefix: str, js_expr: str) -> Any:
    """Run ``cdp eval`` with a JS expression; try to parse JSON from stdout."""
    out = cdp_cmd("eval", target_prefix, js_expr, timeout=60.0)
    out = out.strip()
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{") or line.startswith("["):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return out


def screenshot_page(target_prefix: str, filename: str | None = None) -> Path:
    """Viewport screenshot to OUTPUT_DIR."""
    config.ensure_output_dir()
    name = filename or f"p123_shot_{target_prefix[:8]}.png"
    path = config.OUTPUT_DIR / name
    cdp_cmd("shot", target_prefix, str(path), timeout=60.0)
    return path


def poll_ai_factor_training(
    target_prefix: str,
    interval_sec: float = 60.0,
    max_wait_min: float = 120.0,
    complete_substrings: tuple[str, ...] = ("complete", "Complete", "finished", "Done"),
) -> bool:
    """Poll document body text until a completion substring appears or timeout."""
    deadline = time.time() + max_wait_min * 60.0
    js = "document.body ? document.body.innerText.slice(0,50000) : ''"
    while time.time() < deadline:
        try:
            txt = str(extract_page_data(target_prefix, js))
            if any(s in txt for s in complete_substrings):
                return True
        except Exception:
            pass
        time.sleep(interval_sec)
    return False


def extract_strategy_stats(target_prefix: str) -> dict[str, Any]:
    """Best-effort: scrape text and regex CAGR / Sharpe / Max DD."""
    js = "document.body ? document.body.innerText : ''"
    txt = str(extract_page_data(target_prefix, js))
    stats: dict[str, Any] = {"raw_excerpt": txt[:2000]}
    m = re.search(r"CAGR[:\s]+([0-9.+-]+)\s*%?", txt, re.I)
    if m:
        stats["cagr_pct"] = float(m.group(1))
    m = re.search(r"Sharpe[:\s]+([0-9.]+)", txt, re.I)
    if m:
        stats["sharpe"] = float(m.group(1))
    m = re.search(r"Max[.\s]*DD[:\s]+(-?[0-9.]+)\s*%?", txt, re.I)
    if m:
        stats["max_drawdown_pct"] = float(m.group(1))
    return stats


def extract_compare_all_table(target_prefix: str) -> pd.DataFrame:
    """Placeholder table extraction — returns single-column DataFrame from visible text lines."""
    js = "document.body ? document.body.innerText : ''"
    txt = str(extract_page_data(target_prefix, js))
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    return pd.DataFrame({"line": lines[:500]})


def navigate_and_extract_bulk(
    strategy_urls: list[str],
    target_prefix: str,
) -> pd.DataFrame:
    """Navigate each URL and collect extract_strategy_stats (sequential)."""
    rows: list[dict[str, Any]] = []
    for url in strategy_urls:
        cdp_cmd("nav", target_prefix, url, timeout=90.0)
        time.sleep(2.0)
        stat = extract_strategy_stats(target_prefix)
        stat["url"] = url
        rows.append(stat)
    return pd.DataFrame(rows)
