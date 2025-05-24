# tests/test_db.py

import pytest
import pandas as pd
from sqlalchemy import create_engine
import src.db as db


@pytest.fixture(autouse=True)
def setup_engine(monkeypatch):
    # override engine and Session for in-memory sqlite
    engine = create_engine("sqlite:///:memory:")
    monkeypatch.setattr(db, 'engine', engine)
    monkeypatch.setattr(db, 'Session', db.sessionmaker(bind=engine))
    # create table
    db.metadata.create_all(engine)
    return engine


def test_save_trades(setup_engine):
    df = pd.DataFrame({
        "date":       [pd.Timestamp("2025-01-01")],
        "ticker":     ["A"],
        "action":     ["BUY"],
        "qty":        [10],
        "price":      [100.0],
        "commission": [0.1],
        "slippage":   [0.05]
    })
    mgr = db.DBManager()
    mgr.save_trades(df)
    conn = setup_engine.connect()
    result = conn.execute(db.trades.select()).fetchall()
    assert len(result) == 1
    assert result[0]['ticker'] == "A"
