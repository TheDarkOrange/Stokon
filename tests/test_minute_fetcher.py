# tests/test_minute_fetcher.py

import pytest
import datetime
import pandas as pd
from src.minute_fetcher import MinuteDataFetcher


class DummyIB:
    def connect(self, *args, **kwargs): pass
    def reqHistoricalData(self, *args, **kwargs): return []


@pytest.fixture(autouse=True)
def patch_ib(monkeypatch):
    monkeypatch.setattr('src.minute_fetcher.IB', DummyIB)


def test_fetch_empty():
    mdf = MinuteDataFetcher('host', 0, 0)
    df = mdf.fetch_daily_minute(['AAA'], datetime.date(2025, 1, 2))
    assert isinstance(df, pd.DataFrame)
    assert df.empty
