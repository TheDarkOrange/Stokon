# src/cleaner.py

import pandas as pd


class DataCleaner:
    """Validate & clean fetched OHLCV data."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        - Drops days where <95% of tickers have valid Close
        - Forward/back‐fills per ticker
        - Asserts positive prices & non‐negative volume
        """
        # drop dates with too many missing closes
        n_tickers = len(df.index.unique('Ticker'))
        thresh = int(n_tickers * 0.95)
        valid = (
            df.reset_index()
            .groupby('Date')
            .apply(lambda d: d['Close'].notna().sum() >= thresh)
        )
        good_dates = valid[valid].index
        df = df.loc[good_dates]

        # fill per ticker
        df = df.groupby('Ticker').apply(
            lambda x: x.ffill().bfill()).droplevel(0)

        # sanity checks
        assert (df[['Open', 'High', 'Low', 'Close']] >
                0).all().all(), "Non-positive price!"
        assert (df['Volume'] >= 0).all(), "Negative volume!"

        return df
