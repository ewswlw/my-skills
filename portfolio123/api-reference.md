# P123 API Reference (p123api Python Wrapper)

## Table of Contents
1. [Setup & Authentication](#setup)
2. [Data Retrieval](#data-retrieval)
3. [Universe](#universe)
4. [Rank](#rank)
5. [Screen](#screen)
6. [Strategy](#strategy)
7. [Data Series & Stock Factors](#data-series)
8. [AI Factor](#ai-factor)
9. [API Credits & Limits](#credits)

---

## Setup & Authentication <a name="setup"></a>

```python
# Install
pip install --upgrade p123api

# Usage
import p123api

client = p123api.Client(api_id='YOUR_API_ID', api_key='YOUR_API_KEY')

# Or as context manager
with p123api.Client(api_id='YOUR_API_ID', api_key='YOUR_API_KEY') as client:
    result = client.screen_run({...})
```

API keys: Account Settings → DataMiner & API → Create Key. Requires Research subscription.

---

## Data Retrieval <a name="data-retrieval"></a>

### data() — Retrieve point-in-time data for specific tickers (1 credit per 100K data points)

```python
client.data({
    # Identifier (choose one): tickers, FIGI, p123Uids, CIKs, gvkeys (Compustat only)
    'tickers': ['AAPL', 'MSFT', 'GOOG'],
    'formulas': ['PEExclXorTTM', 'ROE%TTM', 'MktCap', 'Close(0)/Close(252)-1'],
    'startDt': '2020-01-01',
    'endDt': '2025-01-01',
    # Optional
    'frequency': 'Every 4 Weeks',  # Every Week, Every N Weeks (2,3,4,6,8,13,26,52)
    'pitMethod': 'Complete',       # Complete | Prelim
    'precision': 4,                # 2 | 3 | 4
    'currency': 'USD',
    'includeNames': True,
    'region': 'United States',     # Canada, North America, Europe, North Atlantic
    'ignoreErrors': True           # ignore invalid tickers
}, True)  # True = Pandas DataFrame, False = JSON
```

**Note**: Requires data license from FactSet or Compustat for full access. Without license, only IBM, MSFT, INTC with 5 years history.

### data_prices() — EOD prices (1 credit per call)

```python
client.data_prices(
    identifier='AAPL',       # string ticker or int P123 ID
    start='2024-01-01',
    end='2025-01-01',        # or None
    to_pandas=True
)
```

### data_universe() — Point-in-time data for a universe (1 credit per 100K data points)

```python
client.data_universe({
    'universe': 'SP500',           # P123 universe name or custom
    'asOfDts': ['2025-03-08', '2025-03-01'],  # use weekend dates
    'formulas': ['PEExclXorTTM', 'ROE%TTM', 'Close(0)/Close(5)'],
    'names': ['PE', 'ROE', '1wk%'],  # optional, must match formula count
    # Optional
    'pitMethod': 'Complete',
    'precision': 4,                 # None for max precision
    'type': 'stock',                # stock | etf
    'includeNames': True,
    'currency': 'USD',
    'figi': 'Country Composite',    # Country Composite | Share Class
    # Normalization (optional)
    'preproc': {
        'scaling': 'rank',          # minmax | rank | normal
        'scope': 'date',            # dataset | date
        'trimPct': 5.0,
        'outliers': True,           # clip outliers
        'naFill': False,            # fill NAs with middle values
        'outlierLimit': 5,          # for normal scaling
        'excludedFormulas': ['Close(0)/Close(5)'],  # exclude from normalization
        'mlTrainingEnd': '2020-01-01'  # end date when scope=dataset
    }
}, to_pandas=True)
```

**Common Universes**: SP500, SP400, SP600, SP1500, DJIA, Prussell1000, Prussell2000, Prussell3000, NASDAQ100, ALLSTOCKS, ALLFUND, LargeCap, MidCap, SmallCap, MicroCap

---

## Universe <a name="universe"></a>

### universe_update() — Create/update the ApiUniverse

```python
client.universe_update({
    'rules': [
        'MktCap > 500',
        'AvgDailyTot(63) > 200',
        'Close(0) > 5'
    ],
    'type': 'stock',
    'currency': 'USD',
    'startingUniverse': 'Prussell3000'  # optional base universe
})
```

Then use `'universe': 'ApiUniverse'` in other API calls.

---

## Rank <a name="rank"></a>

### rank_ranks() — Retrieve ranks for a universe (1 per 100K data points, min 2)

```python
client.rank_ranks({
    'rankingSystem': 'My Ranking System',  # name or ID
    'asOfDt': '2025-03-08',
    'universe': 'SP500',
    # Optional
    'pitMethod': 'Complete',
    'precision': 2,
    'rankingMethod': 2,                 # 2=NAs Negative, 4=NAs Neutral
    'tickers': 'IBM,MSFT',             # filter specific stocks
    'includeNames': True,
    'includeNaCnt': False,
    'includeFinalStmt': False,
    'nodeDetails': 'composite',         # composite | factor
    'additionalData': ['Close(0)', 'MktCap', 'ZScore(`Pr2SalesQ`,#All)'],
    'currency': 'USD'
}, True)
```

### rank_perf() — Bucket performance test (3 credits)

```python
client.rank_perf({
    'rankingSystem': 'My Ranking System',
    'startDt': '2010-01-01',
    # Optional
    'endDt': '2025-01-01',
    'universe': 'Prussell3000',
    'numBuckets': 10,
    'rebalFreq': 'Every 4 Weeks',
    'slippage': 0.25,
    'benchmark': 'SPY',
    'minPrice': 3,
    'minLiquidity': 5000,
    'outputType': 'ann',        # ann (annualized) | perf (cumulative)
    'transType': 'Long',        # Long | Short
    'rankingMethod': 2,
    'maxNAs': 999,
    'maxReturn': 200
})
```

### rank_update() — Update ApiRankingSystem (1 credit)

```python
client.rank_update({
    'nodes': '''<RankingSystem>
        <RankPerformance>
            <NNodes>2</NNodes>
            <SNode>
                <n>Value</n>
                <Formula>PEExclXorTTM</Formula>
                <LowerIsBetter>1</LowerIsBetter>
                <Weight>50</Weight>
            </SNode>
            <SNode>
                <n>Momentum</n>
                <Formula>Close(0)/Close(252)</Formula>
                <LowerIsBetter>0</LowerIsBetter>
                <Weight>50</Weight>
            </SNode>
        </RankPerformance>
    </RankingSystem>''',
    'type': 'stock',
    'rankingMethod': 2,
    'id': 12345          # optional; omit to use/create ApiRankingSystem
})
```

---

## Screen <a name="screen"></a>

### screen_run() — Run a screen (2 credits)

```python
# Inline screen definition
client.screen_run({
    'screen': {
        'type': 'stock',
        'universe': 'SP500',
        'maxNumHoldings': 25,    # 0 for all
        'method': 'long',        # long | short | long/short | hedged
        'benchmark': 'SPY',
        'currency': 'USD',
        # Ranking (choose one form):
        'ranking': 'My Ranking System',      # by name
        'ranking': 12345,                     # by ID
        'ranking': {'formula': 'PEExclXorTTM', 'lowerIsBetter': True},  # inline formula
        # Rules
        'rules': [
            {'formula': 'MktCap > 1000', 'type': 'long'},
            {'formula': 'ROE%TTM > 10', 'type': 'common'},
            {'formula': 'Close(0) > SMA(200,0)', 'type': 'long'}
        ]
    },
    'asOfDt': '2025-03-08',
    'pitMethod': 'Complete',
    'precision': 2
}, True)

# Run existing screen by ID
client.screen_run({'screen': 12345}, True)
```

### screen_backtest() — Backtest a screen (5 credits)

> **NOTE:** `screen_backtest` is a **BUY-SIDE-ONLY** backtest. It does NOT include sell rules, position-level execution, cash drag, or realistic slippage modeling. **Do not treat screen_backtest results as equivalent to a full strategy simulation.** Use for rapid candidate screening; validate with native P123 simulation. See SKILL.md Validation Hierarchy.

```python
client.screen_backtest({
    'screen': {
        'type': 'stock',
        'universe': 'Prussell3000',
        'maxNumHoldings': 25,
        'method': 'long',
        'benchmark': 'SPY',
        'ranking': {'formula': 'PEExclXorTTM', 'lowerIsBetter': True},
        'rules': [
            {'formula': 'MktCap > 500', 'type': 'long'},
            {'formula': 'Close(0) > 5', 'type': 'long'}
        ]
    },
    'startDt': '2010-01-01',
    # Optional
    'endDt': '2025-01-01',
    'transPrice': 1,             # 1=Open, 3=Avg Hi/Low, 4=Close
    'maxPosPct': 0,
    'slippage': 0.25,
    'longWeight': 100,
    'shortWeight': 100,
    'rankTolerance': 0,
    'carryCost': 0,
    'rebalFreq': 'Every 4 Weeks',
    'riskStatsPeriod': 'Monthly'  # Monthly | Weekly | Daily
}, True)
```

```python
# Option 2: Existing screen by ID (preferred for user-created screens)
backtest = client.screen_backtest({
    'screen': 315954,           # integer screen ID from P123 platform
    'startDt': '2006-01-01',    # membership tier limits earliest date
    'endDt': '2026-03-31',
    'rebalFreq': 'Every 4 Weeks',
    'slippage': 0.5,            # percentage, not decimal
    'transPrice': 1,
    'precision': 2,
    'pitMethod': 'Prelim',
    'riskStatsPeriod': 'Monthly'
}, True)
```

### screen_rolling_backtest() — Rolling backtests (5 credits)

```python
client.screen_rolling_backtest({
    'screen': 12345,
    'startDt': '2010-01-01',
    'endDt': '2025-01-01',
    'frequency': 'Every 4 Weeks',
    'holdingPeriod': 182,        # days
    'slippage': 0.25,
    'transPrice': 1
})
```

---

## Strategy <a name="strategy"></a>

### strategy() — Get strategy summary & statistics (1 credit)

```python
client.strategy(strategy_id=12345)
```

### strategy_holdings() — Get current/historical holdings (1 credit)

```python
client.strategy_holdings(
    strategy_id=12345,
    date='2025-03-08',    # None for today
    to_pandas=True
)
```

### strategy_rebalance() — Get rebalance recommendations (1 credit)

```python
client.strategy_rebalance(
    strategy_id=12345,
    params={
        'pitMethod': 'Complete',
        'op': 'Rebal',          # Rebal | Recon | ReconRebal (for Dynamic Weight)
        'reject': [],            # list of P123 IDs to reject
        'figi': 'Share Class'
    }
)
```

### strategy_rebalance_commit() — Commit transactions (1 credit)

```python
client.strategy_rebalance_commit(
    strategy_id=12345,
    params={
        'op': '<op from rebalance>',
        'ranks': '<ranks from rebalance>',
        'trans': [
            {'p123Uid': 1073741824, 'action': 'BUY', 'price': 150.25,
             'shares': 100, 'comm': 1.0, 'slip': 0.1, 'note': 'API order'}
        ]
    }
)
```

### strategy_transactions() — Transaction history (1 credit)

```python
client.strategy_transactions(
    strategy_id=12345,
    start='2025-01-01',
    end='2025-03-08',
    to_pandas=True
)
```

### strategy_transaction_import() — Import transactions (1 credit)

```python
# CSV format: date,ticker,type,shares,price,commission,notes
# Types: BUY, SELL, COVER, SHORT, DIV, SPLIT, CASH
client.strategy_transaction_import(
    strategy_id=12345,
    data='2025-04-28,IBM,BUY,100,123.45,1.0,API import',
    content_type='text/csv',
    update_existing=False,
    make_rebal_dt_curr=False
)

# Or from file
client.strategy_transaction_import(
    strategy_id=12345,
    data=open('transactions.csv'),
    content_type='text/csv'
)
```

### strategy_transaction_delete() — Delete transactions (1 credit)

```python
client.strategy_transaction_delete(strategy_id=12345, items=[tranId1, tranId2])
```

---

## Data Series & Stock Factors <a name="data-series"></a>

### Custom Data Series (time series of values by date)

```python
# Create
result = client.data_series_create_update({
    'name': 'My Custom Series',
    'description': 'VIX daily values'
})
series_id = result['id']

# Upload data (CSV: date,value)
client.data_series_upload(
    file='series_data.csv',
    series_id=series_id,
    existing_data='overwrite',
    date_format='yyyy-mm-dd',
    decimal_separator='.',
    contains_header_row=True
)

# Delete
client.data_series_delete(series_id=series_id)
```

Use in formulas as: `DataSeries("My Custom Series")` or by ID.

### Custom Stock Factors (values by date × ticker)

```python
# Create
result = client.stock_factor_create_update({
    'name': 'MyMLSignal',
    'description': 'ML prediction scores'
})
factor_id = result['id']

# Upload data (CSV: date,ticker,value)
client.stock_factor_upload(
    file='factors.csv',
    factor_id=factor_id,
    column_separator='comma',
    existing_data='overwrite',
    date_format='yyyy-mm-dd'
)

# Delete
client.stock_factor_delete(factor_id=factor_id)
```

Use in formulas as: `StockFactor("MyMLSignal")` or by ID.

---

## AI Factor <a name="ai-factor"></a>

P123 has built-in AI Factor functionality for machine learning predictions. See the P123 help center for AI Factor API details.

---

## API Credits & Limits <a name="credits"></a>

| Operation | Credits |
|-----------|---------|
| data | 1 per 100K data points |
| data_prices | 1 per call |
| data_universe | 1 per 100K data points |
| universe_update | 1 |
| rank_ranks | 1 per 100K points (min 2) |
| rank_perf | 3 |
| rank_update | 1 |
| screen_run | 2 |
| screen_backtest | 5 |
| screen_rolling_backtest | 5 |
| strategy (all ops) | 1 each |
| data_series (all ops) | 1 each |
| stock_factor (all ops) | 1 each |

Error handling:

```python
try:
    result = client.screen_run({...})
except p123api.ClientException as e:
    print(f"API Error: {e}")
```

**Monthly quota:** 10,000 credits. Warn at 80% (8,000 used) and 95% (9,500 used).

---

## Authentication Best Practices

```python
import os
import p123api

# Use environment variables — never hardcode credentials
api_id = os.environ.get('P123_API_ID')
api_key = os.environ.get('P123_API_KEY')

# Context manager pattern (recommended)
with p123api.Client(api_id=api_id, api_key=api_key) as client:
    result = client.data_prices('SPY', start='2024-01-01', end='2024-01-01')
    print(f"Credits remaining: {result.get('quotaRemaining', 'unknown')}")
```

---

## Retry Logic

```python
from p123api import ClientException
import time

def api_call_with_retry(client, func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ClientException as e:
            err_str = str(e).lower()
            if ('quota' in err_str or 'timeout' in err_str) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    return None
```

Fail fast for auth/validation errors. Retry only for transient (quota, timeout).

---

## Credit Check Helper

```python
def check_credits(client):
    r = client.data_prices('SPY', start='2024-01-01', end='2024-01-01')
    remaining = r.get('quotaRemaining', 0)
    if remaining < 500:
        print("WARNING: Credits below 5% — confirm before expensive operations")
    elif remaining < 2000:
        print("WARNING: Credits below 20% — consider batching")
    return remaining
```

---

## Common Pitfalls

- **data_prices:** Use `start` and `end` (not `startDt`/`endDt`)
- **All other endpoints:** Use `startDt` and `endDt`
- **Rebalance frequency:** `'Every 4 Weeks'` not `'Every Month'`. Valid: Every Day, Every Week, Every 4 Weeks
- **Factor names:** Use `PEExclXorTTM`, `ROE%TTM` — not `#PE`, `#ROE`. Validate via `doc_detail.jsp`
- **data_universe:** May fail with "data license required"; use `data()` with tickers as fallback
- **Naming convention:** All agent-created resources MUST start with `agent` (strategies, screens, ranking systems)
- **Response keys:** API returns snake_case: `annualized_return`, `sharpe_ratio`, `max_drawdown`, `quotaRemaining`
- **Weekend dates:** Use Saturday/Sunday dates for `asOfDts` in `data_universe()` calls
- **screen_backtest startDt:** Standard membership restricts `startDt` to ~2006-01-01. Earlier dates are silently clamped. Check your subscription tier before setting dates before 2006.

---

## Export Convention

Save results to `./p123-output/{operation}_{timestamp}.{csv|json}`.

Example: `screen_backtest_20260312_143022.csv`
