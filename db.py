# src/db.py

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, MetaData, Table
)
from sqlalchemy.orm import sessionmaker
from .config import DB_URL

# Create engine & metadata
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
metadata = MetaData()

# Define trades table schema
trades = Table(
    'trades', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('date', Date, nullable=False),
    Column('ticker', String(10), nullable=False),
    Column('action', String(4), nullable=False),
    Column('qty', Integer, nullable=False),
    Column('avgFillPrice', Float, nullable=False),
    Column('slice_time', String, nullable=True),
    Column('commission', Float, nullable=True),
    Column('slippage', Float, nullable=True),
)


def init_db():
    """Create tables if they don’t exist."""
    metadata.create_all(engine)


class DBManager:
    """Helper to persist trade executions into Postgres."""

    def __init__(self):
        self.session = Session()

    def save_trades(self, df):
        """
        Expects a DataFrame with columns matching the trades table:
        ['date','ticker','action','qty','avgFillPrice','slice_time','commission','slippage']
        """
        # ensure the table exists
        init_db()
        # write out
        df.to_sql('trades', con=engine, if_exists='append', index=False)
