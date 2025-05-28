# tests/test_reporting.py

import pytest
import pandas as pd
import src.reporting as reporting


class DummySMTP:
    def __init__(self, *args, **kwargs): pass
    def starttls(self, context): pass
    def login(self, user, pw): pass
    def send_message(self, msg): self.sent = True
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass


class DummyResp:
    status_code = 200
    text = "ok"
    def raise_for_status(self): pass


@pytest.fixture(autouse=True)
def patch_network(monkeypatch):
    monkeypatch.setattr("src.reporting.smtplib.SMTP", DummySMTP)
    monkeypatch.setattr("src.reporting.requests.post",
                        lambda url, json, timeout: DummyResp())


def test_format_report():
    m = {"date": "2025-05-24", "sharpe": 1.23,
         "max_drawdown": -0.05, "profit_factor": 2.5}
    txt = reporting.format_report(m)
    assert "1.23" in txt and "-5.00%" in txt and "2.50" in txt


def test_send_daily_report_no_errors():
    m = {"date": "2025-05-24", "sharpe": 1.0,
         "max_drawdown": -0.02, "profit_factor": 1.5}
    df = pd.DataFrame([{"ticker": "X", "avgFillPrice": 100, "qty": 1}])
    # should not raise
    reporting.send_daily_report(m, trades_df=df)
