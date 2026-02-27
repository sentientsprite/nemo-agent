#!/usr/bin/env python3
"""
Prediction market copy-trading bot.
Usage: python main.py --dry-run --platform kalshi
"""

import argparse
import logging
import sys
import time

from config import cfg
from copy_engine import CopyEngine
from ledger import Ledger
from signal_source import (
    KalshiLeaderboardSource,
    PolymarketAddressSource,
    WebhookSource,
    SignalSource,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("main")


def build_clients(platform: str):
    kalshi = None
    polymarket = None

    if platform in ("kalshi", "both"):
        from kalshi_client import KalshiClient
        kalshi = KalshiClient(cfg.kalshi)
        if not cfg.dry_run:
            kalshi.login()
            log.info(f"Kalshi authenticated (demo={cfg.kalshi.demo})")

    if platform in ("polymarket", "both"):
        try:
            from polymarket_client import PolymarketClient
            polymarket = PolymarketClient(cfg.polymarket)
            log.info("Polymarket client initialized")
        except ImportError:
            log.warning("py-clob-client not installed, skipping Polymarket")
        except Exception as e:
            log.warning(f"Polymarket init failed: {e}")

    return kalshi, polymarket


def build_sources(platform: str, kalshi_client) -> list[SignalSource]:
    sources: list[SignalSource] = []

    if platform in ("kalshi", "both") and kalshi_client:
        sources.append(KalshiLeaderboardSource(
            kalshi_client,
            leader_ids=cfg.kalshi_leader_ids,
        ))

    if platform in ("polymarket", "both") and cfg.polymarket_leader_addresses:
        sources.append(PolymarketAddressSource(cfg.polymarket_leader_addresses))

    # Always start webhook if configured
    if cfg.webhook_port:
        wh = WebhookSource(port=cfg.webhook_port, secret=cfg.webhook_secret)
        wh.start()
        sources.append(wh)
        log.info(f"Webhook listening on :{cfg.webhook_port}/signal")

    return sources


def main():
    parser = argparse.ArgumentParser(description="Prediction market copy-trading bot")
    parser.add_argument("--dry-run", action="store_true", default=None,
                        help="Paper trading mode (no real orders)")
    parser.add_argument("--platform", choices=["kalshi", "polymarket", "both"],
                        default=None, help="Platform to trade on")
    parser.add_argument("--interval", type=int, default=None,
                        help="Poll interval in seconds")
    args = parser.parse_args()

    # CLI overrides
    if args.dry_run is not None:
        cfg.dry_run = args.dry_run
    if args.platform:
        cfg.platform = args.platform
    if args.interval:
        cfg.poll_interval_seconds = args.interval

    platform = cfg.platform
    dry_label = " [DRY RUN]" if cfg.dry_run else " [LIVE]"
    log.info(f"Starting copy bot — platform={platform}{dry_label}")
    log.info(f"Bankroll: ${cfg.bankroll:.2f} | Poll: {cfg.poll_interval_seconds}s | Delay: {cfg.copy_delay_seconds}s")

    # Init
    kalshi, polymarket = build_clients(platform)
    sources = build_sources(platform, kalshi)
    if not sources:
        log.error("No signal sources configured. Set leader IDs/addresses or enable webhook.")
        sys.exit(1)

    engine = CopyEngine(
        config=cfg,
        kalshi_client=kalshi,
        polymarket_client=polymarket,
    )

    log.info(f"Active sources: {len(sources)} | Starting main loop...")

    # Main loop
    try:
        while True:
            for source in sources:
                try:
                    signals = source.poll()
                except Exception as e:
                    log.error(f"Source poll error: {e}")
                    continue

                for signal in signals:
                    # Filter: only process signals for our platform
                    if platform != "both" and signal.platform != platform:
                        continue
                    try:
                        engine.execute(signal)
                    except Exception as e:
                        log.error(f"Execution error: {e}")

            time.sleep(cfg.poll_interval_seconds)

    except KeyboardInterrupt:
        log.info("Shutting down...")
        ledger = Ledger(cfg.trades_file)
        summary = ledger.summary()
        log.info(f"Session summary: {summary}")


if __name__ == "__main__":
    main()
