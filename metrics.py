# src/metrics.py

import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from .config import METRICS_PUSHGATEWAY

logger = logging.getLogger("trading")


class MetricsPusher:
    """
    Push daily run metrics to a Prometheus Pushgateway if configured.
    """

    def __init__(self, gateway_url: str = METRICS_PUSHGATEWAY):
        self.gateway = gateway_url
        self.registry = CollectorRegistry()
        self.gauges = {
            'daily_sharpe':        Gauge('daily_sharpe',        'Daily Sharpe Ratio',     registry=self.registry),
            'daily_max_drawdown':  Gauge('daily_max_drawdown',  'Daily Max Drawdown',     registry=self.registry),
            'daily_profit_factor': Gauge('daily_profit_factor', 'Daily Profit Factor',    registry=self.registry),
            'daily_total_pnl':     Gauge('daily_total_pnl',     'Daily Total P&L',        registry=self.registry),
            'daily_num_trades':    Gauge('daily_num_trades',    'Number of Trades',       registry=self.registry),
        }

    def push(self, metrics: dict):
        """Push to gateway, or skip if no URL is configured."""
        if not self.gateway:
            logger.warning(
                "No Prometheus Pushgateway configured; skipping metrics push")
            return

        for key, gauge in self.gauges.items():
            if key in metrics:
                gauge.set(metrics[key])

        try:
            push_to_gateway(self.gateway, job='daily_trader', registry=self.registry)
            logger.info("Metrics pushed to Pushgateway")
        except Exception as e:
            logger.error("Metrics push failed; continuing", exc_info=e)
