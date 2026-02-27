"""
Polymarket Crowd Fade Strategy
Bet against 80%+ consensus
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from threading import Thread, Lock
from config import CrowdFadeConfig
from exchanges.polymarket import PolymarketExchange, OrderBook
from utils.risk import RiskManager, Position

log = logging.getLogger(__name__)

@dataclass
class CrowdReading:
    """Snapshot of crowd sentiment."""
    timestamp: datetime
    yes_ratio: float  # 0.0 to 1.0
    no_ratio: float
    consensus: str  # "heavy_yes" | "heavy_no" | "balanced"
    yes_volume: float
    no_volume: float

@dataclass
class CrowdSignal:
    """Confirmed fade signal."""
    side: str  # "YES" | "NO" - the side to bet ON (fading the crowd)
    confidence: float
    reason: str
    reading: CrowdReading
    confirmed_at: datetime

class CrowdDetector:
    """
    Background thread that monitors order books for crowd extremes.
    """
    
    def __init__(self, exchange: PolymarketExchange, config: CrowdFadeConfig):
        self.exchange = exchange
        self.config = config
        self.readings: Dict[str, List[CrowdReading]] = {}
        self.latest_reading: Dict[str, CrowdReading] = {}
        self.lock = Lock()
        self.running = False
        self.thread: Optional[Thread] = None
    
    def start(self, market_id: str, token_id: str):
        """Start background polling."""
        self.running = True
        self.thread = Thread(target=self._poll_loop, args=(market_id, token_id), daemon=True)
        self.thread.start()
        log.info(f"Crowd detector started for {market_id}")
    
    def stop(self):
        """Stop background polling."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        log.info("Crowd detector stopped")
    
    def _poll_loop(self, market_id: str, token_id: str):
        """Background polling thread."""
        while self.running:
            try:
                order_book = self.exchange.get_order_book(market_id, token_id)
                if order_book:
                    self._process_reading(market_id, order_book)
                time.sleep(self.config.poll_interval)
            except Exception as e:
                log.error(f"Crowd detector error: {e}")
                time.sleep(self.config.poll_interval)
    
    def _process_reading(self, market_id: str, order_book: OrderBook):
        """Process order book into crowd reading."""
        ratio, consensus = self.exchange.calculate_crowd_ratio(order_book)
        
        yes_volume = sum(size for _, size in order_book.yes_bids + order_book.yes_asks)
        no_volume = sum(size for _, size in order_book.no_bids + order_book.no_asks)
        
        reading = CrowdReading(
            timestamp=datetime.now(),
            yes_ratio=ratio,
            no_ratio=1 - ratio,
            consensus=consensus,
            yes_volume=yes_volume,
            no_volume=no_volume
        )
        
        with self.lock:
            if market_id not in self.readings:
                self.readings[market_id] = []
            self.readings[market_id].append(reading)
            self.latest_reading[market_id] = reading
            
            # Keep last 100 readings
            self.readings[market_id] = self.readings[market_id][-100:]
    
    def get_latest(self, market_id: str) -> Optional[CrowdReading]:
        """Get latest crowd reading."""
        with self.lock:
            return self.latest_reading.get(market_id)
    
    def get_history(self, market_id: str) -> List[CrowdReading]:
        """Get reading history."""
        with self.lock:
            return self.readings.get(market_id, []).copy()

