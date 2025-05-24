# tests/test_drl_integration.py

import pytest
import pandas as pd
import numpy as np
from src.strategy import StrategyEngine


class FakeModel:
    def predict(self, obs, deterministic=True):
        # pretend there are 3 tickers, always weight = 1
        return np.ones(3), None


def test_drl_blend_creates_valid_series(monkeypatch):
    se = StrategyEngine(drl_model_path="nonexistent.zip")
    se.drl_model = FakeModel()

    # synthetic 1-day, 3-ticker feature
    date = pd.Timestamp("2025-01-01")
    tickers = ["A", "B", "C"]
    idx = pd.MultiIndex.from_product(
        [[date], tickers], names=["Date", "Ticker"])
    feats = pd.DataFrame({
        '5d_mom': [0.1, -0.2, 0.0],
        'rsi':    [20, 50, 80]
    }, index=idx)
    price_df = feats.copy()

    sig = se.generate_signals(price_df, feats)
    # after DRL blend, signals must be floats in [-1,1]
    assert isinstance(sig, pd.Series)
    assert set(np.unique(sig.values)).issubset(set(np.linspace(-1, 1, 201)))
