"""
Technical indicators — pure functions operating on price lists.
"""
from typing import List, Optional, Tuple
import math


def ema(prices: List[float], period: int) -> List[float]:
    """Exponential Moving Average."""
    if len(prices) < period:
        return [float("nan")] * len(prices)
    result = [float("nan")] * (period - 1)
    k = 2.0 / (period + 1)
    sma_val = sum(prices[:period]) / period
    result.append(sma_val)
    for i in range(period, len(prices)):
        sma_val = prices[i] * k + result[-1] * (1 - k)
        result.append(sma_val)
    return result


def sma(prices: List[float], period: int) -> List[float]:
    """Simple Moving Average."""
    if len(prices) < period:
        return [float("nan")] * len(prices)
    result = [float("nan")] * (period - 1)
    for i in range(period - 1, len(prices)):
        result.append(sum(prices[i - period + 1 : i + 1]) / period)
    return result


def rsi(prices: List[float], period: int = 14) -> List[float]:
    """Relative Strength Index (Wilder's smoothing)."""
    if len(prices) < period + 1:
        return [float("nan")] * len(prices)
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(d, 0) for d in deltas]
    losses = [abs(min(d, 0)) for d in deltas]

    result = [float("nan")] * period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        result.append(100.0)
    else:
        rs = avg_gain / avg_loss
        result.append(100.0 - 100.0 / (1.0 + rs))

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100.0 - 100.0 / (1.0 + rs))
    return result


def bollinger_bands(
    prices: List[float], period: int = 20, num_std: float = 2.0
) -> Tuple[List[float], List[float], List[float]]:
    """Returns (upper, middle, lower) bands."""
    mid = sma(prices, period)
    upper = []
    lower = []
    for i in range(len(prices)):
        if math.isnan(mid[i]):
            upper.append(float("nan"))
            lower.append(float("nan"))
        else:
            window = prices[i - period + 1 : i + 1]
            std = (sum((x - mid[i]) ** 2 for x in window) / period) ** 0.5
            upper.append(mid[i] + num_std * std)
            lower.append(mid[i] - num_std * std)
    return upper, mid, lower


def macd(
    prices: List[float], fast: int = 12, slow: int = 26, signal_period: int = 9
) -> Tuple[List[float], List[float], List[float]]:
    """MACD line, signal line, histogram."""
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = []
    for i in range(len(prices)):
        if math.isnan(ema_fast[i]) or math.isnan(ema_slow[i]):
            macd_line.append(float("nan"))
        else:
            macd_line.append(ema_fast[i] - ema_slow[i])
    valid_macd = [v for v in macd_line if not math.isnan(v)]
    signal = ema(valid_macd, signal_period) if len(valid_macd) >= signal_period else [float("nan")] * len(valid_macd)
    signal_full = []
    j = 0
    for v in macd_line:
        if math.isnan(v):
            signal_full.append(float("nan"))
        else:
            signal_full.append(signal[j] if j < len(signal) else float("nan"))
            j += 1
    histogram = []
    for i in range(len(prices)):
        if math.isnan(macd_line[i]) or math.isnan(signal_full[i]):
            histogram.append(float("nan"))
        else:
            histogram.append(macd_line[i] - signal_full[i])
    return macd_line, signal_full, histogram


def avg_volume(volumes: List[float], period: int = 20) -> Optional[float]:
    """Average volume over last `period` bars."""
    if len(volumes) < period:
        return None
    return sum(volumes[-period:]) / period
