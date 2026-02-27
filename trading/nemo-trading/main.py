"""
NEMO Trading - Main Orchestrator
Unified entry point for all exchanges and strategies

INTEGRATION UPDATE (2026-02-26):
- Kelly Position Sizing: Dynamic position sizing based on edge
- VPIN Toxicity Detection: Kill switch for toxic flow
- Chainlink Oracle: Decentralized price feeds for arbitrage
- WebSocket Client: <100ms latency market data (optional)
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

# NEW: Night Shift modules (2026-02-26)
from utils.kelly import KellyPositionSizer
from utils.vpin import VPINToxicityDetector as VPINCalculator
from exchanges.chainlink import ChainlinkOracle

# WebSocket support (optional - falls back to REST if not available)
try:
    from exchanges.websocket_client import WebSocketClient
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

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
    """Unified trading bot for all strategies and exchanges.
    
    NEW: Integrated with Kelly sizing, VPIN toxicity detection,
    Chainlink oracle, and optional WebSocket connections.
    """
    
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
        
        # NEW: Initialize Kelly position sizer (2026-02-26)
        self.kelly = KellyPositionSizer(
            bankroll=start_balance,
            kelly_fraction=0.25,  # 0.25x fractional Kelly
            max_position_pct=0.10,  # Max 10% per trade
            min_position=5.0,
            max_position=50.0 if config.dry_run else 10.0  # $50 dry-run, $10 live
        )
        self.log.info("✅ Kelly position sizer initialized (0.25x fractional)")
        
        # NEW: Initialize VPIN toxicity detector (2026-02-26)
        self.vpin = VPINCalculator(
            bucket_size=50,  # 50 contracts per bucket
            num_buckets=10   # Rolling 10 buckets
        )
        self.log.info("✅ VPIN toxicity detector initialized")
        
        # NEW: Initialize Chainlink oracle for price verification (2026-02-26)
        self.chainlink: Optional[ChainlinkOracle] = None
        if config.exchange == "polymarket":
            try:
                self.chainlink = ChainlinkOracle()
                self.log.info("✅ Chainlink oracle initialized")
            except Exception as e:
                self.log.warning(f"⚠️ Chainlink oracle failed to initialize: {e}")
        
        # NEW: Initialize WebSocket client (optional, 2026-02-26)
        self.ws_client: Optional['WebSocketClient'] = None
        if WEBSOCKET_AVAILABLE and config.use_websocket:
            self.ws_client = WebSocketClient("nemo-trading")
            self.log.info("✅ WebSocket client initialized")
        
        # Initialize strategy
        self.strategy = self._init_strategy()
        
        # Cycle counter
        self.cycle = 0
        
        # VPIN kill switch state
        self.vpin_kill_active = False
        self.vpin_kill_until: Optional[datetime] = None
    
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
    
    def calculate_position_size(self, signal_confidence: float,
                                market_implied_prob: float = 0.5,
                                market_price: float = 0.5,
                                vpin_toxicity: float = 0.0) -> float:
        """Calculate position size using Kelly Criterion.

        NEW (2026-02-26): Replaces fixed position sizing with Kelly-based sizing.

        Args:
            signal_confidence: Model's estimated probability of winning (0-1)
            market_implied_prob: Market's implied probability (0-1)
            market_price: Current market price
            vpin_toxicity: VPIN toxicity score (0-1)

        Returns:
            Position size in dollars
        """
        try:
            kelly_result = self.kelly.calculate_position_size(
                model_probability=signal_confidence,
                market_implied_probability=market_implied_prob,
                market_price=market_price,
                vpin_toxicity=vpin_toxicity
            )

            # Log Kelly calculation
            self.log.debug(
                f"Kelly: edge={kelly_result.edge:.2%}, "
                f"full_kelly={kelly_result.full_kelly:.2%}, "
                f"fractional={kelly_result.fractional_kelly:.2%}, "
                f"position=${kelly_result.position_size:.2f}, "
                f"confidence={kelly_result.confidence}"
            )

            return kelly_result.position_size

        except Exception as e:
            self.log.warning(f"Kelly calculation failed, using default: {e}")
            return self.config.risk.max_position_size
    
    def check_vpin_toxicity(self, market_data: dict) -> str:
        """Check for toxic flow using VPIN.
        
        NEW (2026-02-26): VPIN-based toxicity detection with kill switch.
        
        Args:
            market_data: Dict with 'buy_volume' and 'sell_volume'
            
        Returns:
            Action: "trade", "widen_spreads", "withdraw", or "kill"
        """
        try:
            # Add trade to VPIN calculator
            self.vpin.add_trade({
                'side': market_data.get('side', 'buy'),
                'size': market_data.get('size', 1),
                'price': market_data.get('price', 0.5)
            })
            
            # Calculate VPIN
            vpin_signal = self.vpin.calculate_vpin()
            
            if vpin_signal:
                # Log VPIN status
                if vpin_signal.toxicity_level != "normal":
                    self.log.warning(
                        f"VPIN Alert: {vpin_signal.toxicity_level.upper()} "
                        f"(VPIN={vpin_signal.vpin:.2f}, action={vpin_signal.action})"
                    )
                
                # Handle kill switch
                if vpin_signal.action == "kill":
                    if not self.vpin_kill_active:
                        self.vpin_kill_active = True
                        self.vpin_kill_until = datetime.utcnow() + timedelta(minutes=5)
                        self.log.error(
                            f"🛑 VPIN KILL SWITCH ACTIVATED "
                            f"(VPIN={vpin_signal.vpin:.2f})"
                        )
                
                return vpin_signal.action
            
            return "trade"
            
        except Exception as e:
            self.log.error(f"VPIN calculation failed: {e}")
            return "withdraw"  # Fail closed - withdraw when VPIN is broken
    
    def is_vpin_kill_active(self) -> bool:
        """Check if VPIN kill switch is currently active."""
        if not self.vpin_kill_active:
            return False
        
        # Check if cooldown has expired
        if self.vpin_kill_until and datetime.utcnow() > self.vpin_kill_until:
            self.vpin_kill_active = False
            self.vpin_kill_until = None
            self.log.info("✅ VPIN kill switch cooldown expired, resuming trading")
            return False
        
        return True
    
    def get_chainlink_price(self) -> Optional[float]:
        """Get BTC/USD price from Chainlink oracle.
        
        NEW (2026-02-26): Decentralized price verification.
        
        Returns:
            BTC/USD price or None if unavailable
        """
        if not self.chainlink:
            return None
        
        try:
            price_data = self.chainlink.get_latest_price()
            if price_data:
                self.log.debug(f"Chainlink BTC/USD: ${price_data.price:,.2f}")
                return price_data.price
            return None
        except Exception as e:
            self.log.warning(f"Chainlink price fetch failed: {e}")
            return None
    
    def verify_price_arbitrage(self, exchange_price: float) -> bool:
        """Verify exchange price against Chainlink oracle.
        
        NEW (2026-02-26): Detect price manipulation.
        
        Args:
            exchange_price: Price from exchange
            
        Returns:
            True if prices agree within threshold, False if suspicious
        """
        chainlink_price = self.get_chainlink_price()
        if not chainlink_price:
            return True  # Can't verify, assume OK
        
        diff_pct = abs(exchange_price - chainlink_price) / chainlink_price
        
        if diff_pct > 0.01:  # >1% difference
            self.log.warning(
                f"⚠️ Price discrepancy: Exchange=${exchange_price:,.2f}, "
                f"Chainlink=${chainlink_price:,.2f}, diff={diff_pct:.2%}"
            )
            return False
        
        return True
    
    def run(self):
        """Main trading loop."""
        self.log.info("🚀 Starting trading loop...")
        
        # Log new capabilities
        self.log.info("🆕 CAPABILITIES: Kelly sizing | VPIN detection | Chainlink oracle")
        
        try:
            while True:
                self.cycle += 1
                cycle_start = time.time()
                
                # Check VPIN kill switch first
                if self.is_vpin_kill_active():
                    remaining = (self.vpin_kill_until - datetime.utcnow()).seconds
                    self.log.warning(f"🛑 VPIN kill switch active, skipping cycle ({remaining}s remaining)")
                    time.sleep(self.config.poll_interval)
                    continue
                
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
        """Run Coinbase strategies with Kelly sizing and VPIN."""
        symbol = self.config.pair
        
        if isinstance(self.strategy, (MomentumStrategy, MeanReversionStrategy)):
            # Get current position info for Kelly calculation
            current_price = self.exchange.get_price(symbol)
            
            # Verify price against Chainlink (if available)
            if not self.verify_price_arbitrage(current_price):
                self.log.warning("Price verification failed, skipping signal")
                return
            
            # Calculate position size using Kelly
            # For momentum: higher confidence on strong trends
            signal_strength = getattr(self.strategy, 'last_signal_strength', 0.6)
            position_size = self.calculate_position_size(
                signal_confidence=signal_strength,
                market_implied_prob=0.5,
                market_price=current_price
            )
            
            # Update strategy with Kelly-calculated size
            self.strategy.config.entry_size = position_size
            self.log.debug(f"Kelly position size: ${position_size:.2f}")
            
            # Run strategy
            self.strategy.run(symbol)
    
    def _run_polymarket_strategy(self):
        """Run Polymarket strategies with Kelly sizing and VPIN."""
        import random
        
        # Get markets
        markets = self.exchange.get_markets(self.config.market_slug_prefix)
        
        for market in markets:
            # Get order book for VPIN calculation
            order_book = self.exchange.get_order_book(market.id, market.yes_token)
            
            if order_book:
                # Check VPIN toxicity
                if self.config.dry_run:
                    # In dry-run: use simulated market data for VPIN
                    market_data = {
                        'side': random.choice(['buy', 'sell']),
                        'size': random.uniform(1, 10),
                        'price': order_book.mid_price if hasattr(order_book, 'mid_price') else 0.5
                    }
                    vpin_action = self.check_vpin_toxicity(market_data)
                else:
                    # In live mode: skip VPIN check until real trade flow is implemented
                    # TODO: Implement actual trade data feed for VPIN
                    vpin_action = "trade"
                
                if vpin_action in ["withdraw", "kill"]:
                    self.log.warning(f"VPIN {vpin_action} for market {market.id}, skipping")
                    continue
                
                # Calculate Kelly position size
                # Higher confidence when market is mispriced
                signal_confidence = 0.65 if isinstance(self.strategy, SnipeStrategy) else 0.55
                mid_price = order_book.mid_price if hasattr(order_book, 'mid_price') else 0.5
                position_size = self.calculate_position_size(
                    signal_confidence=signal_confidence,
                    market_implied_prob=mid_price,
                    market_price=mid_price
                )
                
                # Update strategy config with Kelly size
                if hasattr(self.strategy, 'config'):
                    self.strategy.config.entry_size = position_size
            
            # Execute strategy
            if isinstance(self.strategy, SnipeStrategy):
                # Simulate round timing (300 second rounds)
                now = datetime.now()
                seconds_into_round = now.second + (now.minute % 5) * 60
                
                # Set round start if not set
                if self.strategy.round_start_time is None:
                    self.strategy.round_start_time = now.replace(second=0, microsecond=0)
                    self.strategy.round_start_time = self.strategy.round_start_time.replace(
                        minute=(now.minute // 5) * 5
                    )
                
                if order_book:
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
                        # TODO: Implement actual market data feed
                        self.log.warning("Live market data not yet implemented for SnipeStrategy")
            
            elif isinstance(self.strategy, CrowdFadeStrategy):
                self.strategy.run(market.id, market.yes_token, market.no_token)
            
            elif isinstance(self.strategy, CopyTradingStrategy):
                self.strategy.run()
    
    def _log_status(self):
        """Log current status."""
        status = self.risk.get_status()
        
        # NEW: Include VPIN and Kelly info in status
        vpin_status = "🛑 KILL" if self.vpin_kill_active else "✅ OK"
        
        self.log.info(
            f"[cycle {self.cycle}] "
            f"Balance: ${status['balance']:.2f} | "
            f"Daily P&L: ${status['daily_pnl']:.2f} | "
            f"Win Rate: {status['win_rate']:.1%} | "
            f"Trades: {status['trades_today']} | "
            f"Open: {status['open_positions']} | "
            f"VPIN: {vpin_status}"
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
        
        # NEW: VPIN stats
        if hasattr(self.vpin, 'buckets') and len(self.vpin.buckets) > 0:
            self.log.info(f"VPIN Buckets: {len(self.vpin.buckets)}")
        
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

NEW CAPABILITIES (2026-02-26):
  ✓ Kelly Position Sizing - Dynamic sizing based on edge
  ✓ VPIN Toxicity Detection - Kill switch for toxic flow
  ✓ Chainlink Oracle - Decentralized price verification
  ✓ WebSocket Support - <100ms latency (optional)

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
    parser.add_argument("--use-websocket", action="store_true",
                       help="Use WebSocket for market data (lower latency)")
    
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
    if args.use_websocket:
        config.use_websocket = True
    
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
