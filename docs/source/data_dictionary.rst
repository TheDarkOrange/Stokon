# docs/source/data_dictionary.rst

Data Dictionary
===============

**Table: trades**

.. list-table::
   :header-rows: 1
   :widths: 15 15 50

   * - Column
     - Type
     - Description
   * - id
     - Integer
     - Primary key
   * - date
     - Date
     - Trade date
   * - ticker
     - String(10)
     - Ticker symbol
   * - action
     - String(4)
     - 'BUY' or 'SELL'
   * - qty
     - Integer
     - Number of shares
   * - price
     - Float
     - Fill price per share
   * - commission
     - Float
     - Commission charged
   * - slippage
     - Float
     - Slippage assumed per share
   * - slice_time
     - DateTime
     - Child-order timestamp (for TWAP/VWAP)
