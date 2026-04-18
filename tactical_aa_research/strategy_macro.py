"""Macro-conditioned overlays on top of dual-momentum + vol targeting."""
from __future__ import annotations

import numpy as np
import pandas as pd


def apply_macro_risk_off(
    weights: pd.DataFrame,
    macro_f: pd.DataFrame,
    *,
    vix_z_thr: float,
    vix_scale: float,
    nfci_z_thr: float,
    nfci_scale: float,
    lev_tickers: tuple[str, ...] = ("UPRO", "TQQQ", "TMF"),
    agg_share: float = 0.65,
) -> pd.DataFrame:
    """
    At month-end t, reduce LETF weights when macro stress is high; move to AGG/BIL.
    All inputs aligned on index; macro_f must be lag-safe (features at t use data through t).
    """
    w = weights.copy()
    mf = macro_f.reindex(w.index)
    for t in w.index:
        row = mf.loc[t] if t in mf.index else None
        if row is None or row.isna().all():
            continue
        vz = float(row.get("vix_z_12", 0) or 0)
        nz = float(row.get("nfci_z_12", 0) or 0)
        risk_off = 0.0
        if np.isfinite(vz) and vz > vix_z_thr:
            risk_off += float(np.clip(vix_scale * (vz - vix_z_thr), 0.0, 0.35))
        if np.isfinite(nz) and nz > nfci_z_thr:
            risk_off += float(np.clip(nfci_scale * (nz - nfci_z_thr), 0.0, 0.25))
        risk_off = float(np.clip(risk_off, 0.0, 0.55))
        if risk_off <= 0:
            continue
        lev_cols = [c for c in lev_tickers if c in w.columns]
        if not lev_cols:
            continue
        lev_mass = float(w.loc[t, lev_cols].sum())
        if lev_mass <= 0:
            continue
        for c in lev_cols:
            w.loc[t, c] *= 1.0 - risk_off
        reallocated = risk_off * lev_mass
        if "AGG" in w.columns:
            w.loc[t, "AGG"] += reallocated * agg_share
        if "BIL" in w.columns:
            w.loc[t, "BIL"] += reallocated * (1.0 - agg_share)
        s = float(w.loc[t].sum())
        if s > 0:
            w.loc[t] = w.loc[t] / s
    return w


def macro_vol_scale(macro_f: pd.DataFrame, *, vix_hi: float, scale_min: float) -> pd.Series:
    """Multiply target vol by scale in [scale_min, 1.0] when VIX z-score high."""
    vz = macro_f["vix_z_12"].astype(float).reindex(macro_f.index)
    mult = 1.0 - np.clip((vz - vix_hi) * 0.12, 0.0, 1.0 - scale_min)
    return pd.Series(mult, index=macro_f.index).clip(lower=scale_min)
