"""
Coinbase Advanced Trade API wrapper.
Supports both live (coinbase-advanced-py SDK) and dry-run (simulated) modes.
"""
import logging
import time
import uuid
from dataclasses import dataclass
from typing import List, Optional

from config import Config

log = logging.getLogger("exchange")


@dataclass
class Candle:
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Ticker:
    pair: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    timestamp: float


@dataclass
class OrderResult:
    order_id: str
    pair: str
    side: str
    price: float
    quantity: float
    quote_amount: float
    fee: float
    status: str
    dry_run: bool


class Exchange:
    """Unified exchange interface — live or simulated."""

    def __init__(self, config: Config):
        self.cfg = config
        self._client = None
        self._sim_balance_usdc = config.sim_starting_balance
        self._sim_balance_asset: dict[str, float] = {}
        self._last_prices: dict[str, float] = {}

        if not config.dry_run:
            self._init_client()

    def _init_client(self):
        try:
            from coinbase.rest import RESTClient
            self._client = RESTClient(api_key=self.cfg.api_key, api_secret=self.cfg.api_secret)
            log.info("Coinbase REST client initialized")
        except ImportError:
            log.error("coinbase-advanced-py not installed. Install: pip install coinbase-advanced-py")
            raise
        except Exception as e:
            log.error(f"Failed to init Coinbase client: {e}")
            raise

    # ── Market Data ──────────────────────────────────────────────

    def get_candles(self, pair: str, granularity: str = "FIVE_MINUTE", limit: int = 100) -> List[Candle]:
        if self.cfg.dry_run:
            return self._sim_candles(pair, granularity, limit)

        try:
            end = int(time.time())
            gran_secs = {
                "ONE_MINUTE": 60, "FIVE_MINUTE": 300, "FIFTEEN_MINUTE": 900,
                "THIRTY_MINUTE": 1800, "ONE_HOUR": 3600, "TWO_HOUR": 7200,
                "SIX_HOUR": 21600, "ONE_DAY": 86400,
            }
            interval = gran_secs.get(granularity, 300)
            start = end - interval * limit

            resp = self._client.get_candles(
                product_id=pair, start=str(start), end=str(end), granularity=granularity
            )
            candles = []
            for c in resp.get("candles", []):
                candles.append(Candle(
                    timestamp=float(c["start"]),
                    open=float(c["open"]), high=float(c["high"]),
                    low=float(c["low"]), close=float(c["close"]),
                    volume=float(c["volume"]),
                ))
            candles.sort(key=lambda x: x.timestamp)
            return candles
        except Exception as e:
            log.error(f"Error fetching candles for {pair}: {e}")
            return []

    def get_ticker(self, pair: str) -> Optional[Ticker]:
        if self.cfg.dry_run:
            return self._sim_ticker(pair)

        try:
            resp = self._client.get_product(product_id=pair)
            price = float(resp.get("price", 0))
            self._last_prices[pair] = price
            return Ticker(
                pair=pair, price=price,
                bid=float(resp.get("bid", price)),
                ask=float(resp.get("ask", price)),
                volume_24h=float(resp.get("volume_24h", 0)),
                timestamp=time.time(),
            )
        except Exception as e:
            log.error(f"Error fetching ticker for {pair}: {e}")
            return None

    # ── Account ──────────────────────────────────────────────────

    def get_usdc_balance(self) -> float:
        if self.cfg.dry_run:
            return self._sim_balance_usdc

        try:
            accounts = self._client.get_accounts()
            for acct in accounts.get("accounts", []):
                if acct.get("currency") == "USDC":
                    return float(acct["available_balance"]["value"])
            return 0.0
        except Exception as e:
            log.error(f"Error fetching balance: {e}")
            return 0.0

    def get_asset_balance(self, asset: str) -> float:
        if self.cfg.dry_run:
            return self._sim_balance_asset.get(asset, 0.0)

        try:
            accounts = self._client.get_accounts()
            for acct in accounts.get("accounts", []):
                if acct.get("currency") == asset:
                    return float(acct["available_balance"]["value"])
            return 0.0
        except Exception as e:
            log.error(f"Error fetching {asset} balance: {e}")
            return 0.0

    # ── Orders ───────────────────────────────────────────────────

    def market_buy(self, pair: str, quote_size: float) -> OrderResult:
        if self.cfg.dry_run:
            return self._sim_market_buy(pair, quote_size)

        try:
            oid = str(uuid.uuid4())
            resp = self._client.create_order(
                client_order_id=oid, product_id=pair, side="BUY",
                order_configuration={"market_market_ioc": {"quote_size": str(round(quote_size, 2))}},
            )
            order_id = resp.get("order_id", oid)
            time.sleep(0.5)
            fill = self._get_fill(order_id, pair)
            return fill if fill else OrderResult(
                order_id=order_id, pair=pair, side="BUY", price=0, quantity=0,
                quote_amount=quote_size, fee=0, status="PENDING", dry_run=False,
            )
        except Exception as e:
            log.error(f"Market buy failed: {e}")
            return OrderResult(
                order_id="", pair=pair, side="BUY", price=0, quantity=0,
                quote_amount=quote_size, fee=0, status="FAILED", dry_run=False,
            )

    def market_sell(self, pair: str, base_size: float) -> OrderResult:
        if self.cfg.dry_run:
            return self._sim_market_sell(pair, base_size)

        try:
            oid = str(uuid.uuid4())
            resp = self._client.create_order(
                client_order_id=oid, product_id=pair, side="SELL",
                order_configuration={"market_market_ioc": {"base_size": str(round(base_size, 8))}},
            )
            order_id = resp.get("order_id", oid)
            time.sleep(0.5)
            fill = self._get_fill(order_id, pair)
            return fill if fill else OrderResult(
                order_id=order_id, pair=pair, side="SELL", price=0, quantity=base_size,
                quote_amount=0, fee=0, status="PENDING", dry_run=False,
            )
        except Exception as e:
            log.error(f"Market sell failed: {e}")
            return OrderResult(
                order_id="", pair=pair, side="SELL", price=0, quantity=base_size,
                quote_amount=0, fee=0, status="FAILED", dry_run=False,
            )

    def _get_fill(self, order_id: str, pair: str) -> Optional[OrderResult]:
        try:
            order = self._client.get_order(order_id=order_id)
            return OrderResult(
                order_id=order_id, pair=pair,
                side=order.get("side", "BUY"),
                price=float(order.get("average_filled_price", 0)),
                quantity=float(order.get("filled_size", 0)),
                quote_amount=float(order.get("filled_value", 0)),
                fee=float(order.get("total_fees", 0)),
                status=order.get("status", "UNKNOWN"), dry_run=False,
            )
        except Exception as e:
            log.warning(f"Could not fetch fill for {order_id}: {e}")
            return None

    # ── Simulation ───────────────────────────────────────────────

    def _sim_candles(self, pair: str, granularity: str, limit: int) -> List[Candle]:
        import random
        gran_secs = {
            "ONE_MINUTE": 60, "FIVE_MINUTE": 300, "FIFTEEN_MINUTE": 900,
            "THIRTY_MINUTE": 1800, "ONE_HOUR": 3600,
        }
        interval = gran_secs.get(granularity, 300)
        base_prices = {"BTC-USDC": 97000.0, "ETH-USDC": 3400.0}
        base = self._last_prices.get(pair, base_prices.get(pair, 1000.0))

        candles = []
        price = base * (1 + random.uniform(-0.02, 0.02))
        now = time.time()
        start_time = now - interval * limit

        for i in range(limit):
            ts = start_time + i * interval
            change_pct = random.gauss(0, 0.003)
            o = price
            c = o * (1 + change_pct)
            h = max(o, c) * (1 + abs(random.gauss(0, 0.001)))
            l_val = min(o, c) * (1 - abs(random.gauss(0, 0.001)))
            v = random.uniform(50, 500) if "BTC" in pair else random.uniform(500, 5000)
            candles.append(Candle(timestamp=ts, open=round(o, 2), high=round(h, 2),
                                  low=round(l_val, 2), close=round(c, 2), volume=round(v, 2)))
            price = c

        self._last_prices[pair] = price
        return candles

    def _sim_ticker(self, pair: str) -> Ticker:
        base_prices = {"BTC-USDC": 97000.0, "ETH-USDC": 3400.0}
        price = self._last_prices.get(pair, base_prices.get(pair, 1000.0))
        spread = price * 0.0002
        return Ticker(pair=pair, price=price, bid=price - spread, ask=price + spread,
                      volume_24h=10000.0, timestamp=time.time())

    def _sim_market_buy(self, pair: str, quote_size: float) -> OrderResult:
        ticker = self._sim_ticker(pair)
        slipped = ticker.ask * (1 + self.cfg.sim_slippage_pct)
        fee = quote_size * self.cfg.sim_fee_pct
        net_quote = quote_size - fee
        qty = net_quote / slipped

        asset = pair.split("-")[0]
        self._sim_balance_usdc -= quote_size
        self._sim_balance_asset[asset] = self._sim_balance_asset.get(asset, 0) + qty
        self._last_prices[pair] = slipped

        log.info(f"[SIM] BUY {qty:.6f} {asset} @ ${slipped:.2f} (${quote_size:.2f} USDC, fee=${fee:.2f})")
        return OrderResult(
            order_id=f"sim-{uuid.uuid4().hex[:8]}", pair=pair, side="BUY",
            price=slipped, quantity=qty, quote_amount=quote_size,
            fee=fee, status="FILLED", dry_run=True,
        )

    def _sim_market_sell(self, pair: str, base_size: float) -> OrderResult:
        ticker = self._sim_ticker(pair)
        slipped = ticker.bid * (1 - self.cfg.sim_slippage_pct)
        gross = base_size * slipped
        fee = gross * self.cfg.sim_fee_pct
        net = gross - fee

        asset = pair.split("-")[0]
        self._sim_balance_asset[asset] = self._sim_balance_asset.get(asset, 0) - base_size
        self._sim_balance_usdc += net
        self._last_prices[pair] = slipped

        log.info(f"[SIM] SELL {base_size:.6f} {asset} @ ${slipped:.2f} (+${net:.2f} USDC, fee=${fee:.2f})")
        return OrderResult(
            order_id=f"sim-{uuid.uuid4().hex[:8]}", pair=pair, side="SELL",
            price=slipped, quantity=base_size, quote_amount=net,
            fee=fee, status="FILLED", dry_run=True,
        )
