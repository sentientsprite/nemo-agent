"""
Strategy A: Momentum / Trend Following

Entry: EMA crossover confirmed by MACD histogram + volume surge on 5-min candles.
Exit: EMA cross back or MACD histogram reversal.
"""
import logging
import math

from config import Config
from exchange import Exchange
from signals import ema, macd, avg_volume

log = logging.getLogger("momentum")


class Signal:
    def __init__(self, action: str, pair: str, reason: str, strength: float = 0.0):
        self.action = action  # BUY, SELL, HOLD
        self.pair = pair
        self.reason = reason
        self.strength = strength

    def __repr__(self):
        return f"Signal({self.action} {self.pair}: {self.reason} [{self.strength:.0%}])"


class MomentumStrategy:
    def __init__(self, config: Config, exchange: Exchange):
        self.cfg = config
        self.exchange = exchange
        self.name = "momentum"

    def evaluate(self, pair: str) -> Signal:
        candles = self.exchange.get_candles(pair, self.cfg.candle_interval_short, limit=60)
        if len(candles) < 30:
            return Signal("HOLD", pair, "Insufficient data", 0)

        closes = [c.close for c in candles]
        volumes = [c.volume for c in candles]

        ema_fast_vals = ema(closes, self.cfg.ema_fast)
        ema_slow_vals = ema(closes, self.cfg.ema_slow)
        macd_line, signal_line, histogram = macd(closes, 12, 26, self.cfg.macd_signal)
        vol_avg = avg_volume(volumes, 20)

        ef = ema_fast_vals[-1]
        es = ema_slow_vals[-1]
        ef_prev = ema_fast_vals[-2]
        es_prev = ema_slow_vals[-2]
        hist_now = histogram[-1]
        hist_prev = histogram[-2]
        current_vol = volumes[-1]

        if any(math.isnan(v) for v in [ef, es, ef_prev, es_prev, hist_now, hist_prev]):
            return Signal("HOLD", pair, "Indicators not ready", 0)

        # ── BUY Signal ──
        ema_bullish_cross = ef > es and ef_prev <= es_prev
        ema_bullish_trend = ef > es
        macd_bullish = hist_now > 0 and hist_now > hist_prev
        vol_surge = vol_avg is not None and current_vol > vol_avg * self.cfg.momentum_min_volume_ratio

        if ema_bullish_cross and macd_bullish:
            strength = 0.8 if vol_surge else 0.6
            return Signal("BUY", pair, f"EMA cross up + MACD rising (vol={'surge' if vol_surge else 'normal'})", strength)

        if ema_bullish_trend and macd_bullish and vol_surge:
            return Signal("BUY", pair, "Trend continuation + volume surge", 0.5)

        # ── SELL Signal ──
        ema_bearish_cross = ef < es and ef_prev >= es_prev
        macd_bearish = hist_now < 0 and hist_now < hist_prev

        if ema_bearish_cross:
            return Signal("SELL", pair, "EMA cross down — trend reversal", 0.8)

        if macd_bearish and ef < es:
            return Signal("SELL", pair, "MACD declining in downtrend", 0.6)

        # Momentum fading
        if (ema_bullish_trend and hist_now < hist_prev
                and len(histogram) > 2 and not math.isnan(histogram[-3])
                and hist_prev < histogram[-3]):
            return Signal("SELL", pair, "Momentum fading — 3 declining MACD bars", 0.5)

        return Signal("HOLD", pair, f"No signal (EMA {ef:.0f}/{es:.0f}, MACD hist: {hist_now:.2f})", 0)
