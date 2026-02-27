"""
NEMO Trading - Unified Trading Plugin
Supports: Coinbase (CEX), Polymarket (Prediction Markets)
Strategies: Momentum, Mean Reversion, Snipe+Maker, Crowd Fade, Copy Trading
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- Exchange Configuration ---
@dataclass
class CoinbaseConfig:
    api_key: str = field(default_factory=lambda: os.getenv("COINBASE_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("COINBASE_API_SECRET", ""))
    base_url: str = "https://api.coinbase.com"
    sandbox: bool = True  # Default to sandbox

@dataclass
class PolymarketConfig:
    private_key: str = field(default_factory=lambda: os.getenv("POLYMARKET_PRIVATE_KEY", ""))
    funder_address: str = field(default_factory=lambda: os.getenv("FUNDER_ADDRESS", ""))
    clob_host: str = "https://clob.polymarket.com"
    gamma_host: str = "https://gamma-api.polymarket.com"
    chain_id: int = 137  # Polygon
    sandbox: bool = True

# --- Strategy Configuration ---
@dataclass
class MomentumConfig:
    enabled: bool = False
    ema_fast: int = 9
    ema_slow: int = 21
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    min_volume_ratio: float = 1.0
    entry_size: float = 5.0
    stop_loss_pct: float = 0.02  # 2%

@dataclass
class MeanReversionConfig:
    enabled: bool = False
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    bb_period: int = 20
    bb_std: float = 2.0
    entry_size: float = 5.0
    stop_loss_pct: float = 0.02

@dataclass
class SnipeConfig:
    enabled: bool = False
    window_start: int = 260  # seconds before close (5-min round)
    window_end: int = 295
    min_delta: float = 5.0  # $5 BTC move (lowered for more signals in dry-run)
    max_zero_crosses: int = 3  # More tolerant
    entry_size: float = 50.0  # Aggressive for snipe quality
    maker_exit_enabled: bool = True  # Enable maker exit to avoid second taker fee
    maker_exit_threshold: float = 0.55  # 55¢ position value (lowered)
    maker_exit_price: float = 0.90  # 90¢ limit sell
    max_trades_per_round: int = 2  # Allow 2 trades per round

@dataclass
class CrowdFadeConfig:
    enabled: bool = False
    threshold: float = 0.80  # 80% consensus
    confirmation_seconds: float = 10.0
    poll_interval: float = 5.0
    entry_window_start: int = 50  # seconds before close
    entry_window_end: int = 40
    entry_size: float = 30.0
    hold_to_settlement: bool = True  # No exit

@dataclass
class CopyTradingConfig:
    enabled: bool = False
    leader_addresses: list = field(default_factory=list)
    copy_delay_seconds: float = 5.0
    max_trades_per_leader: int = 3
    entry_size: float = 10.0
    platforms: list = field(default_factory=lambda: ["polymarket"])

# --- Risk Management ---
@dataclass
class RiskConfig:
    max_position_size: float = 10.0  # Max $ per trade
    max_daily_loss: float = 50.0  # $50 daily stop
    max_drawdown_pct: float = 0.10  # 10% max drawdown
    consecutive_loss_cooldown: int = 3  # Skip after 3 losses
    daily_trade_limit: int = 20  # Max trades per day

# --- Global Configuration ---
@dataclass
class Config:
    # Exchange selection
    exchange: str = "coinbase"  # coinbase | polymarket
    sandbox: bool = True
    dry_run: bool = True
    
    # Live trading toggle (SAFETY: requires explicit enable + safety key)
    live_trading_enabled: bool = False
    live_trading_safety_key: str = field(default_factory=lambda: os.getenv("LIVE_TRADING_SAFETY_KEY", ""))
    
    # Daily loss limit for live trading (hard stop)
    daily_loss_limit: float = 50.0  # $50 max daily loss
    max_drawdown_pct: float = 0.10  # 10% max drawdown from peak
    
    # Exchange configs
    coinbase: CoinbaseConfig = field(default_factory=CoinbaseConfig)
    polymarket: PolymarketConfig = field(default_factory=PolymarketConfig)
    
    # Strategy selection (only one active at a time)
    strategy: str = "momentum"  # momentum | mean_reversion | snipe | crowd_fade | copy
    
    # Strategy configs
    momentum: MomentumConfig = field(default_factory=MomentumConfig)
    mean_reversion: MeanReversionConfig = field(default_factory=MeanReversionConfig)
    snipe: SnipeConfig = field(default_factory=SnipeConfig)
    crowd_fade: CrowdFadeConfig = field(default_factory=CrowdFadeConfig)
    copy_trading: CopyTradingConfig = field(default_factory=CopyTradingConfig)
    
    # Risk management
    risk: RiskConfig = field(default_factory=RiskConfig)
    
    # Trading pair / market
    pair: str = "BTC-USDC"  # For CEX
    market_slug_prefix: str = "btc-updown-5m"  # For PM
    
    # Logging
    log_level: str = "INFO"
    trades_log: str = "data/trades.jsonl"
    
    # Polling
    poll_interval: float = 15.0  # seconds
    
    # NEW: WebSocket support (2026-02-26)
    use_websocket: bool = False  # Use WebSocket for <100ms latency
    
    def validate(self) -> bool:
        """Validate configuration based on selected exchange and strategy."""
        if self.exchange == "coinbase":
            if not self.coinbase.api_key or not self.coinbase.api_secret:
                if not self.dry_run:
                    raise ValueError("Coinbase API credentials required for live trading")
        elif self.exchange == "polymarket":
            if not self.polymarket.private_key or not self.polymarket.funder_address:
                if not self.dry_run:
                    raise ValueError("Polymarket wallet credentials required for live trading")
        
        # Validate strategy exists
        valid_strategies = ["momentum", "mean_reversion", "snipe", "crowd_fade", "copy"]
        if self.strategy not in valid_strategies:
            raise ValueError(f"Unknown strategy: {self.strategy}. Valid: {valid_strategies}")
        
        # Validate live trading safety
        if self.live_trading_enabled:
            if not self.live_trading_safety_key:
                raise ValueError("LIVE_TRADING_SAFETY_KEY required for live trading")
            if self.dry_run:
                raise ValueError("Cannot enable live trading while dry_run=True")
        
        return True
    
    def enable_live_trading(self, safety_key: str) -> None:
        """Safely enable live trading with confirmation.
        
        Args:
            safety_key: Must match LIVE_TRADING_SAFETY_KEY env var
            
        Raises:
            ValueError: If safety key doesn't match or config invalid
        """
        if safety_key != self.live_trading_safety_key:
            raise ValueError("Invalid safety key. Live trading NOT enabled.")
        
        if self.dry_run:
            self.dry_run = False
            
        self.live_trading_enabled = True
        
        # Log critical warning
        import logging
        logger = logging.getLogger(__name__)
        logger.critical("🔴 LIVE TRADING ENABLED 🔴")
        logger.critical(f"Exchange: {self.exchange}")
        logger.critical(f"Strategy: {self.strategy}")
        logger.critical(f"Daily loss limit: ${self.daily_loss_limit}")
        logger.critical("This is NOT a drill. Real money at risk.")
    
    def disable_live_trading(self) -> None:
        """Immediately disable live trading and switch to dry-run."""
        self.live_trading_enabled = False
        self.dry_run = True
        
        import logging
        logger = logging.getLogger(__name__)
        logger.critical("🟡 LIVE TRADING DISABLED — Switched to dry-run")
    
    @property
    def is_live(self) -> bool:
        """Check if currently trading with real money."""
        return self.live_trading_enabled and not self.dry_run

# Default configs for quick start
DEFAULT_CONFIGS = {
    "coinbase_momentum": Config(
        exchange="coinbase",
        strategy="momentum",
        momentum=MomentumConfig(enabled=True)
    ),
    "coinbase_mean_reversion": Config(
        exchange="coinbase",
        strategy="mean_reversion",
        mean_reversion=MeanReversionConfig(enabled=True)
    ),
    "polymarket_snipe": Config(
        exchange="polymarket",
        strategy="snipe",
        snipe=SnipeConfig(enabled=True)
    ),
    "polymarket_crowd": Config(
        exchange="polymarket",
        strategy="crowd_fade",
        crowd_fade=CrowdFadeConfig(enabled=True)
    ),
    "polymarket_copy": Config(
        exchange="polymarket",
        strategy="copy",
        copy_trading=CopyTradingConfig(enabled=True)
    ),
}
