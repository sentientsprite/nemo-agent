#!/usr/bin/env python3
"""
Kalshi API Client
Paper trading integration for prediction markets
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional

class KalshiClient:
    """Kalshi API client for prediction markets"""
    
    BASE_URL_DEMO = "https://demo-api.kalshi.com/trade-api/v2"
    BASE_URL_LIVE = "https://trading-api.kalshi.com/trade-api/v2"
    
    def __init__(self, credentials_path: str = "~/.nemo/credentials/kalshi.json"):
        """Initialize with credentials"""
        self.creds_path = os.path.expanduser(credentials_path)
        self.credentials = self._load_credentials()
        self.mode = self.credentials.get("mode", "demo")
        self.base_url = self.BASE_URL_DEMO if self.mode == "demo" else self.BASE_URL_LIVE
        self.session = requests.Session()
        
    def _load_credentials(self) -> Dict:
        """Load API credentials from file"""
        if not os.path.exists(self.creds_path):
            raise FileNotFoundError(f"Credentials not found: {self.creds_path}")
        with open(self.creds_path) as f:
            return json.load(f)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authenticated headers"""
        return {
            "Authorization": f"Bearer {self.credentials['api_key']}",
            "Content-Type": "application/json"
        }
    
    def get_balance(self) -> Dict:
        """Get account balance"""
        url = f"{self.base_url}/portfolio/balance"
        resp = self.session.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()
    
    def list_markets(
        self,
        status: str = "open",
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List available markets"""
        url = f"{self.base_url}/markets"
        params = {"status": status, "limit": limit}
        if category:
            params["category"] = category
        
        resp = self.session.get(url, headers=self._get_headers(), params=params)
        resp.raise_for_status()
        return resp.json().get("markets", [])
    
    def get_market(self, market_id: str) -> Dict:
        """Get specific market details"""
        url = f"{self.base_url}/markets/{market_id}"
        resp = self.session.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()
    
    def get_orderbook(self, market_id: str) -> Dict:
        """Get orderbook for a market"""
        url = f"{self.base_url}/markets/{market_id}/orderbook"
        resp = self.session.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()
    
    def place_order(
        self,
        market_id: str,
        side: str,  # 'yes' or 'no'
        amount: int,  # Number of contracts
        price: int,  # Price in cents (0-100)
        order_type: str = "limit"
    ) -> Dict:
        """Place an order"""
        if self.mode != "demo":
            raise PermissionError("Live trading requires explicit approval")
        
        url = f"{self.base_url}/portfolio/orders"
        payload = {
            "market_id": market_id,
            "side": side,
            "amount": amount,
            "price": price,
            "type": order_type
        }
        
        resp = self.session.post(url, headers=self._get_headers(), json=payload)
        resp.raise_for_status()
        
        # Log the trade
        self._log_trade({
            "timestamp": datetime.now().isoformat(),
            "market_id": market_id,
            "side": side,
            "amount": amount,
            "price": price,
            "mode": self.mode,
            "response": resp.json()
        })
        
        return resp.json()
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        url = f"{self.base_url}/portfolio/positions"
        resp = self.session.get(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json().get("positions", [])
    
    def _log_trade(self, trade_data: Dict):
        """Log trade to file"""
        log_dir = os.path.expanduser("~/.nemo/workspace/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "kalshi-trades.jsonl")
        
        with open(log_file, "a") as f:
            f.write(json.dumps(trade_data) + "\n")


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kalshi API Client")
    parser.add_argument("command", choices=["balance", "markets", "order", "positions"])
    parser.add_argument("--market-id", help="Market ID for orders")
    parser.add_argument("--side", choices=["yes", "no"], help="Order side")
    parser.add_argument("--amount", type=int, help="Number of contracts")
    parser.add_argument("--price", type=int, help="Price in cents (0-100)")
    parser.add_argument("--category", help="Filter markets by category")
    
    args = parser.parse_args()
    
    client = KalshiClient()
    
    if args.command == "balance":
        print(json.dumps(client.get_balance(), indent=2))
    elif args.command == "markets":
        markets = client.list_markets(category=args.category)
        for m in markets[:10]:
            print(f"{m['id']}: {m['title'][:60]}...")
    elif args.command == "positions":
        print(json.dumps(client.get_positions(), indent=2))
    elif args.command == "order":
        if not all([args.market_id, args.side, args.amount, args.price]):
            print("Error: --market-id, --side, --amount, --price required")
            return
        result = client.place_order(
            args.market_id, args.side, args.amount, args.price
        )
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
