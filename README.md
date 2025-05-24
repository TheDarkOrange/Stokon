# Stokon

A fully-automated end-of-day equities trading engine with:

- **Modular** data ingestion, cleaning, feature engineering, strategy, backtesting, execution
- **Regime-aware**, **DRL-enhanced**, **optimizer-driven**, **volatility-targeted** signals
- **Intraday stop-losses**, **VWAP/TWAP slicing**, **Prometheus metrics**, **Slack/email reports**
- **CI/CD**, **containerization**, **Kubernetes** scheduling, and **Helm** deployment

---

## 📦 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14
- IB TWS or Gateway running
- Docker & kubectl (for containerized deployments)

### Installation

```bash
git clone git@github.com:TheDarkOrange/Stokon.git
cd Stokon
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
