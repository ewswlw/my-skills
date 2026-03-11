# Test Specification — Vectorbt Tearsheet

Create `tests/test_tearsheet.py` with the following 8 test cases. All tests use synthetic data to avoid external dependencies.

---

## Synthetic Data Fixture

Use this pattern as a shared pytest fixture:

```python
import pytest
import pandas as pd
import numpy as np
import vectorbt as vbt


@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio with known properties."""
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=260, freq="W")
    price = pd.Series(
        100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 260)),
        index=dates,
    )
    entries = pd.Series(False, index=dates)
    entries.iloc[::10] = True  # Entry every 10 weeks
    exits = pd.Series(False, index=dates)
    exits.iloc[5::10] = True  # Exit 5 weeks after each entry

    pf = vbt.Portfolio.from_signals(
        price, entries, exits, init_cash=10000, freq="W"
    )
    benchmark_rets = price.pct_change().dropna()
    return pf, benchmark_rets, entries


@pytest.fixture
def empty_portfolio():
    """Portfolio with no trades (all-zero signals)."""
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=100, freq="W")
    price = pd.Series(
        100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 100)),
        index=dates,
    )
    entries = pd.Series(False, index=dates)
    exits = pd.Series(False, index=dates)
    pf = vbt.Portfolio.from_signals(
        price, entries, exits, init_cash=10000, freq="W"
    )
    return pf


@pytest.fixture
def short_portfolio():
    """Portfolio with <1 year of data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=30, freq="W")
    price = pd.Series(
        100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 30)),
        index=dates,
    )
    entries = pd.Series(False, index=dates)
    entries.iloc[0] = True
    exits = pd.Series(False, index=dates)
    exits.iloc[15] = True
    pf = vbt.Portfolio.from_signals(
        price, entries, exits, init_cash=10000, freq="W"
    )
    return pf
```

---

## Test Cases

### 1. Smoke test

```python
def test_smoke(sample_portfolio):
    pf, benchmark_rets, entries = sample_portfolio
    result = generate_tearsheet(pf, benchmark_rets, entries)
    assert isinstance(result, dict)
    assert "portfolio_stats" in result
    assert "returns_stats" in result
    assert "trades_stats" in result
```

### 2. No benchmark

```python
def test_no_benchmark(sample_portfolio):
    pf, _, entries = sample_portfolio
    result = generate_tearsheet(pf, benchmark_rets=None, entries=entries)
    assert isinstance(result, dict)
    # Benchmark columns should not cause errors
```

### 3. No entries

```python
def test_no_entries(sample_portfolio):
    pf, benchmark_rets, _ = sample_portfolio
    result = generate_tearsheet(pf, benchmark_rets, entries=None)
    # Table 6 (Signals Stats) should be absent or None
    assert result.get("signals_stats") is None
```

### 4. No trades

```python
def test_no_trades(empty_portfolio):
    result = generate_tearsheet(empty_portfolio)
    assert isinstance(result, dict)
    # Trade tables should handle empty state without error
```

### 5. Single trade

```python
def test_single_trade():
    dates = pd.date_range("2023-01-01", periods=20, freq="W")
    price = pd.Series(range(100, 120), index=dates, dtype=float)
    entries = pd.Series(False, index=dates)
    entries.iloc[0] = True
    exits = pd.Series(False, index=dates)
    exits.iloc[10] = True
    pf = vbt.Portfolio.from_signals(
        price, entries, exits, init_cash=10000, freq="W"
    )
    result = generate_tearsheet(pf)
    trade_log = result.get("trade_log")
    assert trade_log is not None
    assert len(trade_log) == 1
    # Verify computed columns exist in the output text
    # # Days should be ~70 (10 weeks * 7 days)
    # Max Loss should be 0.00% (price only goes up)
    # Max Gain should be positive (price rises from 100 to 110)
```

### 6. Short data

```python
def test_short_data(short_portfolio):
    result = generate_tearsheet(short_portfolio)
    period_returns = result.get("period_returns", {})
    # Windows longer than data should be N/A
    assert period_returns.get("1Y") == "N/A"
    assert period_returns.get("3Y (ann.)") == "N/A"
    assert period_returns.get("5Y (ann.)") == "N/A"
    assert period_returns.get("10Y (ann.)") == "N/A"
```

### 7. Markdown export

```python
def test_markdown_export(sample_portfolio, tmp_path):
    pf, benchmark_rets, entries = sample_portfolio
    md_file = tmp_path / "test_tearsheet.md"
    generate_tearsheet(
        pf, benchmark_rets, entries,
        export_md=True, md_path=str(md_file),
    )
    assert md_file.exists()
    content = md_file.read_text()
    assert "## Portfolio Stats" in content
    assert "## Returns Stats" in content
    assert "## Trade-by-Trade" in content
```

### 8. Custom metrics accuracy

```python
def test_custom_metrics(sample_portfolio):
    pf, _, _ = sample_portfolio
    result = generate_tearsheet(pf)
    dd_details = result.get("drawdown_details", {})

    # Recovery Factor = total_return / abs(max_drawdown)
    total_ret = pf.total_return()
    max_dd = pf.drawdowns.max_drawdown()
    expected_rf = total_ret / abs(max_dd) if max_dd != 0 else float("inf")
    assert abs(dd_details["Recovery Factor"] - expected_rf) < 1e-6

    # Ulcer Index = sqrt(mean(drawdown_pct^2))
    value = pf.value()
    rolling_max = value.expanding().max()
    dd_pct = (value - rolling_max) / rolling_max
    expected_ui = np.sqrt((dd_pct ** 2).mean())
    assert abs(dd_details["Ulcer Index"] - expected_ui) < 1e-6
```

---

## Edge Case Matrix

| Scenario | Tables Affected | Expected Behavior |
|----------|----------------|-------------------|
| No trades | 3, 4, 7 | Empty tables, no error |
| No benchmark | 1, 2, 5, 8-11 | Benchmark column omitted |
| No entries | 6 | Table 6 skipped entirely |
| Data < 1 year | 8 | 1Y, 3Y, 5Y, 10Y = "N/A" |
| Data < 1 month | 8, 9, 11, 12 | MTD still works; monthly metrics may be sparse |
| Single trade | 3, 7 | One row in trade log; # Days, Max Loss, Max Gain computed; stats still compute |
| All winning trades | 3, 10 | Avg Losing Trade = N/A; Recovery Factor may be high |
| All losing trades | 3, 10 | Avg Winning Trade = N/A; Profit Factor = 0 |
| Max drawdown = 0 | 10 | Recovery Factor = inf; Serenity Index = inf |
