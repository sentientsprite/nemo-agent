---
name: trading-analysis
description: Post-session trading analysis. Analyzes trading bot logs to identify what went wrong or right, extracts lessons learned, and suggests improvements. Run at the end of each trading session.
---

# Trading Analysis Skill

## Overview

Analyze completed trading sessions to extract insights, identify patterns, and generate actionable recommendations. Run automatically at session end or manually for deep analysis.

## Use Cases

- End-of-session performance review
- Identify winning/losing patterns
- Extract lessons learned
- Generate improvement recommendations
- Track strategy evolution over time

## When to Run

### Automatic (Recommended)
- After 24hr test completes
- After daily trading ends
- After strategy changes

### Manual
- Before strategy adjustments
- After unusual market conditions
- Weekly performance reviews

## Analysis Workflow

### 1. Extract Session Data

```bash
# Parse log for metrics
grep -E "Balance:|P&L:|Trades:|Win Rate:" $LOG_FILE | tail -20
grep -c "entry filled" $LOG_FILE
grep -c "Position opened" $LOG_FILE
grep -c "ERROR" $LOG_FILE
grep -c "WARNING" $LOG_FILE
```

### 2. Identify Patterns

**Winning Patterns**:
- High confidence (>80%) signals
- Specific market conditions
- Entry timing patterns
- Exit success rates

**Losing Patterns**:
- Errors (division by zero, API failures)
- VPIN kill switch activations
- Choppy market detection
- Late entries (low time remaining)

### 3. Calculate Metrics

| Metric | Formula |
|--------|---------|
| Win Rate | Wins / Total Trades |
| Avg Trade Duration | Sum(Exit - Entry) / Trades |
| Profit Factor | Gross Profit / Gross Loss |
| Max Drawdown | (Peak - Trough) / Peak |
| Sharpe Ratio | Return / Volatility |
| Error Rate | Errors / Total Cycles |

### 4. Generate Report

**Report Structure**:
```markdown
# Trading Session Analysis — YYYY-MM-DD

## Summary
- Duration: X hours
- Trades: X (Y wins, Z losses)
- P&L: $X (Y%)
- Win Rate: X%

## What Went Right
- [Pattern 1]
- [Pattern 2]

## What Went Wrong
- [Issue 1]
- [Issue 2]

## Lessons Learned
1. [Lesson]
2. [Lesson]

## Recommendations
1. [Action item]
2. [Action item]

## Next Session
- Strategy adjustments
- Risk parameter changes
```

## Common Issues & Solutions

### Issue: High Error Rate
**Symptoms**: >5% of cycles have errors
**Causes**: 
- Division by zero in position sizing
- API timeouts
- Invalid market data
**Solutions**:
- Add input validation
- Implement retry logic
- Check for None/NaN values

### Issue: Low Win Rate (<50%)
**Symptoms**: More losses than wins
**Causes**:
- Strategy unsuitable for market regime
- Entry thresholds too loose
- Choppy markets
**Solutions**:
- Add volatility filter
- Tighten entry criteria
- Reduce position size in chop

### Issue: VPIN Kill Switch Frequent
**Symptoms**: >10% of time in kill mode
**Causes**:
- Toxic flow prevalent
- VPIN buckets filling too fast
- Market manipulation
**Solutions**:
- Reduce trade frequency
- Increase VPIN threshold
- Avoid specific market times

### Issue: No Trades Executed
**Symptoms**: 0 trades in active session
**Causes**:
- Entry criteria too strict
- Market not moving enough
- API connection issues
**Solutions**:
- Lower min_delta threshold
- Check API connectivity
- Verify market hours

## Metrics to Track Over Time

| Metric | Target | Alert If |
|--------|--------|----------|
| Win Rate | >55% | <50% for 3 sessions |
| Profit Factor | >1.5 | <1.2 |
| Max Drawdown | <10% | >15% |
| Error Rate | <1% | >5% |
| Avg Trade Duration | 2-5 min | <30s or >10min |

## Integration with Other Skills

### Before Analysis
1. Run `trading-monitor` to get session summary
2. Confirm bot stopped cleanly

### After Analysis
1. Update strategy configs based on findings
2. Log lessons to `memory/`
3. Adjust HEARTBEAT alerts if needed

## Example Analysis

### Session: 24hr Snipe+Maker Test

**Raw Data**:
- Duration: 24 hours
- Trades: 156
- Wins: 109 (69.9%)
- Losses: 47 (30.1%)
- P&L: +$127 (25.4%)
- Errors: 3 (0.3%)

**What Went Right**:
- Snipe entries in last 30s highly successful
- Maker exit at 90¢ avoided second taker fee
- VPIN filtered out 12 toxic markets

**What Went Wrong**:
- 3 division by zero errors (Kelly sizing)
- 4 trades entered with <10s remaining (too late)
- Win rate dropped to 45% during high volatility periods

**Lessons**:
1. Kelly sizing needs bounds checking
2. Minimum 15s remaining for entry
3. Add volatility filter for position sizing

**Recommendations**:
1. Fix division by zero in Kelly calc
2. Add min_time_remaining = 15s parameter
3. Reduce size by 50% when volatility > threshold

## Cost Comparison

| Approach | Time | Cost |
|----------|------|------|
| Manual analysis | 30-60 min | Your time |
| This skill | 2-5 min | $0 |
| Sub-agent | 30 min | $0.004 |

**Recommendation**: Use this skill for routine analysis, spawn agent only for complex multi-session pattern analysis.
