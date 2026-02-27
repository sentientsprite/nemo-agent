"""
Mean Reversion Strategy
RSI oversold/overbought + Bollinger Bands
"""
import logging
import math
from datetime import datetime
from typing import List, Optional, Literal
from dataclasses import dataclass
from config import MeanReversionConfig
from exchanges.coinbase import CoinbaseExchange
from utils.risk import RiskManager, Position

log = logging.getLogger(__name__)

@dataclass
class Signal:
    action: Literal["BUY", "SELL", "HOLD"]
    strength: float
    reason: str
    price: float = 0.0

class MeanReversionStrategy:
    """
    Fades extremes using RSI and Bollinger Bands.
    Best for range-bound markets.
    """
    
    def __init__(self, config: MeanReversionConfig, exchange: CoinbaseExchange, risk: RiskManager):
        self.config = config
        self.exchange = exchange
        self.risk = risk
        
        if not config.enabled:
            log.warning("Mean reversion strategy disabled")
    
    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            sma.append(sum(prices[i-period+1:i+1]) / period)
        return sma
    
    def calculate_std(self, prices: List[float], period: int) -> List[float]:
        """Calculate Standard Deviation."""
        if len(prices) < period:
            return []
        
        std = []
        for i in range(period - 1, len(prices)):
            slice_prices = prices[i-period+1:i+1]
            mean = sum(slice_prices) / period
            variance = sum((p - mean) ** 2 for p in slice_prices) / period
            std.append(math.sqrt(variance))
        return std
    
    def calculate_bollinger_bands(self, prices: List[float]) -> tuple[List[float], List[float], List[float]]:
        """Calculate Bollinger Bands (middle, upper, lower)."""
        middle = self.calculate_sma(prices, self.config.bb_period)
        std = self.calculate_std(prices, self.config.bb_period)
        
        upper = [m + self.config.bb_std * s for m, s in zip(middle, std)]
        lower = [m - self.config.bb_std * s for m, s in zip(middle, std)]
        
        return middle, upper, lower
    
    def calculate_rsi(self, prices: List[float]) -> List[float]:
        """Calculate RSI."""
        if len(prices) < self.config.rsi_period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        rsi_values = []
        for i in range(self.config.rsi_period, len(deltas)):
            gains = [d for d in deltas[i-self.config.rsi_period:i] if d > 0]
            losses = [-d for d in deltas[i-self.config.rsi_period:i] if d < 0]
            
            avg_gain = sum(gains) / self.config.rsi_period if gains else 0
            avg_loss = sum(losses) / self.config.rsi_period if losses else 0
            
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(100 - (100 / (1 + rs)))
        
        return rsi_values
    
    def analyze(self, symbol: str) -> Signal:
        """Analyze market and generate mean reversion signal."""
        if not self.config.enabled:
            return Signal("HOLD", 0.0, "Strategy disabled")
        
        # Get candles
        candles = self.exchange.get_candles(symbol, "ONE_MINUTE", 50)
        if len(candles) < self.config.bb_period:
            return Signal("HOLD", 0.0, "Insufficient data")
        
        closes = [c.close for c in candles]
        current_price = closes[-1]
        
        # Calculate indicators
        rsi = self.calculate_rsi(closes)
        middle, upper, lower = self.calculate_bollinger_bands(closes)
        
        if not rsi or not upper or not lower:
            return Signal("HOLD", 0.0, "Indicators not ready")
        
        current_rsi = rsi[-1]
        current_upper = upper[-1]
        current_lower = lower[-1]
        current_middle = middle[-1]
        
        # Oversold conditions (buy signal)
        rsi_oversold = current_rsi < self.config.rsi_oversold
        bb_touch_lower = current_price <= current_lower
        
        # Overbought conditions (sell signal)
        rsi_overbought = current_rsi > self.config.rsi_overbought
        bb_touch_upper = current_price >= current_upper
        
        # Generate signals
        if rsi_oversold and bb_touch_lower:
            return Signal("BUY", 0.9, 
                         f"RSI oversold ({current_rsi:.1f}) + BB lower touch",
                         current_price)
        
        if rsi_oversold:
            return Signal("BUY", 0.7, 
                         f"RSI oversold ({current_rsi:.1f})",
                         current_price)
        
        if bb_touch_lower:
            return Signal("BUY", 0.6,
                         f"BB lower band touch",
                         current_price)
        
        if rsi_overbought and bb_touch_upper:
            return Signal("SELL", 0.9,
                         f"RSI overbought ({current_rsi:.1f}) + BB upper touch",
                         current_price)
        
        if rsi_overbought:
            return Signal("SELL", 0.7,
                         f"RSI overbought ({current_rsi:.1f})",
                         current_price)
        
        if bb_touch_upper:
            return Signal("SELL", 0.6,
                         f"BB upper band touch",
                         current_price)
        
        # Exit signals for existing positions
        position = self.risk.state.positions.get(symbol)
        if position and position.strategy == "mean_reversion":
            # Exit longs at middle band
            if position.side == "BUY" and current_price >= current_middle:
                return Signal("SELL", 0.5, "Exit at middle band (mean reversion complete)", current_price)
            # Exit shorts at middle band
            if position.side == "SELL" and current_price <= current_middle:
                return Signal("BUY", 0.5, "Exit at middle band (mean reversion complete)", current_price)
        
        return Signal("HOLD", 0.0, f"RSI: {current_rsi:.1f}, Price vs BB: mid={current_middle:.2f}", current_price)
    
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
                stop_price = result.price * (1 - self.config.stop_loss_pct)
                position = Position(
                    symbol=symbol,
                    side="BUY",
                    entry_price=result.price,
                    quantity=result.quantity,
                    entry_time=datetime.now(),
                    stop_price=stop_price,
                    strategy="mean_reversion"
                )
                return self.risk.open_position(position)
        
        elif signal.action == "SELL":
            result = self.exchange.market_sell(symbol, trade_value)
            if result.filled:
                stop_price = result.price * (1 + self.config.stop_loss_pct)
                position = Position(
                    symbol=symbol,
                    side="SELL",
                    entry_price=result.price,
                    quantity=result.quantity,
                    entry_time=datetime.now(),
                    stop_price=stop_price,
                    strategy="mean_reversion"
                )
                return self.risk.open_position(position)
        
        return False
    
    def run(self, symbol: str):
        """Main strategy loop."""
        signal = self.analyze(symbol)
        
        if signal.action in ["BUY", "SELL"]:
            log.info(f"MEAN REVERSION SIGNAL: {signal}")
            self.execute(symbol, signal)
        
        # Check exits handled in analyze() for mean reversion
        if signal.action in ["BUY", "SELL"] and signal.reason.startswith("Exit"):
            position = self.risk.state.positions.get(symbol)
            if position:
                if signal.action == "SELL" and position.side == "BUY":
                    result = self.exchange.market_sell(symbol, position.quantity)
                    if result.filled:
                        pnl = self.risk.close_position(symbol, result.price, "mean_reversion_target")
                        log.info(f"EXIT: {symbol} — mean reversion target | P&L: ${pnl:.2f}")
