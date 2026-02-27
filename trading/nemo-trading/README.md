# NEMO Trading — Unified Trading Bot

A unified trading bot supporting both CEX (Coinbase) and prediction markets (Polymarket) with multiple strategies.

## Features

- **Exchanges:** Coinbase Advanced Trade, Polymarket CLOB
- **Strategies:**
  - **Momentum** (Coinbase): EMA crossover + MACD confirmation
  - **Mean Reversion** (Coinbase): RSI + Bollinger Bands
  - **Snipe + Maker** (Polymarket): Late entry with maker exit
  - **Crowd Fade** (Polymarket): Bet against 80%+ consensus
  - **Copy Trading** (Polymarket): Mirror profitable wallets
- **Risk Management:** Universal position sizing, daily limits, drawdown protection
- **Modes:** Dry-run (default), Live trading, Sandbox

## Quick Start

```bash
cd trading/nemo-trading
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run with preset configuration
python main.py --preset polymarket_snipe --dry-run

# Or specify manually
python main.py --exchange polymarket --strategy snipe --dry-run

# Live trading (requires confirmation)
python main.py --preset polymarket_snipe --live
```

## Preset Configurations

| Preset | Exchange | Strategy | Description |
|--------|----------|----------|-------------|
| `coinbase_momentum` | Coinbase | Momentum | EMA crossover + MACD |
| `coinbase_mean_reversion` | Coinbase | Mean Reversion | RSI + Bollinger Bands |
| `polymarket_snipe` | Polymarket | Snipe + Maker | Late entry, maker exit |
| `polymarket_crowd` | Polymarket | Crowd Fade | Bet against 80%+ consensus |
| `polymarket_copy` | Polymarket | Copy Trading | Mirror profitable wallets |

## Environment Variables

```bash
# Coinbase
COINBASE_API_KEY=your_key
COINBASE_API_SECRET=your_secret

# Polymarket
POLYMARKET_PRIVATE_KEY=0x...
FUNDER_ADDRESS=0x...

# Optional
LOG_LEVEL=INFO
DRY_RUN=true
```

## Strategy Details

### Snipe + Maker (Recommended)
- **Entry:** 30-40s before market close
- **Signal:** BTC delta > $20, clear direction
- **Size:** $50 per trade
- **Exit:** Maker order at 90¢ if winning
- **Win Rate:** 70-80% expected

### Crowd Fade
- **Entry:** 40-50s before close
- **Signal:** 80%+ consensus detected via order book
- **Action:** Fade the crowd (bet opposite)
- **Size:** $30 per trade
- **Hold:** To settlement

### Momentum / Mean Reversion
- **Exchanges:** Coinbase only
- **Timeframes:** 5-min candles
- **Indicators:** EMA, MACD, RSI, Bollinger

## Risk Limits (Hardcoded)

- **Max Position:** $10 per trade (live) / $50 (dry-run)
- **Daily Loss Limit:** $50
- **Max Drawdown:** 10%
- **Consecutive Loss Cooldown:** 3 losses
- **Daily Trade Limit:** 20 trades

## Architecture

```
nemo-trading/
├── main.py              # Entry point, orchestration
├── config.py            # All configuration
├── exchanges/
│   ├── coinbase.py      # CEX interface (with dry-run)
│   └── polymarket.py    # CLOB interface (with dry-run)
├── strategies/
│   ├── momentum.py      # EMA + MACD
│   ├── mean_reversion.py # RSI + Bollinger
│   ├── snipe.py         # Snipe + Maker
│   ├── crowd_fade.py    # Contrarian
│   └── copy_trading.py  # Wallet mirroring
└── utils/
    └── risk.py          # Universal risk manager
```

## Testing

```bash
# Dry-run (recommended for testing)
python main.py --preset polymarket_snipe --dry-run

# Watch logs
python main.py --preset polymarket_snipe --dry-run --log-level DEBUG
```

## Safety Checklist Before Live

- [ ] API keys configured and tested
- [ ] Dry-run tested for 24+ hours
- [ ] Win rate > 55% in backtests
- [ ] Max drawdown < 10%
- [ ] Daily loss limit understood
- [ ] Emergency stop procedure known

## License

MIT — Part of NEMO Agent Framework
