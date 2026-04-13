# Reference: Full Code Templates

Read this file when scaffolding `evaluate.py` and `initial.py` for a user's
trading evolution task. Adapt tickers, date ranges, features, and fitness
weights to the user's request.

---

## evaluate.py

```python
"""
ShinkaEvolve evaluator for trading strategy evolution.
Scores candidates by running run_experiment() from the evolved initial.py.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from shinka.core import run_shinka_eval


DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_CSV = DATA_DIR / "SPY.csv"  # <-- adapt to user's ticker / path


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_ohlcv(path: Path) -> pd.DataFrame:
    """Load OHLCV from CSV with a Date column."""
    df = pd.read_csv(path, parse_dates=["Date"]).sort_values("Date")
    df = df.set_index("Date")
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        if c not in df.columns:
            raise ValueError(f"Missing column {c}")
    return df


def download_ohlcv(ticker: str = "SPY",
                    start: str = "2018-01-01",
                    end: str = "2024-12-31") -> pd.DataFrame:
    """Fallback: download via yfinance."""
    try:
        import yfinance as yf
        df = yf.download(ticker, start=start, end=end, auto_adjust=True)
        if df.empty:
            raise RuntimeError(f"yfinance returned empty for {ticker}")
        return df
    except Exception:
        return make_synthetic_ohlcv()


def make_synthetic_ohlcv(n: int = 800, seed: int = 0) -> pd.DataFrame:
    """Deterministic fake data — always works offline."""
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0004, 0.01, size=n)
    close = 100.0 * np.exp(np.cumsum(r))
    idx = pd.date_range("2018-01-01", periods=n, freq="B")
    return pd.DataFrame(
        {
            "Open": close,
            "High": close * 1.001,
            "Low": close * 0.999,
            "Close": close,
            "Volume": rng.integers(1_000_000, 5_000_000, size=n),
        },
        index=idx,
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_output(result: dict) -> Tuple[bool, Optional[str]]:
    """Reject broken candidates."""
    required = [
        "train_sharpe", "test_sharpe",
        "train_max_dd", "test_max_dd",
        "n_train", "n_test",
    ]
    for k in required:
        if k not in result:
            return False, f"missing key {k}"
    if not np.isfinite(result["train_sharpe"]):
        return False, "non-finite train_sharpe"
    if not np.isfinite(result["test_sharpe"]):
        return False, "non-finite test_sharpe"
    if int(result["n_train"]) < 20:
        return False, "too few train points"
    return True, None


# ---------------------------------------------------------------------------
# Aggregation → combined_score
# ---------------------------------------------------------------------------

def aggregate_metrics(results: List[dict]) -> Dict[str, Any]:
    """
    Map run_experiment output to combined_score (higher = better).
    Includes train-test gap penalty to discourage overfitting.
    """
    r = results[0]
    train = float(r["train_sharpe"])
    test = float(r["test_sharpe"])
    dd_pen = max(0.0, -float(r["train_max_dd"]))
    turn = float(r.get("train_mean_turnover", 0.0))

    gap = max(0.0, train - test - 1.0)

    combined = (
        train
        + 0.15 * test
        - 0.05 * turn * 100.0
        - 0.25 * dd_pen
        - 0.50 * gap
    )

    return {
        "combined_score": combined,
        "public": {
            "train_sharpe": train,
            "test_sharpe": test,
            "train_max_dd": r["train_max_dd"],
            "test_max_dd": r["test_max_dd"],
            "mean_turnover": turn,
            "policy_name": r.get("policy_name", ""),
        },
        "private": {},
        "extra_data": r,
        "text_feedback": (
            f"train_sharpe={train:.3f} test_sharpe={test:.3f} "
            f"gap_penalty={gap:.3f} "
            f"policy={r.get('policy_name', '')}"
        ),
    }


# ---------------------------------------------------------------------------
# Experiment kwargs
# ---------------------------------------------------------------------------

def get_experiment_kwargs(run_idx: int) -> dict:
    """Load data and define train/test split."""
    if DEFAULT_CSV.exists():
        ohlcv = load_ohlcv(DEFAULT_CSV)
    else:
        ohlcv = download_ohlcv()

    idx = ohlcv.index.sort_values()
    split = int(len(idx) * 0.7)

    return {
        "ohlcv": ohlcv,
        "train_start": str(idx[0].date()),
        "train_end": str(idx[split - 1].date()),
        "test_start": str(idx[split].date()),
        "test_end": str(idx[-1].date()),
        "fee_bps": 1.0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(program_path: str, results_dir: str) -> None:
    os.makedirs(results_dir, exist_ok=True)

    metrics, correct, err = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_experiment",
        num_runs=1,
        run_workers=1,
        get_experiment_kwargs=get_experiment_kwargs,
        aggregate_metrics_fn=aggregate_metrics,
        validate_fn=validate_output,
    )

    print("correct:", correct, "err:", err)
    print(json.dumps(metrics, indent=2, default=str))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--program_path", default="initial.py")
    p.add_argument("--results_dir", default="results")
    a = p.parse_args()
    main(a.program_path, a.results_dir)
```

