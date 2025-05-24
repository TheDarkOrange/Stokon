# src/order_slicer.py

import pandas as pd
from typing import List, Tuple
import datetime


class TWAPSlicer:
    """Time‐Weighted Average Price slicer: equal‐sized intervals."""

    def __init__(self, intervals: int = 10):
        self.intervals = intervals

    def slice_order(
        self,
        qty: int,
        start: datetime.datetime,
        end: datetime.datetime
    ) -> List[Tuple[datetime.datetime, int]]:
        span = end - start
        delta = span / self.intervals
        base = [qty // self.intervals] * self.intervals
        rem = qty - sum(base)
        for i in range(abs(rem)):
            base[i] += 1 if rem > 0 else -1
        return [(start + i * delta, base[i]) for i in range(self.intervals)]


class VWAPSlicer:
    """Volume‐Weighted Average Price slicer using minute‐volume profile."""

    def __init__(self, minute_data: pd.DataFrame):
        """
        minute_data: MultiIndex (Datetime, Ticker) → must include 'Volume'
        """
        self.minute_data = minute_data

    def slice_order(
        self,
        ticker: str,
        qty: int,
        start: datetime.datetime,
        end: datetime.datetime
    ) -> List[Tuple[datetime.datetime, int]]:
        df = self.minute_data.xs(ticker, level='Ticker')
        window = df.loc[(df.index >= start) & (df.index <= end)]
        total_vol = window['Volume'].sum()
        if total_vol == 0:
            return [(start, qty)]
        weights = window['Volume'] / total_vol
        slice_qty = (weights * qty).round().astype(int)
        diff = qty - slice_qty.sum()
        if diff != 0 and not slice_qty.empty:
            slice_qty.iloc[0] += diff
        return list(zip(window.index.tolist(), slice_qty.tolist()))
