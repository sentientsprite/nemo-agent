"""
Fractional Kelly Criterion Position Sizing
Implements 0.25x Kelly for reduced variance while maintaining edge
"""

import math
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class KellySizing:
    """Result of Kelly calculation"""
    full_kelly: float  # Full Kelly fraction (0-1)
    fractional_kelly: float  # 0.25x Kelly fraction
    position_size: float  # Dollar amount to trade
    edge: float  # Model edge vs market
    win_prob: float  # Estimated win probability
    win_loss_ratio: float  # b = avg_win / avg_loss
    confidence: str  # high/medium/low based on edge size
    

class KellyPositionSizer:
    """
    Fractional Kelly Position Sizer
    
    The Kelly Criterion: f* = (p*b - q) / b
    Where:
    - f* = optimal fraction of bankroll to bet
    - p = probability of winning
    - q = probability of losing (1-p)
    - b = win/loss ratio (avg win / avg loss)
    
    We use 0.25x fractional Kelly to reduce variance:
    position = 0.25 * f* * bankroll
    """
    
    def __init__(
        self,
        bankroll: float = 1000.0,
        kelly_fraction: float = 0.25,
        max_position_pct: float = 0.10,  # Max 10% per trade
        min_position: float = 5.0,  # Minimum trade size
        max_position: float = 50.0  # Maximum trade size (for dry-run)
    ):
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.max_position_pct = max_position_pct
        self.min_position = min_position
        self.max_position = max_position
        
        # Track historical outcomes for adaptive sizing
        self.trade_history: list[dict] = []
        
    def calculate_edge(
        self,
        model_probability: float,
        market_implied_probability: float
    ) -> float:
        """
        Calculate edge: difference between model and market
        
        Args:
            model_probability: Our model's estimated win probability (0-1)
            market_implied_probability: Market price implies this probability
            
        Returns:
            Edge as percentage (e.g., 0.05 = 5% edge)
        """
        return model_probability - market_implied_probability
    
    def estimate_win_probability(
        self,
        model_probability: float,
        edge: float,
        confidence_boost: float = 0.0
    ) -> float:
        """
        Estimate true win probability combining model + edge
        
        Args:
            model_probability: Base model prediction
            edge: Edge over market
            confidence_boost: Additional confidence from other signals (0-0.1)
        """
        # Blend model prob with edge-adjusted estimate
        # Higher edge = more confident in model
        edge_weight = min(abs(edge) * 2, 0.3)  # Max 30% weight from edge
        
        adjusted_prob = model_probability + (edge * edge_weight) + confidence_boost
        
        # Clamp to valid probability range
        return max(0.05, min(0.95, adjusted_prob))
    
    def estimate_win_loss_ratio(
        self,
        market_price: float,
        target_exit: Optional[float] = None,
        stop_loss: Optional[float] = None
    ) -> float:
        """
        Estimate win/loss ratio (b) based on market structure
        
        For prediction markets:
        - If buying YES at $0.50, potential win = $0.50, loss = $0.50
        - Ratio = 1.0
        
        For snipe strategy:
        - Entry at $0.80, exit at $0.90
        - Win = $0.10, Risk = $0.80 (if goes to 0)
        - But with stop at $0.70: Risk = $0.10
        - Ratio = 1.0
        """
        if target_exit and stop_loss:
            # Specific targets provided
            potential_win = abs(target_exit - market_price)
            potential_loss = abs(market_price - stop_loss)
            
            if potential_loss == 0:
                return 1.0  # Default
            
            return potential_win / potential_loss
        
        # Default: assume symmetric for prediction markets
        # Buying at price p: win (1-p), lose p
        # Ratio = (1-p) / p
        if market_price > 0 and market_price < 1:
            return (1 - market_price) / market_price
        
        return 1.0
    
    def calculate_position_size(
        self,
        model_probability: float,
        market_implied_probability: float,
        market_price: float,
        target_exit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        vpin_toxicity: float = 0.0  # VPIN signal (0-1)
    ) -> KellySizing:
        """
        Calculate position size using fractional Kelly
        
        Args:
            model_probability: Our model's win probability estimate
            market_implied_probability: Market price implies this probability
            market_price: Current market price (for win/loss calc)
            target_exit: Target exit price (optional)
            stop_loss: Stop loss price (optional)
            vpin_toxicity: VPIN toxicity score (0-1, higher = more toxic)
            
        Returns:
            KellySizing with position recommendation
        """
        # Calculate edge
        edge = self.calculate_edge(model_probability, market_implied_probability)
        
        # Estimate win probability
        win_prob = self.estimate_win_probability(model_probability, edge)
        loss_prob = 1 - win_prob
        
        # Estimate win/loss ratio
        win_loss_ratio = self.estimate_win_loss_ratio(
            market_price, target_exit, stop_loss
        )
        
        # Kelly Criterion: f* = (p*b - q) / b
        if win_loss_ratio == 0:
            full_kelly = 0
        else:
            full_kelly = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
        
        # Kelly must be positive to trade
        if full_kelly <= 0:
            return KellySizing(
                full_kelly=0,
                fractional_kelly=0,
                position_size=0,
                edge=edge,
                win_prob=win_prob,
                win_loss_ratio=win_loss_ratio,
                confidence="none"
            )
        
        # Apply fractional Kelly (0.25x)
        fractional_kelly = full_kelly * self.kelly_fraction
        
        # Apply VPIN adjustment (reduce size in toxic markets)
        # VPIN > 0.5 starts reducing position, VPIN > 0.8 = no trade
        if vpin_toxicity > 0.8:
            return KellySizing(
                full_kelly=full_kelly,
                fractional_kelly=0,
                position_size=0,
                edge=edge,
                win_prob=win_prob,
                win_loss_ratio=win_loss_ratio,
                confidence="toxic"
            )
        
        vpin_adjustment = 1 - (vpin_toxicity * 0.5)  # Max 50% reduction
        adjusted_kelly = fractional_kelly * vpin_adjustment
        
        # Calculate position size
        raw_position = self.bankroll * adjusted_kelly
        
        # Apply constraints
        max_by_pct = self.bankroll * self.max_position_pct
        position_size = min(raw_position, max_by_pct, self.max_position)
        position_size = max(position_size, self.min_position)
        
        # Confidence level
        if abs(edge) > 0.1:
            confidence = "high"
        elif abs(edge) > 0.05:
            confidence = "medium"
        else:
            confidence = "low"
        
        return KellySizing(
            full_kelly=full_kelly,
            fractional_kelly=adjusted_kelly,
            position_size=position_size,
            edge=edge,
            win_prob=win_prob,
            win_loss_ratio=win_loss_ratio,
            confidence=confidence
        )
    
    def update_bankroll(self, new_bankroll: float):
        """Update bankroll after trades"""
        self.bankroll = new_bankroll
    
    def record_trade(
        self,
        market: str,
        side: str,
        size: float,
        outcome: str,  # 'win' or 'loss'
        pnl: float,
        kelly_used: float
    ):
        """Record trade outcome for analysis"""
        self.trade_history.append({
            "market": market,
            "side": side,
            "size": size,
            "outcome": outcome,
            "pnl": pnl,
            "kelly_fraction": kelly_used,
            "bankroll_after": self.bankroll
        })
    
    def get_performance_stats(self) -> dict:
        """Analyze Kelly sizing performance"""
        if not self.trade_history:
            return {"error": "No trades recorded"}
        
        wins = [t for t in self.trade_history if t["outcome"] == "win"]
        losses = [t for t in self.trade_history if t["outcome"] == "loss"]
        
        total_pnl = sum(t["pnl"] for t in self.trade_history)
        
        return {
            "total_trades": len(self.trade_history),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(self.trade_history) if self.trade_history else 0,
            "total_pnl": total_pnl,
            "avg_kelly": sum(t["kelly_fraction"] for t in self.trade_history) / len(self.trade_history) if self.trade_history else 0,
            "current_bankroll": self.bankroll
        }


