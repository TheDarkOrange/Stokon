# src/drl_agent.py

from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import CheckpointCallback
import pandas as pd

from .env import DRLTradingEnv
from .fetcher import DataFetcher
from .cleaner import DataCleaner
from .features import FeatureEngineer


def train_drl_agent(
    tickers, start, end,
    model_path="models/sac_trader.zip",
    log_dir="logs/",
    total_timesteps=100_000
):
    # prepare data
    raw = DataFetcher().fetch_daily(tickers, start, end)
    clean = DataCleaner().clean(raw)
    feats = FeatureEngineer().build_features(clean)

    # environment
    env = DRLTradingEnv(clean, feats)

    # model
    checkpoint = CheckpointCallback(
        save_freq=10_000, save_path=log_dir, name_prefix="sac")
    model = SAC("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)

    # train
    model.learn(total_timesteps=total_timesteps, callback=checkpoint)
    model.save(model_path)
    print(f"Saved DRL agent to {model_path}")
    return model


if __name__ == "__main__":
    tickers = [
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "NVDA",  # Nvidia
        "AMZN",  # Amazon.com
        "META",  # Meta Platforms
        "BRK.B",  # Berkshire Hathaway Class B
        "GOOGL",  # Alphabet Class A
        "AVGO",  # Broadcom
        "TSLA",  # Tesla
        "GOOG",  # Alphabet Class C
        "LLY",   # Eli Lilly
        "JPM",   # JPMorgan Chase
        "V",     # Visa
        "XOM",   # Exxon Mobil
        "NFLX",  # Netflix
        "COST",  # Costco Wholesale
        "MA",    # Mastercard
        "WMT",   # Walmart
        "UNH",   # UnitedHealth Group
        "PG"     # Procter & Gamble
    ]
    train_drl_agent(tickers, "2020-01-01", "2025-01-01")
