# src/main.py

import argparse
import datetime as dt
import logging
import pandas as pd

from .config import (
    TICKERS,
    SLIPPAGE,
    COMMISSION,
    IB_HOST,
    IB_PORT,
    IB_CLIENT_ID,
)
from .fetcher import DataFetcher
from .cleaner import DataCleaner
from .features import FeatureEngineer
from .strategy import StrategyEngine
from .backtester import Backtester, PerformanceReport
from .execution import ExecutionEngine
from .reporting import send_daily_report
from .metrics import MetricsPusher

# setup logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(module)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_daily_job(dry_run: bool = False):
    today = dt.date.today()
    start = today - dt.timedelta(days=365 * 2)

    logger.info(f"Starting daily job for {today} (dry_run={dry_run})")

    # 1) Fetch & clean
    df_raw = DataFetcher().fetch_daily(TICKERS, start.isoformat(), today.isoformat())
    df_clean = DataCleaner().clean(df_raw)

    # 2) Features & signals
    feats = FeatureEngineer().build_features(df_clean)
    strat = StrategyEngine()
    weights = strat.generate_signals(df_clean, feats)

    # Determine if we can connect to IB
    can_ib = not dry_run and IB_HOST and IB_PORT and IB_PORT > 0

    if not can_ib:
        # Skip minute-level and execution if dry-run or no valid IB settings
        logger.info(
            "🔧 IB disabled: running EOD-only backtest, skipping minute-level and execution.")

        # EOD backtest on daily close returns
        ret = df_clean.groupby("Ticker")["Close"].pct_change().fillna(0)
        pos = weights.groupby("Ticker").shift(1).fillna(0)
        pnl = pos * ret
        daily_ret = pnl.groupby("Date").mean()
        perf = PerformanceReport(daily_ret)

        exec_df = pd.DataFrame(columns=["ticker", "qty", "action", "avgFillPrice"])
    else:
        # 3) Intraday backtest & live execution
        try:
            from .minute_fetcher import MinuteDataFetcher
            from .intraday_backtester import IntradayBacktester
            from .broker import BrokerInterface
        except ImportError as e:
            logger.error("Missing IB modules: %s", e)
            raise

        # Intraday risk check (stop-loss)
        try:
            mdf = MinuteDataFetcher(IB_HOST, IB_PORT, IB_CLIENT_ID)
            minute_df = mdf.fetch_daily_minute(TICKERS, today)
            intrabt = IntradayBacktester(SLIPPAGE, COMMISSION)
            intraday_rets = intrabt.run_intraday(weights, df_clean, minute_df)
            perf = PerformanceReport(intraday_rets)
            logger.info(
                f"Intraday Sharpe: {perf.sharpe:.2f}, MaxDD: {perf.max_drawdown:.2%}")
        except Exception as e:
            logger.error(
                "Intraday backtest failed; falling back to EOD backtest: %s", e)
            # fallback to EOD
            ret = df_clean.groupby("Ticker")["Close"].pct_change().fillna(0)
            pos = weights.groupby("Ticker").shift(1).fillna(0)
            pnl = pos * ret
            daily_ret = pnl.groupby("Date").mean()
            perf = PerformanceReport(daily_ret)
            minute_df = None

        # Live execution if intraday backtest succeeded
        try:
            broker = BrokerInterface(IB_HOST, IB_PORT, IB_CLIENT_ID)
            exec_engine = ExecutionEngine(
                broker, slicing_method="VWAP", twap_intervals=10)
            exec_df = exec_engine.execute(
                weights, df_clean, minute_df, total_capital=1_000_000)
        except Exception as e:
            logger.error("Execution failed; no orders placed: %s", e)
            exec_df = pd.DataFrame(columns=["ticker", "qty", "action", "avgFillPrice"])

    # 4) Reporting & metrics
    metrics = {
        "date": today.isoformat(),
        "sharpe": perf.sharpe,
        "max_drawdown": perf.max_drawdown,
        "profit_factor": perf.profit_factor,
    }
    send_daily_report(metrics, trades_df=exec_df)

    try:
        mp = MetricsPusher()
        mp.push({
            "daily_sharpe":        perf.sharpe,
            "daily_max_drawdown":  perf.max_drawdown,
            "daily_profit_factor": perf.profit_factor,
            "daily_total_pnl":     exec_df.eval("qty * avgFillPrice").sum() if not exec_df.empty else 0.0,
            "daily_num_trades":    len(exec_df),
        })
    except Exception:
        logger.exception("Metrics push failed, continuing without error")

    logger.info("Daily job completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip IB connections & live execution; still compute performance",
    )
    args = parser.parse_args()
    run_daily_job(dry_run=args.dry_run)
