"""
VPIN (Volume-Synchronized Probability of Informed Trading)
Toxicity Detection for Order Flow

VPIN measures the probability that informed traders are active.
High VPIN = toxic flow (informed traders know something you don't)

Formula: VPIN = |V_buy - V_sell| / (V_buy + V_sell)

Thresholds:
- VPIN < 0.3: Normal flow, safe to trade
- VPIN 0.3-0.5: Elevated toxicity, widen spreads
- VPIN > 0.5: High toxicity, consider withdrawing
- VPIN > 0.6: Kill switch (stop trading)
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta


@dataclass
class TradeBucket:
    """Volume bucket for VPIN calculation"""
    buy_volume: float = 0.0
    sell_volume: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_volume(self) -> float:
        return self.buy_volume + self.sell_volume
    
    @property
    def toxicity(self) -> float:
        """Calculate toxicity for this bucket"""
        if self.total_volume == 0:
            return 0.0
        return abs(self.buy_volume - self.sell_volume) / self.total_volume


@dataclass  
class VPINSignal:
    """VPIN calculation result"""
    vpin: float  # Current VPIN value (0-1)
    toxicity_level: str  # normal/elevated/high/critical
    action: str  # trade/widen_spreads/withdraw/kill
    bucket_count: int  # Number of buckets in calculation
    avg_volume: float  # Average volume per bucket
    timestamp: datetime
    

class VPINToxicityDetector:
    """
    Real-time VPIN toxicity detector
    
    Monitors order flow to detect informed trading activity.
    Uses volume-synchronized buckets for calculation.
    """
    
    # Toxicity thresholds
    THRESHOLD_NORMAL = 0.3
    THRESHOLD_ELEVATED = 0.5
    THRESHOLD_HIGH = 0.6
    THRESHOLD_CRITICAL = 0.75
    
    def __init__(
        self,
        bucket_size: float = 100.0,  # Volume per bucket
        num_buckets: int = 50,  # Buckets for VPIN calculation
        window_seconds: int = 300  # 5 minute rolling window
    ):
        """
        Initialize VPIN detector
        
        Args:
            bucket_size: Target volume per bucket (in USD or contracts)
            num_buckets: Number of buckets for VPIN calculation
            window_seconds: Rolling window for active buckets
        """
        self.bucket_size = bucket_size
        self.num_buckets = num_buckets
        self.window_seconds = window_seconds
        
        # Rolling buckets
        self.buckets: deque[TradeBucket] = deque(maxlen=num_buckets)
        self.current_bucket = TradeBucket()
        self.current_volume = 0.0
        
        # Historical VPIN for trend analysis
        self.vpin_history: deque[float] = deque(maxlen=100)
        
        # Kill switch state
        self.kill_switch_active = False
        self.kill_switch_time: Optional[datetime] = None
        self.kill_switch_cooldown_seconds = 300  # 5 min cooldown
        
    def classify_trade(self, trade: dict) -> str:
        """
        Classify trade as buy or sell based on price movement
        
        Uses tick rule:
        - If price > previous price: buy-initiated
        - If price < previous price: sell-initiated
        - If price == previous: use previous classification
        """
        price = trade.get("price", 0)
        prev_price = trade.get("prev_price", price)
        
        if price > prev_price:
            return "buy"
        elif price < prev_price:
            return "sell"
        else:
            # Use volume imbalance or default to buy
            return trade.get("side", "buy")
    
    def add_trade(self, trade: dict):
        """
        Add a trade to the VPIN calculation
        
        Args:
            trade: Dict with 'size', 'price', 'side' (optional), 'timestamp'
        """
        size = trade.get("size", 0)
        side = trade.get("side") or self.classify_trade(trade)
        
        # Add to current bucket
        if side == "buy":
            self.current_bucket.buy_volume += size
        else:
            self.current_bucket.sell_volume += size
        
        self.current_volume += size
        
        # Check if bucket is full
        if self.current_volume >= self.bucket_size:
            # Finalize current bucket
            self.current_bucket.timestamp = datetime.utcnow()
            self.buckets.append(self.current_bucket)
            
            # Start new bucket
            self.current_bucket = TradeBucket()
            self.current_volume = 0.0
            
            # Clean old buckets
            self._clean_old_buckets()
    
    def add_batch_trades(self, trades: List[dict]):
        """Add multiple trades at once"""
        for trade in trades:
            self.add_trade(trade)
    
    def _clean_old_buckets(self):
        """Remove buckets outside the time window"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        while self.buckets and self.buckets[0].timestamp < cutoff:
            self.buckets.popleft()
    
    def calculate_vpin(self) -> VPINSignal:
        """
        Calculate current VPIN from active buckets
        
        Returns:
            VPINSignal with toxicity assessment and recommended action
        """
        self._clean_old_buckets()
        
        # Include current bucket if it has volume
        active_buckets = list(self.buckets)
        if self.current_volume > 0:
            active_buckets.append(self.current_bucket)
        
        if not active_buckets:
            return VPINSignal(
                vpin=0.0,
                toxicity_level="unknown",
                action="trade",
                bucket_count=0,
                avg_volume=0.0,
                timestamp=datetime.utcnow()
            )
        
        # Calculate VPIN: average toxicity across buckets
        toxicities = [b.toxicity for b in active_buckets if b.total_volume > 0]
        vpin = sum(toxicities) / len(toxicities) if toxicities else 0.0
        
        # Store in history
        self.vpin_history.append(vpin)
        
        # Calculate average volume
        avg_volume = sum(b.total_volume for b in active_buckets) / len(active_buckets)
        
        # Determine toxicity level and action
        toxicity_level, action = self._assess_toxicity(vpin)
        
        return VPINSignal(
            vpin=vpin,
            toxicity_level=toxicity_level,
            action=action,
            bucket_count=len(active_buckets),
            avg_volume=avg_volume,
            timestamp=datetime.utcnow()
        )
    
    def _assess_toxicity(self, vpin: float) -> tuple:
        """
        Assess toxicity level and determine action
        
        Returns:
            (toxicity_level, action)
        """
        if self.kill_switch_active:
            # Check if cooldown expired
            if self.kill_switch_time:
                elapsed = (datetime.utcnow() - self.kill_switch_time).total_seconds()
                if elapsed > self.kill_switch_cooldown_seconds:
                    self.kill_switch_active = False
                    self.kill_switch_time = None
                    print("🟢 VPIN kill switch cooldown expired. Trading resumed.")
                else:
                    return ("critical", "kill")
        
        if vpin >= self.THRESHOLD_CRITICAL:
            self.kill_switch_active = True
            self.kill_switch_time = datetime.utcnow()
            return ("critical", "kill")
        elif vpin >= self.THRESHOLD_HIGH:
            return ("high", "withdraw")
        elif vpin >= self.THRESHOLD_ELEVATED:
            return ("elevated", "widen_spreads")
        else:
            return ("normal", "trade")
    
    def check_trade_permission(self) -> dict:
        """
        Check if trading is currently permitted
        
        Returns:
            Dict with permission status and reasoning
        """
        signal = self.calculate_vpin()
        
        return {
            "permitted": signal.action != "kill",
            "action": signal.action,
            "vpin": signal.vpin,
            "toxicity": signal.toxicity_level,
            "spread_adjustment": self.get_spread_adjustment(signal.vpin),
            "message": self._get_action_message(signal)
        }
    
    def get_spread_adjustment(self, vpin: float) -> float:
        """
        Calculate spread widening factor based on VPIN
        
        Returns:
            Multiplier for spread (1.0 = normal, 2.0 = double)
        """
        if vpin < self.THRESHOLD_NORMAL:
            return 1.0
        elif vpin < self.THRESHOLD_ELEVATED:
            # Linear interpolation: 1.0 to 1.5
            return 1.0 + (vpin - self.THRESHOLD_NORMAL) / (self.THRESHOLD_ELEVATED - self.THRESHOLD_NORMAL) * 0.5
        elif vpin < self.THRESHOLD_HIGH:
            # 1.5 to 2.0
            return 1.5 + (vpin - self.THRESHOLD_ELEVATED) / (self.THRESHOLD_HIGH - self.THRESHOLD_ELEVATED) * 0.5
        else:
            return 2.0
    
    def _get_action_message(self, signal: VPINSignal) -> str:
        """Get human-readable action message"""
        messages = {
            "trade": "✅ Normal flow - proceed with trading",
            "widen_spreads": "⚠️ Elevated toxicity - widen spreads by {:.1f}x".format(
                self.get_spread_adjustment(signal.vpin)
            ),
            "withdraw": "🛑 High toxicity - withdraw quotes, don't add new",
            "kill": "🚨 CRITICAL TOXICITY - TRADING HALTED for {}s".format(
                self.kill_switch_cooldown_seconds
            )
        }
        return messages.get(signal.action, "Unknown action")
    
    def get_trend(self) -> str:
        """
        Analyze VPIN trend
        
        Returns:
            'rising', 'falling', or 'stable'
        """
        if len(self.vpin_history) < 10:
            return "insufficient_data"
        
        recent = list(self.vpin_history)[-10:]
        first_half = sum(recent[:5]) / 5
        second_half = sum(recent[5:]) / 5
        
        diff = second_half - first_half
        
        if diff > 0.05:
            return "rising"
        elif diff < -0.05:
            return "falling"
        else:
            return "stable"
    
    def get_stats(self) -> dict:
        """Get detector statistics"""
        signal = self.calculate_vpin()
        
        return {
            "current_vpin": signal.vpin,
            "toxicity_level": signal.toxicity_level,
            "action": signal.action,
            "bucket_count": signal.bucket_count,
            "kill_switch_active": self.kill_switch_active,
            "trend": self.get_trend(),
            "history_length": len(self.vpin_history)
        }
    
    def reset(self):
        """Reset detector state"""
        self.buckets.clear()
        self.current_bucket = TradeBucket()
        self.current_volume = 0.0
        self.vpin_history.clear()
        self.kill_switch_active = False
        self.kill_switch_time = None


