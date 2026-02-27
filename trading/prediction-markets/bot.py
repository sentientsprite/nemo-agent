#!/usr/bin/env python3
"""
Polymarket Copy Trading Bot
Monitors leader addresses and copies their trades with safety limits.
"""

import json
import time
import signal
import sys
from datetime import datetime
from pathlib import Path

from config import cfg, verify_safety_limits
from polymarket_client import PolymarketClient, SafetyMonitor


class PolymarketBot:
    """Main trading bot with safety monitoring."""
    
    def __init__(self):
        self.client = PolymarketClient(cfg.polymarket)
        self.safety = SafetyMonitor(self.client)
        self.running = False
        self.trades_today = 0
        self.daily_loss = 0.0
        
        # Setup data directory
        Path(cfg.data_dir).mkdir(exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        print("\n[SHUTDOWN] Stopping bot...")
        self.running = False
    
    def log_trade(self, trade_data: dict):
        """Log trade to file for auditing."""
        trade_data["timestamp"] = datetime.utcnow().isoformat()
        trade_data["dry_run"] = cfg.dry_run
        
        with open(cfg.trades_file, "a") as f:
            f.write(json.dumps(trade_data) + "\n")
    
    def check_safety_limits(self) -> bool:
        """Check if we can trade based on safety limits."""
        status = self.safety.get_status()
        
        if not status["can_trade"]:
            print(f"[SAFETY] Daily loss limit reached: ${abs(status['daily_pnl']):.2f}")
            return False
        
        return True
    
    def monitor_leaders(self):
        """Monitor leader addresses for new trades."""
        leaders = cfg.polymarket_leader_addresses
        
        if not leaders:
            print("[WARNING] No leader addresses configured")
            return
        
        for leader in leaders:
            try:
                positions = PolymarketClient.get_address_positions(leader)
                print(f"[MONITOR] Leader {leader}: {len(positions)} positions")
                # TODO: Implement copy trading logic
            except Exception as e:
                print(f"[ERROR] Failed to fetch positions for {leader}: {e}")
    
    def run(self):
        """Main bot loop."""
        print("=" * 50)
        print("Polymarket Copy Trading Bot")
        print("=" * 50)
        print(f"Mode: {'LIVE' if not cfg.dry_run else 'DRY RUN'}")
        print(f"Max Trade: ${cfg.risk.max_trade_size_usd}")
        print(f"Stop Loss: -{cfg.risk.stop_loss_pct*100:.0f}%")
        print(f"Daily Limit: ${cfg.risk.daily_loss_limit_usd}")
        print(f"Leaders: {cfg.polymarket_leader_addresses}")
        print(f"Proxy: {cfg.polymarket.proxy_address}")
        print("=" * 50)
        print()
        
        # Verify safety limits on startup
        errors = verify_safety_limits()
        for error in errors:
            print(f"[SAFETY] {error}")
        
        if any(e.startswith("ERROR") for e in errors):
            print("[FATAL] Safety check failed. Exiting.")
            sys.exit(1)
        
        self.running = True
        
        while self.running:
            try:
                # Check safety limits
                if not self.check_safety_limits():
                    print("[SAFETY] Trading halted due to limits")
                    time.sleep(60)
                    continue
                
                # Monitor leaders
                self.monitor_leaders()
                
                # Check our own positions for stop loss
                positions = self.client.get_positions()
                portfolio_value = self.client.get_portfolio_value()
                
                print(f"[STATUS] Portfolio: ${portfolio_value:.2f} | Trades today: {self.trades_today}")
                
                # Sleep until next poll
                time.sleep(cfg.poll_interval_seconds)
                
            except Exception as e:
                print(f"[ERROR] Bot loop error: {e}")
                time.sleep(5)
        
        print("[SHUTDOWN] Bot stopped gracefully")


def main():
    """Entry point."""
    bot = PolymarketBot()
    bot.run()


if __name__ == "__main__":
    main()
