# docs/source/api.rst

API Specification
=================

This system does not currently expose a public REST API.  Planned endpoints:

.. code-block:: yaml

   openapi: 3.0.1
   info:
     title: Trading System API
     version: 1.0.0
   paths:
     /metrics:
       get:
         summary: Get latest run metrics
         responses:
           '200':
             description: JSON of performance metrics
             content:
               application/json:
                 schema:
                   type: object
                   properties:
                     sharpe:
                       type: number
                       description: Sharpe ratio
                     max_drawdown:
                       type: number
                       description: Maximum drawdown
                     profit_factor:
                       type: number
                       description: Profit factor
                     total_pnl:
                       type: number
                       description: Total P&L
                     num_trades:
                       type: integer
                       description: Number of trades executed
     /trades:
       get:
         summary: List trades for a given date
         parameters:
           - in: query
             name: date
             schema:
               type: string
               format: date
             required: true
             description: Date (YYYY-MM-DD) to fetch trades for
         responses:
           '200':
             description: Array of trade objects
             content:
               application/json:
                 schema:
                   type: array
                   items:
                     type: object
                     properties:
                       ticker:
                         type: string
                       action:
                         type: string
                       qty:
                         type: integer
                       price:
                         type: number
                       commission:
                         type: number
                       slippage:
                         type: number
                       slice_time:
                         type: string
                         format: date-time
