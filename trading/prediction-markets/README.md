# Prediction Market Copy-Trading Bot

Copy trades from top prediction market traders on **Kalshi** (USA-legal, CFTC-regulated) and **Polymarket**.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure (copy and edit)
cp .env.example .env

# Dry run
python main.py --dry-run --platform kalshi

# Live (after funding account)
python main.py --platform kalshi
```

## Configuration

All settings via environment variables or `.env` file:

### Kalshi (Primary — USA Legal)
```
KALSHI_EMAIL=you@email.com
KALSHI_PASSWORD=...
# OR use API key auth:
KALSHI_API_KEY=...
KALSHI_API_SECRET=...
KALSHI_DEMO=true          # Use demo API for paper trading
```

### Polymarket (Secondary — USA Restricted)
```
POLYMARKET_PRIVATE_KEY=0x...
POLYMARKET_API_KEY=...
POLYMARKET_API_SECRET=...
POLYMARKET_API_PASSPHRASE=...
```

### Trading Parameters
```
PLATFORM=kalshi            # kalshi | polymarket | both
DRY_RUN=true               # Paper trading mode
BANKROLL=100.0             # USD to allocate
COPY_DELAY_SECONDS=5.0     # Delay before copying
SIZING_RATIO=1.0           # Position size multiplier
POLL_INTERVAL_SECONDS=30   # How often to check for signals
```

### Risk Limits
```
RISK_MAX_PER_MARKET_PCT=0.10      # Max 10% per market
RISK_MAX_TOTAL_EXPOSURE_PCT=0.30  # Max 30% total
RISK_DAILY_LOSS_LIMIT_PCT=0.15    # Stop at 15% daily loss
RISK_MIN_LEADER_WINRATE=0.50      # Drop leader if WR < 50%
RISK_LEADER_WINRATE_WINDOW=20     # Over last N trades
RISK_MAX_POSITIONS_PER_LEADER=3   # Max concurrent per leader
```

## Adding Leaders to Follow

### Kalshi Leaders
Set comma-separated user IDs:
```
KALSHI_LEADER_IDS=user123,user456
```

### Polymarket Addresses
Set comma-separated wallet addresses:
```
POLYMARKET_LEADER_ADDRESSES=0xabc...,0xdef...
```

## Signal Sources

1. **Kalshi Leaderboard** — Polls top traders' positions for changes
2. **Polymarket Address Monitor** — Watches wallet addresses for new positions
3. **Webhook** — POST to `http://localhost:5088/signal`:
   ```json
   {
     "platform": "kalshi",
     "market_id": "TICKER-123",
     "side": "yes",
     "price": 0.65,
     "size": 10,
     "leader_id": "trader42"
   }
   ```
   Secure with `WEBHOOK_SECRET` env var (sent as `Authorization: Bearer <secret>`).

## Architecture

```
Signal Sources → Copy Engine → Risk Check → Execute → Ledger
                                  ↓
                           Portfolio State
```

## Fees

- **Kalshi**: ~$0.02–$0.07 per contract (deducted at trade time)
- **Polymarket**: Free trading, ~2% on winnings

## Trade Log

All trades logged to `data/trades.jsonl` with: timestamp, platform, market, side, price, size, leader_id, signal_source, pnl, fees.

## Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point, main loop |
| `config.py` | Environment-based configuration |
| `kalshi_client.py` | Kalshi REST API wrapper |
| `polymarket_client.py` | Polymarket CLOB wrapper |
| `signal_source.py` | Signal detection (leaderboard, address, webhook) |
| `copy_engine.py` | Core copy logic + sizing |
| `risk.py` | Risk management + portfolio state |
| `ledger.py` | Trade logging (JSONL) |
