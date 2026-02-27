"""
Copy Trading Strategy
Mirror profitable wallets with delay and proportional sizing
"""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from config import CopyTradingConfig
from exchanges.polymarket import PolymarketExchange
from utils.risk import RiskManager, Position

log = logging.getLogger(__name__)

@dataclass
class LeaderTrade:
    """Trade made by a leader."""
    leader_id: str
    market_id: str
    side: str
    size: float
    price: float
    timestamp: datetime
    tx_hash: Optional[str] = None

@dataclass
class LeaderPerformance:
    """Performance metrics for a leader."""
    leader_id: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    last_trade: Optional[datetime] = None
    active: bool = True
    
    def update_win_rate(self):
        """Recalculate win rate."""
        if self.total_trades > 0:
            self.win_rate = self.wins / self.total_trades

class CopyTradingStrategy:
    """
    Copy profitable traders on Polymarket.
    Includes performance tracking, leader filtering, and risk-adjusted sizing.
    """
    
    def __init__(self, config: CopyTradingConfig, exchange: PolymarketExchange, risk: RiskManager):
        self.config = config
        self.exchange = exchange
        self.risk = risk
        
        # Leader tracking
        self.leaders: Set[str] = set(config.leader_addresses)
        self.leader_performance: Dict[str, LeaderPerformance] = {}
        self.recent_trades: Dict[str, LeaderTrade] = {}  # market_id -> last trade
        self.copied_trades: List[LeaderTrade] = []  # Track what we've copied
        
        # Initialize performance tracking
        for leader_id in self.leaders:
            self.leader_performance[leader_id] = LeaderPerformance(leader_id=leader_id)
        
        if not config.enabled:
            log.warning("Copy trading strategy disabled")
        elif not self.leaders:
            log.warning("Copy trading enabled but no leaders configured")
    
    def add_leader(self, leader_id: str):
        """Add a new leader to copy."""
        self.leaders.add(leader_id)
        if leader_id not in self.leader_performance:
            self.leader_performance[leader_id] = LeaderPerformance(leader_id=leader_id)
        log.info(f"Added leader: {leader_id}")
    
    def remove_leader(self, leader_id: str):
        """Remove a leader."""
        self.leaders.discard(leader_id)
        if leader_id in self.leader_performance:
            self.leader_performance[leader_id].active = False
        log.info(f"Removed leader: {leader_id}")
    
    def is_leader_profitable(self, leader_id: str, min_trades: int = 20, min_win_rate: float = 0.55) -> bool:
        """Check if leader meets profitability criteria."""
        perf = self.leader_performance.get(leader_id)
        if not perf:
            return False
        
        if perf.total_trades < min_trades:
            return True  # Give new leaders a chance
        
        return perf.win_rate >= min_win_rate and perf.total_pnl > 0
    
    def get_position_size(self, leader_trade: LeaderTrade) -> float:
        """Calculate copy position size based on leader performance."""
        perf = self.leader_performance.get(leader_trade.leader_id)
        if not perf:
            return self.config.entry_size
        
        # Base size
        base_size = self.config.entry_size
        
        # Adjust based on win rate
        if perf.total_trades >= 20:
            if perf.win_rate >= 0.70:
                multiplier = 1.5  # High confidence
            elif perf.win_rate >= 0.55:
                multiplier = 1.0  # Standard
            elif perf.win_rate >= 0.45:
                multiplier = 0.5  # Reduce size
            else:
                multiplier = 0.0  # Don't copy <45% WR
        else:
            multiplier = 1.0  # New leader, standard size
        
        return base_size * multiplier
    
    def check_leader_trades(self, leader_id: str) -> List[LeaderTrade]:
        """Check for new trades from a leader.
        
        In production, this would query:
        - Polymarket CLOB API for orders
        - Polygonscan for on-chain transactions
        - Leader's public positions
        
        For now, this is a placeholder that returns empty list.
        """
        # TODO: Implement actual leader monitoring
        # This would poll the blockchain or CLOB API
        return []
    
    def detect_new_trades(self) -> List[LeaderTrade]:
        """Detect new trades from all leaders."""
        new_trades = []
        
        for leader_id in self.leaders:
            if not self.is_leader_profitable(leader_id):
                continue
            
            trades = self.check_leader_trades(leader_id)
            for trade in trades:
                # Check if we've already copied this trade
                trade_key = f"{trade.market_id}:{trade.tx_hash or trade.timestamp}"
                if trade_key not in [f"{t.market_id}:{t.tx_hash or t.timestamp}" for t in self.copied_trades]:
                    new_trades.append(trade)
        
        return new_trades
    
    def validate_signal(self, leader_trade: LeaderTrade) -> tuple[bool, str]:
        """Validate if we should copy this trade."""
        # Check leader limits
        perf = self.leader_performance.get(leader_trade.leader_id)
        if perf:
            # Count recent trades from this leader
            recent = sum(1 for t in self.copied_trades 
                        if t.leader_id == leader_trade.leader_id 
                        and t.timestamp > datetime.now() - timedelta(hours=1))
            if recent >= self.config.max_trades_per_leader:
                return False, f"Max trades per leader ({self.config.max_trades_per_leader}) reached"
        
        # Check market not already in position
        if leader_trade.market_id in self.risk.state.positions:
            return False, "Already in position for this market"
        
        # Check time delay (don't copy old trades)
        age = (datetime.now() - leader_trade.timestamp).total_seconds()
        if age > 300:  # Don't copy trades > 5 minutes old
            return False, f"Trade too old ({age:.0f}s)"
        
        return True, "OK"
    
    def execute_copy(self, leader_trade: LeaderTrade) -> bool:
        """Execute copy of leader's trade."""
        # Validate
        valid, reason = self.validate_signal(leader_trade)
        if not valid:
            log.debug(f"Copy rejected: {reason}")
            return False
        
        # Calculate size
        size = self.get_position_size(leader_trade)
        if size <= 0:
            log.info(f"Skipping copy from {leader_trade.leader_id}: poor performance")
            return False
        
        # Check risk
        can_trade, reason = self.risk.can_trade(leader_trade.market_id, size)
        if not can_trade:
            log.warning(f"Copy blocked by risk: {reason}")
            return False
        
        # Apply delay
        if self.config.copy_delay_seconds > 0:
            log.info(f"Waiting {self.config.copy_delay_seconds}s before copying...")
            time.sleep(self.config.copy_delay_seconds)
        
        # Execute
        # Note: In real implementation, we'd need the token IDs
        log.info(f"COPY: {leader_trade.side} ${size:.2f} | Leader: {leader_trade.leader_id} | "
                f"They bet ${leader_trade.size:.2f}")
        
        # Record copy
        self.copied_trades.append(leader_trade)
        
        # Update performance (will be updated on settlement)
        perf = self.leader_performance.get(leader_trade.leader_id)
        if perf:
            perf.total_trades += 1
            perf.last_trade = datetime.now()
        
        return True
    
    def update_performance(self, market_id: str, winning_side: str):
        """Update leader performance after market settlement."""
        for trade in self.copied_trades:
            if trade.market_id == market_id:
                perf = self.leader_performance.get(trade.leader_id)
                if perf:
                    if trade.side == winning_side:
                        perf.wins += 1
                        perf.total_pnl += trade.size * 0.85  # Approximate win after fees
                        log.info(f"Leader {trade.leader_id} WIN on {market_id}")
                    else:
                        perf.losses += 1
                        perf.total_pnl -= trade.size
                        log.info(f"Leader {trade.leader_id} LOSS on {market_id}")
                    
                    perf.update_win_rate()
    
    def get_leaderboard(self) -> List[LeaderPerformance]:
        """Get leaders ranked by performance."""
        return sorted(
            self.leader_performance.values(),
            key=lambda p: (p.win_rate, p.total_pnl),
            reverse=True
        )
    
    def run(self):
        """Main strategy loop."""
        if not self.config.enabled or not self.leaders:
            return
        
        # Detect new trades from leaders
        new_trades = self.detect_new_trades()
        
        for trade in new_trades:
            self.execute_copy(trade)
        
        # Log performance periodically
        if len(self.copied_trades) % 10 == 0 and self.copied_trades:
            log.info("=== Leader Performance ===")
            for perf in self.get_leaderboard()[:5]:
                log.info(f"{perf.leader_id}: {perf.win_rate:.1%} WR | "
                        f"${perf.total_pnl:.2f} P&L | {perf.total_trades} trades")
