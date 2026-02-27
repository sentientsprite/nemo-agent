"""
Signal sources: abstract base + Kalshi leaderboard, Polymarket address watcher, webhook.
"""

import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from flask import Flask, request, jsonify


@dataclass
class Signal:
    """Normalized trade signal from any source."""
    platform: str          # "kalshi" or "polymarket"
    market_id: str         # ticker (Kalshi) or token_id (Polymarket)
    market_title: str
    side: str              # "yes" / "no" (Kalshi) or "buy" / "sell" (Polymarket)
    price: float           # 0.01 - 0.99
    size: float            # contracts / shares
    leader_id: str         # who we're copying
    source_type: str       # "kalshi_leaderboard", "polymarket_address", "webhook"
    timestamp: float = field(default_factory=time.time)
    leader_portfolio: Optional[float] = None  # for proportional sizing


class SignalSource(ABC):
    """Base class for all signal sources."""

    @abstractmethod
    def poll(self) -> list[Signal]:
        """Return new signals since last poll. Must be non-blocking."""
        ...


# ── Kalshi Leaderboard Source ─────────────────────────────────────────

class KalshiLeaderboardSource(SignalSource):
    """
    Poll Kalshi leaderboard for top traders, then diff their positions
    to detect new trades.
    """

    def __init__(self, kalshi_client, leader_ids: list[str] | None = None, top_n: int = 10):
        self.client = kalshi_client
        self.leader_ids = leader_ids or []
        self.top_n = top_n
        self._last_positions: dict[str, dict] = {}  # leader_id -> {ticker: position}

    def poll(self) -> list[Signal]:
        signals: list[Signal] = []

        # If no specific leaders, try leaderboard
        target_ids = self.leader_ids
        if not target_ids:
            lb = self.client.get_leaderboard(limit=self.top_n)
            target_ids = [u.get("user_id", u.get("id", "")) for u in lb if u]

        for leader_id in target_ids:
            try:
                current = self._fetch_leader_positions(leader_id)
            except Exception:
                continue

            prev = self._last_positions.get(leader_id, {})
            new_signals = self._diff_positions(leader_id, prev, current)
            signals.extend(new_signals)
            self._last_positions[leader_id] = current

        return signals

    def _fetch_leader_positions(self, leader_id: str) -> dict:
        """
        Fetch a leader's positions. Kalshi doesn't expose other users'
        positions publicly — this is a placeholder for when they add
        portfolio-sharing or you use a known leader's fills.
        For now, relies on self.leader_ids being your own sub-accounts
        or publicly shared data.
        """
        # Placeholder: in practice you'd call a portfolio-sharing endpoint
        # or scrape a public profile page
        return {}

    def _diff_positions(self, leader_id: str, prev: dict, current: dict) -> list[Signal]:
        signals = []
        for ticker, pos in current.items():
            if ticker not in prev or pos != prev[ticker]:
                signals.append(Signal(
                    platform="kalshi",
                    market_id=ticker,
                    market_title=pos.get("title", ticker),
                    side="yes" if pos.get("position", 0) > 0 else "no",
                    price=pos.get("price", 0.50),
                    size=abs(pos.get("position", 0)),
                    leader_id=leader_id,
                    source_type="kalshi_leaderboard",
                    leader_portfolio=pos.get("portfolio_value"),
                ))
        return signals


# ── Polymarket Address Source ─────────────────────────────────────────

class PolymarketAddressSource(SignalSource):
    """Monitor wallet addresses on Polymarket for new positions."""

    def __init__(self, addresses: list[str]):
        from polymarket_client import PolymarketClient
        self.addresses = addresses
        self._last_positions: dict[str, list[dict]] = {}

    def poll(self) -> list[Signal]:
        from polymarket_client import PolymarketClient
        signals: list[Signal] = []

        for addr in self.addresses:
            try:
                current = PolymarketClient.get_address_positions(addr)
            except Exception:
                continue

            prev = self._last_positions.get(addr, [])
            prev_ids = {p.get("token_id", p.get("asset", "")) for p in prev}

            for pos in current:
                token_id = pos.get("token_id", pos.get("asset", ""))
                if token_id and token_id not in prev_ids:
                    size = float(pos.get("size", pos.get("amount", 0)))
                    if size > 0:
                        signals.append(Signal(
                            platform="polymarket",
                            market_id=token_id,
                            market_title=pos.get("title", pos.get("market", token_id)),
                            side="buy",
                            price=float(pos.get("avg_price", pos.get("price", 0.50))),
                            size=size,
                            leader_id=addr,
                            source_type="polymarket_address",
                        ))

            self._last_positions[addr] = current

        return signals


# ── Webhook Source ────────────────────────────────────────────────────

class WebhookSource(SignalSource):
    """
    Flask endpoint that receives trade signals via POST /signal.
    Runs in a background thread.

    Expected POST body:
    {
      "platform": "kalshi",
      "market_id": "TICKER-123",
      "side": "yes",
      "price": 0.65,
      "size": 10,
      "leader_id": "trader42"
    }
    """

    def __init__(self, port: int = 5088, secret: str = ""):
        self.port = port
        self.secret = secret
        self._queue: list[Signal] = []
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start the Flask webhook server in a daemon thread."""
        app = Flask("webhook_signal")

        @app.route("/signal", methods=["POST"])
        def receive_signal():
            if self.secret:
                token = request.headers.get("Authorization", "")
                if token != f"Bearer {self.secret}":
                    return jsonify({"error": "unauthorized"}), 401

            data = request.get_json(force=True)
            sig = Signal(
                platform=data.get("platform", "kalshi"),
                market_id=data["market_id"],
                market_title=data.get("market_title", data["market_id"]),
                side=data.get("side", "yes"),
                price=float(data.get("price", 0.50)),
                size=float(data.get("size", 1)),
                leader_id=data.get("leader_id", "webhook"),
                source_type="webhook",
            )
            with self._lock:
                self._queue.append(sig)
            return jsonify({"ok": True}), 200

        @app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "ok"}), 200

        self._thread = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=self.port, debug=False),
            daemon=True,
        )
        self._thread.start()

    def poll(self) -> list[Signal]:
        with self._lock:
            signals = list(self._queue)
            self._queue.clear()
        return signals
