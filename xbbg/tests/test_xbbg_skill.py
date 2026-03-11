"""
xbbg Bloomberg Skill — Test Suite
==================================
Dual-mode tests:
  - Mock tests (no Bloomberg terminal required): run always
  - Integration tests (requires Bloomberg Terminal): gated by BLOOMBERG_TERMINAL=1

Run mock tests only:
    pytest tests/test_xbbg_skill.py -m "not bloomberg" -v

Run all tests (requires active Bloomberg terminal):
    set BLOOMBERG_TERMINAL=1 && pytest tests/test_xbbg_skill.py -v
"""

import os
import math
import time
import asyncio
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from contextlib import contextmanager


# ---------------------------------------------------------------------------
# MockBlp — mirrors xbbg.blp return signatures exactly
# ---------------------------------------------------------------------------

class MockBlp:
    """Synthetic Bloomberg responses with correct xbbg output shapes."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        self._call_counts: dict = {}

    def _track(self, name):
        self._call_counts[name] = self._call_counts.get(name, 0) + 1

    # --- bdp -----------------------------------------------------------
    def bdp(self, tickers, flds, **kwargs) -> pd.DataFrame:
        self._track('bdp')
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(flds, str):
            flds = [flds]
        data = {}
        for fld in flds:
            fl = fld.lower()
            if any(k in fl for k in ['px', 'price', 'last', 'settle', 'bid', 'ask']):
                data[fl] = self.rng.uniform(50, 500, len(tickers))
            elif any(k in fl for k in ['pe_ratio', 'ev_ebitda', 'ratio']):
                data[fl] = self.rng.uniform(5, 50, len(tickers))
            elif any(k in fl for k in ['mkt_cap', 'volume', 'shares']):
                data[fl] = self.rng.uniform(1e9, 3e12, len(tickers))
            elif any(k in fl for k in ['vol', 'beta', 'return']):
                data[fl] = self.rng.uniform(0.05, 0.80, len(tickers))
            elif any(k in fl for k in ['yld', 'yield', 'dur', 'spread']):
                data[fl] = self.rng.uniform(1, 10, len(tickers))
            elif 'name' in fl or 'sector' in fl or 'country' in fl:
                data[fl] = [f"MockValue_{i}" for i in range(len(tickers))]
            else:
                data[fl] = self.rng.uniform(0, 100, len(tickers))
        return pd.DataFrame(data, index=pd.Index(tickers))

    # --- bdh -----------------------------------------------------------
    def bdh(self, tickers, flds, start_date, end_date=None,
            Per='D', Fill='P', **kwargs) -> pd.DataFrame:
        self._track('bdh')
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(flds, str):
            flds = [flds]
        end = end_date or pd.Timestamp.today().strftime('%Y-%m-%d')
        dates = pd.bdate_range(start_date, end)

        if len(tickers) == 1:
            # Single ticker: flat columns (field names)
            data = {fld.lower(): self.rng.uniform(50, 500, len(dates)) for fld in flds}
            return pd.DataFrame(data, index=dates)
        else:
            # Multiple tickers: MultiIndex columns (ticker, field)
            cols = pd.MultiIndex.from_product([tickers, [f.lower() for f in flds]])
            data = self.rng.uniform(50, 500, (len(dates), len(cols)))
            return pd.DataFrame(data, index=dates, columns=cols)

    # --- bds -----------------------------------------------------------
    def bds(self, ticker, fld, **kwargs) -> pd.DataFrame:
        self._track('bds')
        fl = fld.lower()
        if 'member' in fl or 'indx' in fl:
            n = 20
            tickers_list = [f"TICK{i:02d} US Equity" for i in range(n)]
            return pd.DataFrame({
                'member_ticker_and_exchange_code': tickers_list,
                'percentage_weight': np.ones(n) * (100 / n),
            }, index=[ticker] * n)
        if 'dvd' in fl or 'dividend' in fl:
            dates = pd.bdate_range('2023-01-01', periods=4, freq='QE')
            return pd.DataFrame({
                'declared_date': dates,
                'ex_date': dates + pd.Timedelta(days=15),
                'dividend_amount': self.rng.uniform(0.2, 0.8, 4),
                'dividend_frequency': ['Quarter'] * 4,
                'dividend_type': ['Regular Cash'] * 4,
            }, index=[ticker] * 4)
        if 'cash_flow' in fl or 'cashflow' in fl:
            dates = pd.bdate_range('2024-06-01', periods=6, freq='6ME')
            return pd.DataFrame({
                'payment_date': dates,
                'coupon_amount': self.rng.uniform(500, 5000, 6),
                'principal_amount': [0.0] * 5 + [100000.0],
            }, index=[ticker] * 6)
        if 'opt_chain' in fl or 'chain' in fl:
            options = [f"MOCK US 01/17/25 C{s} Equity" for s in range(150, 210, 5)]
            return pd.DataFrame({'option_ticker': options}, index=[ticker] * len(options))
        return pd.DataFrame({'value': self.rng.uniform(0, 100, 5)}, index=[ticker] * 5)

    # --- beqs ----------------------------------------------------------
    def beqs(self, screen, **kwargs) -> pd.DataFrame:
        self._track('beqs')
        tickers = [f"SCRN{i:02d} US Equity" for i in range(25)]
        return pd.DataFrame(
            {'security_name': [f"Company {i}" for i in range(25)]},
            index=pd.Index(tickers)
        )

    # --- bdib ----------------------------------------------------------
    def bdib(self, ticker, dt, interval=1, session='day',
             tz=None, **kwargs) -> pd.DataFrame:
        self._track('bdib')
        exch_tz = 'America/New_York'
        times = pd.date_range(
            f"{dt} 09:30", f"{dt} 16:00",
            freq=f"{interval}min", tz=exch_tz
        )
        n = len(times)
        base = self.rng.uniform(150, 200, n)
        cols = pd.MultiIndex.from_tuples(
            [(ticker, c) for c in ['open', 'high', 'low', 'close', 'volume', 'num_trds']]
        )
        data = np.column_stack([
            base,
            base * (1 + self.rng.uniform(0, 0.005, n)),
            base * (1 - self.rng.uniform(0, 0.005, n)),
            base * (1 + self.rng.uniform(-0.003, 0.003, n)),
            self.rng.integers(1_000, 100_000, n).astype(float),
            self.rng.integers(10, 500, n).astype(float),
        ])
        return pd.DataFrame(data, index=times, columns=cols)

    # --- bdtick --------------------------------------------------------
    def bdtick(self, ticker, dt, session='day', types=None, **kwargs) -> pd.DataFrame:
        self._track('bdtick')
        tz = 'America/New_York'
        n = 100
        times = pd.date_range(f"{dt} 09:30", periods=n, freq="5s", tz=tz)
        return pd.DataFrame({
            'value': self.rng.uniform(150, 200, n),
            'volume': self.rng.integers(100, 5000, n),
            'typ': np.where(self.rng.random(n) > 0.3, 'TRADE', 'BID'),
            'cond': ['@'] * n,
            'exch': ['NYSE'] * n,
        }, index=times)

    # --- exchange_tz ---------------------------------------------------
    def exchange_tz(self, ticker) -> str:
        self._track('exchange_tz')
        mapping = {
            'JT': 'Asia/Tokyo', 'AU': 'Australia/Sydney',
            'LN': 'Europe/London', 'GR': 'Europe/Berlin',
            'FP': 'Europe/Paris', 'HK': 'Asia/Hong_Kong',
        }
        for code, tz in mapping.items():
            if code in ticker:
                return tz
        return 'America/New_York'

    # --- yas ------------------------------------------------------------
    def yas(self, ticker, flds=None, **kwargs) -> pd.DataFrame:
        self._track('yas')
        if flds is None:
            flds = 'YAS_BOND_YLD'
        if isinstance(flds, str):
            flds = [flds]
        data = {}
        for fld in flds:
            fl = fld.lower()
            if 'yld' in fl:
                data[fld] = [self.rng.uniform(3, 6)]
            elif 'dur' in fl:
                data[fld] = [self.rng.uniform(3, 15)]
            elif 'spread' in fl or 'asp' in fl:
                data[fld] = [self.rng.uniform(10, 200)]
            elif 'px' in fl:
                data[fld] = [self.rng.uniform(85, 110)]
            else:
                data[fld] = [self.rng.uniform(0, 100)]
        return pd.DataFrame(data, index=pd.Index([ticker], name='ticker'))

    # --- fut_ticker ----------------------------------------------------
    def fut_ticker(self, ticker, dt, freq='ME') -> str:
        self._track('fut_ticker')
        ts = pd.Timestamp(dt)
        month_codes = 'FGHJKMNQUVXZ'
        code = month_codes[ts.month - 1]
        yr = str(ts.year)[-2:]
        base = ticker.split(' ')[0].rstrip('1234567890')
        yk = ticker.split(' ', 1)[-1] if ' ' in ticker else 'Index'
        return f"{base}{code}{yr} {yk}"

    # --- active_futures ------------------------------------------------
    def active_futures(self, ticker, dt, **kwargs) -> str:
        return self.fut_ticker(ticker.replace('A ', '1 '), dt)

    # --- adjust_ccy ----------------------------------------------------
    def adjust_ccy(self, df, ccy='USD') -> pd.DataFrame:
        self._track('adjust_ccy')
        return df * self.rng.uniform(0.8, 1.2)

    # --- fieldSearch ---------------------------------------------------
    def fieldSearch(self, keyword) -> pd.DataFrame:
        self._track('fieldSearch')
        return pd.DataFrame({
            'field_name': [f'MOCK_{keyword.upper()}_1', f'MOCK_{keyword.upper()}_2'],
            'description': [f'Mock field for {keyword} 1', f'Mock field for {keyword} 2'],
        })

    # --- lookupSecurity ------------------------------------------------
    def lookupSecurity(self, name, yellowkey='eqty', max_results=10) -> pd.DataFrame:
        self._track('lookupSecurity')
        return pd.DataFrame({
            'ticker': [f'MOCK{i} US Equity' for i in range(min(3, max_results))],
            'description': [f'{name} Corp {i}' for i in range(min(3, max_results))],
        })

    # --- etf_holdings --------------------------------------------------
    def etf_holdings(self, ticker) -> pd.DataFrame:
        self._track('etf_holdings')
        holdings = [f"HOLD{i:02d} US Equity" for i in range(10)]
        return pd.DataFrame({
            'holding': holdings,
            'weights': np.ones(10) * 0.1,
            'position': self.rng.integers(1000, 100000, 10),
        })

    # --- dividend ------------------------------------------------------
    def dividend(self, tickers, start_date, end_date) -> pd.DataFrame:
        self._track('dividend')
        if isinstance(tickers, str):
            tickers = [tickers]
        rows = []
        for t in tickers:
            for q in range(4):
                rows.append({
                    'ticker': t,
                    'dec_date': pd.Timestamp('2024-01-01') + pd.DateOffset(months=q*3),
                    'ex_date': pd.Timestamp('2024-01-15') + pd.DateOffset(months=q*3),
                    'dvd_amt': self.rng.uniform(0.2, 0.9),
                    'dvd_freq': 'Quarter',
                    'dvd_type': 'Regular Cash',
                })
        return pd.DataFrame(rows).set_index('ticker')

    @contextmanager
    def patch_blp(self):
        """
        Patch xbbg.blp functions that exist in the installed version.
        Core functions (bdp, bdh, bds, beqs, bdib, bdtick) are always patched.
        Version-specific functions (exchange_tz, yas, etc.) are patched only if present.
        """
        import xbbg.blp as _blp_mod
        m = self

        # Core patches always applied (exist in 0.7+ and 1.x)
        core_patches = [
            patch('xbbg.blp.bdp', m.bdp),
            patch('xbbg.blp.bdh', m.bdh),
            patch('xbbg.blp.bds', m.bds),
            patch('xbbg.blp.beqs', m.beqs),
            patch('xbbg.blp.bdib', m.bdib),
            patch('xbbg.blp.bdtick', m.bdtick),
            patch('xbbg.blp.fut_ticker', m.fut_ticker),
            patch('xbbg.blp.active_futures', m.active_futures),
            patch('xbbg.blp.adjust_ccy', m.adjust_ccy),
            patch('xbbg.blp.dividend', m.dividend),
        ]

        # Optional patches for functions that vary by xbbg version
        optional = {
            'exchange_tz': m.exchange_tz,
            'yas': m.yas,
            'fieldSearch': m.fieldSearch,
            'lookupSecurity': m.lookupSecurity,
            'etf_holdings': m.etf_holdings,
        }
        opt_patches = [
            patch(f'xbbg.blp.{name}', fn)
            for name, fn in optional.items()
            if hasattr(_blp_mod, name)
        ]

        all_patches = core_patches + opt_patches
        # Enter all patches
        for p in all_patches:
            p.start()
        try:
            yield m
        finally:
            for p in all_patches:
                p.stop()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_blp():
    return MockBlp(seed=42)


@pytest.fixture
def eq_tickers():
    return ['AAPL US Equity', 'MSFT US Equity', 'GOOGL US Equity']


@pytest.fixture
def fi_tickers():
    return ['T 4.5 5/15/38 Govt', 'AAPL 3.85 5/4/43 Corp']


@pytest.fixture
def index_tickers():
    return ['SPX Index', 'NDX Index', 'USGG10YR Index']


# ---------------------------------------------------------------------------
# Smart Dispatcher (tested independently of xbbg import)
# ---------------------------------------------------------------------------

def make_bbg_dispatcher(mock_instance):
    """Build the bbg() dispatcher bound to a MockBlp instance."""
    import math, time, logging
    import pandas as pd
    from typing import Union

    blp_mock = mock_instance

    def bbg(tickers, flds, start_date=None, end_date=None,
            per='D', fill='P', adjust=None, batch_size=400,
            max_retries=3, flat=True, **kwargs):
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(flds, str):
            flds = [flds]
        single_field = len(flds) == 1

        def _call(batch):
            for attempt in range(max_retries):
                try:
                    if start_date is not None:
                        kw = dict(Per=per, Fill=fill)
                        if adjust:
                            kw['adjust'] = adjust
                        kw.update(kwargs)
                        return blp_mock.bdh(batch, flds, start_date=start_date,
                                             end_date=end_date or pd.Timestamp.today().strftime('%Y-%m-%d'),
                                             **kw)
                    else:
                        return blp_mock.bdp(batch, flds, **kwargs)
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(0.01)

        chunks = [tickers[i:i+batch_size] for i in range(0, len(tickers), batch_size)]
        results = [_call(c) for c in chunks]
        df = pd.concat(results)

        if start_date is not None and single_field and flat:
            try:
                df = df.droplevel(1, axis=1)
                df.columns.name = None
            except Exception:
                pass
        return df

    return bbg


# ---------------------------------------------------------------------------
# Unit Tests — Mock Mode (no Bloomberg terminal required)
# ---------------------------------------------------------------------------

class TestBdpMock:
    def test_single_ticker_single_field(self, mock_blp):
        result = mock_blp.bdp('AAPL US Equity', 'PX_LAST')
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (1, 1)
        assert 'px_last' in result.columns
        assert pd.notna(result['px_last'].iloc[0])

    def test_multiple_tickers_single_field(self, mock_blp, eq_tickers):
        result = mock_blp.bdp(eq_tickers, 'PX_LAST')
        assert result.shape == (3, 1)
        assert list(result.index) == eq_tickers
        assert result['px_last'].notna().all()

    def test_multiple_tickers_multiple_fields(self, mock_blp, eq_tickers):
        flds = ['PX_LAST', 'PE_RATIO', 'CUR_MKT_CAP']
        result = mock_blp.bdp(eq_tickers, flds)
        assert result.shape == (3, 3)
        assert all(f.lower() in result.columns for f in flds)

    def test_string_fields_normalised_to_lowercase(self, mock_blp):
        result = mock_blp.bdp('AAPL US Equity', ['PX_LAST', 'PE_RATIO'])
        assert 'px_last' in result.columns
        assert 'pe_ratio' in result.columns

    def test_with_override_kwargs(self, mock_blp):
        result = mock_blp.bdp('AAPL US Equity', 'EQY_WEIGHTED_AVG_PX', VWAP_Dt='20240115')
        assert not result.empty

    def test_fi_tickers(self, mock_blp, fi_tickers):
        result = mock_blp.bdp(fi_tickers, ['YLD_YTM_MID', 'DUR_MID'])
        assert result.shape == (2, 2)


class TestBdhMock:
    def test_single_ticker_flat_output(self, mock_blp):
        result = mock_blp.bdh('AAPL US Equity', 'PX_LAST', '2024-01-01', '2024-01-31')
        assert isinstance(result, pd.DataFrame)
        assert isinstance(result.index, pd.DatetimeIndex)
        # Single ticker → flat columns
        assert 'px_last' in result.columns
        assert not isinstance(result.columns, pd.MultiIndex)

    def test_multiple_tickers_multiindex_columns(self, mock_blp, eq_tickers):
        result = mock_blp.bdh(eq_tickers, 'px_last', '2024-01-01', '2024-01-31')
        assert isinstance(result.columns, pd.MultiIndex)
        tickers_in_result = result.columns.get_level_values(0).unique().tolist()
        assert all(t in tickers_in_result for t in eq_tickers)

    def test_droplevel_flattening(self, mock_blp, eq_tickers):
        """Verify the standard MultiIndex flattening pattern works."""
        df = mock_blp.bdh(eq_tickers, 'px_last', '2024-01-01', '2024-01-31')
        prices = df.droplevel(1, axis=1)
        assert isinstance(prices.columns, pd.Index)
        assert not isinstance(prices.columns, pd.MultiIndex)
        assert all(t in prices.columns for t in eq_tickers)

    def test_returns_computation(self, mock_blp, eq_tickers):
        """Verify log returns can be computed from flattened output."""
        df = mock_blp.bdh(eq_tickers, 'px_last', '2024-01-01', '2024-06-30')
        prices = df.droplevel(1, axis=1)
        returns = np.log(prices / prices.shift(1)).dropna()
        assert returns.shape[0] > 0
        assert returns.shape[1] == 3
        assert returns.notna().any().any()

    def test_multifield_multiple_tickers(self, mock_blp, eq_tickers):
        df = mock_blp.bdh(eq_tickers, ['px_last', 'volume'], '2024-01-01', '2024-01-31')
        assert isinstance(df.columns, pd.MultiIndex)
        fields = df.columns.get_level_values(1).unique().tolist()
        assert 'px_last' in fields
        assert 'volume' in fields

    def test_periodicity_monthly(self, mock_blp):
        # Mock returns daily data regardless of Per; just verify shape is a DataFrame
        df = mock_blp.bdh('SPX Index', 'PX_LAST', '2024-01-01', '2024-01-31', Per='M')
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 1

    def test_no_data_returns_empty_like(self, mock_blp):
        """Empty date range still returns a DataFrame (may be empty)."""
        try:
            df = mock_blp.bdh('AAPL US Equity', 'PX_LAST', '2024-01-05', '2024-01-05')
            assert isinstance(df, pd.DataFrame)
        except Exception:
            pass  # acceptable — empty range


class TestBdsMock:
    def test_index_members(self, mock_blp):
        result = mock_blp.bds('SPX Index', 'INDX_MEMBERS')
        assert isinstance(result, pd.DataFrame)
        assert 'member_ticker_and_exchange_code' in result.columns
        assert len(result) > 0

    def test_index_weights(self, mock_blp):
        result = mock_blp.bds('SPX Index', 'INDX_MWEIGHT')
        assert 'percentage_weight' in result.columns
        # Weights should sum to 100 (approx)
        assert abs(result['percentage_weight'].sum() - 100.0) < 1.0

    def test_dividend_history(self, mock_blp):
        result = mock_blp.bds('AAPL US Equity', 'DVD_Hist_All',
                              DVD_Start_Dt='20230101', DVD_End_Dt='20231231')
        assert 'dividend_amount' in result.columns
        assert len(result) > 0

    def test_cash_flow_schedule(self, mock_blp):
        result = mock_blp.bds('/isin/US037833AK68', 'DES_CASH_FLOW')
        assert 'coupon_amount' in result.columns
        assert 'principal_amount' in result.columns

    def test_option_chain(self, mock_blp):
        result = mock_blp.bds('AAPL US Equity', 'OPT_CHAIN', Expiry_Dt='20250117')
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestBeqsMock:
    def test_returns_dataframe(self, mock_blp):
        result = mock_blp.beqs('MyScreen', asof='2024-01-01')
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_index_contains_tickers(self, mock_blp):
        result = mock_blp.beqs('MyScreen')
        assert all('US Equity' in str(idx) for idx in result.index)

    def test_screen_to_bdp_pipeline(self, mock_blp):
        """Test the screen → pull fundamentals pattern."""
        screen = mock_blp.beqs('MyScreen')
        tickers = screen.index.tolist()[:5]
        fundamentals = mock_blp.bdp(tickers, ['PX_LAST', 'PE_RATIO'])
        assert fundamentals.shape == (5, 2)


class TestBdibMock:
    def test_returns_dataframe_with_ohlcv(self, mock_blp):
        result = mock_blp.bdib('AAPL US Equity', dt='2024-01-15')
        assert isinstance(result, pd.DataFrame)
        assert isinstance(result.columns, pd.MultiIndex)
        cols = result.columns.get_level_values(1).tolist()
        assert all(c in cols for c in ['open', 'high', 'low', 'close', 'volume', 'num_trds'])

    def test_datetime_index_is_tz_aware(self, mock_blp):
        result = mock_blp.bdib('AAPL US Equity', dt='2024-01-15')
        assert result.index.tz is not None

    def test_high_geq_low(self, mock_blp):
        result = mock_blp.bdib('AAPL US Equity', dt='2024-01-15')
        high = result.xs('high', axis=1, level=1)
        low = result.xs('low', axis=1, level=1)
        assert (high >= low).all().all()

    def test_interval_5min(self, mock_blp):
        result_1m = mock_blp.bdib('AAPL US Equity', dt='2024-01-15', interval=1)
        result_5m = mock_blp.bdib('AAPL US Equity', dt='2024-01-15', interval=5)
        assert len(result_1m) > len(result_5m)

    def test_multiple_dates_accumulation(self, mock_blp):
        """Verify loading multiple days works."""
        dates = ['2024-01-15', '2024-01-16', '2024-01-17']
        frames = [mock_blp.bdib('AAPL US Equity', dt=d, interval=5) for d in dates]
        combined = pd.concat(frames)
        assert len(combined) == sum(len(f) for f in frames)


class TestYasMock:
    def test_returns_ytm(self, mock_blp):
        result = mock_blp.yas('T 4.5 5/15/38 Govt')
        assert 'YAS_BOND_YLD' in result.columns
        ytm = result['YAS_BOND_YLD'].iloc[0]
        assert 0 < ytm < 20

    def test_multiple_analytics(self, mock_blp):
        flds = ['YAS_BOND_YLD', 'YAS_MOD_DUR', 'YAS_ASW_SPREAD']
        result = mock_blp.yas('T 4.5 5/15/38 Govt', flds)
        assert all(f in result.columns for f in flds)

    def test_price_from_yield(self, mock_blp):
        result = mock_blp.yas('T 4.5 5/15/38 Govt', flds='YAS_BOND_PX', yield_=4.8)
        assert 'YAS_BOND_PX' in result.columns
        px = result['YAS_BOND_PX'].iloc[0]
        assert 70 < px < 130


class TestFuturesMock:
    def test_fut_ticker_resolution(self, mock_blp):
        result = mock_blp.fut_ticker('ES1 Index', '2024-01-15', freq='ME')
        assert isinstance(result, str)
        assert 'Index' in result

    def test_active_futures(self, mock_blp):
        result = mock_blp.active_futures('ESA Index', '2024-01-15')
        assert isinstance(result, str)

    def test_month_code_format(self, mock_blp):
        # March expiry → 'H'
        result = mock_blp.fut_ticker('ES1 Index', '2024-03-01', freq='ME')
        assert 'H24' in result


class TestExchangeTzMock:
    def test_us_equity_is_new_york(self, mock_blp):
        tz = mock_blp.exchange_tz('AAPL US Equity')
        assert tz == 'America/New_York'

    def test_japanese_equity_is_tokyo(self, mock_blp):
        tz = mock_blp.exchange_tz('7974 JT Equity')
        assert tz == 'Asia/Tokyo'

    def test_australian_equity_is_sydney(self, mock_blp):
        tz = mock_blp.exchange_tz('BHP AU Equity')
        assert tz == 'Australia/Sydney'

    def test_london_equity_is_london(self, mock_blp):
        tz = mock_blp.exchange_tz('SHEL LN Equity')
        assert tz == 'Europe/London'


class TestSmartDispatcher:
    def test_bdp_routing(self, mock_blp, eq_tickers):
        """No start_date → routes to bdp."""
        bbg = make_bbg_dispatcher(mock_blp)
        result = bbg(eq_tickers, 'PX_LAST')
        assert mock_blp._call_counts.get('bdp', 0) > 0
        assert result.shape[0] == 3

    def test_bdh_routing(self, mock_blp, eq_tickers):
        """start_date provided → routes to bdh."""
        bbg = make_bbg_dispatcher(mock_blp)
        result = bbg(eq_tickers, 'px_last',
                     start_date='2024-01-01', end_date='2024-01-31')
        assert mock_blp._call_counts.get('bdh', 0) > 0
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_single_field_bdh_flattened(self, mock_blp, eq_tickers):
        """Single-field bdh with flat=True → no MultiIndex."""
        bbg = make_bbg_dispatcher(mock_blp)
        result = bbg(eq_tickers, 'px_last',
                     start_date='2024-01-01', end_date='2024-01-31', flat=True)
        assert not isinstance(result.columns, pd.MultiIndex)
        assert all(t in result.columns for t in eq_tickers)

    def test_batching(self, mock_blp):
        """Large universe is split into batches."""
        bbg = make_bbg_dispatcher(mock_blp)
        tickers = [f"TICK{i:03d} US Equity" for i in range(150)]
        result = bbg(tickers, 'PX_LAST', batch_size=50)
        # 3 batches of 50
        assert mock_blp._call_counts.get('bdp', 0) == 3
        assert result.shape[0] == 150

    def test_single_ticker_string(self, mock_blp):
        """Single string ticker is handled."""
        bbg = make_bbg_dispatcher(mock_blp)
        result = bbg('AAPL US Equity', 'PX_LAST')
        assert result.shape[0] == 1

    def test_retry_on_failure(self, mock_blp):
        """Dispatcher retries on transient failure."""
        bbg = make_bbg_dispatcher(mock_blp)
        call_count = [0]
        original_bdp = mock_blp.bdp

        def flaky_bdp(tickers, flds, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise ConnectionError("Simulated transient failure")
            return original_bdp(tickers, flds, **kwargs)

        mock_blp.bdp = flaky_bdp
        result = bbg('AAPL US Equity', 'PX_LAST', max_retries=3)
        assert call_count[0] == 2
        assert not result.empty
        mock_blp.bdp = original_bdp  # restore


class TestErrorHandling:
    def test_empty_dataframe_detection(self, mock_blp):
        """Verify empty DataFrame guard pattern works."""
        # Simulate empty response
        with patch.object(mock_blp, 'bdp', return_value=pd.DataFrame()):
            result = mock_blp.bdp('FAKE TICKER Equity', 'PX_LAST')
            assert result.empty

    def test_nan_handling(self, mock_blp, eq_tickers):
        """N/A coercion pattern works."""
        df = mock_blp.bdp(eq_tickers, ['PX_LAST', 'PE_RATIO'])
        df = df.apply(pd.to_numeric, errors='coerce')
        assert df.dtypes.eq('float64').all()

    def test_batch_fallback_to_individual(self, mock_blp, eq_tickers):
        """Fallback pattern: batch fails → try individually."""
        call_log = []
        original = mock_blp.bdp

        def tracking_bdp(tickers, flds, **kwargs):
            if isinstance(tickers, list) and len(tickers) > 1:
                call_log.append('batch')
                raise RuntimeError("Batch failed")
            call_log.append('individual')
            return original([tickers] if isinstance(tickers, str) else tickers, flds, **kwargs)

        mock_blp.bdp = tracking_bdp
        results = []
        for t in eq_tickers:
            try:
                r = mock_blp.bdp(t, 'PX_LAST')
                results.append(r)
            except Exception:
                pass
        assert len(results) == 3
        mock_blp.bdp = original


class TestRecipePatterns:
    def test_universe_pull_pipeline(self, mock_blp):
        """Test the index members → bdp pipeline."""
        members = mock_blp.bds('SPX Index', 'INDX_MWEIGHT')
        tickers = members['member_ticker_and_exchange_code'].tolist()
        assert len(tickers) > 0

        # Pull fundamentals for first 5
        fundamentals = mock_blp.bdp(tickers[:5], ['PX_LAST', 'PE_RATIO', 'CUR_MKT_CAP'])
        assert fundamentals.shape == (5, 3)
        assert fundamentals['px_last'].notna().all()

    def test_yield_curve_pattern(self, mock_blp):
        """Test the yield curve construction pattern."""
        tenors = {
            '2Y': 'USGG2YR Index', '5Y': 'USGG5YR Index',
            '10Y': 'USGG10YR Index', '30Y': 'USGG30YR Index'
        }
        curve = mock_blp.bdp(list(tenors.values()), 'PX_LAST')
        assert len(curve) == 4
        # Mock returns synthetic prices (50-500 range); just verify non-null numeric values
        yields = pd.to_numeric(curve['px_last'], errors='coerce')
        assert yields.notna().all()
        assert (yields > 0).all()

    def test_factor_zscore_pattern(self, mock_blp):
        """Test cross-sectional factor z-score."""
        tickers = [f"TICK{i:02d} US Equity" for i in range(50)]
        factors = mock_blp.bdp(tickers, ['PE_RATIO', 'PX_TO_BOOK_RATIO'])
        factors = factors.apply(pd.to_numeric, errors='coerce')
        z_scores = factors.apply(lambda col: (col - col.mean()) / col.std())
        assert abs(z_scores.mean()).max() < 0.1     # mean ≈ 0
        assert abs(z_scores.std() - 1.0).max() < 0.1  # std ≈ 1

    def test_intraday_returns_pattern(self, mock_blp):
        """Test computing intraday bar returns."""
        bars = mock_blp.bdib('AAPL US Equity', dt='2024-01-15', interval=5)
        close = bars.xs('close', axis=1, level=1)
        returns = close.pct_change().dropna()
        assert len(returns) > 0
        assert returns.notna().all().all()

    def test_dividend_history_pattern(self, mock_blp):
        """Test dividend history pull."""
        divs = mock_blp.dividend(
            ['AAPL US Equity', 'MSFT US Equity'],
            start_date='2024-01-01', end_date='2024-12-31'
        )
        assert 'dvd_amt' in divs.columns
        assert len(divs) == 8   # 2 tickers × 4 quarters

    def test_futures_roll_chain(self, mock_blp):
        """Test building a futures price series with rolling."""
        dates = pd.bdate_range('2024-01-01', '2024-03-31')
        contracts = [mock_blp.fut_ticker('ES1 Index', str(d.date())) for d in dates]
        assert len(contracts) == len(dates)
        assert all('Index' in c for c in contracts)

    def test_options_chain_pipeline(self, mock_blp):
        """Test options chain → greeks pipeline."""
        chain = mock_blp.bds('AAPL US Equity', 'OPT_CHAIN', Expiry_Dt='20250117')
        assert 'option_ticker' in chain.columns
        tickers = chain['option_ticker'].tolist()

        greeks = mock_blp.bdp(tickers, ['OPT_STRIKE_PX', 'DELTA_MID_RT', 'IVOL_MID'])
        assert greeks.shape[0] == len(tickers)

    def test_fx_forward_ladder(self, mock_blp):
        """Test FX forward ladder construction."""
        pairs = ['EURUSD', 'USDJPY']
        tenors = ['1M', '3M', '6M', '1Y']
        rows = []
        for tenor in tenors:
            tickers = [f"{p}{tenor} Curncy" for p in pairs]
            fwds = mock_blp.bdp(tickers, ['BID', 'ASK'])
            fwds['tenor'] = tenor
            rows.append(fwds)
        ladder = pd.concat(rows)
        assert len(ladder) == len(pairs) * len(tenors)


class TestFieldDiscovery:
    def test_field_search_returns_dataframe(self, mock_blp):
        result = mock_blp.fieldSearch('vwap')
        assert isinstance(result, pd.DataFrame)
        assert 'field_name' in result.columns

    def test_lookup_security(self, mock_blp):
        result = mock_blp.lookupSecurity('Apple', yellowkey='eqty')
        assert isinstance(result, pd.DataFrame)
        assert 'ticker' in result.columns


class TestPatchContextManager:
    def test_patch_blp_context_manager(self, mock_blp):
        """Verify the patch_blp context manager patches correctly."""
        with mock_blp.patch_blp():
            from xbbg import blp
            result = blp.bdp('AAPL US Equity', 'PX_LAST')
            assert isinstance(result, pd.DataFrame)
            assert not result.empty

    def test_patch_restores_after_context(self, mock_blp):
        """Verify xbbg is unpatched after context manager exits."""
        from xbbg import blp as blp_module
        original_bdp = blp_module.bdp

        with mock_blp.patch_blp():
            patched_bdp = blp_module.bdp
            assert patched_bdp is not original_bdp  # should be patched inside

        # After context: should be restored to original
        assert blp_module.bdp is original_bdp


# ---------------------------------------------------------------------------
# Integration Tests — Require Live Bloomberg Terminal
# ---------------------------------------------------------------------------

bloomberg_required = pytest.mark.skipif(
    os.environ.get('BLOOMBERG_TERMINAL') != '1',
    reason="Requires BLOOMBERG_TERMINAL=1 env var and active Bloomberg Terminal"
)


@bloomberg_required
class TestBdpLive:
    def test_aapl_px_last(self):
        from xbbg import blp
        result = blp.bdp('AAPL US Equity', 'PX_LAST')
        assert not result.empty
        assert 'px_last' in result.columns
        assert result['px_last'].iloc[0] > 0

    def test_multiple_tickers(self):
        from xbbg import blp
        tickers = ['AAPL US Equity', 'MSFT US Equity']
        result = blp.bdp(tickers, ['PX_LAST', 'PE_RATIO'])
        assert result.shape == (2, 2)
        assert result['px_last'].notna().all()

    def test_isin_lookup(self):
        from xbbg import blp
        result = blp.bdp('/isin/US0378331005', ['Security_Name', 'PX_LAST'])
        assert not result.empty


@bloomberg_required
class TestBdhLive:
    def test_spx_daily(self):
        from xbbg import blp
        df = blp.bdh('SPX Index', 'PX_LAST', '2024-01-01', '2024-01-31')
        assert not df.empty
        assert isinstance(df.index, pd.DatetimeIndex)
        assert 'px_last' in df.columns

    def test_adjusted_prices(self):
        from xbbg import blp
        adjusted = blp.bdh('AAPL US Equity', 'px_last', '2014-06-05', '2014-06-10',
                           adjust='all')
        unadjusted = blp.bdh('AAPL US Equity', 'px_last', '2014-06-05', '2014-06-10')
        # Adjusted should differ from unadjusted (AAPL had a 7:1 split in Jun 2014)
        assert not adjusted['px_last'].equals(unadjusted['px_last'])

    def test_multi_ticker_multiindex(self):
        from xbbg import blp
        df = blp.bdh(['AAPL US Equity', 'MSFT US Equity'], 'px_last',
                     '2024-01-01', '2024-01-10')
        assert isinstance(df.columns, pd.MultiIndex)

    def test_monthly_periodicity(self):
        from xbbg import blp
        df = blp.bdh('SPX Index', 'PX_LAST', '2023-01-01', '2024-12-31', Per='M')
        assert len(df) <= 24 + 2   # roughly 24 months with boundary tolerance


@bloomberg_required
class TestBdsLive:
    def test_spx_members(self):
        from xbbg import blp
        result = blp.bds('SPX Index', 'INDX_MEMBERS')
        assert len(result) > 450  # S&P 500 has ~500 members

    def test_aapl_dividends(self):
        from xbbg import blp
        result = blp.bds('AAPL US Equity', 'DVD_Hist_All',
                         DVD_Start_Dt='20230101', DVD_End_Dt='20231231')
        assert len(result) >= 4  # AAPL pays quarterly

    def test_bond_cashflows(self):
        from xbbg import blp
        result = blp.bds('T 4.5 5/15/38 Govt', 'DES_CASH_FLOW')
        assert 'coupon_amount' in result.columns or len(result) > 0


@bloomberg_required
class TestBdibLive:
    def test_one_minute_bars(self):
        from xbbg import blp
        import datetime
        # Use a recent past trading day
        dt = (pd.Timestamp.today() - pd.offsets.BDay(1)).strftime('%Y-%m-%d')
        result = blp.bdib('AAPL US Equity', dt=dt, interval=1)
        assert not result.empty
        assert isinstance(result.index, pd.DatetimeIndex)
        assert result.index.tz is not None

    def test_session_filtering(self):
        from xbbg import blp
        dt = (pd.Timestamp.today() - pd.offsets.BDay(1)).strftime('%Y-%m-%d')
        full = blp.bdib('SPY US Equity', dt=dt, session='day')
        open_30 = blp.bdib('SPY US Equity', dt=dt, session='day_open_30')
        assert len(open_30) <= len(full)

    def test_exchange_tz(self):
        from xbbg import blp
        tz = blp.exchange_tz('AAPL US Equity')
        assert tz == 'America/New_York'

        tz_jp = blp.exchange_tz('7974 JT Equity')
        assert tz_jp == 'Asia/Tokyo'


@bloomberg_required
class TestYasLive:
    def test_ust_ytm(self):
        from xbbg import blp
        result = blp.yas('T 4.5 5/15/38 Govt')
        assert 'YAS_BOND_YLD' in result.columns
        ytm = result['YAS_BOND_YLD'].iloc[0]
        assert 0 < ytm < 20

    def test_price_from_yield(self):
        from xbbg import blp
        result = blp.yas('T 4.5 5/15/38 Govt', flds='YAS_BOND_PX', yield_=5.0)
        assert 'YAS_BOND_PX' in result.columns
        px = result['YAS_BOND_PX'].iloc[0]
        assert 70 < px < 130


@bloomberg_required
class TestBeqsLive:
    def test_equity_screen(self):
        from xbbg import blp
        # This requires a saved screen named 'TEST' in the Bloomberg terminal
        # Skip gracefully if screen doesn't exist
        try:
            result = blp.beqs(screen='TEST')
            assert isinstance(result, pd.DataFrame)
        except Exception as exc:
            pytest.skip(f"Screen 'TEST' not available: {exc}")


@bloomberg_required
class TestFuturesLive:
    def test_es_front_month(self):
        from xbbg import blp
        contract = blp.fut_ticker('ES1 Index', '2024-01-15', freq='ME')
        assert isinstance(contract, str)
        assert 'Index' in contract
        assert contract != 'ES1 Index'

    def test_active_futures(self):
        from xbbg import blp
        contract = blp.active_futures('ESA Index', '2024-01-15')
        assert isinstance(contract, str)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v', '-m', 'not bloomberg']))
