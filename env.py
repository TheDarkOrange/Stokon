# src/env.py

import gym
from gym import spaces
import numpy as np
import pandas as pd


class DRLTradingEnv(gym.Env):
    """
    Gym environment for daily equity trading.
    Observation: flattened features.
    Action: portfolio weights [-1,1]^N.
    Reward: next-day PnL net of costs.
    """
    metadata = {'render.modes': ['human']}

    def __init__(
        self,
        price_df: pd.DataFrame,
        feature_df: pd.DataFrame,
        slippage: float = 0.0005,
        commission: float = 0.0002,
    ):
        super().__init__()
        self.dates = sorted(set(price_df.index.get_level_values('Date')))
        self.tickers = sorted(set(price_df.index.get_level_values('Ticker')))
        self.price_df = price_df['Close'].unstack()
        self.feature_df = feature_df.unstack(level='Ticker')
        self.slippage = slippage
        self.commission = commission
        self.cur_step = 0
        self.n = len(self.tickers)

        # spaces
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.n,), dtype=np.float32)
        f = self.feature_df.shape[1] // self.n
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.n * f,), dtype=np.float32
        )

    def reset(self):
        self.cur_step = 0
        self.prev_action = np.zeros(self.n, dtype=np.float32)
        return self._get_obs()

    def _get_obs(self):
        date = self.dates[self.cur_step]
        feats = self.feature_df.loc[date].values.flatten()
        return feats.astype(np.float32)

    def step(self, action):
        date = self.dates[self.cur_step]
        next_date = self.dates[self.cur_step + 1]
        prices = self.price_df.loc[date].values
        next_prices = self.price_df.loc[next_date].values

        returns = (next_prices - prices) / prices
        pnl = np.dot(action, returns) / self.n

        turnover = np.abs(action - self.prev_action).sum() / \
            self.n if self.cur_step > 0 else np.abs(action).sum() / self.n
        cost = turnover * (self.slippage + self.commission)
        reward = pnl - cost

        self.prev_action = action.copy()
        self.cur_step += 1
        done = self.cur_step >= len(self.dates) - 1
        obs = self._get_obs() if not done else np.zeros_like(self._get_obs())
        info = {'pnl': pnl, 'cost': cost}
        return obs, reward, done, info

    def render(self, mode='human'):
        pass

    def close(self):
        pass
