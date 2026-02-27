# Trading Analysis Skill

**Purpose**: Post-session trading analysis to identify patterns and improvements  
**Cost**: $0 (skill-based)  
**Speed**: 2-5 minutes per session

---

## Quick Start

```bash
# Analyze current session
~/.nemo/workspace/skills/trading-analysis/trading-analysis.sh

# Analyze specific log
~/.nemo/workspace/skills/trading-analysis/trading-analysis.sh /tmp/nemo-trading.log

# Named session output
~/.nemo/workspace/skills/trading-analysis/trading-analysis.sh /tmp/nemo-trading.log "my-session"
```

---

## What It Analyzes

| Metric | Description |
|--------|-------------|
| **Trades** | Total trades executed |
| **Positions** | Positions opened |
| **Balance** | Final account balance |
| **P&L** | Profit/Loss |
| **Win Rate** | Percentage of winning trades |
| **Errors** | Error count and rate |
| **Warnings** | Warning count |
| **VPIN Kills** | Kill switch activations |

---

## When to Run

### Automatic (After Each Session)
- Add to bot shutdown script
- Cron job at session end time
- Post-processing hook

### Manual
- Before strategy changes
- After unusual market conditions
- Weekly reviews

---

## Sample Output

```markdown
# Trading Session Analysis — 2026-02-27

## Session Info
- Trades: 12
- Errors: 9 (10% error rate)
- VPIN Kills: 4

## Error Analysis
- Division by Zero: 5
- Strategy Errors: 5

## Recommendations
🔴 High Error Rate: Investigate before next session.
```

---

## Integration

### With Trading Bot
Add to bot's shutdown sequence:
```python
import subprocess
subprocess.run([
    "~/.nemo/workspace/skills/trading-analysis/trading-analysis.sh",
    config.log_path,
    session_name
])
```

### With HEARTBEAT
Update cron to run analysis after 24hr test:
```bash
# After test completes
~/.nemo/workspace/skills/trading-analysis/trading-analysis.sh \
  /tmp/nemo-trading-fixed.log \
  "24hr-test-$(date +%Y%m%d)"
```

---

## Output Location

Analysis reports saved to:
```
trading/nemo-trading/analysis/session-analysis-{name}.md
```

---

## Future Enhancements

- [ ] Compare across multiple sessions
- [ ] Generate charts/visualizations
- [ ] Auto-suggest strategy tweaks
- [ ] Integration with Notion for tracking

---

**Status**: ✅ Operational  
**Last Tested**: 2026-02-27
