"""
Kalshi API wrapper. Supports email/password login and API key auth.
Base URL: https://trading-api.kalshi.com/trade-api/v2
"""

import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

from config import KalshiConfig


class KalshiClient:
    def __init__(self, config: KalshiConfig):
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.member_id: Optional[str] = None

    # ── Auth ──────────────────────────────────────────────────────────

    def login(self) -> dict:
        """Authenticate via email/password. Sets bearer token."""
        if self.config.api_key:
            # API key auth — no login call needed, sign each request
            return {"method": "api_key"}

        resp = self._post("/login", json={
            "email": self.config.email,
            "password": self.config.password,
        }, auth=False)
        self.token = resp.get("token")
        self.member_id = resp.get("member_id")
        return resp

    def _headers(self, method: str = "GET", path: str = "") -> dict:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.api_key and self.config.api_secret:
            # HMAC API key signing
            ts = str(int(time.time()))
            msg = ts + method.upper() + path
            sig = hmac.new(
                self.config.api_secret.encode(),
                msg.encode(),
                hashlib.sha256,
            ).hexdigest()
            headers["KALSHI-ACCESS-KEY"] = self.config.api_key
            headers["KALSHI-ACCESS-SIGNATURE"] = sig
            headers["KALSHI-ACCESS-TIMESTAMP"] = ts
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ── HTTP helpers ──────────────────────────────────────────────────

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        r = self.session.get(url, headers=self._headers("GET", path), params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, json: Optional[dict] = None, auth: bool = True) -> Any:
        url = f"{self.base_url}{path}"
        hdrs = self._headers("POST", path) if auth else {"Content-Type": "application/json"}
        r = self.session.post(url, headers=hdrs, json=json, timeout=15)
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        r = self.session.delete(url, headers=self._headers("DELETE", path), timeout=15)
        r.raise_for_status()
        return r.json() if r.text else {}

    # ── Markets ───────────────────────────────────────────────────────

    def list_markets(
        self,
        limit: int = 100,
        status: str = "open",
        category: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> dict:
        """List markets with optional category filter."""
        params: dict = {"limit": limit, "status": status}
        if category:
            params["series_ticker"] = category
        if cursor:
            params["cursor"] = cursor
        return self._get("/markets", params=params)

    def get_market(self, ticker: str) -> dict:
        return self._get(f"/markets/{ticker}")

    def get_orderbook(self, ticker: str, depth: int = 10) -> dict:
        return self._get(f"/markets/{ticker}/orderbook", params={"depth": depth})

    def get_market_history(self, ticker: str, limit: int = 100) -> dict:
        return self._get(f"/markets/{ticker}/history", params={"limit": limit})

    # ── Events ────────────────────────────────────────────────────────

    def list_events(self, limit: int = 50, status: str = "open") -> dict:
        return self._get("/events", params={"limit": limit, "status": status})

    # ── Trading ───────────────────────────────────────────────────────

    def place_order(
        self,
        ticker: str,
        side: str,           # "yes" or "no"
        action: str = "buy", # "buy" or "sell"
        count: int = 1,
        order_type: str = "market",  # "market" or "limit"
        yes_price: Optional[int] = None,  # price in cents (1-99)
        no_price: Optional[int] = None,
        expiration_ts: Optional[int] = None,
    ) -> dict:
        """
        Place an order on Kalshi.
        - side: "yes" or "no"
        - yes_price/no_price: limit price in cents (1-99)
        - count: number of contracts
        """
        body: dict = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "count": count,
            "type": order_type,
        }
        if order_type == "limit":
            if yes_price is not None:
                body["yes_price"] = yes_price
            elif no_price is not None:
                body["no_price"] = no_price
        if expiration_ts:
            body["expiration_ts"] = expiration_ts
        return self._post("/portfolio/orders", json=body)

    def cancel_order(self, order_id: str) -> dict:
        return self._delete(f"/portfolio/orders/{order_id}")

    def get_orders(self, ticker: Optional[str] = None, status: Optional[str] = None) -> dict:
        params: dict = {}
        if ticker:
            params["ticker"] = ticker
        if status:
            params["status"] = status
        return self._get("/portfolio/orders", params=params)

    # ── Portfolio ─────────────────────────────────────────────────────

    def get_positions(self, status: str = "open") -> dict:
        return self._get("/portfolio/positions", params={"settlement_status": status})

    def get_balance(self) -> dict:
        return self._get("/portfolio/balance")

    def get_portfolio_value(self) -> float:
        """Return total portfolio value = cash balance + sum of position market values."""
        balance = self.get_balance()
        cash = balance.get("balance", 0) / 100.0  # cents to dollars
        positions = self.get_positions()
        pos_value = 0.0
        for pos in positions.get("market_positions", []):
            # position value ≈ contracts × current market price
            count = pos.get("position", 0)
            # We'd need market price for unrealized; use realized for now
            pos_value += pos.get("market_exposure", 0) / 100.0
        return cash + pos_value

    def get_fills(self, ticker: Optional[str] = None, limit: int = 100) -> dict:
        params: dict = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        return self._get("/portfolio/fills", params=params)

    # ── Leaderboard (undocumented/public) ─────────────────────────────

    def get_leaderboard(self, limit: int = 20) -> list[dict]:
        """
        Attempt to fetch Kalshi leaderboard. This endpoint may change.
        Falls back to empty list if unavailable.
        """
        try:
            resp = self._get("/users/leaderboard", params={"limit": limit})
            return resp.get("users", resp.get("rankings", []))
        except requests.HTTPError:
            return []
