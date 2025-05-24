# tests/test_fetcher.py

import pytest
import pandas as pd
from src.fetcher import DataFetcher


@pytest.fixture
def df():
    # fetch 1 month of data for a small universe
    fetcher = DataFetcher()
    return fetcher.fetch_daily(["AAPL", "MSFT"], start="2025-01-01", end="2025-02-01")


def test_shape_and_index(df):
    # should have all NYSE trading days × 2 tickers
    from pandas_market_calendars import get_calendar
    days = get_calendar("NYSE").schedule("2025-01-01", "2025-02-01").index
    assert len(df.index.unique(level="Date")) == len(days)
    assert set(df.index.get_level_values("Ticker")) == {"AAPL", "MSFT"}


def test_no_nans_after_fill(df):
    assert not df.isna().any().any()


def test_positive_prices(df):
    assert (df[['Open', 'High', 'Low', 'Close']] > 0).all().all()
    assert (df['Volume'] >= 0).all()
