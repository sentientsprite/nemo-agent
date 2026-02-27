"""
WebSocket Client for Real-Time Market Data
Replaces REST polling with <100ms latency connections

Supports:
- Polymarket CLOB WebSocket
- Coinbase Advanced Trade WebSocket
- Auto-reconnection with exponential backoff
- Heartbeat/ping for connection health
- Fallback to polling on WebSocket failure
"""

import asyncio
import json
import time
import logging
from typing import Optional, Callable, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# WebSocket library
try:
    import websockets
    from websockets.exceptions import ConnectionClosed, InvalidStatusCode
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️ websockets not installed. Install with: pip install websockets")


class ConnectionState(Enum):
    """WebSocket connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class LatencyMetrics:
    """Track connection latency metrics"""
    last_ping_time: float = 0.0
    last_pong_time: float = 0.0
    current_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    samples: list = field(default_factory=list)
    
    def record_ping(self):
        """Record ping sent"""
        self.last_ping_time = time.time()
    
    def record_pong(self):
        """Record pong received"""
        self.last_pong_time = time.time()
        latency = (self.last_pong_time - self.last_ping_time) * 1000
        self.current_latency_ms = latency
        self.samples.append(latency)
        
        # Keep last 100 samples
        if len(self.samples) > 100:
            self.samples = self.samples[-100:]
        
        # Update stats
        self.avg_latency_ms = sum(self.samples) / len(self.samples)
        self.max_latency_ms = max(self.max_latency_ms, latency)
        self.min_latency_ms = min(self.min_latency_ms, latency)


class WebSocketClient:
    """
    Generic WebSocket client with auto-reconnection
    """
    
    def __init__(
        self,
        name: str,
        url: str,
        on_message: Callable[[dict], None],
        on_connect: Optional[Callable[[], None]] = None,
        on_disconnect: Optional[Callable[[], None]] = None,
        ping_interval: int = 30,
        reconnect_delay: float = 1.0,
        max_reconnect_delay: float = 60.0
    ):
        """
        Initialize WebSocket client
        
        Args:
            name: Client name for logging
            url: WebSocket URL
            on_message: Callback for received messages
            on_connect: Callback on successful connection
            on_disconnect: Callback on disconnection
            ping_interval: Seconds between pings
            reconnect_delay: Initial reconnect delay (doubles each attempt)
            max_reconnect_delay: Maximum reconnect delay
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets package required. Install: pip install websockets")
        
        self.name = name
        self.url = url
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.ping_interval = ping_interval
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_delay = max_reconnect_delay
        
        self.state = ConnectionState.DISCONNECTED
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_attempts = 0
        self.metrics = LatencyMetrics()
        self._stop_event = asyncio.Event()
        self._ping_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        
        # Subscriptions to restore on reconnect
        self.subscriptions: Set[str] = set()
        
    async def connect(self):
        """Connect to WebSocket server"""
        self.state = ConnectionState.CONNECTING
        
        try:
            self.websocket = await websockets.connect(self.url)
            self.state = ConnectionState.CONNECTED
            self.reconnect_attempts = 0
            
            logging.info(f"✅ {self.name} connected to {self.url}")
            
            if self.on_connect:
                await self._safe_callback(self.on_connect)
            
            # Restore subscriptions
            await self._restore_subscriptions()
            
            # Start tasks
            self._ping_task = asyncio.create_task(self._ping_loop())
            self._receive_task = asyncio.create_task(self._receive_loop())
            
        except Exception as e:
            logging.error(f"❌ {self.name} connection failed: {e}")
            self.state = ConnectionState.ERROR
            await self._reconnect()
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self._stop_event.set()
        
        if self._ping_task:
            self._ping_task.cancel()
        if self._receive_task:
            self._receive_task.cancel()
        
        if self.websocket:
            await self.websocket.close()
        
        self.state = ConnectionState.DISCONNECTED
        logging.info(f"🔌 {self.name} disconnected")
    
    async def send(self, message: dict):
        """Send message to WebSocket"""
        if self.state != ConnectionState.CONNECTED or not self.websocket:
            logging.warning(f"⚠️ {self.name} not connected, cannot send")
            return
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logging.error(f"❌ {self.name} send failed: {e}")
            await self._reconnect()
    
    async def subscribe(self, channel: str, params: Optional[dict] = None):
        """Subscribe to a channel"""
        sub_id = f"{channel}:{json.dumps(params or {})}"
        self.subscriptions.add(sub_id)
        
        message = {
            "type": "subscribe",
            "channel": channel
        }
        if params:
            message.update(params)
        
        await self.send(message)
    
    async def unsubscribe(self, channel: str):
        """Unsubscribe from a channel"""
        await self.send({"type": "unsubscribe", "channel": channel})
        
        # Remove from subscriptions
        self.subscriptions = {s for s in self.subscriptions if not s.startswith(channel)}
    
    async def _receive_loop(self):
        """Main receive loop"""
        try:
            while not self._stop_event.is_set():
                if not self.websocket:
                    break
                
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=self.ping_interval * 2
                    )
                    
                    # Parse and handle message
                    data = json.loads(message)
                    
                    # Handle pong
                    if data.get("type") == "pong":
                        self.metrics.record_pong()
                        continue
                    
                    # Call user handler
                    await self._safe_callback(self.on_message, data)
                    
                except asyncio.TimeoutError:
                    logging.warning(f"⏱️ {self.name} receive timeout")
                    await self._reconnect()
                    break
                    
        except ConnectionClosed:
            logging.warning(f"🔌 {self.name} connection closed")
            await self._reconnect()
        except Exception as e:
            logging.error(f"❌ {self.name} receive error: {e}")
            await self._reconnect()
    
    async def _ping_loop(self):
        """Send periodic pings"""
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self.ping_interval)
                
                if self.websocket and self.state == ConnectionState.CONNECTED:
                    self.metrics.record_ping()
                    await self.send({"type": "ping"})
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"❌ {self.name} ping error: {e}")
    
    async def _reconnect(self):
        """Reconnect with exponential backoff"""
        if self.state == ConnectionState.RECONNECTING:
            return
        
        self.state = ConnectionState.RECONNECTING
        
        if self.on_disconnect:
            await self._safe_callback(self.on_disconnect)
        
        # Calculate delay
        delay = min(
            self.reconnect_delay * (2 ** self.reconnect_attempts),
            self.max_reconnect_delay
        )
        self.reconnect_attempts += 1
        
        logging.info(f"🔄 {self.name} reconnecting in {delay:.1f}s (attempt {self.reconnect_attempts})")
        
        await asyncio.sleep(delay)
        await self.connect()
    
    async def _restore_subscriptions(self):
        """Restore subscriptions after reconnect"""
        for sub_id in self.subscriptions:
            parts = sub_id.split(":", 1)
            channel = parts[0]
            params = json.loads(parts[1]) if len(parts) > 1 else None
            
            message = {"type": "subscribe", "channel": channel}
            if params:
                message.update(params)
            
            await self.send(message)
    
    async def _safe_callback(self, callback: Callable, *args):
        """Safely execute callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logging.error(f"❌ {self.name} callback error: {e}")
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "url": self.url,
            "reconnect_attempts": self.reconnect_attempts,
            "latency_ms": {
                "current": round(self.metrics.current_latency_ms, 2),
                "avg": round(self.metrics.avg_latency_ms, 2),
                "min": round(self.metrics.min_latency_ms, 2) if self.metrics.min_latency_ms != float('inf') else None,
                "max": round(self.metrics.max_latency_ms, 2)
            },
            "subscriptions": len(self.subscriptions)
        }


class PolymarketWebSocket(WebSocketClient):
    """
    Polymarket CLOB WebSocket client
    """
    
    WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws"
    
    def __init__(self, api_key: str, on_market_data: Callable[[dict], None]):
        super().__init__(
            name="Polymarket",
            url=self.WS_URL,
            on_message=self._handle_message,
            on_connect=self._on_connect
        )
        self.api_key = api_key
        self.on_market_data = on_market_data
        self.markets: Set[str] = set()
    
    async def subscribe_market(self, market_slug: str):
        """Subscribe to market updates"""
        self.markets.add(market_slug)
        await self.subscribe("market", {"market": market_slug})
    
    async def _on_connect(self):
        """Authenticate on connect"""
        await self.send({
            "type": "auth",
            "apiKey": self.api_key
        })
    
    async def _handle_message(self, data: dict):
        """Handle incoming market data"""
        msg_type = data.get("type")
        
        if msg_type == "book":
            # Order book update
            await self._safe_callback(self.on_market_data, {
                "type": "orderbook",
                "market": data.get("market"),
                "bids": data.get("bids", []),
                "asks": data.get("asks", []),
                "timestamp": time.time()
            })
            
        elif msg_type == "trade":
            # Trade execution
            await self._safe_callback(self.on_market_data, {
                "type": "trade",
                "market": data.get("market"),
                "price": data.get("price"),
                "size": data.get("size"),
                "side": data.get("side"),
                "timestamp": time.time()
            })


class CoinbaseWebSocket(WebSocketClient):
    """
    Coinbase Advanced Trade WebSocket client
    """
    
    WS_URL = "wss://advanced-trade-ws.coinbase.com"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        on_ticker: Callable[[dict], None]
    ):
        super().__init__(
            name="Coinbase",
            url=self.WS_URL,
            on_message=self._handle_message,
            on_connect=self._on_connect
        )
        self.api_key = api_key
        self.api_secret = api_secret
        self.on_ticker = on_ticker
        self.products: Set[str] = set()
    
    async def subscribe_ticker(self, product_id: str):
        """Subscribe to ticker updates"""
        self.products.add(product_id)
        await self.subscribe("ticker", {"product_ids": [product_id]})
    
    async def subscribe_level2(self, product_id: str):
        """Subscribe to Level 2 order book"""
        self.products.add(product_id)
        await self.subscribe("level2", {"product_ids": [product_id]})
    
    async def _on_connect(self):
        """Subscribe to channels on connect"""
        # Coinbase uses JWT auth, handled differently
        pass
    
    async def _handle_message(self, data: dict):
        """Handle incoming ticker data"""
        channel = data.get("channel")
        
        if channel == "ticker":
            events = data.get("events", [])
            for event in events:
                if event.get("type") == "update":
                    for ticker in event.get("tickers", []):
                        await self._safe_callback(self.on_ticker, {
                            "product_id": ticker.get("product_id"),
                            "price": float(ticker.get("price", 0)),
                            "volume_24h": float(ticker.get("volume_24_h", 0)),
                            "timestamp": time.time()
                        })


# Fallback polling adapter
class PollingFallback:
    """
    Fallback to REST polling if WebSocket fails
    """
    
    def __init__(
        self,
        poll_interval: float = 15.0,
        on_data: Optional[Callable[[dict], None]] = None
    ):
        self.poll_interval = poll_interval
        self.on_data = on_data
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
    
    async def start(self, poll_func: Callable[[], dict]):
        """Start polling"""
        self._task = asyncio.create_task(self._poll_loop(poll_func))
    
    async def stop(self):
        """Stop polling"""
        self._stop_event.set()
        if self._task:
            self._task.cancel()
    
    async def _poll_loop(self, poll_func: Callable[[], dict]):
        """Polling loop"""
        try:
            while not self._stop_event.is_set():
                try:
                    data = await poll_func()
                    if self.on_data:
                        await self._safe_callback(self.on_data, data)
                except Exception as e:
                    logging.error(f"Polling error: {e}")
                
                await asyncio.sleep(self.poll_interval)
        except asyncio.CancelledError:
            pass
    
    async def _safe_callback(self, callback: Callable, *args):
        """Safely execute callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logging.error(f"Callback error: {e}")


# Example usage
if __name__ == "__main__":
    print("🔌 WebSocket Client Demo\n")
    
    async def demo():
        # Mock handlers
        def on_message(msg):
            print(f"📨 Received: {msg.get('type')}")
        
        def on_connect():
            print("✅ Connected!")
        
        def on_disconnect():
            print("🔌 Disconnected")
        
        # Create client
        client = WebSocketClient(
            name="Demo",
            url="wss://echo.websocket.org/",
            on_message=on_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect
        )
        
        # Connect
        await client.connect()
        
        # Wait a bit
        await asyncio.sleep(5)
        
        # Show stats
        print(f"\nStats: {client.get_stats()}")
        
        # Disconnect
        await client.disconnect()
    
    # Run demo
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n👋 Demo ended")
