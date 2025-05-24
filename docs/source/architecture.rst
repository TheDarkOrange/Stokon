
# docs/source/architecture.rst

Architecture
============

The **Stokon** trading system is composed of modular stages:

.. mermaid::

   classDiagram
       DataFetcher --> DataCleaner
       DataCleaner --> FeatureEngineer
       FeatureEngineer --> StrategyEngine
       StrategyEngine --> Backtester
       StrategyEngine --> ExecutionEngine
       ExecutionEngine --> BrokerInterface
       ExecutionEngine --> DBManager

Sequence Diagram
----------------

.. mermaid::

   sequenceDiagram
     participant F as Fetcher
     participant C as Cleaner
     participant E as Engineer
     participant S as Strategy
     participant B as Backtester
     participant X as Executor

     F->>C: fetch raw OHLCV
     C->>E: clean & backfill data
     E->>S: compute features
     S->>B: generate signals
     B-->>S: backtest report
     S->>X: target weights
     X->>Broker: submit orders
     X->>DB: record trades
