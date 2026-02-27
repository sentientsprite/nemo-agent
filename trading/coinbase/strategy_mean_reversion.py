"""
Strategy B: Mean Reversion

Entry: RSI oversold/overbought + price at Bollinger Band extremes.
Exit: RSI returns to neutral zone or price returns to BB middle.
"""
import logging
import math

from config import Config
from exchange import Exchange
from signals import rsi, bollinger_bands

log = logging.getLogger("mean_reversion")


class Signal:
    def __init__(self, action: str, pair: str, reason: str, strength: float = 0.0):
        self.action = action
        self.pair = pair
        self.reason = reason
        self.strength = strength

    def __repr__(self):
        return f"Signal({self.action} {self.pair}: {self.reason} [{self.strength:.0%}])"


class MeanReversionStrategy:
    def __init__(self, config: Config, exchange: Exchange):
        self.cfg = config
        self.exchange = exchange
        self.name = "mean_reversion"

    def evaluate(self, pair: str) -> Signal:
        candles = self.exchange.get_candles(pair, self.cfg.candle_interval_short, limit=60)
        if len(candles) < 30:
            return Signal("HOLD", pair, "Insufficient data", 0)

        closes = [c.close for c in candles]
        price = closes[-1]

        rsi_vals = rsi(closes, self.cfg.rsi_period)
        current_rsi = rsi_vals[-1]
        prev_rsi = rsi_vals[-2] if len(rsi_vals) > 1 else float("nan")

        bb_upper, bb_mid, bb_lower = bollinger_bands(closes, self.cfg.bb_period, self.cfg.bb_std)
        upper = bb_upper[-1]
        mid = bb_mid[-1]
        lower = bb_lower[-1]

        if any(math.isnan(v) for v in [current_rsi, upper, mid, lower]):
            return Signal("HOLD", pair, "Indicators not ready", 0)

        # ── BUY: oversold + at lower BB ──
        oversold = current_rsi <= self.cfg.rsi_oversold
        at_lower_band = price <= lower
        rsi_turning_up = not math.isnan(prev_rsi) and current_rsi > prev_rsi

        if oversold and at_lower_band:
            strength = 0.85 if rsi_turning_up else 0.65
            return Signal("BUY", pair,
                          f"Oversold RSI={current_rsi:.1f} + price at lower BB (${lower:.0f})"
                          + (" [RSI turning up]" if rsi_turning_up else ""), strength)

        if oversold and rsi_turning_up:
            return Signal("BUY", pair, f"RSI oversold {current_rsi:.1f} and turning up", 0.5)

        # ── SELL: overbought + at upper BB ──
        overbought = current_rsi >= self.cfg.rsi_overbought
        at_upper_band = price >= upper
        rsi_turning_down = not math.isnan(prev_rsi) and current_rsi < prev_rsi

        if overbought and at_upper_band:
            strength = 0.85 if rsi_turning_down else 0.65
            return Signal("SELL", pair,
                          f"Overbought RSI={current_rsi:.1f} + price at upper BB (${upper:.0f})"
                          + (" [RSI turning down]" if rsi_turning_down else ""), strength)

        if overbought and rsi_turning_down:
            return Signal("SELL", pair, f"RSI overbought {current_rsi:.1f} and turning down", 0.5)

        # ── EXIT: RSI neutral + price near mid ──
        rsi_neutral = self.cfg.mr_exit_rsi_low <= current_rsi <= self.cfg.mr_exit_rsi_high
        price_near_mid = abs(price - mid) / mid < 0.005

        if rsi_neutral and price_near_mid:
            return Signal("EXIT", pair, f"RSI neutral ({current_rsi:.1f}) + price near BB mid", 0.7)

        return Signal("HOLD", pair,
                      f"No signal (RSI={current_rsi:.1f}, BB={lower:.0f}/{mid:.0f}/{upper:.0f})", 0)
