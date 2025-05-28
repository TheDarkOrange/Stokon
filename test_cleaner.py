# tests/test_cleaner.py

import pytest
import pandas as pd
from src.cleaner import DataCleaner


@pytest.fixture
def raw_df():
    idx = pd.MultiIndex.from_product(
        [pd.to_datetime(["2025-01-02", "2025-01-03"]), ["X", "Y"]],
        names=["Date", "Ticker"]
    )
    df = pd.DataFrame({
        "Open":   [1, None, 2, 2],
        "High":   [1, 2, None, 3],
        "Low":    [1, 1, 2, None],
        "Close":  [1, 2, 2, 3],
        "Volume": [100, None, 200, 300],
    }, index=idx)
    return df


def test_clean_drops_and_fills(raw_df):
    cleaner = DataCleaner()
    clean = cleaner.clean(raw_df)
    # no NaNs remain, and all closes positive
    assert not clean.isna().any().any()
    assert (clean["Close"] > 0).all()
