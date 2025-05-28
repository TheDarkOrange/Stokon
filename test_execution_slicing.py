# tests/test_execution_slicing.py

import pytest
import pandas as pd
from src.execution import ExecutionEngine


class DummyBroker:
    def __init__(self): self.orders = []

    def send_order(self, ticker, qty, action):
        self.orders.append((ticker, qty, action))
        return {'ticker': ticker, 'qty': qty, 'action': action}


class DummyRM:
    pass


@pytest.fixture
def setup_data():
    date = pd.Timestamp('2025-01-02')
    tickers = ['X']
    w = pd.Series([0.5], index=pd.MultiIndex.from_tuples(
        [(date, 'X')], names=['Date', 'Ticker']))
    price = pd.DataFrame({'Close': [100]}, index=w.index)
    times = [pd.Timestamp('2025-01-02 09:30'),
             pd.Timestamp('2025-01-02 09:31')]
    md = pd.DataFrame({'Volume': [1, 1]}, index=pd.MultiIndex.from_product(
        [times, tickers], names=['Datetime', 'Ticker']))
    return w, price, md


@pytest.mark.parametrize("method", ["TWAP", "VWAP"])
def test_execute_slicing(setup_data, method):
    w, price, md = setup_data
    broker = DummyBroker()
    engine = ExecutionEngine(broker, slicing_method=method, twap_intervals=2)
    df = engine.execute(w, price, md, total_capital=1000)
    # should issue 2 child orders summing to qty=5
    assert len(broker.orders) == 2
    assert sum(q for _, q, _ in broker.orders) == 5
    assert len(df) == 2
