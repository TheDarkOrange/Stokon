# src/minute_fetcher.py

"""Utilities for fetching minute-level data using Alpaca's market data API."""

try:
    from alpaca_trade_api import REST
except Exception:  # pragma: no cover - optional dependency
    REST = None

import pandas as pd
import datetime
from typing import List


class MinuteDataFetcher:
    """Fetch 1-minute bars for a given date via Alpaca data API."""

    def __init__(self, base_url: str, key: str, secret: str):
        if REST is None:
            raise ImportError("alpaca_trade_api is required for MinuteDataFetcher")
        self.api = REST(key_id=key, secret_key=secret, base_url=base_url)

    def fetch_daily_minute(
        self,
        tickers: List[str],
        date: datetime.date
    ) -> pd.DataFrame:
        dfs = []
        start = f"{date.isoformat()}T09:30:00Z"
        end = f"{date.isoformat()}T16:00:00Z"
        for sym in tickers:
            try:
                bars = self.api.get_bars(sym, '1Min', start=start, end=end).df
                if bars.empty:
                    continue
                bars['Ticker'] = sym
                dfs.append(bars)
            except Exception:
                continue
        if not dfs:
            return pd.DataFrame()
        df_all = pd.concat(dfs)
        df_all.index.name = 'Datetime'
        df_all = df_all.reset_index().set_index(['Datetime', 'Ticker'])
        df_all = df_all.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume'
        })
        return df_all[['Open', 'High', 'Low', 'Close', 'Volume']]
