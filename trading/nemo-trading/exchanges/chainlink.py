"""
Chainlink BTC/USD Oracle Integration for NEMO Trading Bot
Uses Chainlink AggregatorV3Interface for decentralized price feeds
"""

import os
import json
import time
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Web3 for blockchain interaction
try:
    from web3 import Web3
    from web3.contract import Contract
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("⚠️ web3 not installed. Install with: pip install web3")

# Chainlink BTC/USD Aggregator on Polygon
CHAINLINK_BTC_USD_POLYGON = "0xc907E116054Ad103354f2D33Fd1d85D32C3F5ed0"

# ABI for AggregatorV3Interface (minimal)
AGGREGATOR_V3_ABI = json.loads("""[
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "description",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint80", "name": "_roundId", "type": "uint80"}],
        "name": "getRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]""")


@dataclass
class PriceData:
    """Standardized price data from oracle"""
    price: float
    timestamp: datetime
    round_id: int
    decimals: int
    source: str
    
    @property
    def age_seconds(self) -> float:
        """How old is this price data?"""
        return (datetime.utcnow() - self.timestamp).total_seconds()
    
    @property
    def is_stale(self, max_age_seconds: int = 3600) -> bool:
        """Check if price is stale (default: 1 hour)"""
        return self.age_seconds > max_age_seconds


class ChainlinkOracle:
    """
    Chainlink Price Feed Oracle Client
    Provides decentralized BTC/USD prices with staleness checks
    """
    
    def __init__(
        self,
        rpc_url: Optional[str] = None,
        aggregator_address: str = CHAINLINK_BTC_USD_POLYGON,
        max_price_age: int = 3600  # 1 hour default
    ):
        """
        Initialize Chainlink Oracle
        
        Args:
            rpc_url: Polygon RPC endpoint (defaults to public)
            aggregator_address: Chainlink aggregator contract address
            max_price_age: Maximum acceptable price age in seconds
        """
        if not WEB3_AVAILABLE:
            raise ImportError("web3 package required. Install: pip install web3")
        
        self.rpc_url = rpc_url or os.getenv("POLYGON_RPC", "https://polygon-rpc.com")
        self.aggregator_address = Web3.to_checksum_address(aggregator_address)
        self.max_price_age = max_price_age
        
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.contract: Contract = self.w3.eth.contract(
            address=self.aggregator_address,
            abi=AGGREGATOR_V3_ABI
        )
        
        # Cache for last fetched price
        self._last_price: Optional[PriceData] = None
        
    def get_latest_price(self) -> PriceData:
        """
        Fetch latest BTC/USD price from Chainlink
        
        Returns:
            PriceData with price, timestamp, and metadata
            
        Raises:
            ConnectionError: If RPC connection fails
            ValueError: If price data is invalid
        """
        try:
            # Fetch latest round data
            round_id, answer, started_at, updated_at, answered_in_round = \
                self.contract.functions.latestRoundData().call()
            
            # Get decimals for scaling
            decimals = self.contract.functions.decimals().call()
            
            # Convert to human-readable price
            price = answer / (10 ** decimals)
            
            # Convert timestamp
            timestamp = datetime.utcfromtimestamp(updated_at)
            
            price_data = PriceData(
                price=price,
                timestamp=timestamp,
                round_id=round_id,
                decimals=decimals,
                source="chainlink"
            )
            
            self._last_price = price_data
            
            # Log staleness warning
            if price_data.is_stale(self.max_price_age):
                print(f"⚠️ Chainlink price is stale: {price_data.age_seconds:.0f}s old")
            
            return price_data
            
        except Exception as e:
            raise ConnectionError(f"Failed to fetch Chainlink price: {e}")
    
    def get_historical_price(self, rounds_ago: int = 10) -> list[PriceData]:
        """
        Get historical prices for trend analysis
        
        Args:
            rounds_ago: How many rounds back to fetch
            
        Returns:
            List of PriceData objects
        """
        prices = []
        latest_round_id = self.contract.functions.latestRoundData().call()[0]
        
        for i in range(min(rounds_ago, int(latest_round_id))):
            try:
                round_id = latest_round_id - i
                data = self.contract.functions.getRoundData(round_id).call()
                
                decimals = self.contract.functions.decimals().call()
                price = data[1] / (10 ** decimals)
                timestamp = datetime.utcfromtimestamp(data[3])
                
                prices.append(PriceData(
                    price=price,
                    timestamp=timestamp,
                    round_id=round_id,
                    decimals=decimals,
                    source="chainlink"
                ))
            except Exception as e:
                print(f"⚠️ Failed to fetch round {round_id}: {e}")
                continue
        
        return prices
    
    def compare_with_coinbase(self, coinbase_price: float) -> dict:
        """
        Compare Chainlink oracle price with Coinbase exchange price
        Useful for arbitrage detection
        
        Args:
            coinbase_price: Current BTC/USD price from Coinbase
            
        Returns:
            Dict with both prices, spread, and arbitrage signal
        """
        chainlink_data = self.get_latest_price()
        chainlink_price = chainlink_data.price
        
        spread_pct = abs(chainlink_price - coinbase_price) / coinbase_price * 100
        
        # Arbitrage opportunity if spread > 0.5% and Chainlink not stale
        arbitrage_signal = (
            spread_pct > 0.5 and 
            not chainlink_data.is_stale(self.max_price_age)
        )
        
        return {
            "chainlink_price": chainlink_price,
            "chainlink_timestamp": chainlink_data.timestamp.isoformat(),
            "chainlink_stale": chainlink_data.is_stale(self.max_price_age),
            "coinbase_price": coinbase_price,
            "spread_usd": abs(chainlink_price - coinbase_price),
            "spread_pct": spread_pct,
            "arbitrage_signal": arbitrage_signal,
            "recommendation": "ARBITRAGE" if arbitrage_signal else "HOLD"
        }
    
    def health_check(self) -> dict:
        """Check oracle health and connectivity"""
        try:
            price_data = self.get_latest_price()
            return {
                "status": "healthy",
                "connected": True,
                "latest_price": price_data.price,
                "last_update": price_data.timestamp.isoformat(),
                "age_seconds": price_data.age_seconds,
                "stale": price_data.is_stale(self.max_price_age)
            }
        except Exception as e:
            return {
                "status": "error",
                "connected": False,
                "error": str(e)
            }


# Convenience function for quick price checks
def get_btc_price() -> float:
    """Quick BTC/USD price from Chainlink"""
    oracle = ChainlinkOracle()
    return oracle.get_latest_price().price


if __name__ == "__main__":
    # Test the oracle
    print("🔮 Testing Chainlink Oracle...")
    
    oracle = ChainlinkOracle()
    
    # Health check
    health = oracle.health_check()
    print(f"\nHealth Check: {health}")
    
    # Latest price
    price_data = oracle.get_latest_price()
    print(f"\n📊 BTC/USD: ${price_data.price:,.2f}")
    print(f"   Updated: {price_data.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Age: {price_data.age_seconds:.0f}s")
    print(f"   Stale: {price_data.is_stale()}")
    
    # Historical prices
    print("\n📈 Historical (last 5 rounds):")
    historical = oracle.get_historical_price(rounds_ago=5)
    for p in historical:
        print(f"   ${p.price:,.2f} @ {p.timestamp.strftime('%H:%M:%S')}")
