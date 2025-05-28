# src/tuner.py

import numpy as np
import pandas as pd
from sklearn.model_selection import ParameterGrid
from typing import List, Dict, Any

from ta.momentum import RSIIndicator
from .fetcher import DataFetcher
from .cleaner import DataCleaner
from .backtester import Backtester
from .config import SLIPPAGE, COMMISSION


def build_features(
    df: pd.DataFrame,
    mom_short: int,
    mom_long: int,
    rsi_window: int
) -> pd.DataFrame:
    f = df.copy()
    f['mom_short'] = f.groupby('Ticker')['Close'].pct_change(mom_short)
    f['mom_long'] = f.groupby('Ticker')['Close'].pct_change(mom_long)
    f['rsi'] = f.groupby('Ticker')['Close'] \
        .apply(lambda x: RSIIndicator(x, window=rsi_window).rsi())
    return f.dropna()


def gen_mom_signals(
    feats: pd.DataFrame,
    short_q: float = 0.1,
    long_q: float = 0.9
) -> pd.Series:
    s = feats['mom_short']
    sig_list = []
    for date, grp in s.groupby(level=0):
        hi = grp.quantile(long_q)
        lo = grp.quantile(short_q)
        sig_list.append(pd.Series(
            np.where(grp >= hi, 1, np.where(grp <= lo, -1, 0)),
            index=grp.index
        ))
    return pd.concat(sig_list).sort_index()


def walk_forward_splits(
    dates: pd.DatetimeIndex,
    train_len: int,
    test_len: int
) -> List[Dict[str, pd.DatetimeIndex]]:
    splits = []
    for start in range(0, len(dates) - train_len - test_len + 1, test_len):
        tr = dates[start: start + train_len]
        te = dates[start + train_len: start + train_len + test_len]
        splits.append({'train': tr, 'test': te})
    return splits


def tune_hyperparameters(
    tickers: List[str],
    start: str,
    end: str,
    param_grid: Dict[str, List[Any]],
    train_len: int,
    test_len: int
) -> pd.DataFrame:
    raw = DataFetcher().fetch_daily(tickers, start, end)
    clean = DataCleaner().clean(raw)
    dates = clean.index.get_level_values('Date').unique().sort_values()
    splits = walk_forward_splits(dates, train_len, test_len)

    results = []
    for params in ParameterGrid(param_grid):
        sharpes = []
        for sp in splits:
            mask = clean.index.get_level_values(
                'Date').isin(sp['train'].union(sp['test']))
            window_df = clean.loc[mask]

            feats = build_features(
                window_df,
                mom_short=params['mom_short'],
                mom_long=params['mom_long'],
                rsi_window=params['rsi_window']
            )
            sig_full = gen_mom_signals(feats)
            test_mask = sig_full.index.get_level_values(
                'Date').isin(sp['test'])
            sig_test = sig_full[test_mask]

            price_test = window_df.loc[
                window_df.index.get_level_values('Date').isin(sp['test'])
            ]
            bt = Backtester()
            perf = bt.run_backtest(
                price_test,
                sig_test,
                slippage=params.get('slippage', SLIPPAGE),
                commission=params.get('commission', COMMISSION)
            )
            sharpes.append(perf.sharpe)

        avg_sharpe = float(np.mean(sharpes))
        res = params.copy()
        res['avg_sharpe'] = avg_sharpe
        results.append(res)

    df = pd.DataFrame(results)
    return df.sort_values('avg_sharpe', ascending=False).reset_index(drop=True)
