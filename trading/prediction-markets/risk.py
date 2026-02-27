"""
Risk management engine.
- Max 10% bankroll per market
- Max 30% total exposure
- Daily loss limit 15%
- Max 3 positions from same leader
- Stop following leader if win rate < 50% over last 20 trades
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from config import RiskConfig


@dataclass
class PortfolioState:
    """Tracks current exposure and performance."""
    bankroll: float = 0.0
    # market_id -> USD exposure
    market_exposure: dict[str, float] = field(default_factory=dict)
    # leader_id -> count of open positions
    leader_position_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    # leader_id -> list of recent (win: bool) outcomes
    leader_results: dict[str, list[bool]] = field(default_factory=lambda: defaultdict(list))
    # daily P&L tracking
    daily_pnl: float = 0.0
    daily_reset_ts: float = field(default_factory=lambda: _start_of_day())

    @property
    def total_exposure(self) -> float:
        return sum(self.market_exposure.values())

    @property
    def total_exposure_pct(self) -> float:
        return self.total_exposure / self.bankroll if self.bankroll > 0 else 0.0

    def market_exposure_pct(self, market_id: str) -> float:
        exp = self.market_exposure.get(market_id, 0.0)
        return exp / self.bankroll if self.bankroll > 0 else 0.0

    def daily_loss_pct(self) -> float:
        if self.bankroll <= 0:
            return 0.0
        return abs(min(self.daily_pnl, 0)) / self.bankroll

    def reset_daily_if_needed(self):
        now_day = _start_of_day()
        if now_day > self.daily_reset_ts:
            self.daily_pnl = 0.0
            self.daily_reset_ts = now_day


def _start_of_day() -> float:
    """Timestamp of midnight UTC today."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.timestamp()


@dataclass
class RiskVerdict:
    allowed: bool
    reason: str = ""
    adjusted_size: Optional[float] = None


class RiskEngine:
    def __init__(self, config: RiskConfig, state: PortfolioState):
        self.config = config
        self.state = state

    def check(self, market_id: str, leader_id: str, size_usd: float) -> RiskVerdict:
        """Run all risk checks. Returns verdict with optional adjusted size."""
        self.state.reset_daily_if_needed()

        # 1. Daily loss limit
        if self.state.daily_loss_pct() >= self.config.daily_loss_limit_pct:
            return RiskVerdict(False, f"Daily loss limit hit ({self.config.daily_loss_limit_pct:.0%})")

        # 2. Total exposure cap
        new_total = self.state.total_exposure + size_usd
        if new_total / self.state.bankroll > self.config.max_total_exposure_pct:
            max_allowed = (self.config.max_total_exposure_pct * self.state.bankroll) - self.state.total_exposure
            if max_allowed <= 0:
                return RiskVerdict(False, f"Total exposure limit ({self.config.max_total_exposure_pct:.0%})")
            size_usd = max_allowed  # shrink to fit

        # 3. Per-market cap
        current_market = self.state.market_exposure.get(market_id, 0.0)
        max_market = self.config.max_per_market_pct * self.state.bankroll
        if current_market + size_usd > max_market:
            room = max_market - current_market
            if room <= 0:
                return RiskVerdict(False, f"Market exposure limit ({self.config.max_per_market_pct:.0%})")
            size_usd = room

        # 4. Max positions per leader
        if self.state.leader_position_count[leader_id] >= self.config.max_positions_per_leader:
            return RiskVerdict(False, f"Max {self.config.max_positions_per_leader} positions per leader")

        # 5. Leader win rate check
        results = self.state.leader_results.get(leader_id, [])
        if len(results) >= self.config.leader_winrate_window:
            recent = results[-self.config.leader_winrate_window:]
            wr = sum(recent) / len(recent)
            if wr < self.config.min_leader_winrate:
                return RiskVerdict(
                    False,
                    f"Leader {leader_id} win rate {wr:.0%} < {self.config.min_leader_winrate:.0%} "
                    f"over last {self.config.leader_winrate_window} trades",
                )

        return RiskVerdict(True, "ok", adjusted_size=size_usd)

    # ── State mutations ───────────────────────────────────────────────

    def record_open(self, market_id: str, leader_id: str, size_usd: float):
        self.state.market_exposure[market_id] = self.state.market_exposure.get(market_id, 0.0) + size_usd
        self.state.leader_position_count[leader_id] += 1

    def record_close(self, market_id: str, leader_id: str, size_usd: float, pnl: float, won: bool):
        self.state.market_exposure[market_id] = max(
            0, self.state.market_exposure.get(market_id, 0.0) - size_usd
        )
        self.state.leader_position_count[leader_id] = max(
            0, self.state.leader_position_count[leader_id] - 1
        )
        self.state.daily_pnl += pnl
        self.state.leader_results[leader_id].append(won)
