# src/broker.py

from ib_insync import IB, MarketOrder, Stock


class BrokerInterface:
    """Interactive Brokers REST/WebSocket wrapper via ib_insync."""

    def __init__(self, host: str, port: int, client_id: int):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)

    def send_order(self, ticker: str, qty: int, action: str) -> dict:
        """
        action: 'BUY' or 'SELL'
        Blocks until filled.
        """
        contract = Stock(ticker, 'SMART', 'USD')
        order = MarketOrder(action, qty)
        trade = self.ib.placeOrder(contract, order)
        trade.waitUntilFilled()
        return {
            'ticker': ticker,
            'action': action,
            'qty': qty,
            'avgFillPrice': trade.orderStatus.avgFillPrice
        }
