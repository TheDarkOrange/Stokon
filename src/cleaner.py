# src/cleaner.py

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Validate & clean the fetched OHLCV data."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        - Drops dates where <95% of tickers have a valid Close
        - Converts any non-positive prices to NaN
        - Forward/back‐fills per ticker
        - Drops any rows still containing NaNs (i.e. tickers with no data)
        - Ensures final DataFrame has no NaNs or non-positive prices
        """
        # 1) drop dates with too many missing closes
        n_tickers = len(df.index.unique('Ticker'))
        thresh = int(n_tickers * 0.95)
        valid = (
            df.reset_index()
            .groupby('Date')
            .apply(lambda d: d['Close'].notna().sum() >= thresh)
        )
        good_dates = valid[valid].index
        df = df.loc[good_dates]

        # 2) convert non-positive prices to NaN
        price_cols = ['Open', 'High', 'Low', 'Close']
        for col in price_cols:
            mask = df[col] <= 0
            if mask.any():
                logger.warning(
                    f"Found {mask.sum()} non-positive values in {col}, marking as NaN")
                df.loc[mask, col] = np.nan

        # 3) forward/back-fill per ticker
        df = df.groupby('Ticker').apply(lambda x: x.ffill().bfill()).droplevel(0)

        # 4) drop any rows still containing NaNs
        before = len(df)
        df = df.dropna()
        dropped = before - len(df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} rows still containing NaNs after fill")

        # 5) final sanity checks
        if df[price_cols].isna().any().any():
            raise RuntimeError(
                "DataCleaner: NaNs remain in price columns after dropna()")
        if (df[price_cols] <= 0).any().any():
            raise RuntimeError("DataCleaner: Non-positive price remains after cleanup")
        if (df['Volume'] < 0).any():
            raise RuntimeError("DataCleaner: Negative volume found")

        return df
