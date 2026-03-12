# Portfolio123 API Reference

Complete p123api endpoint reference, auth, credits, error handling, and code examples.

## Auth Setup

```python
import os
import p123api

# Use environment variables — never hardcode
api_id = os.environ.get('P123_API_ID')
api_key = os.environ.get('P123_API_KEY')

# Context manager pattern (recommended)
with p123api.Client(api_id=api_id, api_key=api_key) as client:
    result = client.data_prices('SPY', start='2024-01-01', end='2024-01-01')
    print(f"Credits remaining: {result.get('quotaRemaining', 'unknown')}")
```

**Credentials:** Account Settings → DataMiner & API on portfolio123.com

## Credit Cost Table

| Endpoint | Credits | Notes |
|----------|---------|-------|
| data_prices | 1 | Per request |
| data | TBD | Log via continual learning on first use |
| data_universe | TBD | Requires data license |
| rank_update | TBD | |
| rank_ranks | TBD | |
| rank_perf | TBD | |
| screen_run | 2 | Per request |
| screen_backtest | 5 | Per request |
| screen_rolling_backtest | ~5-10 | Estimate; log actual |
| strategy_get | TBD | |
| strategy_holdings | TBD | |
| aifactor_predict | TBD | |

**Monthly quota:** 10,000 credits. Warn at 80% (8,000 used) and 95% (9,500 used).

## Error Handling with Retry

```python
from p123api import ClientException
import time

def api_call_with_retry(client, func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs) if not kwargs else func(*args, **kwargs)
        except ClientException as e:
            err_str = str(e).lower()
            if ('quota' in err_str or 'timeout' in err_str) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    return None
```

**Fail fast** for auth/validation errors. **Retry** only for transient (quota, timeout).

## Response Format

API returns **snake_case** keys: `annualized_return`, `sharpe_ratio`, `total_return`, `max_drawdown`, `standard_dev`, `sortino_ratio`, `quotaRemaining`.

## Endpoints

### data_prices

```python
result = client.data_prices(
    identifier='SPY',  # or ticker string
    start='2024-01-01',
    end='2024-01-31'
)
# 1 credit. Use start/end (not startDt/endDt)
```

### data (factor data)

```python
data = client.data({
    'tickers': ['IBM', 'INTC', 'MSFT'],
    'formulas': ['PEExclXorTTM', 'ROE%TTM'],  # Use validated names from factor-quickref
    'startDt': '2024-01-01',
    'endDt': '2024-01-31',
    'pitMethod': 'Complete',
    'precision': 2
})
```

### data_universe

```python
data = client.data_universe({
    'universe': 'sp500',
    'formulas': ['PEExclXorTTM', 'ROE%TTM'],
    'asOfDts': ['2024-01-01', '2024-01-15', '2024-01-31']
})
# Many factors require data license; use data() with tickers as fallback
```

### rank_update

```python
# Pass XML string. Label MUST start with "agent"
client.rank_update(xml_string)
```

### rank_ranks

```python
rankings = client.rank_ranks({
    'rankingSystem': 'agent_value_momentum',
    'universe': 'sp500',
    'asOfDt': '2024-01-15'
})
```

### rank_perf

```python
perf = client.rank_perf({
    'rankingSystem': 'agent_value_momentum',
    'universe': 'sp500',
    'startDt': '2023-01-01',
    'endDt': '2024-01-01',
    'rebalFreq': 'Every 4 Weeks'  # Valid: Every Day, Every Week, Every 4 Weeks
})
```

### screen_run

```python
result = client.screen_run({
    'screen': {'type': 'stock', 'universe': 'nasdaq100'},
    'asOfDt': '2024-01-15'
})
# 2 credits
```

### screen_backtest

```python
backtest = client.screen_backtest({
    'screen': {'type': 'stock', 'universe': 'nasdaq100'},
    'startDt': '2023-01-01',
    'endDt': '2024-01-01',
    'rebalFreq': 'Every 4 Weeks'
})
# 5 credits
```

### screen_rolling_backtest

```python
rolling = client.screen_rolling_backtest({
    'screen': {'type': 'stock', 'universe': 'nasdaq100'},
    'startDt': '2023-01-01',
    'endDt': '2024-01-01',
    'holdingPeriod': 252,
    'frequency': 'Every 4 Weeks'
})
```

### strategy_get, strategy_holdings

```python
strategy = client.strategy_get(strategy_id='12345')
holdings = client.strategy_holdings(strategy_id='12345')
# Read-only. Strategy must exist (created on platform). Name must start with "agent"
```

### aifactor_predict

```python
predictions = client.aifactor_predict(
    predictor_id='12345',
    {
        'universe': 'sp500',
        'asOfDt': '2024-01-15',
        'precision': 4,
        'includeNames': True
    }
)
```

## Common Pitfalls

- **data_prices:** Use `start` and `end` (not startDt/endDt)
- **Other endpoints:** Use `startDt` and `endDt`
- **Rebalance frequency:** `'Every 4 Weeks'` not `'Every Month'`. Valid: Every Day, Every Week, Every 4 Weeks
- **Factor names:** Use PEExclXorTTM, ROE%TTM — not #PE, #ROE. Validate via doc_detail.jsp
- **data_universe:** Often fails with "data license required"; use data() with tickers instead

## Credit Check Helper

```python
def check_credits(client):
    r = client.data_prices('SPY', start='2024-01-01', end='2024-01-01')
    remaining = r.get('quotaRemaining', 0)
    if remaining < 500:
        print("⚠️ Credits below 5% — confirm before expensive operations")
    elif remaining < 2000:
        print("⚠️ Credits below 20% — consider batching")
    return remaining
```

## Export Convention

Save results to `./p123-output/{operation}_{timestamp}.{csv|json}`. Example: `screen_backtest_20260312_143022.csv`.
