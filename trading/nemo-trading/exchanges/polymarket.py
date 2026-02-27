"""
Polymarket CLOB Exchange Interface
"""
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import ApiCreds, OrderArgs
    POLYMARKET_SDK = True
except ImportError:
    POLYMARKET_SDK = False
    logging.warning("py-clob-client not installed. Using mock mode.")

log = logging.getLogger(__name__)

@dataclass
class Market:
    id: str
    slug: str
    question: str
    yes_token: str
    no_token: str
    expiration: datetime

@dataclass
class OrderBook:
    market_id: str
    yes_bids: List[tuple]  # (price, size)
    yes_asks: List[tuple]
    no_bids: List[tuple]
    no_asks: List[tuple]

@dataclass
class OrderResult:
    order_id: str
    status: str
    price: float
    size: float
    side: str  # "YES" | "NO"
    filled: bool

class PolymarketExchange:
    """Polymarket CLOB exchange interface."""
    
    name = "Polymarket"
    
    def __init__(self, private_key: str, funder_address: str, 
                 clob_host: str = "https://clob.polymarket.com",
                 chain_id: int = 137, dry_run: bool = True):
        self.private_key = private_key
        self.funder_address = funder_address
        self.clob_host = clob_host
        self.chain_id = chain_id
        self.dry_run = dry_run
        self.client = None
        
        if not dry_run and POLYMARKET_SDK and private_key:
            # Initialize real client
            try:
                self.client = ClobClient(
                    host=clob_host,
                    key=private_key,
                    chain_id=chain_id,
                    funder=funder_address
                )
                log.info("Polymarket client initialized")
            except Exception as e:
                log.error(f"Failed to initialize Polymarket client: {e}")
        elif dry_run:
            log.info("Polymarket exchange in DRY-RUN mode")
            self._simulated_positions = {}
    
    def get_markets(self, slug_prefix: str = "btc-updown") -> List[Market]:
        """Get active markets matching slug prefix."""
        if self.dry_run:
            # Return simulated BTC 5-min markets
            return [
                Market(
                    id=f"btc-updown-5m-{int(datetime.now().timestamp())}",
                    slug=f"{slug_prefix}-5m",
                    question="Will BTC go up in 5 minutes?",
                    yes_token="yes_token_123",
                    no_token="no_token_456",
                    expiration=datetime.now()
                )
            ]
        return []
    
    def get_order_book(self, market_id: str, token_id: str) -> Optional[OrderBook]:
        """Get order book for specific token."""
        if self.dry_run:
            # Simulate order book with realistic spread
            import random
            mid = 0.55  # 55% probability
            spread = 0.02
            
            return OrderBook(
                market_id=market_id,
                yes_bids=[(mid - spread, 1000), (mid - spread*2, 2000)],
                yes_asks=[(mid + spread, 1000), (mid + spread*2, 2000)],
                no_bids=[(1 - mid - spread, 1000)],
                no_asks=[(1 - mid + spread, 1000)]
            )
        return None
    
    def calculate_crowd_ratio(self, order_book: OrderBook) -> tuple[float, str]:
        """Calculate YES/NO volume ratio to detect crowd consensus."""
        yes_volume = sum(size for _, size in order_book.yes_bids + order_book.yes_asks)
        no_volume = sum(size for _, size in order_book.no_bids + order_book.no_asks)
        
        total = yes_volume + no_volume
        if total == 0:
            return 0.5, "balanced"
        
        yes_ratio = yes_volume / total
        
        if yes_ratio > 0.80:
            return yes_ratio, "heavy_yes"
        elif yes_ratio < 0.20:
            return yes_ratio, "heavy_no"
        else:
            return yes_ratio, "balanced"
    
    def place_order(self, market_id: str, token_id: str, side: str, 
                    size: float, price: float, order_type: str = "market") -> OrderResult:
        """Place order on CLOB."""
        if self.dry_run:
            import random
            
            # Simulate fill
            fill_price = price if order_type == "limit" else price * (1 + random.gauss(0, 0.01))
            fee = size * 0.0315 if order_type == "market" else 0  # 3.15% taker fee
            
            log.info(f"[DRY-RUN] {order_type.upper()} {side} {size} @ ${fill_price:.3f} "
                    f"(fee=${fee:.2f})")
            
            return OrderResult(
                order_id=f"dry-{datetime.now().timestamp()}",
                status="FILLED",
                price=fill_price,
                size=size,
                side=side,
                filled=True
            )
        
        return OrderResult("", "FAILED", 0, 0, side, False)
    
    def get_positions(self) -> Dict[str, dict]:
        """Get current positions."""
        if self.dry_run:
            return self._simulated_positions
        return {}
    
    def get_balance(self) -> float:
        """Get USDC balance."""
        if self.dry_run:
            return 500.0  # Simulated starting balance
        return 0.0
