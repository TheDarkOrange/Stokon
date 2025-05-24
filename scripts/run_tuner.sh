#!/usr/bin/env bash
# scripts/run_tuner.sh

source /path/to/venv/bin/activate
cd /path/to/Stokon

python - << 'EOF'
from src.tuner import tune_hyperparameters
import pandas as pd

grid = {
  "mom_short": [5,10,15],
  "mom_long":  [20,40,60],
  "rsi_window":[14,21],
  "slippage":  [0.0005, 0.001],
  "commission":[0.0002,0.0005]
}
df = tune_hyperparameters(
  tickers=["AAPL","MSFT","GOOG"],
  start="2020-01-01",
  end="2025-01-01",
  param_grid=grid,
  train_len=252*2,
  test_len=252
)
print(df.head(10))
df.to_csv("tuning_results.csv", index=False)
EOF
