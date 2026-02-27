#!/usr/bin/env python3
"""
Coinbase Trading Bot — Orchestrator

Usage:
    python main.py --dry-run --strategy momentum
    python main.py --dry-run --strategy mean_reversion
    python main.py --strategy momentum --pair BTC-USDC
"""
import argparse
import logging
import signal
import sys
import time

from config import Config
from exchange import Exchange
from ledger import Ledger, TradeRecord
from risk import RiskManager, Position
from strategy_momentum import MomentumStrategy
from strategy_mean_reversion import MeanReversionStrategy


def setup_logging(level: str = "INFO"):
    fmt = "%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s"
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                        format=fmt, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)


log = logging.getLogger("main")


class TradingBot:
    def __init__(self, config: Config):
        self.cfg = config
        self.exchange = Exchange(config)
        self.ledger = Ledger(config.ledger_path)
        self.risk = RiskManager(config, self.ledger)
        self.running = True

        if config.strategy == "momentum":
            self.strategy = MomentumStrategy(config, self.exchange)
        elif config.strategy == "mean_reversion":
            self.strategy = MeanReversionStrategy(config, self.exchange)
        else:
            raise ValueError(f"Unknown strategy: {config.strategy}")

        log.info(f"Strategy: {self.strategy.name}")
        log.info(f"Pairs: {config.pairs}")
        log.info(f"Dry-run: {config.dry_run}")

    def run(self):
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        balance = self.exchange.get_usdc_balance()
        self.risk.set_daily_start_balance(balance)
        log.info(f"Starting balance: ${balance:.2f} USDC")

        cycle = 0
        while self.running:
            try:
                cycle += 1
                self._tick(cycle)
                time.sleep(self.cfg.poll_interval_sec)
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.error(f"Tick error: {e}", exc_info=True)
                time.sleep(self.cfg.poll_interval_sec * 2)

        self._print_summary()

    def _tick(self, cycle: int):
        balance = self.exchange.get_usdc_balance()

        for pair in self.cfg.pairs:
            # Check stop-losses on open positions
            if self.risk.has_position(pair):
                ticker = self.exchange.get_ticker(pair)
                if ticker and self.risk.check_stop_loss(pair, ticker.price):
                    self._close_position(pair, ticker.price, "stop-loss")
                    continue

                sig = self.strategy.evaluate(pair)
                pos = self.risk.get_position(pair)
                if pos and pos.side == "BUY" and sig.action in ("SELL", "EXIT"):
                    t = self.exchange.get_ticker(pair)
                    self._close_position(pair, t.price if t else pos.entry_price, sig.reason)
                    continue

            # Look for entries
            if not self.risk.has_position(pair):
                can, reason = self.risk.can_trade(balance)
                if not can:
                    if cycle % 20 == 1:
                        log.debug(f"Cannot trade: {reason}")
                    continue

                sig = self.strategy.evaluate(pair)
                if sig.action == "BUY" and sig.strength >= 0.5:
                    self._open_position(pair, sig, balance)

        if cycle % 40 == 0:
            log.info(f"[cycle {cycle}] Balance: ${balance:.2f} | Positions: {list(self.risk.positions.keys())} | Today P&L: ${self.ledger.today_pnl():.2f}")

    def _open_position(self, pair: str, sig, balance: float):
        usdc_amount = self.risk.position_size_usdc(balance, 0)
        if usdc_amount < self.cfg.min_trade_usdc:
            return

        log.info(f"ENTRY SIGNAL: {sig}")
        result = self.exchange.market_buy(pair, usdc_amount)

        if result.status != "FILLED":
            log.warning(f"Order not filled: {result.status}")
            return

        stop = self.risk.compute_stop_price(result.price, "BUY")
        pos = Position(
            pair=pair, side="BUY", entry_price=result.price,
            quantity=result.quantity, stop_price=stop,
            order_id=result.order_id, strategy=self.strategy.name,
            signal=sig.reason,
        )
        self.risk.record_open(pos)

        self.ledger.log(TradeRecord(
            timestamp=time.time(), pair=pair, side="BUY",
            price=result.price, quantity=result.quantity,
            quote_amount=result.quote_amount, fee=result.fee,
            order_id=result.order_id, strategy=self.strategy.name,
            signal=sig.reason, dry_run=self.cfg.dry_run,
        ))

    def _close_position(self, pair: str, current_price: float, reason: str):
        pos = self.risk.get_position(pair)
        if not pos:
            return

        log.info(f"EXIT: {pair} — {reason}")
        result = self.exchange.market_sell(pair, pos.quantity)

        if result.status != "FILLED":
            log.warning(f"Sell order not filled: {result.status}")
            return

        pnl = self.risk.record_close(pair, result.price, result.fee)

        self.ledger.log(TradeRecord(
            timestamp=time.time(), pair=pair, side="SELL",
            price=result.price, quantity=result.quantity,
            quote_amount=result.quote_amount, fee=result.fee,
            order_id=result.order_id, strategy=self.strategy.name,
            signal=reason, dry_run=self.cfg.dry_run, pnl=pnl,
        ))
        if pnl is not None:
            log.info(f"Closed {pair}: P&L=${pnl:.2f}")

    def _shutdown(self, *args):
        log.info("Shutting down...")
        self.running = False

    def _print_summary(self):
        summary = self.ledger.summary()
        balance = self.exchange.get_usdc_balance()
        log.info("=" * 60)
        log.info("SESSION SUMMARY")
        log.info(f"  Total trades: {summary.get('total_trades', 0)}")
        log.info(f"  Closed: {summary.get('closed', 0)}")
        log.info(f"  Wins: {summary.get('wins', 0)} | Losses: {summary.get('losses', 0)}")
        wr = summary.get('win_rate', 0)
        log.info(f"  Win rate: {wr:.0%}" if isinstance(wr, float) else f"  Win rate: {wr}")
        log.info(f"  Total P&L: ${summary.get('total_pnl', 0):.2f}")
        log.info(f"  Avg P&L/trade: ${summary.get('avg_pnl', 0):.2f}")
        log.info(f"  Best: ${summary.get('best_trade', 0):.2f} | Worst: ${summary.get('worst_trade', 0):.2f}")
        log.info(f"  Final balance: ${balance:.2f} USDC")
        log.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Coinbase Trading Bot")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Simulated trading (no API keys needed)")
    parser.add_argument("--strategy", choices=["momentum", "mean_reversion"], default="momentum")
    parser.add_argument("--pair", default=None, help="Override primary trading pair")
    parser.add_argument("--balance", type=float, default=None, help="Sim starting balance")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    cfg = Config()
    cfg.dry_run = args.dry_run or cfg.dry_run
    cfg.strategy = args.strategy
    if args.pair:
        cfg.pairs = [args.pair]
        cfg.primary_pair = args.pair
    if args.balance and cfg.dry_run:
        cfg.sim_starting_balance = args.balance
    cfg.log_level = args.log_level

    setup_logging(cfg.log_level)

    log.info("=" * 60)
    log.info("COINBASE TRADING BOT")
    log.info(f"  Mode: {'DRY-RUN (simulated)' if cfg.dry_run else 'LIVE'}")
    log.info(f"  Strategy: {cfg.strategy}")
    log.info(f"  Pairs: {cfg.pairs}")
    log.info(f"  Poll interval: {cfg.poll_interval_sec}s")
    log.info(f"  Risk: {cfg.max_position_pct:.0%} per trade, {cfg.stop_loss_pct:.0%} stop-loss")
    log.info("=" * 60)

    if not cfg.dry_run and (not cfg.api_key or not cfg.api_secret):
        log.error("COINBASE_API_KEY and COINBASE_API_SECRET required for live trading")
        sys.exit(1)

    bot = TradingBot(cfg)
    bot.run()


if __name__ == "__main__":
    main()
