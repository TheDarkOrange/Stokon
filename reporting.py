# src/reporting.py

import logging
import json
import requests
from typing import Dict, Any

from .config import SLACK_WEBHOOK_URL

# Structured logger
logger = logging.getLogger("trading")
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter(json.dumps({
        "time":   "%(asctime)s",
        "level":  "%(levelname)s",
        "module": "%(module)s",
        "message": "%(message)s"
    }))
    h.setFormatter(fmt)
    logger.addHandler(h)


def send_slack(message: str, webhook_url: str = SLACK_WEBHOOK_URL) -> None:
    """Send a plain-text message to Slack via webhook, or skip if not configured."""
    if not webhook_url:
        logger.warning("No Slack webhook configured; skipping Slack report")
        return

    try:
        resp = requests.post(webhook_url, json={"text": message}, timeout=5)
        if resp.status_code != 200:
            logger.error(
                "Slack webhook returned non-200",
                extra={"status": resp.status_code, "resp": resp.text}
            )
        else:
            logger.info("Slack message sent")
    except Exception as e:
        logger.error("Slack send failed; continuing", exc_info=e)


def format_report(metrics: Dict[str, Any]) -> str:
    """
    Build a human-readable report from metrics.
    """
    return (
        f"*Daily Trading Report for {metrics['date']}*\n"
        f"> Sharpe Ratio: {metrics['sharpe']:.2f}\n"
        f"> Max Drawdown: {metrics['max_drawdown']:.2%}\n"
        f"> Profit Factor: {metrics['profit_factor']:.2f}\n"
        f"> Total P&L: ${metrics.get('total_pnl', 0.0):.2f}\n"
        f"> Number of Trades: {metrics.get('num_trades', 0)}\n"
    )


def send_daily_report(
    metrics: Dict[str, Any],
    trades_df=None
) -> None:
    """
    Send Slack report only; never raises.
    """
    if trades_df is not None:
        # add PnL and trade count if available
        try:
            metrics["total_pnl"] = (trades_df["qty"] * trades_df["avgFillPrice"]).sum()
        except Exception:
            metrics.setdefault("total_pnl", 0.0)
        try:
            metrics["num_trades"] = len(trades_df)
        except Exception:
            metrics.setdefault("num_trades", 0)

    text = format_report(metrics)

    # Only post to Slack now
    send_slack(text)
