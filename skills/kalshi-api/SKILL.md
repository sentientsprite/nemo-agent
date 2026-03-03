# Kalshi API Skill

**Purpose**: Interface with Kalshi prediction markets for paper and live trading  
**Status**: In Development  
**Created**: March 2, 2026  
**API Docs**: https://trading-api.readme.io/reference/

---

## Overview

Kalshi is a regulated prediction market exchange in the US. This skill provides:
- Market data retrieval
- Paper trading (demo mode)
- Live trading (when approved)
- Portfolio tracking
- Automated strategy execution

---

## Configuration

### API Credentials
Store in `~/.nemo/credentials/kalshi.json`:
```json
{
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET",
  "mode": "demo"
}
```

### Modes
- `demo` — Paper trading with fake money (default)
- `live` — Real money trading (requires explicit approval)

---

## Commands

### Get Markets
```bash
kalshi markets list --category sports --status open
kalshi markets get --id KC-WS-2024
```

### Get Balance
```bash
kalshi balance
```

### Place Order (Demo)
```bash
kalshi order create --market KC-WS-2024 --side yes --amount 100 --price 55
```

### Get Positions
```bash
kalshi positions list
```

---

## Strategy Integration

See `strategies/` folder for example implementations:
- `momentum.py` — Momentum-based entry/exit
- `mean_reversion.py` — RSI + Bollinger Bands
- `snipe_maker.py` — Late entry, maker exit
- `crowd_fade.py` — Bet against 80%+ consensus

---

## Safety Rules

1. **Default to demo mode** — Never use live without explicit approval
2. **Max position size** — 5% of portfolio ($50 max initially)
3. **Daily loss limit** — Stop if down >$20 in a day
4. **Logging** — All trades logged to `logs/kalshi-trades.jsonl`

---

**NEMO's Note**: *"Prediction markets are the purest form of trading — no fundamentals, just probabilities. The edge is in the math."* 🐟
