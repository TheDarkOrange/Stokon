# tests/test_intraday_backtester.py

import pandas as pd
import pytest
from src.intraday_backtester import IntradayBacktester


@pytest.fixture
def simple_data():
    date = pd.Timestamp('2025-01-02')
    tickers = ['A', 'B']
    idx = pd.MultiIndex.from_product(
        [[date], tickers], names=['Date', 'Ticker'])
    daily = pd.DataFrame({
        'High':  [110, 120],
        'Low':   [90, 100],
        'Close': [105, 115],
    }, index=idx)

    times = pd.date_range('2025-01-02 09:30', '2025-01-02 09:31', freq='1min')
    rows = []
    for t in times:
        rows.append({'Datetime': t, 'Ticker': 'A',
                    'Low': 91 if t == times[1] else 95, 'Close': 95})
        rows.append({'Datetime': t, 'Ticker': 'B', 'Low': 105, 'Close': 115})
    md = pd.DataFrame(rows).set_index(['Datetime', 'Ticker'])

    # weights: long 1 unit each
    w = pd.Series([1.0, 1.0], index=idx)
    return w, daily, md


def test_intraday_stop_and_eod(simple_data):
    w, daily, md = simple_data
    bt = IntradayBacktester(slippage=0.001, commission=0.001)
    ret = bt.run_intraday(w, daily, md)
    # For A: stop from 95→92 = -0.03158, cost=0.002 ⇒ ≈ -0.03358
    # For B: flat 0 return, cost=0.002 ⇒ -0.002
    # total ≈ -0.03558
    assert pytest.approx(ret.iloc[0], rel=1e-3) == -0.03558
