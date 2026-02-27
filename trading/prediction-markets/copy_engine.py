"""
Core copy-trading engine.
Signal → risk check → size → delay → execute → log.
"""

import logging
import time
from typing import Optional

from config import Config
from signal_source import Signal
from risk import RiskEngine, PortfolioState
from ledger import Ledger, TradeRecord

log = logging.getLogger(__name__)


class CopyEngine:
    def __init__(
        self,
        config: Config,
        kalshi_client=None,
        polymarket_client=None,
        risk_engine: Optional[RiskEngine] = None,
        ledger: Optional[Ledger] = None,
    ):
        self.config = config
        self.kalshi = kalshi_client
        self.polymarket = polymarket_client
        self.ledger = ledger or Ledger(config.trades_file)

        if risk_engine:
            self.risk = risk_engine
        else:
            state = PortfolioState(bankroll=config.bankroll)
            self.risk = RiskEngine(config.risk, state)

    def execute(self, signal: Signal) -> Optional[TradeRecord]:
        """Process a single signal through the full copy pipeline."""
        log.info(f"Signal: {signal.platform} {signal.market_id} {signal.side} "
                 f"@{signal.price} x{signal.size} from {signal.leader_id}")

        # 1. Calculate proportional position size
        size_usd = self._calculate_size(signal)
        if size_usd <= 0:
            log.info("Skipping: calculated size ≤ 0")
            return None

        # 2. Risk check
        verdict = self.risk.check(signal.market_id, signal.leader_id, size_usd)
        if not verdict.allowed:
            log.warning(f"Risk blocked: {verdict.reason}")
            return None
        size_usd = verdict.adjusted_size or size_usd

        # 3. Configurable delay
        if self.config.copy_delay_seconds > 0:
            log.info(f"Delay {self.config.copy_delay_seconds}s before execution")
            time.sleep(self.config.copy_delay_seconds)

        # 4. Execute
        order_id = ""
        fees = 0.0
        if self.config.dry_run:
            log.info(f"[DRY RUN] Would place: {signal.platform} {signal.market_id} "
                     f"{signal.side} ${size_usd:.2f}")
        else:
            order_id, fees = self._place_order(signal, size_usd)

        # 5. Update risk state
        self.risk.record_open(signal.market_id, signal.leader_id, size_usd)

        # 6. Log
        record = TradeRecord(
            timestamp=time.time(),
            platform=signal.platform,
            market_id=signal.market_id,
            market_title=signal.market_title,
            side=signal.side,
            price=signal.price,
            size=size_usd,
            leader_id=signal.leader_id,
            signal_source=signal.source_type,
            fees=fees,
            dry_run=self.config.dry_run,
            order_id=order_id,
        )
        self.ledger.log(record)
        log.info(f"Logged trade: {record.market_id} {record.side} ${record.size:.2f}")
        return record

    def _calculate_size(self, signal: Signal) -> float:
        """
        Proportional sizing: scale leader's position to our bankroll.
        If leader portfolio is known: (signal.size / leader_portfolio) * our_bankroll * ratio
        Otherwise: use signal size directly, capped by bankroll.
        """
        if signal.leader_portfolio and signal.leader_portfolio > 0:
            proportion = signal.size / signal.leader_portfolio
            size = proportion * self.config.bankroll * self.config.sizing_ratio
        else:
            # Direct dollar sizing with ratio
            size = signal.size * signal.price * self.config.sizing_ratio
            # Cap at a reasonable fraction of bankroll
            size = min(size, self.config.bankroll * self.config.risk.max_per_market_pct)

        return round(max(size, 0), 2)

    def _place_order(self, signal: Signal, size_usd: float) -> tuple[str, float]:
        """Place the actual order. Returns (order_id, fees)."""
        try:
            if signal.platform == "kalshi" and self.kalshi:
                return self._place_kalshi(signal, size_usd)
            elif signal.platform == "polymarket" and self.polymarket:
                return self._place_polymarket(signal, size_usd)
            else:
                log.error(f"No client for platform {signal.platform}")
                return "", 0.0
        except Exception as e:
            log.error(f"Order failed: {e}")
            return "", 0.0

    def _place_kalshi(self, signal: Signal, size_usd: float) -> tuple[str, float]:
        """Place on Kalshi. Convert USD to contract count."""
        price_cents = int(signal.price * 100)
        count = max(1, int(size_usd / signal.price))
        # Kalshi fee ~$0.035 per contract average
        est_fee = count * 0.035

        resp = self.kalshi.place_order(
            ticker=signal.market_id,
            side=signal.side,  # "yes" or "no"
            action="buy",
            count=count,
            order_type="limit",
            yes_price=price_cents if signal.side == "yes" else None,
            no_price=price_cents if signal.side == "no" else None,
        )
        order_id = resp.get("order", {}).get("order_id", "")
        return order_id, est_fee

    def _place_polymarket(self, signal: Signal, size_usd: float) -> tuple[str, float]:
        """Place on Polymarket CLOB."""
        shares = size_usd / signal.price if signal.price > 0 else 0
        if shares <= 0:
            return "", 0.0

        resp = self.polymarket.place_limit_order(
            token_id=signal.market_id,
            side="buy" if signal.side in ("yes", "buy") else "sell",
            price=signal.price,
            size=round(shares, 2),
        )
        order_id = resp.get("orderID", resp.get("id", ""))
        return order_id, 0.0  # Polymarket: no trading fee, ~2% on winnings