class CrowdFadeStrategy:
    """
    Bet against the crowd when consensus exceeds 80%.
    Crowd is wrong ~60% of the time at extremes.
    """
    
    def __init__(self, config: CrowdFadeConfig, exchange: PolymarketExchange, risk: RiskManager):
        self.config = config
        self.exchange = exchange
        self.risk = risk
        self.detector: Optional[CrowdDetector] = None
        self.pending_confirmation: Dict[str, CrowdReading] = {}  # market_id -> reading awaiting confirmation
        self.confirmed_signals: Dict[str, CrowdSignal] = {}  # market_id -> confirmed signal
        self.round_start_time: Optional[datetime] = None
        
        if not config.enabled:
            log.warning("Crowd fade strategy disabled")
    
    def set_round(self, start_time: datetime):
        """Called at start of each new round."""
        self.round_start_time = start_time
        self.pending_confirmation.clear()
        self.confirmed_signals.clear()
        
        # Start detector if not running
        if self.detector and self.config.enabled:
            # Detector should be started per-market
            pass
    
    def start_detector(self, market_id: str, yes_token: str):
        """Start crowd detection for a market."""
        if self.config.enabled and not self.detector:
            self.detector = CrowdDetector(self.exchange, self.config)
            self.detector.start(market_id, yes_token)
    
    def stop_detector(self):
        """Stop crowd detection."""
        if self.detector:
            self.detector.stop()
            self.detector = None
    
    def seconds_elapsed(self) -> float:
        """Get seconds elapsed in current round."""
        if not self.round_start_time:
            return 0
        return (datetime.now() - self.round_start_time).total_seconds()
    
    def seconds_remaining(self) -> float:
        """Get seconds remaining in 5-min round."""
        return 300 - self.seconds_elapsed()
    
    def evaluate(self, market_id: str) -> Optional[CrowdSignal]:
        """
        Evaluate crowd fade opportunity.
        
        Returns confirmed signal or None.
        """
        if not self.config.enabled or not self.detector:
            return None
        
        elapsed = self.seconds_elapsed()
        remaining = self.seconds_remaining()
        
        # Check if in entry window
        if not (self.config.entry_window_end <= remaining <= self.config.entry_window_start):
            return None
        
        # Get latest reading
        reading = self.detector.get_latest(market_id)
        if not reading:
            return None
        
        # Check for extreme consensus
        if reading.consensus not in ["heavy_yes", "heavy_no"]:
            return None
        
        # Check if we already have a confirmed signal
        if market_id in self.confirmed_signals:
            return self.confirmed_signals[market_id]
        
        # Check if we're awaiting confirmation
        if market_id in self.pending_confirmation:
            pending = self.pending_confirmation[market_id]
            
            # Check if confirmation period has elapsed
            elapsed_since = (datetime.now() - pending.timestamp).total_seconds()
            if elapsed_since >= self.config.confirmation_seconds:
                # Get current reading
                current = self.detector.get_latest(market_id)
                if current and current.consensus == pending.consensus:
                    # Confirmed! Create signal
                    fade_side = "NO" if pending.consensus == "heavy_yes" else "YES"
                    confidence = max(pending.yes_ratio, pending.no_ratio)
                    
                    signal = CrowdSignal(
                        side=fade_side,
                        confidence=confidence,
                        reason=f"Fading {pending.consensus} consensus ({confidence:.1%})",
                        reading=pending,
                        confirmed_at=datetime.now()
                    )
                    
                    self.confirmed_signals[market_id] = signal
                    del self.pending_confirmation[market_id]
                    
                    log.info(f"CROWD FADE CONFIRMED: {fade_side} | {signal.reason}")
                    return signal
                else:
                    # Consensus changed, cancel
                    del self.pending_confirmation[market_id]
                    log.info("Crowd consensus changed, canceling pending signal")
        else:
            # New extreme detected, start confirmation
            self.pending_confirmation[market_id] = reading
            log.info(f"Crowd extreme detected: {reading.consensus} ({max(reading.yes_ratio, reading.no_ratio):.1%}) - awaiting confirmation")
        
        return None
    
    def execute(self, market_id: str, yes_token: str, no_token: str, signal: CrowdSignal) -> bool:
        """Execute crowd fade trade."""
        # Check risk
        can_trade, reason = self.risk.can_trade(market_id, self.config.entry_size)
        if not can_trade:
            log.warning(f"Trade blocked: {reason}")
            return False
        
        # Select token
        token_id = yes_token if signal.side == "YES" else no_token
        
        # Execute
        result = self.exchange.place_order(
            market_id=market_id,
            token_id=token_id,
            side=signal.side,
            size=self.config.entry_size,
            price=0,  # Market order
            order_type="market"
        )
        
        if result.filled:
            position = Position(
                symbol=market_id,
                side=signal.side,
                entry_price=result.price,
                quantity=result.size,
                entry_time=datetime.now(),
                stop_price=None,  # Hold to settlement
                strategy="crowd_fade"
            )
            
            if self.risk.open_position(position):
                log.info(f"Crowd fade entry: {signal.side} {result.size} @ {result.price}")
                return True
        
        return False
    
    def run(self, market_id: str, yes_token: str, no_token: str):
        """Main strategy loop - call periodically."""
        # Start detector if needed
        self.start_detector(market_id, yes_token)
        
        # Evaluate for signal
        signal = self.evaluate(market_id)
        if signal:
            self.execute(market_id, yes_token, no_token, signal)
        
        # No exit logic - hold to settlement as per config
