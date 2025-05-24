# tests/test_backtester.py

import pandas as pd
import numpy as np
from src.backtester import Backtester


def test_backtester_simple_profit():
    dates = pd.date_range("2025-01-01", "2025-01-03", freq="D")
    tickers = ["X"]
    idx = pd.MultiIndex.from_product(
        [dates, tickers], names=["Date", "Ticker"])
    # simple uptrend
    df = pd.DataFrame({"Close": [100, 101, 102]}, index=idx)

    # always long
    sig = pd.Series(1, index=idx)
    bt = Backtester()
    perf = bt.run_backtest(df, sig, slippage=0.0, commission=0.0)
    # first-day return = (101-100)/100 = 0.01
    daily = perf.returns
    assert np.isclose(daily.iloc[0], 0.01)
    # Sharpe should be positive
    assert perf.sharpe > 0
