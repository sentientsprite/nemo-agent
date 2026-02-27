"""
Coinbase Momentum Strategy
EMA crossover + MACD confirmation
"""
import logging
from datetime import datetime
from typing import List, Optional, Literal
from dataclasses import dataclass
from config import MomentumConfig
from exchanges.coinbase import CoinbaseExchange, Candle
from utils.risk import RiskManager, Position

log = logging.getLogger(__name__)

@dataclass
class Signal:
    action: Literal["BUY", "SELL", "HOLD"]
    strength: float  # 0.0 to 1.0
    reason: str
    price: float = 0.0

class MomentumStrategy:
    """
    Trend-following strategy using EMA crossover and MACD.
    Best for trending markets, suffers in chop.
    """
    
    def __init__(self, config: MomentumConfig, exchange: CoinbaseExchange, risk: RiskManager):
        self.config = config
        self.exchange = exchange
        self.risk = risk
        
        if not config.enabled:
            log.warning("Momentum strategy disabled")
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate EMA for price series."""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # SMA start
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def calculate_macd(self, prices: List[float]) -> tuple[List[float], List[float], List[float]]:
        """Calculate MACD line, signal line, and histogram."""
        ema_fast = self.calculate_ema(prices, self.config.macd_fast)
        ema_slow = self.calculate_ema(prices, self.config.macd_slow)
        
        # MACD line = fast EMA - slow EMA
        macd_line = [f - s for f, s in zip(ema_fast[-len(ema_slow):], ema_slow)]
        
        # Signal line = EMA of MACD line
        signal_line = self.calculate_ema(macd_line, self.config.macd_signal)
        
        # Histogram = MACD line - signal line
        histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]
        
        return macd_line, signal_line, histogram
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI."""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        rsi_values = []
        for i in range(period, len(deltas)):
            gains = [d for d in deltas[i-period:i] if d > 0]
            losses = [-d for d in deltas[i-period:i] if d < 0]
            
            avg_gain = sum(gains) / period if gains else 0
            avg_loss = sum(losses) / period if losses else 0
            
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(100 - (100 / (1 + rs)))
        
        return rsi_values
    
    def analyze(self, symbol: str) -> Signal:
        """Analyze market and generate signal."""
        if not self.config.enabled:
            return Signal("HOLD", 0.0, "Strategy disabled")
        
        # Get candles
        candles = self.exchange.get_candles(symbol, "ONE_MINUTE", 100)
        if len(candles) < 50:
            return Signal("HOLD", 0.0, "Insufficient data")
        
        closes = [c.close for c in candles]
        volumes = [c.volume for c in candles]
        
        # Calculate EMAs
        ema_fast = self.calculate_ema(closes, self.config.ema_fast)
        ema_slow = self.calculate_ema(closes, self.config.ema_slow)
        
        if len(ema_fast) < 2 or len(ema_slow) < 2:
            return Signal("HOLD", 0.0, "Indicators not ready")
        
        # EMA crossover
        ef_current, ef_prev = ema_fast[-1], ema_fast[-2]
        es_current, es_prev = ema_slow[-1], ema_slow[-2]
        
        bullish_cross = ef_current > es_current and ef_prev <= es_prev
        bearish_cross = ef_current < es_current and ef_prev >= es_prev
        bullish_trend = ef_current > es_current
        bearish_trend = ef_current < es_current
        
        # Calculate MACD
        try:
            macd_line, signal_line, histogram = self.calculate_macd(closes)
            macd_bullish = histogram[-1] > 0 if histogram else False
            macd_rising = len(histogram) > 1 and histogram[-1] > histogram[-2] if len(histogram) > 1 else False
        except Exception:
            macd_bullish = False
            macd_rising = False
        
        # Volume check
        avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 0
        current_volume = volumes[-1] if volumes else 0
        volume_surge = current_volume > avg_volume * self.config.min_volume_ratio
        
        # Generate signal
        current_price = closes[-1]
        
        if bullish_cross and macd_bullish:
            strength = 0.8 if volume_surge else 0.6
            return Signal("BUY", strength, 
                         f"EMA cross up + MACD rising (vol={'surge' if volume_surge else 'normal'})",
                         current_price)
        
        if bearish_cross and not macd_bullish:
            strength = 0.8 if volume_surge else 0.6
            return Signal("SELL", strength,
                         f"EMA cross down + MACD falling (vol={'surge' if volume_surge else 'normal'})",
                         current_price)
        
        if bullish_trend and macd_bullish and volume_surge:
            return Signal("BUY", 0.5, "Trend continuation + volume surge", current_price)
        
        if bearish_trend and not macd_bullish:
            return Signal("SELL", 0.5, "Bearish trend continuation", current_price)
        
        return Signal("HOLD", 0.0, "No clear signal", current_price)
    
    def execute(self, symbol: str, signal: Signal) -> bool:
        """Execute trade based on signal."""
        if signal.action == "HOLD":
            return False
        
        # Check if we can trade
        trade_value = self.config.entry_size
        can_trade, reason = self.risk.can_trade(symbol, trade_value)
        if not can_trade:
            log.warning(f"Trade blocked: {reason}")
            return False
        
        # Execute
        if signal.action == "BUY":
            result = self.exchange.market_buy(symbol, trade_value)
            if result.filled:
                # Set stop loss
                stop_price = result.price * (1 - self.config.stop_loss_pct)
                position = Position(
                    symbol=symbol,
                    side="BUY",
                    entry_price=result.price,
                    quantity=result.quantity,
                    entry_time=datetime.now(),
                    stop_price=stop_price,
                    strategy="momentum"
                )
                return self.risk.open_position(position)
        
        elif signal.action == "SELL":
            # For shorts, we'd need margin - skip for now
            log.info("SELL signal - short selling not implemented")
            return False
        
        return False
    
    def check_exits(self, symbol: str, current_price: float) -> Optional[str]:
        """Check if position should be exited."""
        position = self.risk.state.positions.get(symbol)
        if not position or position.strategy != "momentum":
            return None
        
        # Check stop loss
        if self.risk.check_stop_loss(symbol, current_price):
            return "stop_loss"
        
        # Check trend reversal (exit on bearish signal for longs)
        signal = self.analyze(symbol)
        if position.side == "BUY" and signal.action == "SELL":
            return "trend_reversal"
        
        return None
    
    def run(self, symbol: str):
        """Main strategy loop."""
        # Check for entry
        signal = self.analyze(symbol)
        if signal.action in ["BUY", "SELL"]:
            log.info(f"ENTRY SIGNAL: {signal}")
            self.execute(symbol, signal)
        
        # Check for exit on existing position
        ticker = self.exchange.get_ticker(symbol)
        if ticker:
            exit_reason = self.check_exits(symbol, ticker.price)
            if exit_reason:
                position = self.risk.state.positions.get(symbol)
                if position:
                    result = self.exchange.market_sell(symbol, position.quantity)
                    if result.filled:
                        pnl = self.risk.close_position(symbol, result.price, exit_reason)
                        log.info(f"EXIT: {symbol} — {exit_reason} | P&L: ${pnl:.2f}")
