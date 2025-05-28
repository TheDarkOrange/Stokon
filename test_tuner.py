# tests/test_tuner.py

import pytest
import pandas as pd
import numpy as np
from src.tuner import (
    build_features, gen_mom_signals,
    walk_forward_splits, tune_hyperparameters
)


class DummyFetcher:
    def __init__(self): pass

    def fetch_daily(self, tickers, start, end):
        dates = pd.bdate_range(start, end)
        ticks = ["A", "B"]
        rows = []
        for d in dates:
            for i, sym in enumerate(ticks):
                p = 100 + dates.get_loc(d) + i
                rows.append({
                    "Date": d, "Ticker": sym,
                    "Open": p, "High": p+1, "Low": p-1,
                    "Close": p, "Volume": 1000
                })
        return pd.DataFrame(rows).set_index(["Date", "Ticker"])


@pytest.fixture(autouse=True)
def patch_fetcher(monkeypatch):
    import src.tuner as tuner
    monkeypatch.setattr(tuner, "DataFetcher", DummyFetcher)


def test_build_and_signal():
    dates = pd.bdate_range("2025-01-01", periods=10)
    tickers = ["X"]
    idx = pd.MultiIndex.from_product(
        [dates, tickers], names=["Date", "Ticker"])
    df = pd.DataFrame({"Close": np.arange(10)}, index=idx)
    feats = build_features(df, mom_short=1, mom_long=2, rsi_window=3)
    # expect drops for lookback of max(1,2,3)=3
    assert all(feats.groupby(level="Ticker").size() == 10 - 3)
    sig = gen_mom_signals(feats, short_q=0.2, long_q=0.8)
    assert set(sig.unique()).issubset({-1, 0, 1})


def test_walk_forward_splits():
    dates = pd.date_range("2025-01-01", periods=20)
    splits = walk_forward_splits(dates, train_len=10, test_len=5)
    assert len(splits) == 2
    for sp in splits:
        assert len(sp['train']) == 10
        assert len(sp['test']) == 5


def test_tune_hyperparameters_returns_df(tmp_path):
    grid = {
        "mom_short": [1, 2],
        "mom_long":  [3],
        "rsi_window": [3],
        "slippage":  [0.0],
        "commission": [0.0]
    }
    df = tune_hyperparameters(
        tickers=["A", "B"],
        start="2025-01-01",
        end="2025-02-01",
        param_grid=grid,
        train_len=5,
        test_len=5
    )
    assert isinstance(df, pd.DataFrame)
    # one row per grid point
    assert df.shape[0] == 2 * 1 * 1 * 1 * 1
    assert 'avg_sharpe' in df.columns
