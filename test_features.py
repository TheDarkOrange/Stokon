# tests/test_features.py

import pytest
import pandas as pd
import numpy as np
from src.features import FeatureEngineer


def test_build_features():
    dates = pd.date_range("2025-01-01", periods=25, freq="B")
    tickers = ["A"]
    idx = pd.MultiIndex.from_product(
        [dates, tickers], names=["Date", "Ticker"])
    base = np.arange(len(dates))
    df = pd.DataFrame({
        "Open":   base,
        "High":   base + 1,
        "Low":    base - 1,
        "Close":  base,
        "Volume": np.ones(len(dates)) * 1000
    }, index=idx)

    feats = FeatureEngineer().build_features(df)
    # should have at least these columns and no NaNs
    for col in ['5d_mom', '20d_mom', '20d_vol', 'rsi', 'tsi']:
        assert col in feats.columns
    assert not feats.isna().any().any()
