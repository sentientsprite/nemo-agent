"""
Configuration for the Poly-Bot trading system.
Includes all strategy parameters and risk settings.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List

# =============================================================================
# MARKET SETTINGS
# =============================================================================

ROUND_DURATION = 300  # 5 minutes in seconds
PRICE_TICK_SIZE = 0.01  # 1 cent minimum price movement
MAX_POSITION_SIZE = 100  # Maximum $100 position

# =============================================================================
# BASE STRATEGY CONFIG
# =============================================================================

class BaseConfig:
    """Base configuration shared across strategies."""
    
    # Market parameters
    MARKET_ID = "POLY-USD"
    MIN_CONFIDENCE = 0.65
    
    # Risk parameters
    MAX_POSITIONS_PER_ROUND = 3
    STOP_LOSS_PCT = 0.15  # 15% stop loss
    TAKE_PROFIT_PCT = 0.25  # 25% take profit
    
    # Order sizing
    BASE_ORDER_SIZE = 20  # $20 base position
    MAX_ORDER_SIZE = 50  # $50 max position
    
    # Signal thresholds
    MIN_DELTA = 5.0  # Minimum $5 delta to enter
    MAX_ZERO_CROSSES = 3  # Maximum zero crosses for confidence
    
    # Time windows (seconds into round)
    ENTRY_WINDOW_START = 30
    ENTRY_WINDOW_END = 240
    EXIT_WINDOW_START = 250
    EXIT_WINDOW_END = 295

# =============================================================================
# SNIPE + MAKER STRATEGY CONFIG
# =============================================================================

class SnipeMakerConfig:
    """Configuration for Snipe + Maker strategy."""
    
    # Enable flags
    SNIPE_ENTRY_ENABLED = True
    MAKER_EXIT_ENABLED = True
    
    # Snipe window (seconds into 5-min round)
    # 260s = 4m20s, 295s = 4m55s
    SNIPE_WINDOW_START = 260
    SNIPE_WINDOW_END = 295
    
    # Snipe entry conditions
    SNIPE_MIN_DELTA = 20.0  # $20 minimum delta (high conviction)
    SNIPE_MAX_ZERO_CROSSES = 2  # Less than 2 zero crosses (clear direction)
    
    # Snipe sizing
    SNIPE_SIZE = 50  # $50 aggressive position for high-quality snipes
    
    # Maker exit conditions
    MAKER_EXIT_THRESHOLD = 0.60  # 60¢ position value to trigger maker exit
    MAKER_EXIT_TIME_CUTOFF = 15  # 15 seconds left in round
    MAKER_EXIT_PRICE = 0.90  # Limit sell at 90¢
    
    # Risk management
    ONE_SNIPE_PER_ROUND = True  # Only 1 snipe per round (maximize quality)
    SNIPE_COOLDOWN_ROUNDS = 1  # Wait 1 round between snipes

# =============================================================================
# EXECUTION CONFIG
# =============================================================================

class ExecutionConfig:
    """Order execution parameters."""
    
    # Order types
    USE_MARKET_ORDERS_FOR_SNIPE = True  # Market orders for snipe (taker fee OK)
    USE_LIMIT_ORDERS_FOR_MAKER_EXIT = True  # Limit orders for maker exit
    
    # Fee structure (example)
    TAKER_FEE = 0.001  # 0.1% taker fee
    MAKER_FEE = -0.0002  # -0.02% maker rebate
    
    # Order retry settings
    MAX_ORDER_RETRIES = 3
    ORDER_RETRY_DELAY = 0.5  # seconds
    
    # Dry run mode
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# =============================================================================
# LOGGING CONFIG
# =============================================================================

class LoggingConfig:
    """Logging configuration."""
    
    LOG_LEVEL = "INFO"
    LOG_TO_FILE = True
    LOG_FILE = "logs/poly_bot.log"
    LOG_TO_CONSOLE = True
    
    # Performance tracking
    TRACK_PNL_SEPARATELY = True
    SNIPE_PNL_LOG = "logs/snipe_pnl.jsonl"
    BASELINE_PNL_LOG = "logs/baseline_pnl.jsonl"
    
    # Decision logging
    LOG_SNIPE_DECISIONS = True
    SNIPE_DECISION_LOG = "logs/snipe_decisions.jsonl"

# =============================================================================
@dataclass
class StrategyState:
    """Mutable state for strategy tracking."""
    
    # Round tracking
    current_round: int = 0
    seconds_into_round: float = 0.0
    
    # Position tracking
    has_position: bool = False
    position_side: str = ""  # "YES" or "NO"
    position_size: float = 0.0
    entry_price: float = 0.0
    position_value: float = 0.0
    
    # Snipe tracking
    snipe_taken_this_round: bool = False
    snipe_count_today: int = 0
    last_snipe_round: int = -1
    
    # Signal tracking
    zero_crosses: int = 0
    last_delta: float = 0.0
    delta_history: List[float] = field(default_factory=list)
    
    # Performance
    total_pnl: float = 0.0
    snipe_pnl: float = 0.0
    baseline_pnl: float = 0.0
    
    def reset_round(self):
        """Reset per-round state."""
        self.snipe_taken_this_round = False
        self.zero_crosses = 0
        self.delta_history = []
        
    def can_snipe(self) -> bool:
        """Check if snipe is allowed this round."""
        if not SnipeMakerConfig.SNIPE_ENTRY_ENABLED:
            return False
        if SnipeMakerConfig.ONE_SNIPE_PER_ROUND and self.snipe_taken_this_round:
            return False
        cooldown = SnipeMakerConfig.SNIPE_COOLDOWN_ROUNDS
        if self.current_round - self.last_snipe_round <= cooldown:
            return False
        return True

# =============================================================================
# Global config instance
# =============================================================================

CONFIG = {
    "base": BaseConfig,
    "snipe_maker": SnipeMakerConfig,
    "execution": ExecutionConfig,
    "logging": LoggingConfig,
}
