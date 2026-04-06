"""Upload ML scores as StockFactor and macro/regime as DataSeries."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import p123api

from . import config
from .data_pull import get_client, _api_call_with_retry


def _timestamp_path(prefix: str, ext: str) -> Path:
    config.ensure_output_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return config.OUTPUT_DIR / f"{prefix}_{ts}.{ext}"


def upload_stock_factor(
    client: p123api.Client,
    name: str,
    predictions_df: pd.DataFrame,
    description: str = "",
) -> dict[str, Any]:
    """
    Create/update StockFactor and upload CSV (date, ticker, value).

    Column names normalized to date, ticker, value.
    """
    if not name.startswith("agent"):
        name = f"agent_{name}"

    df = predictions_df.copy()
    col_map = {
        "asOfDt": "date",
        "Date": "date",
        "DATE": "date",
        "Ticker": "ticker",
        "TICKER": "ticker",
        "Value": "value",
        "prediction": "value",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    for req in ("date", "ticker", "value"):
        if req not in df.columns:
            raise ValueError(f"predictions_df must have column '{req}' (or aliases)")

    csv_path = _timestamp_path("stock_factor_upload", "csv")
    df[["date", "ticker", "value"]].to_csv(
        csv_path, index=False, encoding="utf-8", date_format="%Y-%m-%d"
    )

    result = _api_call_with_retry(
        client.stock_factor_create_update,
        {"name": name, "description": description or f"agent pipeline {name}"},
    )
    factor_id = result.get("id")
    if factor_id is None:
        raise RuntimeError(f"stock_factor_create_update missing id: {result}")

    with open(csv_path, "r", encoding="utf-8") as fh:
        _api_call_with_retry(
            client.stock_factor_upload,
            factor_id=factor_id,
            data=fh,
            column_separator="comma",
            existing_data="overwrite",
            date_format="yyyy-mm-dd",
        )
    return {"factor_id": factor_id, "name": name, "csv_path": str(csv_path)}


def upload_data_series(
    client: p123api.Client,
    name: str,
    series_df: pd.DataFrame,
    description: str = "",
) -> dict[str, Any]:
    """Create/update DataSeries; CSV date,value."""
    if not name.startswith("agent"):
        name = f"agent_{name}"

    df = series_df.copy()
    if "value" not in df.columns:
        raise ValueError("series_df must have 'value'")
    dcol = "date" if "date" in df.columns else "asOfDt"
    if dcol not in df.columns:
        raise ValueError("series_df must have 'date' or 'asOfDt'")
    out = pd.DataFrame({"date": pd.to_datetime(df[dcol]).dt.strftime("%Y-%m-%d"), "value": df["value"]})
    csv_path = _timestamp_path("data_series_upload", "csv")
    out.to_csv(csv_path, index=False, encoding="utf-8")

    result = _api_call_with_retry(
        client.data_series_create_update,
        {"name": name, "description": description or f"agent pipeline {name}"},
    )
    series_id = result.get("id")
    if series_id is None:
        raise RuntimeError(f"data_series_create_update missing id: {result}")

    with open(csv_path, "r", encoding="utf-8") as fh:
        _api_call_with_retry(
            client.data_series_upload,
            series_id=series_id,
            data=fh,
            existing_data="overwrite",
            date_format="yyyy-mm-dd",
            decimal_separator=".",
            contains_header_row=True,
        )
    return {"series_id": series_id, "name": name, "csv_path": str(csv_path)}


def verify_stock_factor_formula(client: p123api.Client, factor_name: str) -> bool:
    """Quick ``data()`` with StockFactor(name) for IBM on one date."""
    try:
        r = _api_call_with_retry(
            client.data,
            {
                "tickers": ["IBM"],
                "formulas": [f'StockFactor("{factor_name}")'],
                "startDt": "2024-06-01",
                "endDt": "2024-06-01",
                "pitMethod": "Complete",
                "ignoreErrors": True,
            },
            True,
        )
        return r is not None and len(r) > 0
    except Exception:
        return False


def upload_stock_factor_auto(predictions_df: pd.DataFrame, name: str) -> dict[str, Any]:
    """Convenience: open client, upload, return result."""
    with get_client() as client:
        return upload_stock_factor(client, name, predictions_df)
