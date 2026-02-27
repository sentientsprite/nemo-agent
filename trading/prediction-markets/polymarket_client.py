"""
Polymarket CLOB wrapper using py-clob-client.
Auth via private key + API credentials.
Handles VPN/proxy scenarios with custom RPC configuration.
"""

import os
import requests
from typing import Any, Optional
from urllib.parse import urljoin

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import (
        ApiCreds,
        OrderArgs,
        OrderType,
    )
    from py_clob_client.order_builder.constants import BUY, SELL

    HAS_CLOB = True
except ImportError:
    HAS_CLOB = False

from config import PolymarketConfig, cfg


class PolymarketClient:
    """
    Thin wrapper around py-clob-client for the Polymarket CLOB.
    Designed for VPN deployment with safety checks.
    """

    CLOB_URL = "https://clob.polymarket.com"

    def __init__(self, config: PolymarketConfig):
        if not HAS_CLOB:
            raise ImportError("py-clob-client not installed. pip install py-clob-client")
        self.config = config
        self.client = self._build_client()

    def _build_client(self) -> "ClobClient":
        """Build CLOB client with proper credential handling."""
        creds = ApiCreds(
            api_key=self.config.api_key,
            api_secret=self.config.api_secret,
            api_passphrase=self.config.api_passphrase,
        ) if self.config.api_key else None

        # Use custom RPC if specified (for VPN/proxy scenarios)
        client_kwargs = {
            "key": self.config.private_key or None,
            "chain_id": self.config.chain_id,
            "creds": creds,
            "funder": self.config.funder or None,
        }
        
        # Add custom RPC URL if provided
        if self.config.rpc_url:
            client_kwargs["rpc_url"] = self.config.rpc_url

        client = ClobClient(self.CLOB_URL, **client_kwargs)

        # Derive API creds if we don't have them yet
        if not creds and self.config.private_key:
            try:
                client.set_api_creds(client.derive_api_key())
            except Exception as e:
                print(f"Warning: Could not derive API key: {e}")
                print("Operating in read-only mode")

        return client

    @staticmethod
    def check_connectivity(host: str = "clob.polymarket.com", timeout: int = 5) -> bool:
        """Check connectivity to Polymarket CLOB (for VPN verification)."""
        try:
            response = requests.get(f"https://{host}/health", timeout=timeout)
            return response.status_code == 200
        except Exception:
            # Try alternative endpoints
            try:
                response = requests.get(f"https://{host}/markets", timeout=timeout)
                return response.status_code == 200
            except Exception:
                return False

    # ── Markets ───────────────────────────────────────────────────────

    def get_markets(self, next_cursor: str = "", limit: int = 100) -> dict:
        """Fetch active markets from the CLOB."""
        return self.client.get_markets(next_cursor=next_cursor)

    def get_market(self, condition_id: str) -> dict:
        return self.client.get_market(condition_id)

    def get_orderbook(self, token_id: str) -> dict:
        return self.client.get_order_book(token_id)

    def get_simplified_markets(self) -> list[dict]:
        return self.client.get_simplified_markets()

    # ── Trading ───────────────────────────────────────────────────────

    def place_limit_order(
        self,
        token_id: str,
        side: str,       # "buy" or "sell"
        price: float,    # 0.01 - 0.99
        size: float,     # number of shares
        dry_run: bool = True,
    ) -> dict:
        """
        Place a limit order on the CLOB.
        Safety: respects max_trade_size_usd limit.
        """
        # Safety check: calculate order value
        order_value = price * size
        max_value = cfg.risk.max_trade_size_usd
        
        if order_value > max_value:
            raise ValueError(
                f"Order value ${order_value:.2f} exceeds max ${max_value:.2f}"
            )
        
        if dry_run or cfg.dry_run:
            print(f"[DRY RUN] Would place {side} order: {size} shares @ {price} = ${order_value:.2f}")
            return {"dry_run": True, "side": side, "price": price, "size": size}

        order_side = BUY if side.lower() == "buy" else SELL
        order_args = OrderArgs(
            price=price,
            size=size,
            side=order_side,
            token_id=token_id,
        )
        signed = self.client.create_order(order_args)
        return self.client.post_order(signed, OrderType.GTC)

    def cancel_order(self, order_id: str) -> dict:
        return self.client.cancel(order_id)

    def cancel_all(self) -> dict:
        return self.client.cancel_all()

    # ── Positions / Portfolio ─────────────────────────────────────────

    def get_positions(self) -> list[dict]:
        """Get current positions. Returns list of balances by token."""
        try:
            # py-clob-client ≥ 0.14
            return self.client.get_balances()
        except AttributeError:
            # Fallback: call REST directly
            try:
                return self.client.get_positions()
            except Exception:
                return []

    def get_open_orders(self) -> list[dict]:
        return self.client.get_orders()

    def get_trades(self, limit: int = 100) -> list[dict]:
        try:
            return self.client.get_trades(limit=limit)
        except Exception:
            return []
    
    def get_portfolio_value(self) -> float:
        """Calculate current portfolio value in USD."""
        positions = self.get_positions()
        total = 0.0
        for pos in positions:
            # Position value = shares * current price
            shares = float(pos.get("size", 0))
            price = float(pos.get("avg_price", 0))
            total += shares * price
        return total

    # ── Address monitoring (public, no auth needed) ───────────────────

    @staticmethod
    def get_address_positions(address: str) -> list[dict]:
        """
        Fetch positions for an arbitrary Polymarket address.
        Uses the public Polymarket profile API.
        """
        import requests
        url = f"https://polymarket.com/api/profile/{address}/positions"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            # Fallback: gamma-api
            try:
                url2 = f"https://gamma-api.polymarket.com/positions?user={address}"
                r2 = requests.get(url2, timeout=10)
                r2.raise_for_status()
                return r2.json()
            except Exception:
                return []
    
    @staticmethod
    def get_proxy_positions(proxy_address: str = "0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a") -> list[dict]:
        """Get positions for the proxy/delegated trading address."""
        return PolymarketClient.get_address_positions(proxy_address)


class SafetyMonitor:
    """Monitors trading activity for safety limit violations."""
    
    def __init__(self, client: PolymarketClient):
        self.client = client
        self.daily_pnl = 0.0
        self.max_daily_loss = cfg.risk.daily_loss_limit_usd
        self.stop_loss_pct = cfg.risk.stop_loss_pct
    
    def check_stop_loss(self, entry_value: float, current_value: float) -> bool:
        """Check if stop loss has been triggered."""
        if entry_value <= 0:
            return False
        loss_pct = (current_value - entry_value) / entry_value
        if loss_pct <= -self.stop_loss_pct:
            print(f"STOP LOSS TRIGGERED: Loss of {loss_pct*100:.1f}% exceeds limit of {self.stop_loss_pct*100:.1f}%")
            return True
        return False
    
    def check_daily_limit(self, pnl_change: float) -> bool:
        """Check if daily loss limit has been exceeded."""
        self.daily_pnl += pnl_change
        if self.daily_pnl <= -self.max_daily_loss:
            print(f"DAILY LOSS LIMIT REACHED: ${abs(self.daily_pnl):.2f} loss exceeds ${self.max_daily_loss:.2f} limit")
            return True
        return False
    
    def get_status(self) -> dict:
        """Get current safety status."""
        return {
            "daily_pnl": self.daily_pnl,
            "daily_limit": self.max_daily_loss,
            "stop_loss_pct": self.stop_loss_pct,
            "can_trade": self.daily_pnl > -self.max_daily_loss,
        }
