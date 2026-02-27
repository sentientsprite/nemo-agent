# Coinbase Trading Bot

Modular crypto trading bot for Coinbase Advanced Trade. Supports momentum and mean-reversion strategies on USDC pairs.

## Quick Start (Dry Run)

```bash
cd trading/coinbase
pip install -r requirements.txt  # only needed for live trading
python main.py --dry-run --strategy momentum
python main.py --dry-run --strategy mean_reversion
python main.py --dry-run --strategy momentum --pair ETH-USDC --balance 5000
```

No API keys needed for dry-run — uses simulated random-walk candles and fills.

## Live Trading

```bash
export COINBASE_API_KEY="your-cdp-api-key"
export COINBASE_API_SECRET="your-cdp-api-secret"
python main.py --strategy momentum
```

Get API keys from [Coinbase Developer Platform](https://portal.cdp.coinbase.com/). Enable **trade** permissions.

## Strategies

### Momentum (Strategy A)
- Detects trends on 5-min candles using EMA(9/21) crossovers + MACD histogram
- Enters on momentum confirmation with volume surge
- Exits on EMA cross-back or MACD reversal

### Mean Reversion (Strategy B)
- Identifies overbought/oversold via RSI(14) + Bollinger Bands(20, 2σ)
- Buys at lower BB when RSI < 30, sells at upper BB when RSI > 70
- Exits when RSI returns to neutral (45-55) and price near BB midline

## Risk Management

| Rule | Default | Env Var |
|------|---------|---------|
| Max position size | 5% of portfolio | `MAX_POSITION_PCT` |
| Stop-loss | 2% per position | `STOP_LOSS_PCT` |
| Daily drawdown halt | 10% | `MAX_DAILY_DRAWDOWN_PCT` |
| Consecutive loss skip | 3 losses → skip 1 | `CONSECUTIVE_LOSS_LIMIT` |
| Min trade size | $10 USDC | `MIN_TRADE_USDC` |

## Configuration

All parameters are env-configurable. See `config.py` for full list:

```bash
export TRADING_PAIRS="BTC-USDC,ETH-USDC"
export POLL_INTERVAL=15
export EMA_FAST=9
export EMA_SLOW=21
export RSI_PERIOD=14
export RSI_OVERSOLD=30
export RSI_OVERBOUGHT=70
export LOG_LEVEL=DEBUG
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Orchestrator — CLI entry point |
| `config.py` | All tunable parameters |
| `exchange.py` | Coinbase API wrapper + dry-run simulator |
| `strategy_momentum.py` | EMA/MACD trend following |
| `strategy_mean_reversion.py` | RSI/Bollinger mean reversion |
| `signals.py` | Technical indicator calculations |
| `risk.py` | Position sizing, stop-loss, drawdown limits |
| `ledger.py` | Trade logging to JSONL |

## Architecture

```
main.py (orchestrator)
  ├── config.py (parameters)
  ├── exchange.py (Coinbase API / simulator)
  ├── strategy_*.py (signal generation)
  │   └── signals.py (indicators)
  ├── risk.py (position & drawdown mgmt)
  └── ledger.py (trade logging)
```

Designed as a NEMO sub-agent plugin. Run as standalone process, started/stopped by the main agent.
