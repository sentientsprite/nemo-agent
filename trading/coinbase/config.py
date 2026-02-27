"""
Configuration — all tunable parameters, env-overridable.
"""
import os
from dataclasses import dataclass, field
from typing import List


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _env_float(key: str, default: float) -> float:
    return float(os.environ.get(key, str(default)))


def _env_int(key: str, default: int) -> int:
    return int(os.environ.get(key, str(default)))


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key, str(default)).lower()
    return val in ("true", "1", "yes")


@dataclass
class Config:
    # --- Coinbase API ---
    api_key: str = field(default_factory=lambda: _env("COINBASE_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: _env("COINBASE_API_SECRET", ""))

    # --- Trading pairs ---
    pairs: List[str] = field(default_factory=lambda: _env("TRADING_PAIRS", "BTC-USDC,ETH-USDC").split(","))
    primary_pair: str = field(default_factory=lambda: _env("PRIMARY_PAIR", "BTC-USDC"))

    # --- Mode ---
    dry_run: bool = field(default_factory=lambda: _env_bool("DRY_RUN", True))
    strategy: str = field(default_factory=lambda: _env("STRATEGY", "momentum"))

    # --- Timeframes ---
    candle_interval_short: str = field(default_factory=lambda: _env("CANDLE_SHORT", "FIVE_MINUTE"))
    candle_interval_long: str = field(default_factory=lambda: _env("CANDLE_LONG", "FIFTEEN_MINUTE"))
    poll_interval_sec: int = field(default_factory=lambda: _env_int("POLL_INTERVAL", 15))

    # --- Risk management ---
    max_position_pct: float = field(default_factory=lambda: _env_float("MAX_POSITION_PCT", 0.05))
    stop_loss_pct: float = field(default_factory=lambda: _env_float("STOP_LOSS_PCT", 0.02))
    max_daily_drawdown_pct: float = field(default_factory=lambda: _env_float("MAX_DAILY_DRAWDOWN_PCT", 0.10))
    consecutive_loss_limit: int = field(default_factory=lambda: _env_int("CONSECUTIVE_LOSS_LIMIT", 3))
    min_trade_usdc: float = field(default_factory=lambda: _env_float("MIN_TRADE_USDC", 10.0))

    # --- Momentum strategy params ---
    ema_fast: int = field(default_factory=lambda: _env_int("EMA_FAST", 9))
    ema_slow: int = field(default_factory=lambda: _env_int("EMA_SLOW", 21))
    macd_signal: int = field(default_factory=lambda: _env_int("MACD_SIGNAL", 9))
    momentum_min_volume_ratio: float = field(default_factory=lambda: _env_float("MOMENTUM_VOL_RATIO", 1.5))

    # --- Mean reversion strategy params ---
    rsi_period: int = field(default_factory=lambda: _env_int("RSI_PERIOD", 14))
    rsi_oversold: float = field(default_factory=lambda: _env_float("RSI_OVERSOLD", 30.0))
    rsi_overbought: float = field(default_factory=lambda: _env_float("RSI_OVERBOUGHT", 70.0))
    bb_period: int = field(default_factory=lambda: _env_int("BB_PERIOD", 20))
    bb_std: float = field(default_factory=lambda: _env_float("BB_STD", 2.0))
    mr_exit_rsi_low: float = field(default_factory=lambda: _env_float("MR_EXIT_RSI_LOW", 45.0))
    mr_exit_rsi_high: float = field(default_factory=lambda: _env_float("MR_EXIT_RSI_HIGH", 55.0))

    # --- Logging ---
    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))
    ledger_path: str = field(default_factory=lambda: _env("LEDGER_PATH", "trades.jsonl"))

    # --- Dry-run sim ---
    sim_starting_balance: float = field(default_factory=lambda: _env_float("SIM_BALANCE", 10000.0))
    sim_slippage_pct: float = field(default_factory=lambda: _env_float("SIM_SLIPPAGE", 0.001))
    sim_fee_pct: float = field(default_factory=lambda: _env_float("SIM_FEE", 0.006))
