"""
Order execution module for Poly-Bot.
Handles order placement, monitoring, and P&L tracking.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable

from config import (
    ExecutionConfig,
    LoggingConfig,
    StrategyState,
    SnipeMakerConfig,
    ROUND_DURATION,
)

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"

class OrderSide(Enum):
    """Order sides."""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class Order:
    """Order representation."""
    id: str
    side: OrderSide
    order_type: OrderType
    size: float
    price: Optional[float] = None
    limit_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_size: float = 0.0
    avg_fill_price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionResult:
    """Result of order execution."""
    success: bool
    order: Optional[Order]
    pnl: float = 0.0
    fees: float = 0.0
    message: str = ""

class ExchangeInterface(ABC):
    """Abstract interface for exchange operations."""
    
    @abstractmethod
    def place_market_order(self, side: OrderSide, size: float) -> Order:
        pass
    
    @abstractmethod
    def place_limit_order(self, side: OrderSide, size: float, price: float) -> Order:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus:
        pass
    
    @abstractmethod
    def get_position_value(self, side: str) -> float:
        pass

class SimulatedExchange(ExchangeInterface):
    """
    Simulated exchange for dry-run mode.
    Simulates fills with some slippage and latency.
    """
    
    def __init__(self):
        self.orders = {}
        self.order_counter = 0
        self.current_yes_price = 0.50
        self.current_no_price = 0.50
        self.slippage = 0.001  # 0.1% slippage
        logger.info("[DRY RUN] SimulatedExchange initialized")
    
    def set_market_prices(self, yes_price: float, no_price: float):
        """Update simulated market prices."""
        self.current_yes_price = yes_price
        self.current_no_price = no_price
    
    def _generate_order_id(self) -> str:
        self.order_counter += 1
        return f"sim_{int(time.time())}_{self.order_counter}"
    
    def place_market_order(self, side: OrderSide, size: float) -> Order:
        order_id = self._generate_order_id()
        
        # Simulate slippage
        if side == OrderSide.BUY:
            fill_price = self.current_yes_price * (1 + self.slippage)
        else:
            fill_price = self.current_no_price * (1 - self.slippage)
        
        order = Order(
            id=order_id,
            side=side,
            order_type=OrderType.MARKET,
            size=size,
            price=fill_price,
            status=OrderStatus.FILLED,
            filled_size=size,
            avg_fill_price=fill_price,
        )
        
        self.orders[order_id] = order
        logger.info(f"[DRY RUN] Market order placed: {side.value} ${size:.2f} @ {fill_price:.3f}")
        
        return order
    
    def place_limit_order(self, side: OrderSide, size: float, price: float) -> Order:
        order_id = self._generate_order_id()
        
        order = Order(
            id=order_id,
            side=side,
            order_type=OrderType.LIMIT,
            size=size,
            limit_price=price,
            status=OrderStatus.PENDING,
        )
        
        self.orders[order_id] = order
        logger.info(f"[DRY RUN] Limit order placed: {side.value} ${size:.2f} @ {price:.3f}")
        
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            logger.info(f"[DRY RUN] Order cancelled: {order_id}")
            return True
        return False
    
    def get_order_status(self, order_id: str) -> OrderStatus:
        if order_id in self.orders:
            return self.orders[order_id].status
        return OrderStatus.FAILED
    
    def get_position_value(self, side: str) -> float:
        """Get current position value based on market prices."""
        if side.lower() == "yes":
            return self.current_yes_price
        return self.current_no_price
    
    def try_fill_limit_order(self, order_id: str) -> bool:
        """Simulate limit order fill check."""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status != OrderStatus.PENDING:
            return False
        
        # Check if limit price is hit
        if order.side == OrderSide.SELL:
            # For sell, fill if market price >= limit price
            if self.current_yes_price >= order.limit_price:
                order.status = OrderStatus.FILLED
                order.filled_size = order.size
                order.avg_fill_price = order.limit_price
                logger.info(f"[DRY RUN] Limit order filled: {order_id} @ {order.limit_price:.3f}")
                return True
        
        return False

class Executor:
    """
    Order executor with support for:
    - Market orders (for snipe entry)
    - Limit orders (for maker exit)
    - P&L tracking
    """
    
    def __init__(self, state: StrategyState, exchange: Optional[ExchangeInterface] = None):
        self.state = state
        self.exchange = exchange or SimulatedExchange()
        self.config = ExecutionConfig
        self.logger = logging.getLogger("Executor")
        
        # Track open orders
        self.open_orders: Dict[str, Order] = {}
        self.current_position_order: Optional[Order] = None
    
    def _calculate_fees(self, order: Order) -> float:
        """Calculate fees for an order."""
        if order.order_type == OrderType.MARKET:
            return order.size * self.config.TAKER_FEE
        else:
            # Maker rebate (negative fee)
            return order.size * self.config.MAKER_FEE
    
    def _log_pnl(self, pnl: float, is_snipe: bool = False):
        """Log P&L separately for snipe vs baseline."""
        if not LoggingConfig.TRACK_PNL_SEPARATELY:
            return
        
        log_file = (
            LoggingConfig.SNIPE_PNL_LOG if is_snipe else LoggingConfig.BASELINE_PNL_LOG
        )
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "round": self.state.current_round,
            "pnl": pnl,
            "type": "snipe" if is_snipe else "baseline",
            "cumulative_pnl": self.state.snipe_pnl if is_snipe else self.state.baseline_pnl,
        }
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to log P&L: {e}")
    
    def enter_position(
        self,
        side: str,
        size: float,
        is_snipe: bool = False,
        reason: str = ""
    ) -> ExecutionResult:
        """
        Enter a position.
        Uses market order for snipe entries.
        """
        if self.state.has_position:
            return ExecutionResult(
                success=False,
                order=None,
                message="Already have position"
            )
        
        # Determine order type
        if is_snipe and self.config.USE_MARKET_ORDERS_FOR_SNIPE:
            order_type = OrderType.MARKET
            order_side = OrderSide.BUY if side == "YES" else OrderSide.BUY
        else:
            order_type = OrderType.MARKET
            order_side = OrderSide.BUY
        
        # Place order (with retries)
        order = None
        for attempt in range(self.config.MAX_ORDER_RETRIES):
            try:
                if order_type == OrderType.MARKET:
                    order = self.exchange.place_market_order(order_side, size)
                break
            except Exception as e:
                self.logger.warning(f"Order attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.ORDER_RETRY_DELAY)
        
        if not order:
            return ExecutionResult(
                success=False,
                order=None,
                message="Failed to place order after retries"
            )
        
        # Update state
        self.state.has_position = True
        self.state.position_side = side
        self.state.position_size = size
        self.state.entry_price = order.avg_fill_price
        self.current_position_order = order
        
        if is_snipe:
            self.state.snipe_taken_this_round = True
            self.state.last_snipe_round = self.state.current_round
            self.state.snipe_count_today += 1
        
        fees = self._calculate_fees(order)
        
        self.logger.info(
            f"Position entered: {side} ${size:.2f} @ {order.avg_fill_price:.3f} "
            f"(fees: ${fees:.3f}, snipe: {is_snipe})"
        )
        
        return ExecutionResult(
            success=True,
            order=order,
            fees=fees,
            message=f"Entered {side} position: {reason}"
        )
    
    def exit_position(
        self,
        use_maker_exit: bool = False,
        maker_price: Optional[float] = None,
        reason: str = ""
    ) -> ExecutionResult:
        """
        Exit a position.
        Can use maker exit (limit order) for fee savings.
        """
        if not self.state.has_position:
            return ExecutionResult(
                success=False,
                order=None,
                message="No position to exit"
            )
        
        side = self.state.position_side
        size = self.state.position_size
        entry_price = self.state.entry_price
        
        order = None
        
        # Try maker exit if enabled and conditions met
        if use_maker_exit and self.config.USE_LIMIT_ORDERS_FOR_MAKER_EXIT and maker_price:
            order = self.exchange.place_limit_order(OrderSide.SELL, size, maker_price)
            self.open_orders[order.id] = order
            
            self.logger.info(
                f"Maker exit placed: {side} ${size:.2f} @ limit {maker_price:.3f}"
            )
            
            # Return pending - will check fill status later
            return ExecutionResult(
                success=True,
                order=order,
                message=f"Maker exit placed: {reason}"
            )
        
        # Otherwise, market exit
        for attempt in range(self.config.MAX_ORDER_RETRIES):
            try:
                order = self.exchange.place_market_order(OrderSide.SELL, size)
                break
            except Exception as e:
                self.logger.warning(f"Exit attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.ORDER_RETRY_DELAY)
        
        if not order:
            return ExecutionResult(
                success=False,
                order=None,
                message="Failed to exit position"
            )
        
        # Calculate P&L
        exit_value = order.avg_fill_price * size
        entry_cost = entry_price * size
        pnl = exit_value - entry_cost
        fees = self._calculate_fees(order)
        net_pnl = pnl - fees
        
        # Determine if this was a snipe position
        is_snipe = self.state.snipe_taken_this_round
        
        # Update P&L tracking
        self.state.total_pnl += net_pnl
        if is_snipe:
            self.state.snipe_pnl += net_pnl
        else:
            self.state.baseline_pnl += net_pnl
        
        self._log_pnl(net_pnl, is_snipe)
        
        # Clear position state
        self.state.has_position = False
        self.state.position_side = ""
        self.state.position_size = 0.0
        self.state.entry_price = 0.0
        self.current_position_order = None
        
        self.logger.info(
            f"Position exited: {side} ${size:.2f} @ {order.avg_fill_price:.3f} "
            f"(PnL: ${pnl:.3f}, fees: ${fees:.3f}, net: ${net_pnl:.3f})"
        )
        
        return ExecutionResult(
            success=True,
            order=order,
            pnl=net_pnl,
            fees=fees,
            message=f"Exited {side} position: {reason}"
        )
    
    def check_maker_exit_fill(self) -> Optional[ExecutionResult]:
        """
        Check if maker exit limit order has filled.
        Returns ExecutionResult if filled, None otherwise.
        """
        for order_id, order in list(self.open_orders.items()):
            if order.status != OrderStatus.PENDING:
                continue
            
            # Check for fill (in simulation, this tries to fill)
            if isinstance(self.exchange, SimulatedExchange):
                if self.exchange.try_fill_limit_order(order_id):
                    # Order filled!
                    del self.open_orders[order_id]
                    
                    # Calculate P&L
                    size = self.state.position_size
                    entry_price = self.state.entry_price
                    exit_value = order.avg_fill_price * size
                    entry_cost = entry_price * size
                    pnl = exit_value - entry_cost
                    fees = self._calculate_fees(order)  # Maker rebate (negative)
                    net_pnl = pnl - fees
                    
                    is_snipe = self.state.snipe_taken_this_round
                    
                    # Update state
                    self.state.total_pnl += net_pnl
                    if is_snipe:
                        self.state.snipe_pnl += net_pnl
                    else:
                        self.state.baseline_pnl += net_pnl
                    
                    self._log_pnl(net_pnl, is_snipe)
                    
                    # Clear position
                    self.state.has_position = False
                    self.state.position_side = ""
                    self.state.position_size = 0.0
                    self.state.entry_price = 0.0
                    self.current_position_order = None
                    
                    self.logger.info(
                        f"Maker exit FILLED: ${size:.2f} @ {order.avg_fill_price:.3f} "
                        f"(PnL: ${pnl:.3f}, fees: ${fees:.3f}, net: ${net_pnl:.3f})"
                    )
                    
                    return ExecutionResult(
                        success=True,
                        order=order,
                        pnl=net_pnl,
                        fees=fees,
                        message="Maker exit filled"
                    )
            else:
                # Real exchange - check status
                status = self.exchange.get_order_status(order_id)
                if status == OrderStatus.FILLED:
                    # Similar logic for real fills
                    pass
        
        return None
    
    def cancel_pending_maker_exits(self):
        """Cancel any pending maker exit orders (e.g., if round ending)."""
        for order_id in list(self.open_orders.keys()):
            self.exchange.cancel_order(order_id)
            del self.open_orders[order_id]
            self.logger.info(f"Cancelled pending maker exit: {order_id}")
