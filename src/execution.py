# src/execution.py

import pandas as pd
from .broker import BrokerInterface
from .order_slicer import VWAPSlicer, TWAPSlicer


class ExecutionEngine:
    """Execute target weights via a broker using TWAP or VWAP slicing."""

    def __init__(
        self,
        broker: BrokerInterface,
        slicing_method: str = 'TWAP',
        twap_intervals: int = 10
    ):
        self.broker = broker
        self.slicing_method = slicing_method.upper()
        self.twap_intervals = twap_intervals

    def execute(
        self,
        weights: pd.Series,
        price_df: pd.DataFrame,
        minute_data: pd.DataFrame,
        total_capital: float
    ) -> pd.DataFrame:
        today = weights.index.get_level_values('Date').max()
        w = weights.xs(today, level='Date').fillna(0)
        px = price_df.xs(today, level='Date')['Close']
        alloc = w * total_capital
        qty = (alloc / px).round().astype(int)

        # choose slicer
        if self.slicing_method == 'VWAP':
            slicer = VWAPSlicer(minute_data)
        else:
            slicer = TWAPSlicer(intervals=self.twap_intervals)

        dt_idx = minute_data.index.get_level_values('Datetime')
        mask = dt_idx.normalize() == pd.to_datetime(today)
        times = dt_idx[mask]
        if not times.empty:
            start_dt, end_dt = times.min(), times.max()
        else:
            start_dt = end_dt = None

        executions = []
        for ticker, q in qty.items():
            if q == 0:
                continue
            if self.slicing_method == 'VWAP' and start_dt:
                schedule = slicer.slice_order(ticker, q, start_dt, end_dt)
            else:
                schedule = slicer.slice_order(
                    q, start_dt, end_dt) if start_dt else [(None, q)]
            for dt, slice_q in schedule:
                if slice_q == 0:
                    continue
                action = 'BUY' if slice_q > 0 else 'SELL'
                conf = self.broker.send_order(ticker, abs(slice_q), action)
                conf['slice_time'] = dt
                executions.append(conf)

        return pd.DataFrame(executions)
