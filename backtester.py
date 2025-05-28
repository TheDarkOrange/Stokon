# src/backtester.py

import pandas as pd
import numpy as np


class PerformanceReport:
    """Container for backtest performance metrics."""

    def __init__(self, returns: pd.Series):
        self.returns = returns
        self.sharpe = self._calc_sharpe()
        self.max_drawdown = self._calc_max_drawdown()
        self.profit_factor = self._calc_profit_factor()

    def _calc_sharpe(self, rf: float = 0.0) -> float:
        return (self.returns.mean() - rf) / self.returns.std() * np.sqrt(252)

    def _calc_max_drawdown(self) -> float:
        cum = (1 + self.returns).cumprod()
        dd = cum / cum.cummax() - 1
        return dd.min()

    def _calc_profit_factor(self) -> float:
        wins = self.returns[self.returns > 0].sum()
        losses = -self.returns[self.returns < 0].sum()
        return wins / losses if losses > 0 else np.nan


class Backtester:
    """Daily backtest with slippage and commission costs."""

    def run_backtest(
        self,
        price_df: pd.DataFrame,
        signals: pd.Series,
        slippage: float,
        commission: float
    ) -> PerformanceReport:
        # daily pct returns per ticker
        ret = price_df.groupby('Ticker')['Close'].pct_change().fillna(0)
        # lag signals to next day open
        pos = signals.groupby('Ticker').shift(1).fillna(0)
        pnl = pos * ret
        trades = pos.diff().abs()
        cost = trades * (slippage + commission)
        net = pnl - cost
        daily = net.groupby('Date').mean()
        return PerformanceReport(daily)
