# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env into os.environ

# Database
DB_URL = os.getenv("DATABASE_URL")

# Trading universe (comma-separated in .env or hardcode here)
TICKERS = os.getenv("TICKERS", "AAPL,MSFT,GOOG").split(",")

# Backtest parameters
SLIPPAGE = float(os.getenv("SLIPPAGE", 0.0005))
COMMISSION = float(os.getenv("COMMISSION", 0.0002))

# Alpaca API
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL")
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

# Email reporting
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 0))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
REPORT_EMAIL = os.getenv("REPORT_EMAIL", EMAIL_USER)

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Prometheus Pushgateway
METRICS_PUSHGATEWAY = os.getenv("METRICS_PUSHGATEWAY", "")
