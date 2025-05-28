# src/broker.py

"""Broker interface implemented using the Alpaca trade API."""

try:
    from alpaca_trade_api import REST
except Exception:  # pragma: no cover - optional dependency
    REST = None


class BrokerInterface:
    """Simple wrapper over Alpaca's REST trade API."""

    def __init__(self, base_url: str, key: str, secret: str):
        if REST is None:
            raise ImportError("alpaca_trade_api is required for BrokerInterface")
        self.api = REST(key_id=key, secret_key=secret, base_url=base_url)

    def send_order(self, ticker: str, qty: int, action: str) -> dict:
        """Submit a market order and wait until it is filled."""
        side = 'buy' if action.upper() == 'BUY' else 'sell'
        order = self.api.submit_order(
            symbol=ticker,
            qty=qty,
            side=side,
            type='market',
            time_in_force='day'
        )
        order = self.api.get_order(order.id)
        return {
            'ticker': ticker,
            'action': action,
            'qty': qty,
            'avgFillPrice': float(order.filled_avg_price or 0)
        }
