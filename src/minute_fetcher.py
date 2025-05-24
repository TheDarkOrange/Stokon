# src/minute_fetcher.py

from ib_insync import IB, Stock, util
import pandas as pd
import datetime
from typing import List


class MinuteDataFetcher:
    """Fetch 1-minute bars for a given date via Interactive Brokers."""

    def __init__(self, host: str, port: int, client_id: int):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)

    def fetch_daily_minute(
        self,
        tickers: List[str],
        date: datetime.date
    ) -> pd.DataFrame:
        dfs = []
        for sym in tickers:
            contract = Stock(sym, 'SMART', 'USD')
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime=date.strftime("%Y%m%d 23:59:59"),
                durationStr='1 D',
                barSizeSetting='1 min',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            if not bars:
                continue
            df = util.df(bars)
            df['Ticker'] = sym
            dfs.append(df)
        if not dfs:
            return pd.DataFrame()
        df_all = pd.concat(dfs, ignore_index=True)
        df_all.set_index(['date', 'Ticker'], inplace=True)
        df_all.index.names = ['Datetime', 'Ticker']
        return (
            df_all
            .rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low',
                'close': 'Close', 'volume': 'Volume'
            })
            [['Open', 'High', 'Low', 'Close', 'Volume']]
        )
