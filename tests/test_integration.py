# tests/test_integration.py

import pandas as pd
import pytest
from src import main


class DummyFetcher:
    def fetch_daily(self, *args, **kwargs):
        dates = pd.bdate_range("2025-01-01", periods=3)
        tickers = ["AAA", "BBB"]
        rows = []
        for d in dates:
            for t in tickers:
                rows.append({
                    "Open": 100, "High": 101, "Low": 99,
                    "Close": 100, "Volume": 1000
                })
        idx = pd.MultiIndex.from_product(
            [dates, tickers], names=["Date", "Ticker"])
        return pd.DataFrame(rows, index=idx)


class DummyMinuteFetcher:
    def fetch_daily_minute(self, *args, **kwargs):
        return pd.DataFrame()


@pytest.fixture(autouse=True)
def patch_components(monkeypatch):
    from src.fetcher import DataFetcher
    from src.minute_fetcher import MinuteDataFetcher
    from src.broker import BrokerInterface
    monkeypatch.setattr(DataFetcher, "fetch_daily", DummyFetcher().fetch_daily)
    monkeypatch.setattr(MinuteDataFetcher, "fetch_daily_minute",
                        DummyMinuteFetcher().fetch_daily_minute)
    monkeypatch.setattr(BrokerInterface, "__init__",
                        lambda self, *a, **k: None)
    monkeypatch.setattr(BrokerInterface, "send_order", lambda self, ticker, qty, action: {
                        "ticker": ticker, "qty": qty, "action": action})


def test_end_to_end_runs_without_error(capsys):
    main.run_daily_job(dry_run=False)
    out = capsys.readouterr().out
    assert "Intraday Sharpe" in out
