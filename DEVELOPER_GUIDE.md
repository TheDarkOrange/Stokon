# Developer Quick-Start

Welcome to **Stokon**! This guide helps new developers get up to speed.

## Branching & Commits

- Use GitFlow: `feature/*`, `hotfix/*` branches
- Follow Conventional Commits for changelog

## Local Workflow

```bash
# Activate environment
source venv/bin/activate

# Run unit tests
pytest --maxfail=1 --disable-warnings -q

# Run linter
flake8 src tests

# Smoke-fetch a ticker
python - << 'EOF'
from src.fetcher import DataFetcher
print(DataFetcher().fetch_daily(['AAPL'], '2025-01-01','2025-02-01').head())
EOF
```
