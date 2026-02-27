#!/usr/bin/env python3
"""
Poly-Bot: Automated trading bot with Snipe + Maker strategy.

Usage:
    python main.py --strategy snipe_maker --dry-run
    python main.py --strategy baseline --dry-run
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional

from config import (
    BaseConfig,
    SnipeMakerConfig,
    ExecutionConfig,
    LoggingConfig,
    StrategyState,
    ROUND_DURATION,
)
from strategy import (
    BaselineStrategy,
    SnipeMakerStrategy,
    SignalDirection,
    MarketSignal,
    process_market_data,
)
from executor import Executor, ExecutionResult, SimulatedExchange

# Setup logging
def setup_logging():
    """Configure logging."""
    log_level = getattr(logging, LoggingConfig.LOG_LEVEL.upper())
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    if LoggingConfig.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if LoggingConfig.LOG_TO_FILE:
        os.makedirs(os.path.dirname(LoggingConfig.LOG_FILE), exist_ok=True)
        file_handler = logging.FileHandler(LoggingConfig.LOG_FILE)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Create log directories
    os.makedirs("logs", exist_ok=True)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Poly-Bot Trading System")
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["baseline", "snipe_maker", "both"],
        default="snipe_maker",
        help="Trading strategy to use"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run in simulation mode (no real trades)"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=10,
        help="Number of rounds to simulate"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Seconds between simulation steps"
    )
    return parser.parse_args()

class TradingBot:
    """Main trading bot orchestrator."""
    
    def __init__(self, strategy_name: str, dry_run: bool = True):
        self.strategy_name = strategy_name
        self.dry_run = dry_run
        self.logger = logging.getLogger("TradingBot")
        
        # Initialize state
        self.state = StrategyState()
        
        # Initialize exchange
        self.exchange = SimulatedExchange()
        
        # Initialize executor
        self.executor = Executor(self.state, self.exchange)
        
        # Initialize strategy
        self.strategy = self._create_strategy(strategy_name)
        
        # Performance tracking
        self.trades = []
        self.snipe_trades = []
        self.baseline_trades = []
        
        self.logger.info(f"TradingBot initialized with strategy: {strategy_name}")
        self.logger.info(f"Dry run mode: {dry_run}")
    
    def _create_strategy(self, name: str) -> object:
        """Create strategy instance."""
        if name == "baseline":
            return BaselineStrategy(self.state)
        elif name == "snipe_maker":
            return SnipeMakerStrategy(self.state)
        else:
            raise ValueError(f"Unknown strategy: {name}")
    
    def _simulate_market_data(self, seconds_into_round: float) -> dict:
        """
        Simulate market data for testing.
        Creates varying conditions for different scenarios.
        """
        # Simulate price movement through the round
        progress = seconds_into_round / ROUND_DURATION
        
        # Create some realistic scenarios
        if self.state.current_round % 3 == 0:
            # High volatility scenario
            base_yes = 0.50 + 0.20 * (progress - 0.5) + 0.1 * (progress > 0.8)
            delta = 25 + 10 * (progress > 0.8)  # High delta for snipe
            order_book_imbalance = 0.6 if progress > 0.7 else 0.2
        elif self.state.current_round % 3 == 1:
            # Low volatility scenario
            base_yes = 0.50 + 0.05 * (progress - 0.5)
            delta = 8 + 5 * (progress > 0.8)  # Low delta
            order_book_imbalance = 0.1
        else:
            # Medium volatility with clear direction
            base_yes = 0.45 + 0.15 * progress
            delta = 15 + 10 * (progress > 0.85)
            order_book_imbalance = 0.5 if progress > 0.6 else 0.3
        
        # Add some noise
        base_yes = max(0.05, min(0.95, base_yes + (0.02 * (seconds_into_round % 7 - 3))))
        base_no = 1.0 - base_yes
        
        mid_price = (base_yes + base_no) / 2
        
        return {
            "yes_price": base_yes,
            "no_price": base_no,
            "mid_price": mid_price,
            "order_book_imbalance": order_book_imbalance,
            "recent_trades": []
        }
    
    def _update_position_value(self):
        """Update current position value based on market prices."""
        if not self.state.has_position:
            return 0.0
        
        if self.state.position_side == "YES":
            value = self.exchange.current_yes_price * self.state.position_size
        else:
            value = self.exchange.current_no_price * self.state.position_size
        
        self.state.position_value = value
        return value
    
    def run_round(self, round_num: int, delay: float = 0.1):
        """Run a single trading round."""
        self.state.current_round = round_num
        self.state.reset_round()
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"ROUND {round_num} START")
        self.logger.info(f"Strategy: {self.strategy_name}")
        self.logger.info(f"{'='*60}")
        
        # Simulate the 5-minute round in compressed time
        step = 5  # Check every 5 seconds
        for seconds in range(0, ROUND_DURATION + 1, step):
            self.state.seconds_into_round = seconds
            
            # Simulate market data
            market_data = self._simulate_market_data(seconds)
            self.exchange.set_market_prices(
                market_data["yes_price"],
                market_data["no_price"]
            )
            
            # Process signal
            signal = process_market_data(
                market_data["yes_price"],
                market_data["no_price"],
                market_data["mid_price"],
                market_data["order_book_imbalance"],
                market_data["recent_trades"],
                self.state
            )
            
            # Update position value
            position_value = self._update_position_value()
            
            # Log market state (throttled)
            if seconds % 30 == 0 or seconds > 250:
                self.logger.debug(
                    f"t={seconds:3d}s | delta=${signal.delta:5.2f} | "
                    f"zc={signal.zero_crosses} | dir={signal.direction.value:7s} | "
                    f"pos={'YES' if self.state.has_position else '---'} | "
                    f"val=${position_value:.2f}"
                )
            
            # Check entry conditions
            if not self.state.has_position:
                should_enter, reason = self.strategy.should_enter(signal, seconds)
                if should_enter:
                    is_snipe = isinstance(self.strategy, SnipeMakerStrategy)
                    side = "YES" if signal.direction == SignalDirection.YES else "NO"
                    size = self.strategy.get_position_size()
                    
                    result = self.executor.enter_position(
                        side=side,
                        size=size,
                        is_snipe=is_snipe,
                        reason=reason
                    )
                    
                    if result.success:
                        trade = {
                            "round": round_num,
                            "time": seconds,
                            "type": "entry",
                            "side": side,
                            "size": size,
                            "price": result.order.avg_fill_price,
                            "is_snipe": is_snipe,
                            "reason": reason
                        }
                        self.trades.append(trade)
                        if is_snipe:
                            self.snipe_trades.append(trade)
                        else:
                            self.baseline_trades.append(trade)
            
            # Check maker exit fill (if pending)
            if self.open_orders_exist():
                fill_result = self.executor.check_maker_exit_fill()
                if fill_result:
                    trade = {
                        "round": round_num,
                        "time": seconds,
                        "type": "exit",
                        "side": self.state.position_side,
                        "size": self.state.position_size,
                        "price": fill_result.order.avg_fill_price,
                        "pnl": fill_result.pnl,
                        "maker_exit": True
                    }
                    self.trades.append(trade)
            
            # Check exit conditions
            if self.state.has_position and not self.open_orders_exist():
                should_exit, reason = self.strategy.should_exit(signal, seconds, position_value)
                
                if should_exit:
                    # Check if maker exit
                    use_maker = False
                    maker_price = None
                    if isinstance(self.strategy, SnipeMakerStrategy):
                        use_maker = self.strategy.is_maker_exit(position_value, seconds)
                        maker_price = self.strategy.get_maker_exit_price() if use_maker else None
                    
                    result = self.executor.exit_position(
                        use_maker_exit=use_maker,
                        maker_price=maker_price,
                        reason=reason
                    )
                    
                    if result.success:
                        trade = {
                            "round": round_num,
                            "time": seconds,
                            "type": "exit",
                            "side": self.state.position_side,
                            "size": self.state.position_size,
                            "price": result.order.avg_fill_price if result.order else 0,
                            "pnl": result.pnl,
                            "maker_exit": use_maker,
                            "reason": reason
                        }
                        self.trades.append(trade)
            
            # Cancel pending maker exits near round end
            if seconds > ROUND_DURATION - 10 and self.open_orders_exist():
                self.executor.cancel_pending_maker_exits()
            
            time.sleep(delay)
        
        # End of round cleanup
        if self.state.has_position:
            self.logger.info(f"Round {round_num}: Settling remaining position")
            result = self.executor.exit_position(reason="End of round settlement")
            if result.success and result.pnl != 0:
                trade = {
                    "round": round_num,
                    "time": ROUND_DURATION,
                    "type": "exit",
                    "side": self.state.position_side,
                    "pnl": result.pnl,
                    "settlement": True
                }
                self.trades.append(trade)
        
        self.logger.info(f"ROUND {round_num} COMPLETE")
    
    def open_orders_exist(self) -> bool:
        """Check if there are pending maker exit orders."""
        return len(self.executor.open_orders) > 0
    
    def print_performance_report(self):
        """Print detailed performance report."""
        self.logger.info(f"\n{'='*60}")
        self.logger.info("PERFORMANCE REPORT")
        self.logger.info(f"{'='*60}")
        
        # Overall stats
        total_trades = len([t for t in self.trades if t["type"] == "exit"])
        total_pnl = self.state.total_pnl
        
        self.logger.info(f"\nOverall Performance:")
        self.logger.info(f"  Total trades: {total_trades}")
        self.logger.info(f"  Total P&L: ${total_pnl:.2f}")
        self.logger.info(f"  Rounds with snipes: {self.state.snipe_count_today}")
        
        # Snipe vs Baseline comparison
        self.logger.info(f"\nStrategy Comparison:")
        self.logger.info(f"  Snipe P&L: ${self.state.snipe_pnl:.2f}")
        self.logger.info(f"  Baseline P&L: ${self.state.baseline_pnl:.2f}")
        
        if self.state.baseline_pnl != 0:
            improvement = (self.state.snipe_pnl - self.state.baseline_pnl) / abs(self.state.baseline_pnl) * 100
            self.logger.info(f"  Snipe vs Baseline: {improvement:+.1f}%")
        
        # Trade breakdown
        if self.trades:
            self.logger.info(f"\nTrade History:")
            for trade in self.trades:
                if trade["type"] == "exit":
                    maker_tag = " [MAKER]" if trade.get("maker_exit") else ""
                    snipe_tag = " [SNIPE]" if trade in self.snipe_trades else ""
                    self.logger.info(
                        f"  Round {trade['round']}: "
                        f"PnL=${trade.get('pnl', 0):+.2f}{maker_tag}{snipe_tag}"
                    )

def run_comparison_test(rounds: int = 10, delay: float = 0.01):
    """
    Run both strategies on identical market data for comparison.
    """
    logger = logging.getLogger("ComparisonTest")
    logger.info("\n" + "="*60)
    logger.info("RUNNING STRATEGY COMPARISON TEST")
    logger.info("="*60)
    
    # Run baseline
    logger.info("\n>>> Running Baseline Strategy <<<")
    baseline_bot = TradingBot("baseline", dry_run=True)
    for round_num in range(1, rounds + 1):
        baseline_bot.run_round(round_num, delay)
    
    baseline_pnl = baseline_bot.state.total_pnl
    baseline_trades = len([t for t in baseline_bot.trades if t["type"] == "exit"])
    
    # Run snipe_maker
    logger.info("\n>>> Running Snipe + Maker Strategy <<<")
    snipe_bot = TradingBot("snipe_maker", dry_run=True)
    for round_num in range(1, rounds + 1):
        snipe_bot.run_round(round_num, delay)
    
    snipe_pnl = snipe_bot.state.total_pnl
    snipe_trades = len([t for t in snipe_bot.trades if t["type"] == "exit"])
    snipe_count = snipe_bot.state.snipe_count_today
    maker_exits = len([t for t in snipe_bot.trades if t.get("maker_exit")])
    
    # Print comparison
    logger.info(f"\n{'='*60}")
    logger.info("COMPARISON RESULTS")
    logger.info(f"{'='*60}")
    logger.info(f"\nBaseline Strategy:")
    logger.info(f"  Total P&L: ${baseline_pnl:.2f}")
    logger.info(f"  Trades: {baseline_trades}")
    logger.info(f"  Avg per trade: ${baseline_pnl/max(1,baseline_trades):.2f}")
    
    logger.info(f"\nSnipe + Maker Strategy:")
    logger.info(f"  Total P&L: ${snipe_pnl:.2f}")
    logger.info(f"  Trades: {snipe_trades}")
    logger.info(f"  Snipes taken: {snipe_count}")
    logger.info(f"  Maker exits: {maker_exits}")
    logger.info(f"  Avg per trade: ${snipe_pnl/max(1,snipe_trades):.2f}")
    
    logger.info(f"\nDifference:")
    diff = snipe_pnl - baseline_pnl
    logger.info(f"  Snipe - Baseline: ${diff:+.2f}")
    if baseline_pnl != 0:
        pct = diff / abs(baseline_pnl) * 100
        logger.info(f"  Improvement: {pct:+.1f}%")
    
    return {
        "baseline_pnl": baseline_pnl,
        "snipe_pnl": snipe_pnl,
        "difference": diff,
        "snipe_count": snipe_count,
        "maker_exits": maker_exits
    }

def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger("Main")
    
    logger.info("="*60)
    logger.info("POLY-BOT TRADING SYSTEM")
    logger.info("="*60)
    logger.info(f"Strategy: {args.strategy}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Rounds: {args.rounds}")
    
    # Print config summary
    logger.info(f"\nConfiguration:")
    logger.info(f"  Snipe window: {SnipeMakerConfig.SNIPE_WINDOW_START}-{SnipeMakerConfig.SNIPE_WINDOW_END}s")
    logger.info(f"  Snipe min delta: ${SnipeMakerConfig.SNIPE_MIN_DELTA:.2f}")
    logger.info(f"  Snipe size: ${SnipeMakerConfig.SNIPE_SIZE:.0f}")
    logger.info(f"  Maker exit threshold: ${SnipeMakerConfig.MAKER_EXIT_THRESHOLD:.2f}")
    logger.info(f"  Maker exit price: ${SnipeMakerConfig.MAKER_EXIT_PRICE:.2f}")
    
    if args.strategy == "both":
        # Run comparison test
        results = run_comparison_test(args.rounds, args.delay)
    else:
        # Run single strategy
        bot = TradingBot(args.strategy, dry_run=args.dry_run)
        
        for round_num in range(1, args.rounds + 1):
            bot.run_round(round_num, args.delay)
        
        bot.print_performance_report()
        
        # Print snipe stats if applicable
        if args.strategy == "snipe_maker":
            logger.info(f"\nSnipe Statistics:")
            logger.info(f"  Snipes taken: {bot.state.snipe_count_today}")
            maker_exits = len([t for t in bot.trades if t.get("maker_exit")])
            logger.info(f"  Maker exits attempted: {maker_exits}")
    
    logger.info("\n" + "="*60)
    logger.info("BOT SHUTDOWN COMPLETE")
    logger.info("="*60)

if __name__ == "__main__":
    main()
