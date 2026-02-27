"""
Universal Risk Manager for NEMO Trading
Tracks positions, enforces limits, manages drawdown
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from config import RiskConfig

log = logging.getLogger(__name__)

@dataclass
class Position:
    symbol: str
    side: str  # "BUY" | "SELL" | "YES" | "NO"
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_price: Optional[float] = None
    strategy: str = ""
    pnl: float = 0.0

@dataclass
class SessionState:
    """Tracks trading session state."""
    start_balance: float = 0.0
    current_balance: float = 0.0
    daily_pnl: float = 0.0
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    consecutive_losses: int = 0
    trades_today: int = 0
    max_drawdown: float = 0.0
    peak_balance: float = 0.0
    halted: bool = False
    halt_reason: str = ""
    positions: Dict[str, Position] = field(default_factory=dict)
    
    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.wins / self.total_trades
    
    @property
    def drawdown_pct(self) -> float:
        if self.peak_balance == 0:
            return 0.0
        return (self.peak_balance - self.current_balance) / self.peak_balance

class RiskManager:
    """Universal risk manager for all strategies."""
    
    def __init__(self, config: RiskConfig, start_balance: float = 10000.0):
        self.config = config
        self.state = SessionState(
            start_balance=start_balance,
            current_balance=start_balance,
            peak_balance=start_balance
        )
        log.info(f"Risk manager initialized | Start: ${start_balance:.2f}")
    
    def can_trade(self, symbol: str, proposed_size: float) -> tuple[bool, str]:
        """Check if trade is allowed under risk rules."""
        if self.state.halted:
            return False, f"Trading halted: {self.state.halt_reason}"
        
        # Check daily loss limit
        if self.state.daily_pnl < -self.config.max_daily_loss:
            self.state.halted = True
            self.state.halt_reason = f"Daily loss limit hit: ${self.state.daily_pnl:.2f}"
            return False, self.state.halt_reason
        
        # Check drawdown
        if self.state.drawdown_pct > self.config.max_drawdown_pct:
            self.state.halted = True
            self.state.halt_reason = f"Max drawdown hit: {self.state.drawdown_pct:.1%}"
            return False, self.state.halt_reason
        
        # Check consecutive losses
        if self.state.consecutive_losses >= self.config.consecutive_loss_cooldown:
            return False, f"Cooldown: {self.state.consecutive_losses} consecutive losses"
        
        # Check position size
        if proposed_size > self.config.max_position_size:
            return False, f"Position size ${proposed_size:.2f} > max ${self.config.max_position_size:.2f}"
        
        # Check daily trade limit
        if self.state.trades_today >= self.config.daily_trade_limit:
            return False, f"Daily trade limit reached: {self.state.trades_today}"
        
        # Check if already in position
        if symbol in self.state.positions:
            return False, f"Already in position: {symbol}"
        
        return True, "OK"
    
    def open_position(self, position: Position) -> bool:
        """Record new position."""
        can_trade, reason = self.can_trade(position.symbol, position.entry_price * position.quantity)
        if not can_trade:
            log.warning(f"Trade blocked: {reason}")
            return False
        
        self.state.positions[position.symbol] = position
        self.state.trades_today += 1
        self.state.total_trades += 1
        log.info(f"Position opened: {position.symbol} {position.side} @ {position.entry_price}")
        return True
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "") -> Optional[float]:
        """Close position and record P&L."""
        if symbol not in self.state.positions:
            log.warning(f"No position to close: {symbol}")
            return None
        
        position = self.state.positions.pop(symbol)
        
        # Calculate P&L
        if position.side in ["BUY", "YES"]:
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity
        
        position.pnl = pnl
        self.state.daily_pnl += pnl
        self.state.current_balance += pnl
        
        # Update peak/drawdown
        if self.state.current_balance > self.state.peak_balance:
            self.state.peak_balance = self.state.current_balance
        
        # Update win/loss tracking
        if pnl > 0:
            self.state.wins += 1
            self.state.consecutive_losses = 0
            log.info(f"Win: {symbol} +${pnl:.2f} | {reason}")
        else:
            self.state.losses += 1
            self.state.consecutive_losses += 1
            log.info(f"Loss: {symbol} ${pnl:.2f} | {reason}")
        
        return pnl
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """Check if stop loss triggered."""
        if symbol not in self.state.positions:
            return False
        
        position = self.state.positions[symbol]
        if position.stop_price is None:
            return False
        
        if position.side in ["BUY", "YES"]:
            return current_price <= position.stop_price
        else:
            return current_price >= position.stop_price
    
    def compute_stop_price(self, entry_price: float, side: str, stop_pct: float) -> float:
        """Compute stop loss price."""
        if side in ["BUY", "YES"]:
            return entry_price * (1 - stop_pct)
        else:
            return entry_price * (1 + stop_pct)
    
    def get_status(self) -> dict:
        """Get current risk status."""
        return {
            "balance": self.state.current_balance,
            "daily_pnl": self.state.daily_pnl,
            "drawdown": self.state.drawdown_pct,
            "win_rate": self.state.win_rate,
            "trades_today": self.state.trades_today,
            "consecutive_losses": self.state.consecutive_losses,
            "open_positions": len(self.state.positions),
            "halted": self.state.halted,
        }
    
    def reset_daily(self):
        """Reset daily counters (call at midnight)."""
        self.state.daily_pnl = 0.0
        self.state.trades_today = 0
        log.info("Daily counters reset")
