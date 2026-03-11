#!/usr/bin/env python
# Template for extract_raw_data.py

import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime
import json
from pathlib import Path

# --- Core Settings (MUST BE ADAPTED FROM PAPER REQUIREMENTS) ---
STRATEGY_NAME = "[strategy_name]"  # e.g., "value_momentum_sp500"
TICKERS = ["AAPL", "SPY"]  # List of tickers
FIELDS = ["Adj Close", "Volume"] # e.g., ["Adj Close", "Close", "Volume"]
START_DATE = "2010-01-01"
END_DATE = "2023-12-31"
# ----------------------------------------------------------------

BASE_DIR = Path(f"/home/ubuntu/Academic Research/replication/{STRATEGY_NAME}")
DATA_DIR = BASE_DIR / "data"


def fetch_data_yfinance(tickers, start, end):
    """Fetches data using yfinance library."""
    print(f"--> Attempting to fetch data via yfinance for {len(tickers)} tickers...")
    try:
        data = yf.download(tickers, start=start, end=end, progress=False)
        if data.empty:
            print("yfinance returned an empty dataframe.")
            return None
        print("yfinance fetch successful.")
        return data
    except Exception as e:
        print(f"yfinance fetch failed: {e}")
        return None

def fetch_data_fred(tickers, start, end):
    """Fetches macroeconomic data from FRED."""
    print(f"--> Attempting to fetch FRED data for {len(tickers)} tickers...")
    try:
        data = web.DataReader(tickers, 'fred', start, end)
        if data.empty:
            print("pandas_datareader (FRED) returned an empty dataframe.")
            return None
        print("FRED fetch successful.")
        return data
    except Exception as e:
        print(f"FRED fetch failed: {e}")
        return None

def main():
    """Main data extraction and processing logic."""
    print(f"Starting data extraction for: {STRATEGY_NAME}")
    
    # Simple routing for data source based on ticker format
    is_macro = all(['.' not in t and t.isupper() and len(t) < 10 for t in TICKERS])

    if is_macro:
        raw_data = fetch_data_fred(TICKERS, START_DATE, END_DATE)
    else:
        raw_data = fetch_data_yfinance(TICKERS, START_DATE, END_DATE)

    if raw_data is None or raw_data.empty:
        print("FATAL: All data sources failed. Could not retrieve any data.")
        return

    # --- Data Cleaning and Formatting ---
    df = raw_data.copy()

    # For yfinance, select only the required fields
    if not is_macro and isinstance(df.columns, pd.MultiIndex):
        df = df[FIELDS]
        df.columns = df.columns.droplevel(0)

    df.index.name = 'date'
    df = df.sort_index()

    # Save raw pull
    raw_csv_path = DATA_DIR / "raw_data.csv"
    df.to_csv(raw_csv_path)
    print(f"\nSaved raw data to {raw_csv_path}")

    # Trim NaN rows at start/end
    first_valid = df.first_valid_index()
    last_valid = df.last_valid_index()
    if first_valid is not None and last_valid is not None:
        trimmed_df = df.loc[first_valid:last_valid]
        final_csv_path = DATA_DIR / "final_validated_data.csv"
        trimmed_df.to_csv(final_csv_path)
        print(f"Saved final validated (trimmed) data to {final_csv_path}")
    else:
        print("WARNING: No valid data found, final CSV not created.")

    # --- Log Execution ---
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'strategy': STRATEGY_NAME,
        'tickers': TICKERS,
        'fields': FIELDS,
        'date_range': f"{START_DATE} to {END_DATE}",
        'success': True
    }
    with open(BASE_DIR / "logs" / "extraction.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print("\nData extraction complete.")

if __name__ == "__main__":
    main()
