"""
Polymarket Snipe + Maker Strategy
High-confidence late entry with maker exit
"""
import logging
from datetime import datetime
from typing import Optional
from config import SnipeConfig
from exchanges.polymarket import PolymarketExchange, OrderBook
from utils.risk import RiskManager, Position

log = logging.getLogger(__name__)

class SnipeStrategy:
    """
    Enter 30-40s before market close when direction is clear.
    Exit via maker order if winning to avoid second taker fee.
    """
    
    def __init__(self, config: SnipeConfig, exchange: PolymarketExchange, risk: RiskManager):
        self.config = config
        self.exchange = exchange
        self.risk = risk
        self.round_start_time: Optional[datetime] = None
        self.snipe_triggered = False
        
        if not config.enabled:
            log.warning("Snipe strategy disabled in config")
    
    def set_round(self, start_time: datetime):
        """Called at start of each new round."""
        self.round_start_time = start_time
        self.snipe_triggered = False
        log.info(f"New round started: {start_time}")
    
    def seconds_elapsed(self) -> float:
        """Get seconds elapsed in current round."""
        if not self.round_start_time:
            return 0
        return (datetime.now() - self.round_start_time).total_seconds()
    
    def seconds_remaining(self) -> float:
        """Get seconds remaining in 5-min round."""
        return 300 - self.seconds_elapsed()
    
    def evaluate(self, order_book: OrderBook, current_delta: float, 
                 zero_crosses: int) -> Optional[str]:
        """
        Evaluate snipe opportunity.
        
        Returns:
            "YES" | "NO" | None (no signal)
        """
        if not self.config.enabled:
            return None
        
        # Check if we need to reset for new round ( > 300s elapsed)
        elapsed = self.seconds_elapsed()
        if elapsed > 300:
            log.info("New round detected, resetting snipe state")
            self.snipe_triggered = False
            self.round_start_time = datetime.now()
            elapsed = 0
        
        if self.snipe_triggered:
            return None  # Only one snipe per round
        
        remaining = self.seconds_remaining()
        
        # Check if in snipe window
        if not (self.config.window_start <= elapsed <= self.config.window_end):
            return None
        
        # Check filters
        if abs(current_delta) < self.config.min_delta:
            log.debug(f"Delta {current_delta:.2f} < min {self.config.min_delta}")
            return None
        
        if zero_crosses > self.config.max_zero_crosses:
            log.debug(f"Zero crosses {zero_crosses} > max {self.config.max_zero_crosses}")
            return None
        
        # Determine direction
        signal = "YES" if current_delta > 0 else "NO"
        confidence = min(abs(current_delta) / 50.0, 1.0)  # Normalize to 0-1
        
        log.info(f"SNIPE SIGNAL: {signal} | Delta: ${current_delta:.2f} | "
                f"Remaining: {remaining:.1f}s | Confidence: {confidence:.1%}")
        
        return signal
    
    def execute_entry(self, market_id: str, token_id: str, side: str) -> bool:
        """Execute snipe entry."""
        if not self.risk.can_trade(market_id, self.config.entry_size):
            log.warning("Risk manager blocked trade")
            return False
        
        # Market order (accept taker fee for speed)
        result = self.exchange.place_order(
            market_id=market_id,
            token_id=token_id,
            side=side,
            size=self.config.entry_size,
            price=0,  # Market order
            order_type="market"
        )
        
        if result.filled:
            # Record position
            position = Position(
                symbol=market_id,
                side=side,
                entry_price=result.price,
                quantity=result.size,
                entry_time=datetime.now(),
                stop_price=None,  # Hold to settlement
                strategy="snipe"
            )
            
            if self.risk.open_position(position):
                self.snipe_triggered = True
                log.info(f"Snipe entry filled: {side} {result.size} @ {result.price}")
                return True
        
        return False
    
    def evaluate_exit(self, position: Position, current_price: float, 
                     seconds_remaining: float) -> Optional[str]:
        """
        Evaluate maker exit opportunity.
        
        Returns:
            "maker_exit" | "hold" | None
        """
        if not self.config.maker_exit_enabled:
            return None
        
        # Check if in exit window (last 15s)
        if seconds_remaining > 15:
            return None
        
        # Check if position is winning
        position_value = current_price * position.quantity
        entry_value = position.entry_price * position.quantity
        
        if position_value < entry_value * self.config.maker_exit_threshold:
            return None  # Not winning enough
        
        log.info(f"Maker exit triggered: Position value ${position_value:.2f} "
                f"({position_value/entry_value:.1%} of entry)")
        
        return "maker_exit"
    
    def execute_exit(self, market_id: str, position: Position) -> bool:
        """Execute maker exit."""
        # Place limit order at 90¢ (maker, no fee)
        result = self.exchange.place_order(
            market_id=market_id,
            token_id=position.side.lower() + "_token",  # Assumes token naming
            side="SELL" if position.side == "YES" else "YES",  # Close position
            size=position.quantity,
            price=self.config.maker_exit_price,
            order_type="limit"
        )
        
        if result.status == "PENDING":
            log.info(f"Maker exit placed: {position.quantity} @ {self.config.maker_exit_price}")
            return True
        
        return False
    
    def run(self, market_id: str, yes_token: str, no_token: str,
            order_book: OrderBook, current_delta: float, zero_crosses: int):
        """Main strategy loop - call every few seconds."""
        
        # Check for entry opportunity
        signal = self.evaluate(order_book, current_delta, zero_crosses)
        if signal:
            token_id = yes_token if signal == "YES" else no_token
            self.execute_entry(market_id, token_id, signal)
        
        # Check for exit opportunity on existing position
        position = self.risk.state.positions.get(market_id)
        if position and position.strategy == "snipe":
            remaining = self.seconds_remaining()
            current_price = 0.75  # Would get from order book
            
            exit_signal = self.evaluate_exit(position, current_price, remaining)
            if exit_signal == "maker_exit":
                self.execute_exit(market_id, position)