# Convenience functions
def calculate_kelly_position(
    model_prob: float,
    market_prob: float,
    bankroll: float = 1000.0,
    market_price: float = 0.5
) -> float:
    """Quick Kelly position size calculation"""
    sizer = KellyPositionSizer(bankroll=bankroll)
    sizing = sizer.calculate_position_size(
        model_probability=model_prob,
        market_implied_probability=market_prob,
        market_price=market_price
    )
    return sizing.position_size


# Example usage
if __name__ == "__main__":
    print("📊 Fractional Kelly Position Sizing Demo\n")
    
    sizer = KellyPositionSizer(bankroll=1000.0)
    
    # Example: High confidence prediction
    sizing = sizer.calculate_position_size(
        model_probability=0.75,  # We think 75% chance
        market_implied_probability=0.55,  # Market thinks 55%
        market_price=0.55,
        target_exit=0.90,
        stop_loss=0.45
    )
    
    print(f"Model Probability: 75%")
    print(f"Market Implied: 55%")
    print(f"Edge: {sizing.edge*100:.1f}%")
    print(f"Full Kelly: {sizing.full_kelly*100:.2f}%")
    print(f"0.25x Kelly: {sizing.fractional_kelly*100:.2f}%")
    print(f"Position Size: ${sizing.position_size:.2f}")
    print(f"Confidence: {sizing.confidence}")
    
    print("\n" + "="*50)
    
    # Example: No edge (don't trade)
    sizing2 = sizer.calculate_position_size(
        model_probability=0.52,
        market_implied_probability=0.52,
        market_price=0.52
    )
    
    print(f"\nNo Edge Example:")
    print(f"Position Size: ${sizing2.position_size:.2f} (no trade)")