# Integration with Risk Manager
class VPINRiskAdapter:
    """
    Adapter to integrate VPIN with existing risk management
    """
    
    def __init__(self, detector: VPINToxicityDetector):
        self.detector = detector
    
    def check_risk(self, trade_params: dict) -> dict:
        """
        Check if trade is allowed given current VPIN
        
        Args:
            trade_params: Dict with trade details
            
        Returns:
            Risk assessment dict
        """
        permission = self.detector.check_trade_permission()
        
        if not permission["permitted"]:
            return {
                "allowed": False,
                "reason": "VPIN kill switch active",
                "vpin": permission["vpin"],
                "cooldown_remaining": self.detector.kill_switch_cooldown_seconds
            }
        
        # Adjust position size based on toxicity
        spread_mult = permission["spread_adjustment"]
        
        return {
            "allowed": True,
            "vpin": permission["vpin"],
            "toxicity": permission["toxicity"],
            "spread_multiplier": spread_mult,
            "position_size_adjustment": 1.0 / spread_mult  # Reduce size in toxic markets
        }


# Example usage
if __name__ == "__main__":
    print("☠️ VPIN Toxicity Detector Demo\n")
    
    detector = VPINToxicityDetector(bucket_size=1000, num_buckets=10)
    
    # Simulate normal trading
    print("Simulating normal balanced flow...")
    for i in range(20):
        detector.add_trade({"size": 100, "side": "buy" if i % 2 == 0 else "sell"})
    
    signal = detector.calculate_vpin()
    print(f"VPIN: {signal.vpin:.3f} - {signal.toxicity_level} - {signal.action}")
    
    # Simulate toxic flow (informed traders selling)
    print("\nSimulating toxic flow (informed selling)...")
    detector.reset()
    for i in range(20):
        detector.add_trade({"size": 100, "side": "sell"})  # All sells
    
    signal = detector.calculate_vpin()
    print(f"VPIN: {signal.vpin:.3f} - {signal.toxicity_level} - {signal.action}")
    print(f"Kill switch active: {detector.kill_switch_active}")
    
    print("\n" + "="*50)
    print(detector.check_trade_permission())
