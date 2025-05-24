# src/fetcher.py

from typing import List
import pandas as pd
import yfinance as yf
import pandas_market_calendars as mcal


class DataFetcher:
    """Fetch and adjust end-of-day price data, backfilled to full trading calendar."""

    def __init__(self, calendar_name: str = "NYSE"):
        self.cal = mcal.get_calendar(calendar_name)

    def fetch_daily(
        self,
        tickers: List[str],
        start: str,
        end: str,
    ) -> pd.DataFrame:
        """
        Returns MultiIndex (Date, Ticker) × [Open, High, Low, Close, Volume],
        adjusted for splits & dividends, reindexed to all trading days.
        """
        # 1) Download raw data + corporate actions
        raw = yf.download(
            tickers,
            start=start,
            end=end,
            group_by='ticker',
            auto_adjust=False,
            actions=True,
            threads=True,
        )

        # 2) Build adjusted price DataFrame per ticker
        adj_dfs = {}
        price_cols = ['Open', 'High', 'Low', 'Close']
        for sym in tickers:
            df_sym = raw[sym].copy()
            # split adjustments
            splits = df_sym['Splits'].replace(0, 1)
            split_adj = splits[::-1].cumprod()[::-1]
            # dividend adjustments via Adj Close if available
            if 'Adj Close' in raw[sym]:
                div_adj = raw[sym]['Adj Close'] / df_sym['Close']
            else:
                div_adj = 1.0
            adj_factor = split_adj * div_adj
            for col in price_cols:
                df_sym[col] = df_sym[col] * adj_factor
            adj_dfs[sym] = df_sym[price_cols + ['Volume']]

        # 3) Stack into MultiIndex
        df = pd.concat(adj_dfs, axis=1).stack(level=1)
        df.index.set_names(['Date', 'Ticker'], inplace=True)

        # 4) Reindex to full trading days
        sched = self.cal.schedule(start_date=start, end_date=end)
        all_days = sched.index.normalize()
        idx = pd.MultiIndex.from_product(
            [all_days, tickers], names=['Date', 'Ticker'])
        df = df.reindex(idx)

        # 5) Fill gaps per ticker
        df = df.groupby('Ticker').apply(
            lambda x: x.ffill().bfill()).droplevel(0)
        return df
