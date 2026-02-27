"""
Risk management — position sizing, stop-losses, drawdown protection.
"""
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from config import Config
from ledger import Ledger

log = logging.getLogger("risk")


@dataclass
class Position:
    pair: str
    side: str
    entry_price: float
    quantity: float
    entry_time: float = field(default_factory=time.time)
    stop_price: Optional[float] = None
    order_id: str = ""
    strategy: str = ""
    signal: str = ""


class RiskManager:
    def __init__(self, config: Config, ledger: Ledger):
        self.cfg = config
        self.ledger = ledger
        self.positions: dict[str, Position] = {}
        self.consecutive_losses = 0
        self.daily_start_balance: Optional[float] = None
        self.halted = False
        self._skip_next = False

    def set_daily_start_balance(self, balance: float):
        self.daily_start_balance = balance
        self.halted = False
        self.consecutive_losses = 0
        self._skip_next = False
        log.info(f"Daily start balance set: ${balance:.2f}")

    def position_size_usdc(self, balance: float, price: float) -> float:
        max_usdc = balance * self.cfg.max_position_pct
        return max(min(max_usdc, balance), 0.0)

    def compute_stop_price(self, entry_price: float, side: str) -> float:
        if side == "BUY":
            return entry_price * (1.0 - self.cfg.stop_loss_pct)
        else:
            return entry_price * (1.0 + self.cfg.stop_loss_pct)

    def check_stop_loss(self, pair: str, current_price: float) -> bool:
        pos = self.positions.get(pair)
        if not pos or pos.stop_price is None:
            return False
        if pos.side == "BUY" and current_price <= pos.stop_price:
            log.warning(f"STOP-LOSS triggered for {pair}: price={current_price:.2f} <= stop={pos.stop_price:.2f}")
            return True
        return False

    def can_trade(self, balance: float) -> tuple[bool, str]:
        if self.halted:
            return False, "HALTED: daily drawdown limit reached"

        if self._skip_next:
            self._skip_next = False
            log.info("Skipping signal due to consecutive loss cooldown")
            return False, "Skipping: consecutive loss cooldown"

        if self.consecutive_losses >= self.cfg.consecutive_loss_limit:
            self._skip_next = True
            self.consecutive_losses = 0
            return False, f"Hit {self.cfg.consecutive_loss_limit} consecutive losses, skipping next"

        if self.daily_start_balance and self.daily_start_balance > 0:
            drawdown = (self.daily_start_balance - balance) / self.daily_start_balance
            if drawdown >= self.cfg.max_daily_drawdown_pct:
                self.halted = True
                log.critical(f"HALTED: daily drawdown {drawdown:.1%} >= {self.cfg.max_daily_drawdown_pct:.0%}")
                return False, f"HALTED: drawdown {drawdown:.1%}"

        if len(self.positions) > 0:
            return False, f"Already in {len(self.positions)} position(s)"

        min_trade = self.cfg.min_trade_usdc
        max_alloc = balance * self.cfg.max_position_pct
        if max_alloc < min_trade:
            return False, f"Position size ${max_alloc:.2f} below minimum ${min_trade:.2f}"

        return True, "OK"

    def record_open(self, pos: Position):
        self.positions[pos.pair] = pos
        log.info(f"Opened {pos.side} {pos.pair}: qty={pos.quantity:.6f} @ ${pos.entry_price:.2f}, stop=${pos.stop_price:.2f}")

    def record_close(self, pair: str, exit_price: float, fee: float) -> Optional[float]:
        pos = self.positions.pop(pair, None)
        if not pos:
            return None
        if pos.side == "BUY":
            pnl = (exit_price - pos.entry_price) * pos.quantity - fee
        else:
            pnl = (pos.entry_price - exit_price) * pos.quantity - fee

        if pnl <= 0:
            self.consecutive_losses += 1
            log.info(f"Loss #{self.consecutive_losses}: ${pnl:.2f}")
        else:
            self.consecutive_losses = 0
            log.info(f"Win: +${pnl:.2f} (streak reset)")

        return round(pnl, 4)

    def has_position(self, pair: str) -> bool:
        return pair in self.positions

    def get_position(self, pair: str) -> Optional[Position]:
        return self.positions.get(pair)
