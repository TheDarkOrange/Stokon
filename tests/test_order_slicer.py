# tests/test_order_slicer.py

import pytest
import pandas as pd
from datetime import datetime
from src.order_slicer import TWAPSlicer, VWAPSlicer


def test_twap_slicer():
    start = pd.Timestamp('2025-01-02 09:30')
    end = pd.Timestamp('2025-01-02 16:00')
    slicer = TWAPSlicer(intervals=10)
    sched = slicer.slice_order(100, start, end)
    assert len(sched) == 10
    assert sum(q for _, q in sched) == 100
    delta = (end - start) / 10
    assert sched[0][0] == start
    assert sched[-1][0] == start + 9 * delta


def test_vwap_slicer():
    times = [
        pd.Timestamp('2025-01-02 09:30'),
        pd.Timestamp('2025-01-02 09:31'),
        pd.Timestamp('2025-01-02 09:32'),
    ]
    vols = [100, 200, 700]
    rows = [{'Datetime': t, 'Ticker': 'X', 'Volume': v}
            for t, v in zip(times, vols)]
    df = pd.DataFrame(rows).set_index(['Datetime', 'Ticker'])
    slicer = VWAPSlicer(df)
    sched = slicer.slice_order('X', 1000, times[0], times[-1])
    qtys = [q for _, q in sched]
    assert qtys == [100, 200, 700]
    assert sum(qtys) == 1000
