# Validation Test Suite Implementation

This document provides the template code for the 6 validation test scripts. Each script should be saved in the `tests/` directory of the strategy folder and adapted with the specific requirements extracted from the paper.

## Aspect 1: Field Availability

**File**: `tests/test_availability.py`

```python
import yfinance as yf
import pandas_datareader.data as web
import json
from pathlib import Path

# --- Settings ---
STRATEGY_NAME = "[strategy_name]"
BASE_DIR = Path(f"/home/ubuntu/Academic Research/replication/{STRATEGY_NAME}")
TICKERS = ["AAPL", "SPY"] # From requirements
START_DATE = "2010-01-01"
# ----------------

def test_availability():
    results = {}
    available_count = 0
    for ticker in TICKERS:
        try:
            # Try yfinance first
            data = yf.download(ticker, start=START_DATE, period="1mo", progress=False)
            if not data.empty and data.notna().any().any():
                results[ticker] = {"source": "yfinance", "status": "available"}
                available_count += 1
                print(f"OK: {ticker} (yfinance)")
                continue

            # Try FRED as fallback for macro
            try:
                data = web.DataReader(ticker, 'fred', START_DATE)
                if not data.empty:
                    results[ticker] = {"source": "fred", "status": "available"}
                    available_count += 1
                    print(f"OK: {ticker} (FRED)")
                    continue
            except Exception:
                pass # FRED failed, mark as unavailable

            results[ticker] = {"source": "none", "status": "unavailable"}
            print(f"FAIL: {ticker}")

        except Exception as e:
            results[ticker] = {"source": "none", "status": f"error: {e}"}
            print(f"ERROR: {ticker} -> {e}")

    score = int((available_count / len(TICKERS)) * 10) if TICKERS else 0
    final_result = {"aspect": "availability", "overall_score": score, "details": results}
    
    with open(BASE_DIR / "results" / "aspect1_availability.json", "w") as f:
        json.dump(final_result, f, indent=2)
    
    print(f"\nScore: {score}/10")

if __name__ == "__main__":
    test_availability()
```

## Aspect 2: Date Alignment

**File**: `tests/test_date_alignment.py`

```python
import pandas as pd
import json
from pathlib import Path

# --- Settings ---
STRATEGY_NAME = "[strategy_name]"
BASE_DIR = Path(f"/home/ubuntu/Academic Research/replication/{STRATEGY_NAME}")
PAPER_START = "2010-01-01"
PAPER_END = "2023-12-31"
# ----------------

def test_date_alignment():
    csv_path = BASE_DIR / "data" / "final_validated_data.csv"
    df = pd.read_csv(csv_path, index_col='date', parse_dates=True)

    actual_start = df.index.min()
    actual_end = df.index.max()

    start_ok = actual_start <= pd.Timestamp(PAPER_START)
    end_ok = actual_end >= pd.Timestamp(PAPER_END)

    score = 0
    if start_ok: score += 5
    if end_ok: score += 5

    results = {
        "aspect": "date_alignment",
        "overall_score": score,
        "paper_range": f"{PAPER_START} to {PAPER_END}",
        "actual_range": f"{actual_start.date()} to {actual_end.date()}",
    }

    with open(BASE_DIR / "results" / "aspect2_date_alignment.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nScore: {score}/10")

if __name__ == "__main__":
    test_date_alignment()
```

## Aspect 3: Adjustment Method

**File**: `tests/test_adjustment_method.py`

```python
# This test is more qualitative. It checks if both Adj Close and Close are available.
import pandas as pd
import json
from pathlib import Path

# --- Settings ---
STRATEGY_NAME = "[strategy_name]"
BASE_DIR = Path(f"/home/ubuntu/Academic Research/replication/{STRATEGY_NAME}")
# ----------------

def test_adjustment():
    csv_path = BASE_DIR / "data" / "raw_data.csv"
    df = pd.read_csv(csv_path, header=[0, 1], index_col=0, parse_dates=True)

    has_adj_close = 'Adj Close' in df.columns.get_level_values(0)
    has_close = 'Close' in df.columns.get_level_values(0)
    
    score = 0
    if has_adj_close and has_close:
        score = 10 # Both available, can match paper
    elif has_adj_close:
        score = 8 # Can only use adjusted
    elif has_close:
        score = 6 # Can only use unadjusted

    results = {
        "aspect": "adjustment_method",
        "overall_score": score,
        "adj_close_available": has_adj_close,
        "close_available": has_close,
    }

    with open(BASE_DIR / "results" / "aspect3_adjustment.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nScore: {score}/10")

if __name__ == "__main__":
    test_adjustment()
```

## Aspects 4, 5, 6

Templates for `test_spot_checks.py`, `test_summary_stats.py`, and `test_completeness.py` follow the same pattern. They load `data/final_validated_data.csv` and `data/reference_values.json`, perform comparisons, and calculate a score from 1 to 10. The logic from the original `xbbg-data-extractor.md` can be adapted directly, replacing Bloomberg-specific column names with the format from `yfinance`.