---

## initial.py

```python
"""
Evolvable trading policy.
Only code inside EVOLVE-BLOCK-START / EVOLVE-BLOCK-END is mutated by Shinka.
run_experiment() is the fixed entry point called by evaluate.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# EVOLVE-BLOCK-START
def compute_target_position(features: pd.DataFrame) -> pd.Series:
    """
    Map per-row features to a position in [-1, 1].

    Available columns (built by run_experiment):
        ret_1   — 1-day return
        ret_5   — 5-day return
        vol_20  — 20-day rolling volatility
        rsi_14  — 14-day RSI

    Must return a Series aligned to features.index.
    """
    mom = features["ret_5"].fillna(0.0)
    pos = np.tanh(mom * 50.0)
    return pd.Series(pos, index=features.index)


def describe_policy() -> str:
    """Short name for logging."""
    return "tanh(50 * ret_5) baseline"
# EVOLVE-BLOCK-END


# ---- Fixed harness (not evolved) ----

def run_experiment(
    *,
    ohlcv: pd.DataFrame,
    train_start: str,
    train_end: str,
    test_start: str,
    test_end: str,
    fee_bps: float = 1.0,
    **_: object,
) -> dict:
    """
    Called by evaluate.py via run_shinka_eval.
    Returns a dict of metrics for aggregation.
    """
    px = ohlcv["Close"].astype(float)
    rets = px.pct_change()

    # Build features
    feats = pd.DataFrame(index=ohlcv.index)
    feats["ret_1"] = rets
    feats["ret_5"] = px.pct_change(5)
    feats["vol_20"] = rets.rolling(20).std()

    delta = px.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / (roll_down + 1e-12)
    feats["rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

    # Signal → position (clipped, no lookahead via shift)
    position = compute_target_position(feats).clip(-1.0, 1.0).fillna(0.0)
    strat_rets = position.shift(1).fillna(0.0) * rets

    # Costs
    turnover = position.diff().abs().fillna(0.0)
    costs = turnover * (fee_bps / 10000.0)
    net = strat_rets - costs

    # Split
    train = net.loc[train_start:train_end].dropna()
    test = net.loc[test_start:test_end].dropna()

    def sharpe(x: pd.Series) -> float:
        if len(x) < 5 or float(x.std()) == 0.0:
            return 0.0
        return float(np.sqrt(252.0) * x.mean() / x.std())

    def max_dd(x: pd.Series) -> float:
        eq = (1.0 + x).cumprod()
        peak = eq.cummax()
        dd = eq / peak - 1.0
        return float(dd.min())

    train_sharpe = sharpe(train)
    test_sharpe = sharpe(test)
    train_turn = float(turnover.loc[train_start:train_end].mean())

    return {
        "train_sharpe": train_sharpe,
        "test_sharpe": test_sharpe,
        "train_max_dd": max_dd(train),
        "test_max_dd": max_dd(test),
        "train_mean_turnover": train_turn,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "policy_name": describe_policy(),
    }
```

---

## Adapting for a specific user

When creating these files for a user, modify:

1. **`DEFAULT_CSV`** — point to their data file or change the yfinance ticker
2. **Features in `run_experiment`** — add user-requested indicators (MACD, Bollinger, etc.)
3. **Feature docstring in `compute_target_position`** — list actual available columns
4. **`fee_bps`** — adjust to asset class (equities ~1-5 bps, futures ~0.5-2 bps, crypto ~5-10 bps)
5. **`combined_score` weights** — tune gap penalty, DD penalty per user preference
6. **`llm_models`** in the runner config — match user's available API keys
