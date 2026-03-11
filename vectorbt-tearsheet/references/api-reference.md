# Vectorbt API Reference — Native Stats Methods

Full metric tables for Tables 1-7 of the tearsheet. Read this file when you need exact metric names, keys, and notes for each native vectorbt stats method.

---

## Critical: Frequency Must Be Set

If `freq=` is not passed when creating the Portfolio, all duration-based and annualized metrics (Sharpe, Calmar, Omega, Sortino, annualized return/volatility) will raise `UserWarning` and return NaN.

```python
# Always pass freq=
pf = vbt.Portfolio.from_signals(
    close=price,
    entries=entries,
    exits=exits,
    init_cash=10000,
    freq="W",  # "D" for daily, "W" for weekly, "M" for monthly
)
```

---

## Table 1 — Portfolio Stats: `pf.stats()`

| Metric | Key | Notes |
|--------|-----|-------|
| Start | `start` | First date in data |
| End | `end` | Last date in data |
| Period | `period` | Duration as timedelta |
| Start Value | `start_value` | Initial cash |
| End Value | `end_value` | Final portfolio value |
| Total Return [%] | `total_return` | Cumulative return |
| Benchmark Return [%] | `benchmark_return` | Requires benchmark_rets at Portfolio creation |
| Max Gross Exposure [%] | `max_gross_exposure` | Peak exposure |
| Total Fees Paid | `total_fees_paid` | Sum of all fees |
| Max Drawdown [%] | `max_dd` | Deepest peak-to-trough |
| Max Drawdown Duration | `max_dd_duration` | Longest drawdown period |
| Total Trades | `total_trades` | Including open trades |
| Total Closed Trades | `total_closed_trades` | Completed round-trips |
| Total Open Trades | `total_open_trades` | Still open at end |
| Open Trade PnL | `open_trade_pnl` | Unrealized P&L |
| Win Rate [%] | `win_rate` | % of trades profitable |
| Best Trade [%] | `best_trade` | Highest single-trade return |
| Worst Trade [%] | `worst_trade` | Lowest single-trade return |
| Avg Winning Trade [%] | `avg_winning_trade` | Mean return of winners |
| Avg Losing Trade [%] | `avg_losing_trade` | Mean return of losers |
| Avg Winning Trade Duration | `avg_winning_trade_duration` | Mean duration of winners |
| Avg Losing Trade Duration | `avg_losing_trade_duration` | Mean duration of losers |
| Profit Factor | `profit_factor` | Gross profit / gross loss |
| Expectancy | `expectancy` | Average trade P&L |
| Sharpe Ratio | `sharpe_ratio` | Requires freq |
| Calmar Ratio | `calmar_ratio` | Requires freq |
| Omega Ratio | `omega_ratio` | Requires freq |
| Sortino Ratio | `sortino_ratio` | Requires freq |

### Tag-based filtering

```python
# Only trade metrics
pf.stats(tags=['trades'])

# Only portfolio-level metrics
pf.stats(tags=['portfolio'])

# Include open trades
pf.stats(settings=dict(incl_open=True))
```

---

## Table 2 — Returns Stats: `returns.vbt.returns(freq=).stats()`

```python
returns = pf.returns()
ret_acc = returns.vbt.returns(freq="W")

# Without benchmark
ret_stats = ret_acc.stats()

# With benchmark (adds Alpha and Beta)
ret_stats = ret_acc.stats(settings=dict(benchmark_rets=benchmark_rets))

# With custom risk-free rate
ret_stats = ret_acc.stats(settings=dict(benchmark_rets=benchmark_rets, risk_free=0.02))
```

| Metric | Notes |
|--------|-------|
| Start | Index start |
| End | Index end |
| Duration | Total duration |
| Total Return [%] | Cumulative |
| Benchmark Return [%] | Only with benchmark_rets |
| Annualized Return [%] | CAGR |
| Annualized Volatility [%] | Std * sqrt(ann_factor) |
| Sharpe Ratio | Annualized |
| Calmar Ratio | Return / max drawdown |
| Max Drawdown [%] | Peak to trough |
| Omega Ratio | Threshold = 0 |
| Sortino Ratio | Downside deviation |
| Skew | Return distribution skewness |
| Kurtosis | Return distribution kurtosis |
| Tail Ratio | Right tail / left tail |
| Common Sense Ratio | Tail ratio * profit factor |
| Value at Risk | 5th percentile of returns |
| Alpha | Only with benchmark_rets; Jensen's alpha |
| Beta | Only with benchmark_rets; market sensitivity |

---

## Table 3 — Trades Stats: `pf.trades.stats()`

| Metric | Notes |
|--------|-------|
| Start | First trade date |
| End | Last trade date |
| Period | Total trading period |
| Total Records | Number of trade records |
| Total Long Trades | Count of long trades |
| Total Short Trades | Count of short trades |
| Total Closed Trades | Completed trades |
| Total Open Trades | Still open |
| Open Trade PnL | Unrealized P&L |
| Win Rate [%] | Percentage profitable |
| Max Win Streak | Consecutive wins |
| Max Loss Streak | Consecutive losses |
| Best Trade [%] | Highest return |
| Worst Trade [%] | Lowest return |
| Avg Winning Trade [%] | Mean winning return |
| Avg Losing Trade [%] | Mean losing return |
| Avg Winning Trade Duration | Mean winner duration |
| Avg Losing Trade Duration | Mean loser duration |
| Profit Factor | Gross profits / gross losses |
| Expectancy | Average P&L per trade |
| SQN | System Quality Number |

