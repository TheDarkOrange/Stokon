# src/intraday_backtester.py

import pandas as pd
from ta.volatility import AverageTrueRange


class IntradayBacktester:
    """
    Simulate:
      • Entry at first‐minute close
      • ATR‐based stop‐loss intraday
      • End‐of‐day exit
      • Slippage & commission
    """

    def __init__(
        self,
        slippage: float,
        commission: float,
        atr_window: int = 14,
        atr_mult: float = 3.0
    ):
        self.slippage = slippage
        self.commission = commission
        self.atr_window = atr_window
        self.atr_mult = atr_mult

    def run_intraday(
        self,
        weights: pd.Series,
        daily_price: pd.DataFrame,
        minute_data: pd.DataFrame
    ) -> pd.Series:
        w_df = weights.unstack(level='Ticker')
        dates = w_df.index
        results = {}

        for date in dates:
            w = w_df.loc[date].fillna(0)
            if w.abs().sum() == 0:
                results[date] = 0.0
                continue

            # minute bars for this date
            df_min = minute_data[
                minute_data.index.get_level_values(
                    'Datetime').normalize() == date
            ]
            if df_min.empty:
                results[date] = 0.0
                continue

            # entry prices
            first = df_min.groupby('Ticker').first()['Close']
            entry_price = first

            # compute ATR‐based stops
            stops = {}
            for ticker in entry_price.index:
                df_hist = daily_price.xs(ticker, level='Ticker').reset_index()
                atr = AverageTrueRange(
                    high=df_hist['High'],
                    low=df_hist['Low'],
                    close=df_hist['Close'],
                    window=self.atr_window
                ).average_true_range().iloc[-1]
                stops[ticker] = entry_price[ticker] - self.atr_mult * atr

            pnl = 0.0
            cost = w.abs().sum() * (self.slippage + self.commission)
            remaining = w.copy()

            # intraday stop checks
            for dt, grp in df_min.groupby(level='Datetime', sort=True):
                lows = grp['Low']
                hit = lows <= pd.Series(stops)
                for ticker_sym in hit.index[hit]:
                    if remaining[ticker_sym] == 0:
                        continue
                    r = (stops[ticker_sym] - entry_price[ticker_sym]
                         ) / entry_price[ticker_sym]
                    pnl += remaining[ticker_sym] * r
                    cost += abs(remaining[ticker_sym]) * \
                        (self.slippage + self.commission)
                    remaining[ticker_sym] = 0.0

            # EOD exit
            exit_price = df_min.groupby('Ticker').last()['Close']
            for ticker_sym, wgt in remaining.items():
                if wgt == 0:
                    continue
                r = (exit_price[ticker_sym] -
                     entry_price[ticker_sym]) / entry_price[ticker_sym]
                pnl += wgt * r
                cost += abs(wgt) * (self.slippage + self.commission)

            results[date] = pnl - cost

        return pd.Series(results)
