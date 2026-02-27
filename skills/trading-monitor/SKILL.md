---
name: trading-monitor
description: Monitor NEMO trading bot health, extract metrics from logs, and report trading performance. Use when checking if the bot is running, analyzing trading logs, extracting P&L metrics, or debugging trading issues.
---

# Trading Monitor Skill

## Overview

Monitor trading bot health and performance through log analysis and process inspection. Extract actionable metrics without spawning expensive sub-agents.

## Use Cases

- Check if trading bot is running (PID status)
- Tail logs for recent errors or trades
- Extract performance metrics (P&L, win rate, trades)
- Monitor VPIN/kill switch status
- Debug trading issues

## Core Tools

### 1. Check Bot Status

```bash
# Check if process is running
ps aux | grep "python.*main\.py" | grep -v grep

# Check specific PID
ps -p <PID> -o pid,etime,%cpu,%mem,command
```

### 2. Tail Trading Log

```bash
# Recent activity (last 50 lines)
tail -50 /tmp/nemo-trading-fixed.log

# Search for specific patterns
grep -E "(ERROR|WARNING|Trade|Position)" /tmp/nemo-trading-fixed.log | tail -20

# Extract metrics from status lines
grep "Balance:" /tmp/nemo-trading-fixed.log | tail -1
```

### 3. Extract Metrics

```bash
# Parse metrics from log
grep -oP "Balance: \$[0-9.]+" /tmp/nemo-trading-fixed.log | tail -1
grep -oP "Trades: [0-9]+" /tmp/nemo-trading-fixed.log | tail -1
grep -oP "Win Rate: [0-9.]+%" /tmp/nemo-trading-fixed.log | tail -1
grep -oP "VPIN: [✅⚠️🔴]" /tmp/nemo-trading-fixed.log | tail -1
```

### 4. Count Errors

```bash
# Error count in last hour
grep "$(date '+%Y-%m-%d %H:')" /tmp/nemo-trading-fixed.log | grep -c "ERROR"

# VPIN kill switch activations
grep -c "VPIN KILL SWITCH ACTIVATED" /tmp/nemo-trading-fixed.log
```

## Workflow

### Quick Health Check

1. Check PID running
2. Tail last 10 log lines
3. Extract current metrics
4. Report status

### Deep Analysis

1. Get error count (last hour)
2. Count trades executed
3. Analyze VPIN patterns
4. Check Kelly/Chainlink status
5. Generate summary

## Output Format

```markdown
## Trading Bot Status — HH:MM

| Metric | Value |
|--------|-------|
| Status | 🟢 Running / 🔴 Stopped |
| PID | 75997 |
| Runtime | 2h 15min |
| Trades | 12 |
| Balance | $500.00 |
| Win Rate | 0.0% |
| VPIN | ✅ OK |

### Recent Activity
- Last 5 log entries...

### Issues (if any)
- Error count: 2
- Warnings: 5 VPIN alerts
```

## Log Locations

| Bot | Log Path |
|-----|----------|
| Snipe+Maker (fixed) | `/tmp/nemo-trading-fixed.log` |
| Snipe+Maker (original) | `/tmp/nemo-trading-kelly.log` |
| Coinbase | `/tmp/nemo-trading.log` |

## Common Patterns

### Healthy Bot
- PID running
- Regular "cycle" log entries
- VPIN: ✅ OK or occasional warnings
- New rounds detected every 5 min

### Issues to Watch
- "ERROR" in logs
- VPIN: 🔴 CRITICAL for extended periods
- No trades in >30 min during market hours
- Kill switch active >10 min (stuck)

### Error Patterns
- `float division by zero` — Position sizing math
- `VPIN calculation failed` — Flow toxicity detection
- `Strategy error` — Individual trade failure

## Integration

Use this skill instead of spawning agents for:
- Hourly status checks
- Quick debugging
- Metrics extraction
- Log grepping

**Cost**: $0 (vs $0.004 per agent)  
**Speed**: 5 seconds (vs 30 min)
