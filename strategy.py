# src/strategy.py

import pandas as pd
import numpy as np
from stable_baselines3 import SAC


class StrategyEngine:
    """
    Ensemble of momentum (5d), RSI pullback, and optional DRL agent.
    """

    def __init__(self, drl_model_path: str = "models/sac_trader.zip"):
        try:
            self.drl_model = SAC.load(drl_model_path)
        except Exception:
            self.drl_model = None

    def generate_signals(
        self,
        price_df: pd.DataFrame,
        features: pd.DataFrame
    ) -> pd.Series:
        """
        Returns MultiIndex (Date, Ticker) → signal ∈ {-1,0,+1}
        """
        # Momentum decile signals
        mom = features['5d_mom']
        mom_sig = mom.groupby(level=0).apply(
            lambda x: pd.Series(
                np.where(
                    x >= x.quantile(0.9), 1,
                    np.where(x <= x.quantile(0.1), -1, 0)
                ),
                index=x.index
            )
        )

        # RSI pullback: buy RSI<30, sell RSI>40
        rsi = features['rsi']
        rsi_sig = pd.Series(0, index=rsi.index)
        rsi_sig[rsi < 30] = 1
        rsi_sig[rsi > 40] = -1

        # Combine and clip
        signal = mom_sig.add(rsi_sig, fill_value=0).clip(-1, 1)

        # Blend DRL only for the latest date if available
        if self.drl_model is not None:
            last_date = signal.index.get_level_values('Date').max()
            # build observation from last feature row
            obs = features.unstack('Ticker').loc[last_date].values.flatten()
            drl_act, _ = self.drl_model.predict(obs, deterministic=True)
            tickers = signal.xs(last_date, level='Date').index
            drl_ser = pd.Series(drl_act, index=tickers)
            # override last-date signals with 50/50 blend
            for t in tickers:
                original = signal.loc[(last_date, t)]
                signal.loc[(last_date, t)] = 0.5 * original + 0.5 * drl_ser[t]

        return signal
