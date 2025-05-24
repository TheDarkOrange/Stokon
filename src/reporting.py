# src/reporting.py

import logging
import json
import smtplib
import ssl
import requests
from email.message import EmailMessage
from typing import Dict, Any

from .config import (
    REPORT_EMAIL,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USER,
    EMAIL_PASS,
    SLACK_WEBHOOK_URL,
)

# structured logger
logger = logging.getLogger("trading")
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter(json.dumps({
        "time": "%(asctime)s",
        "level": "%(levelname)s",
        "module": "%(module)s",
        "message": "%(message)s"
    }))
    h.setFormatter(fmt)
    logger.addHandler(h)


def send_email(subject: str, body: str, to: str = REPORT_EMAIL) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg.set_content(body)

    ctx = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls(context=ctx)
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    logger.info("Email sent", extra={"subject": subject})


def send_slack(message: str, webhook_url: str = SLACK_WEBHOOK_URL) -> None:
    if not webhook_url:
        logger.warning("No Slack webhook configured; skipping.")
        return
    resp = requests.post(webhook_url, json={"text": message}, timeout=5)
    if resp.status_code != 200:
        logger.error("Slack failed", extra={
                     "status": resp.status_code, "resp": resp.text})
        resp.raise_for_status()
    logger.info("Slack message sent")


def format_report(metrics: Dict[str, Any]) -> str:
    return (
        f"*Daily Report {metrics['date']}*\n"
        f"> Sharpe: {metrics['sharpe']:.2f}\n"
        f"> MaxDD: {metrics['max_drawdown']:.2%}\n"
        f"> ProfitFactor: {metrics['profit_factor']:.2f}\n"
        f"> TotalPnL: ${metrics.get('total_pnl',0):.2f}\n"
        f"> Trades: {metrics.get('num_trades',0)}\n"
    )


def send_daily_report(metrics: Dict[str, Any], trades_df=None) -> None:
    if trades_df is not None:
        metrics["total_pnl"] = (
            trades_df["qty"] * trades_df["avgFillPrice"]).sum()
        metrics["num_trades"] = len(trades_df)
    text = format_report(metrics)
    try:
        send_slack(text)
    except Exception:
        logger.exception("Slack report failed")
    try:
        send_email(f"Daily Trading Report: {metrics['date']}", text)
    except Exception:
        logger.exception("Email report failed")
