# tests/test_strategy.py

import pytest
import pandas as pd
import numpy as np
from src.strategy import StrategyEngine


def test_generate_signals_basic():
    # create synthetic features
    dates = pd.date_range("2025-01-01", periods=30, freq="B")
    tickers = ["X", "Y"]
    idx = pd.MultiIndex.from_product(
        [dates, tickers], names=["Date", "Ticker"])
    feats = pd.DataFrame(index=idx)
    np.random.seed(0)
    feats['5d_mom'] = np.random.randn(len(idx))
    feats['rsi'] = np.random.uniform(0, 100, len(idx))

    price_df = feats.copy()  # not used for base signals
    se = StrategyEngine(drl_model_path="nonexistent_model.zip")
    signals = se.generate_signals(price_df, feats)

    # signals must be a series indexed same as feats, values in [-1,0,1]
    assert isinstance(signals, pd.Series)
    assert signals.index.equals(feats.index)
    assert set(signals.unique()).issubset({-1, 0, 1})
