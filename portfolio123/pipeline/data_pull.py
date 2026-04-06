"""P123 API wrappers: universe data, prices, credits, retries, license fallback."""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import p123api
from p123api import ClientException

from . import config

_MAX_RETRIES = 3
_BACKOFF_SEC = 2.0


def _maybe_add_vault_to_path() -> None:
    """Allow optional ``from src.data_validation ...`` when OBSIDIAN_VAULT is set."""
    root = config.OBSIDIAN_VAULT_ROOT
    if root and root.is_dir():
        s = str(root)
        if s not in sys.path:
            sys.path.insert(0, s)


@contextmanager
def get_client() -> Iterator[p123api.Client]:
    """Authenticated p123api client context manager."""
    if not config.P123_API_ID or not config.P123_API_KEY:
        raise RuntimeError(
            "Set P123_API_ID and P123_API_KEY in "
            f"{config.SKILL_ROOT / '.env'!s} or environment."
        )
    client = p123api.Client(api_id=config.P123_API_ID, api_key=config.P123_API_KEY)
    try:
        yield client
    finally:
        client.close()


def _api_call_with_retry(
    func: Any,
    *args: Any,
    max_retries: int = _MAX_RETRIES,
    **kwargs: Any,
) -> Any:
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ClientException as e:
            last_err = e
            err_str = str(e).lower()
            if ("quota" in err_str or "timeout" in err_str) and attempt < max_retries - 1:
                time.sleep(_BACKOFF_SEC ** attempt)
                continue
            raise
    raise last_err  # pragma: no cover


def check_credits(client: p123api.Client) -> int:
    """Return quotaRemaining from a minimal data_prices call; warn at 80% / 95%."""
    r = _api_call_with_retry(
        client.data_prices,
        "SPY",
        start="2024-01-01",
        end="2024-01-01",
        to_pandas=False,
    )
    remaining = int(r.get("quotaRemaining", 0) or 0)
    used = config.MONTHLY_CREDIT_QUOTA - remaining
    if remaining < (config.MONTHLY_CREDIT_QUOTA - config.CREDIT_WARN_95_PCT):
        print(
            f"WARNING: P123 credits below 5% — {remaining} remaining "
            f"(used ~{used})."
        )
    elif remaining < (config.MONTHLY_CREDIT_QUOTA - config.CREDIT_WARN_80_PCT):
        print(
            f"WARNING: P123 credits below 20% — {remaining} remaining."
        )
    return remaining


def pull_universe_data(
    universe: str,
    as_of_dts: list[str],
    formulas: list[str],
    names: list[str] | None = None,
    preproc: dict[str, Any] | None = None,
    pit_method: str = "Complete",
    batch_size: int | None = None,
    to_pandas: bool = True,
) -> pd.DataFrame:
    """
    Batched ``data_universe`` — splits ``as_of_dts`` to manage credits / payload size.

    Falls back to ``data()`` with IBM,MSFT,INTC if universe call fails with license error.
    """
    batch_size = batch_size or config.DEFAULT_BATCH_DATES
    if names is not None and len(names) != len(formulas):
        raise ValueError("names must match formulas length")

    frames: list[pd.DataFrame] = []
    with get_client() as client:
        check_credits(client)
        for i in range(0, len(as_of_dts), batch_size):
            batch = as_of_dts[i : i + batch_size]
            payload: dict[str, Any] = {
                "universe": universe,
                "asOfDts": batch,
                "formulas": formulas,
                "pitMethod": pit_method,
                "includeNames": True,
                "currency": "USD",
            }
            if names:
                payload["names"] = names
            if preproc:
                payload["preproc"] = preproc
            try:
                part = _api_call_with_retry(
                    client.data_universe,
                    payload,
                    to_pandas=to_pandas,
                )
            except ClientException as e:
                err = str(e).lower()
                if "data license" in err or "license required" in err:
                    return _fallback_data_tickers(
                        client,
                        formulas,
                        batch,
                        names,
                        pit_method,
                        to_pandas,
                    )
                raise
            if part is not None and len(part) > 0:
                frames.append(part)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _fallback_data_tickers(
    client: p123api.Client,
    formulas: list[str],
    as_of_dts: list[str],
    names: list[str] | None,
    pit_method: str,
    to_pandas: bool,
) -> pd.DataFrame:
    """FactSet/Compustat license fallback: IBM, MSFT, INTC per api-reference."""
    tickers = ["IBM", "MSFT", "INTC"]
    frames: list[pd.DataFrame] = []
    for start in as_of_dts[:1]:  # minimal slice for demo fallback
        payload = {
            "tickers": tickers,
            "formulas": formulas,
            "startDt": start,
            "endDt": start,
            "pitMethod": pit_method,
            "includeNames": True,
            "currency": "USD",
        }
        if names:
            payload["names"] = names
        part = _api_call_with_retry(client.data, payload, to_pandas=to_pandas)
        if part is not None and len(part) > 0:
            frames.append(part)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def pull_price_data(
    identifier: str,
    start: str,
    end: str | None = None,
    to_pandas: bool = True,
) -> pd.DataFrame | dict[str, Any]:
    """Wrap ``data_prices`` (note: ``start``/``end``, not startDt/endDt)."""
    with get_client() as client:
        check_credits(client)
        return _api_call_with_retry(
            client.data_prices,
            identifier,
            start=start,
            end=end,
            to_pandas=to_pandas,
        )


def save_dataframe_csv(df: pd.DataFrame, operation: str) -> Path:
    """Write to OUTPUT_DIR with timestamped name."""
    config.ensure_output_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = config.OUTPUT_DIR / f"{operation}_{ts}.csv"
    df.to_csv(path, encoding="utf-8", index=False)
    return path


def validate_panel_optional(df: pd.DataFrame, source: str = "p123") -> pd.DataFrame:
    """
    If vault ``src.data_validation`` is importable and ``P123_RUN_VALIDATION=1``,
    run ``validate(..., skip_validation=True)``. Otherwise return df unchanged.
    """
    if os.environ.get("P123_RUN_VALIDATION") != "1":
        return df
    _maybe_add_vault_to_path()
    try:
        from src.data_validation import validate  # type: ignore[import-untyped]
        from src.data_validation.orchestrator import ValidationConfig  # type: ignore[import-untyped]
    except ImportError:
        return df
    try:
        cfg = ValidationConfig(source=source)
        vd = validate(df, cfg, skip_validation=True)
        return vd.df
    except Exception:
        return df
