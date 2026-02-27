# Poly-Bot: Snipe + Maker Strategy

Automated trading bot with high-confidence snipe entries and maker fee optimization.

## Features

### 1. Snipe Entry Strategy
- **Window**: 260-295 seconds into the 5-minute round (35-second window)
- **Conditions**: 
  - Delta > $20 (high conviction)
  - Zero crosses < 2 (clear direction)
  - Confidence ≥ 65%
  - Clear directional signal
- **Execution**: Market order (taker fee acceptable for high confidence)
- **Size**: $50 (aggressive for quality setups)
- **Limit**: 1 snipe per round, with cooldown between rounds

### 2. Maker Exit Strategy
- **Trigger**: Position value ≥ $0.60 with ≤15 seconds remaining
- **Execution**: Limit sell at $0.90
- **Benefit**: No second taker fee if filled (maker rebate)
- **Fallback**: Hold to settlement if not filled

### 3. P&L Tracking
- Separate tracking for snipe vs baseline performance
- Detailed decision logging with reasoning
- Comparative performance analysis

## Project Structure

```
poly-bot/
├── config.py      # Configuration parameters
├── strategy.py    # Trading strategy implementations
├── executor.py    # Order execution and P&L tracking
├── main.py        # Bot orchestration and CLI
└── README.md      # This file
```

## Configuration

### Snipe + Maker Parameters (`SnipeMakerConfig`)

```python
SNIPE_ENTRY_ENABLED = True
SNIPE_WINDOW_START = 260      # 4m20s into round
SNIPE_WINDOW_END = 295        # 4m55s into round
SNIPE_MIN_DELTA = 20.0        # $20 minimum delta
SNIPE_MAX_ZERO_CROSSES = 2    # Less than 2 zero crosses
SNIPE_SIZE = 50               # $50 position size

MAKER_EXIT_ENABLED = True
MAKER_EXIT_THRESHOLD = 0.60   # 60¢ position value
MAKER_EXIT_TIME_CUTOFF = 15   # 15 seconds left
MAKER_EXIT_PRICE = 0.90       # Limit sell at 90¢
```

## Usage

### Run Snipe + Maker Strategy
```bash
python main.py --strategy snipe_maker --rounds 20
```

### Run Baseline Strategy (for comparison)
```bash
python main.py --strategy baseline --rounds 20
```

### Run Both Strategies (comparison test)
```bash
python main.py --strategy both --rounds 20
```

### Options
- `--strategy`: Choose strategy (`baseline`, `snipe_maker`, `both`)
- `--rounds`: Number of rounds to simulate (default: 10)
- `--delay`: Seconds between simulation steps (default: 0.1)
- `--dry-run`: Run in simulation mode (default: true)

## Testing

### Dry Run Mode
All trades are simulated by default. To enable live trading:
```bash
DRY_RUN=false python main.py --strategy snipe_maker
```

### Strategy Comparison
Run both strategies on identical market data:
```bash
python main.py --strategy both --rounds 50
```

### View Logs
```bash
tail -f logs/poly_bot.log
tail -f logs/snipe_decisions.jsonl
tail -f logs/snipe_pnl.jsonl
```

## Key Implementation Details

### 1. Snipe Entry Logic
```python
def should_enter(signal, seconds_into_round):
    # Time window check
    if not (260 <= seconds_into_round <= 295):
        return False
    
    # High conviction conditions
    if signal.delta < 20.0:
        return False
    if signal.zero_crosses >= 2:
        return False
    if signal.direction == NEUTRAL:
        return False
    
    # All conditions met - execute snipe
    return True
```

### 2. Maker Exit Logic
```python
def should_exit(signal, seconds_into_round, position_value):
    # Standard exits (stop loss, etc.)
    ...
    
    # Maker exit opportunity
    time_remaining = 300 - seconds_into_round
    if (position_value >= 0.60 and time_remaining <= 15):
        return True  # Use limit order at $0.90
```

### 3. Decision Logging
Every snipe decision is logged with:
- Timestamp
- Round number
- Seconds into round
- Market conditions (delta, zero crosses, direction)
- Decision result (enter/exit)
- Reasoning

## Performance Comparison

The bot tracks:
- **Snipe P&L**: All trades from snipe entries
- **Baseline P&L**: Trades from baseline strategy
- **Improvement %**: Snipe vs baseline performance
- **Maker exit rate**: How often maker exits fill
- **Fee savings**: Maker rebates vs taker fees

## Risk Management

- **One snipe per round**: Prevents overtrading
- **Cooldown period**: Configurable rounds between snipes
- **Stop loss**: 15% on all positions
- **Position limits**: Max $50 per snipe
- **Time limits**: Only enter in 260-295s window

## Future Enhancements

- [ ] Live exchange integration (Kalshi API)
- [ ] Real-time market data feed
- [ ] Web dashboard for monitoring
- [ ] Alert notifications (Discord/Slack)
- [ ] Machine learning signal enhancement
- [ ] Multi-market support

## License

MIT License - See LICENSE file