### Additional trade accessors

```python
pf.trades.winning           # Filtered: winning trades only
pf.trades.losing            # Filtered: losing trades only
pf.trades.winning.count()   # Count of winners
pf.trades.losing.count()    # Count of losers
pf.trades.profit_factor()   # Scalar profit factor
pf.trades.expectancy()      # Scalar expectancy
pf.trades.win_rate()        # Scalar win rate
```

---

## Table 4 — Positions Stats: `pf.positions.stats()`

Same structure as trades stats but grouped by positions. Positions aggregate multiple entry/exit trades into single position records.

```python
positions_stats = pf.positions.stats()
positions_df = pf.positions.records_readable  # DataFrame
```

---

## Table 5 — Drawdowns Stats: `pf.drawdowns.stats()`

| Metric | Notes |
|--------|-------|
| Start | First drawdown |
| End | Last drawdown |
| Period | Total period |
| Total Records | Number of drawdown events |
| Total Recovered Drawdowns | Count that fully recovered |
| Total Active Drawdowns | Still in drawdown at end |
| Active Drawdown [%] | Current drawdown depth |
| Active Duration | How long current DD has lasted |
| Max Drawdown [%] | Deepest drawdown |
| Avg Drawdown [%] | Mean drawdown depth |
| Max Drawdown Duration | Longest drawdown |
| Avg Drawdown Duration | Mean drawdown duration |
| Max Recovery Duration | Longest recovery time |
| Avg Recovery Duration | Mean recovery time |

### Additional drawdown accessors

```python
pf.drawdowns.max_drawdown()          # Scalar max drawdown
pf.drawdowns.drawdown.mean()         # Scalar avg drawdown
pf.drawdowns.duration.mean()         # Scalar avg DD duration
pf.drawdowns.records_readable        # Drawdown-by-drawdown DataFrame
```

---

## Table 6 — Signals Stats: `entries.vbt.signals.stats()`

Only available when `entries` (bool pd.Series) is provided.

| Metric | Notes |
|--------|-------|
| Start | First index |
| End | Last index |
| Period | Duration |
| Total | Total number of True signals |
| Rate [%] | Percentage of periods with True signal |

---

## Table 7 — Trade-by-Trade: `pf.trades.records_readable` + Computed Columns

Returns a DataFrame with one row per trade. Native columns from vectorbt plus 3 computed columns.

### Native columns (from `pf.trades.records_readable`)

| Column | Description |
|--------|-------------|
| Trade Id | Sequential trade identifier |
| Column | Asset column (for multi-asset portfolios) |
| Size | Position size |
| Entry Timestamp | When the trade was entered |
| Avg Entry Price | Volume-weighted entry price |
| Entry Fees | Fees paid on entry |
| Exit Timestamp | When the trade was exited |
| Avg Exit Price | Volume-weighted exit price |
| Exit Fees | Fees paid on exit |
| PnL | Profit or loss in currency |
| Return | Return as decimal (format as %) |
| Direction | Long or Short |
| Status | Open or Closed |
| Parent Id | Parent position identifier |

### Computed columns (added after Return)

| Column | Description | Computation |
|--------|-------------|-------------|
| # Days | Calendar days in the trade | `(Exit Timestamp - Entry Timestamp).days`. For open trades (Exit Timestamp is NaT), use `pf.close.index[-1]` as the exit reference. Format as integer. |
| Max Loss | Worst return vs entry price at any observation during the trade | Slice `pf.close` from entry to exit date, compute `(prices - entry_px) / entry_px`, take `.min()`. Format as percentage. |
| Max Gain | Best return vs entry price at any observation during the trade | Same price slice, take `.max()`. Format as percentage. |

### Display column order

```
Entry Date | Exit Date | Entry Px | Exit Px | PnL | Return | # Days | Max Loss | Max Gain | Direction | Status
```

### Usage

```python
trade_log = pf.trades.records_readable
close_prices = pf.close
last_date = close_prices.index[-1]

# Compute per-trade metrics
for _, row in trade_log.iterrows():
    entry_ts = row["Entry Timestamp"]
    exit_ts = row["Exit Timestamp"]
    entry_px = row["Avg Entry Price"]

    exit_ref = last_date if pd.isna(exit_ts) else exit_ts

    # Calendar days
    days = (exit_ref - entry_ts).days

    # Max Loss / Max Gain
    trade_prices = close_prices.loc[entry_ts:exit_ref]
    intra_returns = (trade_prices - entry_px) / entry_px
    max_loss = float(intra_returns.min())
    max_gain = float(intra_returns.max())
```

---

## Other Useful Methods

| Method | Returns |
|--------|---------|
| `pf.returns()` | Return series (pd.Series) |
| `pf.value()` | Equity curve (pd.Series) |
| `pf.cash()` | Cash series (pd.Series) |
| `pf.total_return()` | Scalar total return |
| `pf.gross_exposure()` | Gross exposure series |
| `pf.net_exposure()` | Net exposure series |
| `pf.orders.stats()` | Order analytics (Series) |
| `pf.orders.records_readable` | Order-by-order DataFrame |
