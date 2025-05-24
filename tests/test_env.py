# tests/test_env.py

import pytest
import pandas as pd
import numpy as np
from src.env import DRLTradingEnv


@pytest.fixture
def small_env():
    dates = pd.date_range("2025-01-01", periods=10, freq="B")
    tickers = ["A", "B", "C"]
    # price_df: only Close needed
    price = np.linspace(100, 110, len(dates))
    price_df = pd.DataFrame(
        {'Close': np.tile(price, len(tickers))},
        index=pd.MultiIndex.from_product(
            [dates, tickers], names=["Date", "Ticker"])
    )
    # feature_df: same index, arbitrary floats
    feats = pd.DataFrame(
        np.random.randn(len(price_df), 5),
        index=price_df.index
    )
    env = DRLTradingEnv(price_df, feats)
    return env


def test_reset_and_step(small_env):
    obs = small_env.reset()
    assert isinstance(obs, np.ndarray)
    assert obs.shape == small_env.observation_space.shape
    action = small_env.action_space.sample()
    obs2, reward, done, info = small_env.step(action)
    assert isinstance(reward, float)
    assert 'pnl' in info and 'cost' in info
