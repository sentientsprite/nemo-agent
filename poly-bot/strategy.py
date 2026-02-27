"""
Trading strategy implementations for Poly-Bot.
Includes Snipe + Maker strategy and baseline strategy.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, Dict, Any

from config import (
    BaseConfig,
    SnipeMakerConfig,
    ExecutionConfig,
    LoggingConfig,
    StrategyState,
    ROUND_DURATION,
)

logger = logging.getLogger(__name__)

class SignalDirection(Enum):
    """Direction of market signal."""
    NEUTRAL = "neutral"
    YES = "yes"
    NO = "no"

@dataclass
class MarketSignal:
    """Processed market signal."""
    direction: SignalDirection
    delta: float
    confidence: float
    zero_crosses: int
    timestamp: datetime

class Strategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, state: StrategyState):
        self.state = state
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def should_enter(self, signal: MarketSignal, seconds_into_round: float) -> Tuple[bool, Optional[str]]:
        """Determine if we should enter a position."""
        pass
    
    @abstractmethod
    def should_exit(self, signal: MarketSignal, seconds_into_round: float, position_value: float) -> Tuple[bool, Optional[str]]:
        """Determine if we should exit a position."""
        pass
    
    @abstractmethod
    def get_position_size(self) -> float:
        """Get position size for entry."""
        pass

class BaselineStrategy(Strategy):
    """
    Baseline strategy: Standard entry/exit with time-based windows.
    """
    
    def __init__(self, state: StrategyState):
        super().__init__(state)
        self.config = BaseConfig
    
    def should_enter(self, signal: MarketSignal, seconds_into_round: float) -> Tuple[bool, Optional[str]]:
        """
        Check if we should enter a position using baseline logic.
        """
        # Check time window
        if seconds_into_round < self.config.ENTRY_WINDOW_START:
            return False, "Too early in round"
        if seconds_into_round > self.config.ENTRY_WINDOW_END:
            return False, "Entry window closed"
        
        # Check if already positioned
        if self.state.has_position:
            return False, "Already have position"
        
        # Check minimum delta
        if signal.delta < self.config.MIN_DELTA:
            return False, f"Delta {signal.delta:.2f} below minimum {self.config.MIN_DELTA}"
        
        # Check confidence
        if signal.confidence < self.config.MIN_CONFIDENCE:
            return False, f"Confidence {signal.confidence:.2f} below threshold"
        
        # Check zero crosses
        if signal.zero_crosses > self.config.MAX_ZERO_CROSSES:
            return False, f"Too many zero crosses: {signal.zero_crosses}"
        
        # Check direction
        if signal.direction == SignalDirection.NEUTRAL:
            return False, "Neutral direction"
        
        reason = f"Baseline entry: delta=${signal.delta:.2f}, confidence={signal.confidence:.2f}, direction={signal.direction.value}"
        return True, reason
    
    def should_exit(self, signal: MarketSignal, seconds_into_round: float, position_value: float) -> Tuple[bool, Optional[str]]:
        """
        Check if we should exit position using baseline logic.
        """
        if not self.state.has_position:
            return False, "No position"
        
        # Time-based exit
        if seconds_into_round > self.config.EXIT_WINDOW_END:
            return True, "End of round exit"
        
        # Stop loss check
        entry_cost = self.state.position_size
        if position_value < entry_cost * (1 - self.config.STOP_LOSS_PCT):
            return True, f"Stop loss triggered: value=${position_value:.2f}"
        
        # Take profit check
        if position_value > entry_cost * (1 + self.config.TAKE_PROFIT_PCT):
            return True, f"Take profit triggered: value=${position_value:.2f}"
        
        # Direction reversal
        current_side = self.state.position_side
        if (current_side == "YES" and signal.direction == SignalDirection.NO) or \
           (current_side == "NO" and signal.direction == SignalDirection.YES):
            return True, f"Direction reversal: {signal.direction.value}"
        
        return False, "Holding position"
    
    def get_position_size(self) -> float:
        """Get baseline position size."""
        return self.config.BASE_ORDER_SIZE

class SnipeMakerStrategy(Strategy):
    """
    Snipe + Maker Strategy
    
    Entry: High-confidence snipes in the final 30-40s of the round
    - Trigger: Delta > $20, zero_crosses < 2, clear direction
    - Aggressive $50 position for quality setups
    - Market order (taker fee acceptable for high confidence)
    
    Exit: Maker exit if winning
    - If position > 60¢ with 15s left, place limit sell at 90¢
    - If filled = no second taker fee
    - If not filled, hold to settlement
    """
    
    def __init__(self, state: StrategyState):
        super().__init__(state)
        self.snipe_config = SnipeMakerConfig
        self.base_config = BaseConfig
    
    def _log_decision(self, decision_type: str, result: bool, reason: str, details: Dict[str, Any]):
        """Log snipe decision with full reasoning."""
        if not LoggingConfig.LOG_SNIPE_DECISIONS:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "round": self.state.current_round,
            "seconds_into_round": self.state.seconds_into_round,
            "decision_type": decision_type,
            "result": result,
            "reason": reason,
            "details": details,
        }
        
        try:
            with open(LoggingConfig.SNIPE_DECISION_LOG, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to log decision: {e}")
        
        # Also log to regular logger
        self.logger.info(f"[SNIPE DECISION] {decision_type}: {result} - {reason}")
    
    def should_enter(self, signal: MarketSignal, seconds_into_round: float) -> Tuple[bool, Optional[str]]:
        """
        Snipe entry logic: High conviction entries in final 30-40s.
        """
        details = {
            "seconds_into_round": seconds_into_round,
            "snipe_window": [self.snipe_config.SNIPE_WINDOW_START, self.snipe_config.SNIPE_WINDOW_END],
            "delta": signal.delta,
            "zero_crosses": signal.zero_crosses,
            "direction": signal.direction.value,
            "can_snipe": self.state.can_snipe(),
        }
        
        # Check if snipe entry is enabled
        if not self.snipe_config.SNIPE_ENTRY_ENABLED:
            self._log_decision("ENTRY", False, "Snipe entry disabled", details)
            return False, "Snipe entry disabled"
        
        # Check snipe window (260-295s = 4m20s to 4m55s)
        if seconds_into_round < self.snipe_config.SNIPE_WINDOW_START:
            self._log_decision("ENTRY", False, "Before snipe window", details)
            return False, f"Too early for snipe: {seconds_into_round:.0f}s"
        
        if seconds_into_round > self.snipe_config.SNIPE_WINDOW_END:
            self._log_decision("ENTRY", False, "Snipe window closed", details)
            return False, "Snipe window closed"
        
        # Check if we can snipe this round
        if not self.state.can_snipe():
            self._log_decision("ENTRY", False, "Snipe not allowed this round", details)
            return False, "Snipe not available (already taken or cooldown)"
        
        # Check if already positioned
        if self.state.has_position:
            self._log_decision("ENTRY", False, "Already have position", details)
            return False, "Already have position"
        
        # Check snipe-specific conditions
        if signal.delta < self.snipe_config.SNIPE_MIN_DELTA:
            reason = f"Delta ${signal.delta:.2f} below snipe threshold ${self.snipe_config.SNIPE_MIN_DELTA}"
            self._log_decision("ENTRY", False, reason, details)
            return False, reason
        
        if signal.zero_crosses >= self.snipe_config.SNIPE_MAX_ZERO_CROSSES:
            reason = f"Zero crosses {signal.zero_crosses} >= limit {self.snipe_config.SNIPE_MAX_ZERO_CROSSES}"
            self._log_decision("ENTRY", False, reason, details)
            return False, reason
        
        if signal.direction == SignalDirection.NEUTRAL:
            self._log_decision("ENTRY", False, "Neutral direction", details)
            return False, "Neutral direction"
        
        # Check confidence
        if signal.confidence < self.base_config.MIN_CONFIDENCE:
            reason = f"Confidence {signal.confidence:.2f} below threshold {self.base_config.MIN_CONFIDENCE}"
            self._log_decision("ENTRY", False, reason, details)
            return False, reason
        
        # All conditions met - SNIPE!
        reason = (
            f"🎯 SNIPE ENTRY: delta=${signal.delta:.2f}, "
            f"zero_crosses={signal.zero_crosses}, "
            f"direction={signal.direction.value}, "
            f"time={seconds_into_round:.0f}s, "
            f"size=${self.get_position_size():.0f}"
        )
        self._log_decision("ENTRY", True, reason, details)
        return True, reason
    
    def should_exit(self, signal: MarketSignal, seconds_into_round: float, position_value: float) -> Tuple[bool, Optional[str]]:
        """
        Maker exit logic: Try to exit as maker if winning.
        """
        details = {
            "seconds_into_round": seconds_into_round,
            "position_value": position_value,
            "entry_cost": self.state.position_size if self.state.has_position else 0,
            "maker_exit_enabled": self.snipe_config.MAKER_EXIT_ENABLED,
        }
        
        if not self.state.has_position:
            return False, "No position"
        
        # Time-based exit at end of round
        if seconds_into_round > ROUND_DURATION - 5:
            self._log_decision("EXIT", True, "End of round settlement", details)
            return True, "End of round - settling position"
        
        # Stop loss - always exit immediately
        entry_cost = self.state.position_size
        if position_value < entry_cost * (1 - self.base_config.STOP_LOSS_PCT):
            reason = f"Stop loss: value=${position_value:.2f} vs cost=${entry_cost:.2f}"
            self._log_decision("EXIT", True, reason, details)
            return True, reason
        
        # Maker exit logic
        if self.snipe_config.MAKER_EXIT_ENABLED:
            time_remaining = ROUND_DURATION - seconds_into_round
            
            # Check if we're winning and have enough time for maker exit
            if (position_value >= self.snipe_config.MAKER_EXIT_THRESHOLD and 
                time_remaining <= self.snipe_config.MAKER_EXIT_TIME_CUTOFF):
                
                reason = (
                    f"🎯 MAKER EXIT: position=${position_value:.2f} >= "
                    f"${self.snipe_config.MAKER_EXIT_THRESHOLD:.2f} threshold, "
                    f"{time_remaining:.0f}s remaining, "
                    f"limit @ ${self.snipe_config.MAKER_EXIT_PRICE:.2f}"
                )
                self._log_decision("EXIT", True, reason, details)
                return True, reason
        
        # Take profit check (regular)
        if position_value > entry_cost * (1 + self.base_config.TAKE_PROFIT_PCT):
            reason = f"Take profit: value=${position_value:.2f}"
            self._log_decision("EXIT", True, reason, details)
            return True, reason
        
        self._log_decision("EXIT", False, "Holding position", details)
        return False, "Holding position"
    
    def is_maker_exit(self, position_value: float, seconds_into_round: float) -> bool:
        """
        Check if this should be a maker exit (limit order).
        Returns True if conditions for maker exit are met.
        """
        if not self.snipe_config.MAKER_EXIT_ENABLED:
            return False
        
        time_remaining = ROUND_DURATION - seconds_into_round
        
        return (
            position_value >= self.snipe_config.MAKER_EXIT_THRESHOLD and
            time_remaining <= self.snipe_config.MAKER_EXIT_TIME_CUTOFF
        )
    
    def get_position_size(self) -> float:
        """Get snipe position size (aggressive)."""
        return self.snipe_config.SNIPE_SIZE
    
    def get_maker_exit_price(self) -> float:
        """Get the limit price for maker exit."""
        return self.snipe_config.MAKER_EXIT_PRICE

# =============================================================================
# Signal Processor
# =============================================================================

def process_market_data(
    yes_price: float,
    no_price: float,
    mid_price: float,
    order_book_imbalance: float,
    recent_trades: list,
    state: StrategyState
) -> MarketSignal:
    """
    Process raw market data into a trading signal.
    """
    # Calculate delta (spread between sides)
    delta = abs(yes_price - no_price)
    
    # Determine direction
    if order_book_imbalance > 0.3:
        direction = SignalDirection.YES
    elif order_book_imbalance < -0.3:
        direction = SignalDirection.NO
    else:
        direction = SignalDirection.NEUTRAL
    
    # Calculate confidence based on delta and order book
    confidence = min(0.95, 0.5 + (delta / 100) + abs(order_book_imbalance) * 0.3)
    
    # Track zero crossings
    if state.delta_history:
        last_direction = 1 if state.delta_history[-1] > 0 else -1
        current_direction = 1 if delta > state.delta_history[-1] else -1
        if last_direction != current_direction and delta > 5:
            state.zero_crosses += 1
    
    state.delta_history.append(delta)
    state.last_delta = delta
    
    return MarketSignal(
        direction=direction,
        delta=delta,
        confidence=confidence,
        zero_crosses=state.zero_crosses,
        timestamp=datetime.now()
    )
