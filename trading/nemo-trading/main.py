"""
NEMO Trading - Main Orchestrator
Unified entry point for all exchanges and strategies
"""
import argparse
import logging
import sys
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config, DEFAULT_CONFIGS
from exchanges.coinbase import CoinbaseExchange
from exchanges.polymarket import PolymarketExchange
from utils.risk import RiskManager

# Import all strategies
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.snipe import SnipeStrategy
from strategies.crowd_fade import CrowdFadeStrategy
from strategies.copy_trading import CopyTradingStrategy

# Setup logging
def setup_logging(log_level: str = "INFO"):
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    
    # File handler for persistence
    file_handler = logging.FileHandler('/tmp/nemo-trading.log', mode='a')
    file_handler.setFormatter(formatter)
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level))
    root.handlers = []  # Clear existing
    root.addHandler(console)
    root.addHandler(file_handler)

class TradingBot:
    """Unified trading bot for all strategies and exchanges."""
    
    def __init__(self, config: Config):
        self.config = config
        self.config.validate()
        
        setup_logging(config.log_level)
        self.log = logging.getLogger(__name__)
        
        self.log.info("=" * 60)
        self.log.info("🐟 NEMO TRADING BOT")
        self.log.info("=" * 60)
        self.log.info(f"Exchange: {config.exchange}")
        self.log.info(f"Strategy: {config.strategy}")
        self.log.info(f"Mode: {'DRY-RUN' if config.dry_run else 'LIVE'}")
        self.log.info(f"Sandbox: {config.sandbox}")
        self.log.info("=" * 60)
        
        # Initialize exchange
        self.exchange = self._init_exchange()
        
        # Initialize risk manager
        start_balance = 10000.0 if config.exchange == "coinbase" else 500.0
        self.risk = RiskManager(config=config.risk, start_balance=start_balance)
        
        # Initialize strategy
        self.strategy = self._init_strategy()
        
        # Cycle counter
        self.cycle = 0
    
    def _init_exchange(self):
        """Initialize appropriate exchange."""
        if self.config.exchange == "coinbase":
            return CoinbaseExchange(
                api_key=self.config.coinbase.api_key,
                api_secret=self.config.coinbase.api_secret,
                sandbox=self.config.coinbase.sandbox,
                dry_run=self.config.dry_run
            )
        elif self.config.exchange == "polymarket":
            return PolymarketExchange(
                private_key=self.config.polymarket.private_key,
                funder_address=self.config.polymarket.funder_address,
                clob_host=self.config.polymarket.clob_host,
                chain_id=self.config.polymarket.chain_id,
                dry_run=self.config.dry_run
            )
        else:
            raise ValueError(f"Unknown exchange: {self.config.exchange}")
    
    def _init_strategy(self):
        """Initialize selected strategy."""
        strategy_map = {
            "momentum": (MomentumStrategy, self.config.momentum),
            "mean_reversion": (MeanReversionStrategy, self.config.mean_reversion),
            "snipe": (SnipeStrategy, self.config.snipe),
            "crowd_fade": (CrowdFadeStrategy, self.config.crowd_fade),
            "copy": (CopyTradingStrategy, self.config.copy_trading),
        }
        
        if self.config.strategy not in strategy_map:
            raise ValueError(f"Unknown strategy: {self.config.strategy}")
        
        strategy_class, strategy_config = strategy_map[self.config.strategy]
        
        # Validate strategy works with exchange
        if self.config.strategy in ["momentum", "mean_reversion"] and self.config.exchange != "coinbase":
            raise ValueError(f"{self.config.strategy} strategy only works with Coinbase")
        
        if self.config.strategy in ["snipe", "crowd_fade", "copy"] and self.config.exchange != "polymarket":
            raise ValueError(f"{self.config.strategy} strategy only works with Polymarket")
        
        return strategy_class(strategy_config, self.exchange, self.risk)
    
    def run(self):
        """Main trading loop."""
        self.log.info("🚀 Starting trading loop...")
        
        try:
            while True:
                self.cycle += 1
                cycle_start = time.time()
                
                # Log status periodically
                if self.cycle % 40 == 0:
                    self._log_status()
                
                # Execute strategy
                self._execute_strategy()
                
                # Check risk limits
                if self.risk.state.halted:
                    self.log.error(f"🛑 Trading halted: {self.risk.state.halt_reason}")
                    break
                
                # Sleep until next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.config.poll_interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.log.info("\n⚠️ Shutdown requested by user")
        finally:
            self.shutdown()
    
    def _execute_strategy(self):
        """Execute current strategy."""
        try:
            if self.config.exchange == "coinbase":
                self._run_coinbase_strategy()
            elif self.config.exchange == "polymarket":
                self._run_polymarket_strategy()
        except Exception as e:
            self.log.error(f"Strategy error: {e}")
    
    def _run_coinbase_strategy(self):
        """Run Coinbase strategies."""
        symbol = self.config.pair
        
        if isinstance(self.strategy, (MomentumStrategy, MeanReversionStrategy)):
            self.strategy.run(symbol)
    
    def _run_polymarket_strategy(self):
        """Run Polymarket strategies."""
        import random
        
        # Get markets
        markets = self.exchange.get_markets(self.config.market_slug_prefix)
        
        for market in markets:
            # Execute strategy
            if isinstance(self.strategy, SnipeStrategy):
                order_book = self.exchange.get_order_book(market.id, market.yes_token)
                if order_book:
                    # Simulate round timing (300 second rounds)
                    now = datetime.now()
                    
                    # Set round start if not set
                    if self.strategy.round_start_time is None:
                        self.strategy.round_start_time = now.replace(second=0, microsecond=0)
                        self.strategy.round_start_time = self.strategy.round_start_time.replace(
                            minute=(now.minute // 5) * 5
                        )
                    
                    if self.config.dry_run:
                        # In dry-run: generate simulated market data with randomness
                        if random.random() < 0.3:  # 30% chance of tradeable signal
                            current_delta = random.uniform(8.0, 50.0) * random.choice([-1, 1])
                            zero_crosses = random.randint(0, 2)
                        else:
                            current_delta = random.uniform(-5.0, 5.0)  # Chop
                            zero_crosses = random.randint(2, 5)
                        
                        self.strategy.run(market.id, market.yes_token, market.no_token, 
                                         order_book, current_delta, zero_crosses)
                    else:
                        # In live mode: use real market data
                        self.log.warning("Live market data not yet implemented for SnipeStrategy")
            
            elif isinstance(self.strategy, CrowdFadeStrategy):
                self.strategy.run(market.id, market.yes_token, market.no_token)
            
            elif isinstance(self.strategy, CopyTradingStrategy):
                self.strategy.run()
    
    def _log_status(self):
        """Log current status."""
        status = self.risk.get_status()
        
        self.log.info(
            f"[cycle {self.cycle}] "
            f"Balance: ${status['balance']:.2f} | "
            f"Daily P&L: ${status['daily_pnl']:.2f} | "
            f"Win Rate: {status['win_rate']:.1%} | "
            f"Trades: {status['trades_today']} | "
            f"Open: {status['open_positions']}"
        )
    
    def shutdown(self):
        """Graceful shutdown."""
        self.log.info("=" * 60)
        self.log.info("📊 SESSION SUMMARY")
        self.log.info("=" * 60)
        
        status = self.risk.get_status()
        start_balance = self.risk.state.start_balance
        final_balance = status['balance']
        total_return = ((final_balance - start_balance) / start_balance) * 100
        
        self.log.info(f"Cycles: {self.cycle}")
        self.log.info(f"Total Trades: {self.risk.state.total_trades}")
        self.log.info(f"Wins: {self.risk.state.wins}")
        self.log.info(f"Losses: {self.risk.state.losses}")
        self.log.info(f"Win Rate: {status['win_rate']:.1%}")
        self.log.info(f"Start Balance: ${start_balance:.2f}")
        self.log.info(f"Final Balance: ${final_balance:.2f}")
        self.log.info(f"Total P&L: ${status['daily_pnl']:.2f}")
        self.log.info(f"Return: {total_return:+.2f}%")
        self.log.info(f"Max Drawdown: {status['drawdown']:.1%}")
        self.log.info("=" * 60)
        self.log.info("🐟 NEMO Trading Bot stopped")
        self.log.info("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="🐟 NEMO Trading Bot - Unified Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run with preset
  python main.py --preset polymarket_snipe
  
  # Live trading (requires confirmation)
  python main.py --preset polymarket_snipe --live
  
  # Custom configuration
  python main.py --exchange polymarket --strategy snipe --live
  
  # With debug logging
  python main.py --preset coinbase_momentum --log-level DEBUG

Presets:
  coinbase_momentum      - Momentum on Coinbase (EMA + MACD)
  coinbase_mean_reversion - Mean reversion on Coinbase (RSI + BB)
  polymarket_snipe       - Late snipe on Polymarket
  polymarket_crowd       - Crowd fade on Polymarket
  polymarket_copy        - Copy trading on Polymarket
        """
    )
    
    parser.add_argument("--preset", choices=list(DEFAULT_CONFIGS.keys()),
                       help="Use predefined configuration")
    parser.add_argument("--exchange", choices=["coinbase", "polymarket"],
                       help="Exchange to trade on")
    parser.add_argument("--strategy", 
                       choices=["momentum", "mean_reversion", "snipe", "crowd_fade", "copy"],
                       help="Trading strategy")
    parser.add_argument("--live", action="store_true",
                       help="⚠️  Enable LIVE trading (default: dry-run)")
    parser.add_argument("--pair", default="BTC-USDC",
                       help="Trading pair for CEX (default: BTC-USDC)")
    parser.add_argument("--market-prefix", default="btc-updown-5m",
                       help="Market prefix for PM (default: btc-updown-5m)")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    args = parser.parse_args()
    
    # Build config
    if args.preset:
        config = DEFAULT_CONFIGS[args.preset]
    else:
        config = Config()
    
    # Override with CLI args
    if args.exchange:
        config.exchange = args.exchange
    if args.strategy:
        config.strategy = args.strategy
    if args.live:
        config.dry_run = False
    if args.pair:
        config.pair = args.pair
    if args.market_prefix:
        config.market_slug_prefix = args.market_prefix
    if args.log_level:
        config.log_level = args.log_level
    
    # Safety check for live trading
    if not config.dry_run:
        print("\n" + "=" * 60)
        print("⚠️  WARNING: LIVE TRADING MODE")
        print("=" * 60)
        print(f"Exchange: {config.exchange}")
        print(f"Strategy: {config.strategy}")
        print(f"Real money will be used!")
        print("=" * 60 + "\n")
        
        confirm = input('Type "YES" to confirm live trading: ')
        if confirm != "YES":
            print("Aborted.")
            sys.exit(1)
    
    # Create and run bot
    try:
        bot = TradingBot(config)
        bot.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
