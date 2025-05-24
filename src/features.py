# src/features.py

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, TSIIndicator
from ta.volatility import BollingerBands


class FeatureEngineer:
    """Compute momentum, volatility, RSI, TSI features."""

    def build_features(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Input: MultiIndex (Date, Ticker) × [Open, High, Low, Close, Volume]
        Output: same index with added columns: 5d_mom, 20d_mom, 20d_vol, rsi, tsi
        """
        df = price_df.copy()
        df['5d_mom'] = df.groupby('Ticker')['Close'].pct_change(5)
        df['20d_mom'] = df.groupby('Ticker')['Close'].pct_change(20)
        df['20d_vol'] = (
            df.groupby('Ticker')['Close']
              .rolling(20).std()
              .reset_index(level=0, drop=True)
        )
        df['rsi'] = (
            df.groupby('Ticker')['Close']
              .apply(lambda x: RSIIndicator(x, window=14).rsi())
        )
        df['tsi'] = (
            df.groupby('Ticker')['Close']
              .apply(lambda x: TSIIndicator(x, window_slow=25, window_fast=13).tsi())
        )

        df = df.dropna()
        return df
