# tests/test_minute_fetcher.py

import pytest
import datetime
import pandas as pd
from src.minute_fetcher import MinuteDataFetcher


class DummyREST:
    def __init__(self, *args, **kwargs):
        pass
    def get_bars(self, *args, **kwargs):
        class Result:
            df = pd.DataFrame()
        return Result()


@pytest.fixture(autouse=True)
def patch_rest(monkeypatch):
    monkeypatch.setattr('src.minute_fetcher.REST', DummyREST)


def test_fetch_empty():
    mdf = MinuteDataFetcher('url', 'key', 'secret')
    df = mdf.fetch_daily_minute(['AAA'], datetime.date(2025, 1, 2))
    assert isinstance(df, pd.DataFrame)
    assert df.empty
