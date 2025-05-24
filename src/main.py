# src/main.py

import argparse
import datetime as dt
import pandas as pd

from .config import (
    TICKERS, SLIPPAGE, COMMISSION,
    IB_HOST, IB_PORT, IB_CLIENT_ID,
)
from .fetcher import DataFetcher
from .cleaner import DataCleaner
from .features import FeatureEngineer
from .strategy import StrategyEngine
from .backtester import Backtester, PerformanceReport
from .minute_fetcher import MinuteDataFetcher
from .intraday_backtester import IntradayBacktester
from .broker import BrokerInterface
from .execution import ExecutionEngine
from .order_slicer import TWAPSlicer, VWAPSlicer
from .reporting import send_daily_report
from .metrics import MetricsPusher
from .db import init_db, DBManager


def run_daily_job(dry_run: bool = False):
    today = dt.date.today()
    start = today - dt.timedelta(days=365*2)

    # 1) Fetch & clean
    df_raw = DataFetcher().fetch_daily(TICKERS, start.isoformat(), today.isoformat())
    df_clean = DataCleaner().clean(df_raw)

    # 2) Features & signals
    feats = FeatureEngineer().build_features(df_clean)
    strat = StrategyEngine()
    weights = strat.generate_signals(df_clean, feats)

    # 3) Intraday backtest for risk check
    mdf = MinuteDataFetcher(IB_HOST, IB_PORT, IB_CLIENT_ID)
    minute_df = mdf.fetch_daily_minute(TICKERS, today)
    intrabt = IntradayBacktester(SLIPPAGE, COMMISSION)
    daily_rets = intrabt.run_intraday(weights, df_clean, minute_df)
    perf_daily = PerformanceReport(daily_rets)
    print(
        f"Intraday Sharpe: {perf_daily.sharpe:.2f}, MaxDD: {perf_daily.max_drawdown:.2%}")

    # 4) Execute
    init_db()
    if not dry_run:
        broker = BrokerInterface(IB_HOST, IB_PORT, IB_CLIENT_ID)
        exec_engine = ExecutionEngine(
            broker, slicing_method='VWAP', twap_intervals=10)
        exec_df = exec_engine.execute(
            weights, df_clean, minute_df, total_capital=1_000_000)
        DBManager().save_trades(exec_df)
    else:
        exec_df = pd.DataFrame(
            columns=['ticker', 'qty', 'action', 'avgFillPrice'])

    # 5) Reporting & metrics
    metrics = {
        'date': today.isoformat(),
        'sharpe': perf_daily.sharpe,
        'max_drawdown': perf_daily.max_drawdown,
        'profit_factor': perf_daily.profit_factor,
    }
    send_daily_report(metrics, trades_df=exec_df)
    mp = MetricsPusher()
    mp.push({
        'daily_sharpe': perf_daily.sharpe,
        'daily_max_drawdown': perf_daily.max_drawdown,
        'daily_profit_factor': perf_daily.profit_factor,
        'daily_total_pnl': exec_df.eval('qty * avgFillPrice').sum() if not exec_df.empty else 0.0,
        'daily_num_trades': len(exec_df),
    })


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true",
                   help="skip real order placement")
    args = p.parse_args()
    run_daily_job(dry_run=args.dry_run)
