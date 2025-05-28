# src/fetcher.py

from typing import List
import pandas as pd
import yfinance as yf
import pandas_market_calendars as mcal
import logging

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetch EOD OHLCV data (auto-adjusted), backfilled to the NYSE calendar.
    Falls back to synthetic flat data if all tickers fail to download.
    """

    def __init__(self, calendar_name: str = "NYSE"):
        self.cal = mcal.get_calendar(calendar_name)

    def fetch_daily(
        self,
        tickers: List[str],
        start: str,
        end: str,
    ) -> pd.DataFrame:
        # 1) Attempt per-ticker download
        price_frames = []
        for sym in tickers:
            try:
                # auto_adjust=True already handles splits & dividends
                df_sym = yf.Ticker(sym) \
                    .history(start=start, end=end, auto_adjust=True) \
                    .loc[:, ["Open", "High", "Low", "Close", "Volume"]]
                if df_sym.empty:
                    raise ValueError("No data returned")
                df_sym["Ticker"] = sym
                df_sym.index.name = "Date"
                price_frames.append(df_sym)
            except Exception as e:
                logger.warning(f"Skipping {sym}: {e}")

        # 2) If none succeeded, generate synthetic flat data
        if not price_frames:
            logger.warning(
                "All tickers failed to fetch; generating synthetic flat-price data.")
            sched = self.cal.schedule(start_date=start, end_date=end)
            all_days = sched.index.normalize()
            idx = pd.MultiIndex.from_product(
                [all_days, tickers], names=["Date", "Ticker"])
            df = pd.DataFrame(
                {
                    "Open": 100.0,
                    "High": 100.0,
                    "Low": 100.0,
                    "Close": 100.0,
                    "Volume": 0,
                },
                index=idx
            )
            return df

        # 3) Concatenate what did download
        df = pd.concat(price_frames)
        df = df.reset_index().set_index(["Date", "Ticker"]).sort_index()

        # 4) Reindex to full trading days
        sched = self.cal.schedule(start_date=start, end_date=end)
        all_days = sched.index.normalize()
        idx_full = pd.MultiIndex.from_product(
            [all_days, tickers], names=["Date", "Ticker"])
        df = df.reindex(idx_full)

        # 5) Forward/backfill per ticker
        df = df.groupby("Ticker").apply(lambda x: x.ffill().bfill()).droplevel(0)

        return df
