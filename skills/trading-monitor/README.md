# Trading Monitor Skill

**Purpose**: Monitor NEMO trading bot health and extract metrics  
**Cost**: $0 (vs $0.004 for agent)  
**Speed**: 5 seconds (vs 30 minutes)

---

## Quick Start

```bash
# Run health check
~/.nemo/workspace/skills/trading-monitor/trading-monitor.sh

# Check specific log
~/.nemo/workspace/skills/trading-monitor/trading-monitor.sh /tmp/nemo-trading.log
```

---

## What It Monitors

| Metric | Source |
|--------|--------|
| Process status | PID check |
| Runtime | ps aux |
| Trades executed | Log grep |
| Balance | Log extraction |
| Win rate | Log extraction |
| VPIN status | Log extraction |
| Error count | Last hour |
| Warning count | Last hour |
| Recent trades | Log tail |
| VPIN kill switches | Log grep |

---

## Sample Output

```
=== Trading Bot Health Check ===

🔍 Process Status:
  Status: 🟢 RUNNING
  PID: 75997
  Runtime: 02:07:46
  CPU: 0.0
  Memory: 0.1

📊 Latest Metrics:
  Balance: $500.00
  Trades: 11
  Win Rate: 0.0%
  VPIN: ✅ OK

⚠️  Issues (Last Hour):
  Errors: 0
  Warnings: 6

💰 Recent Trades:
  Position opened: btc-updown-5m-1772182482 YES
  Snipe entry filled: YES 48.75 @ 0.0
  ...
```

---

## Log Locations

| Bot Instance | Log Path |
|--------------|----------|
| Polymarket (fixed) | `/tmp/nemo-trading-fixed.log` |
| Polymarket (original) | `/tmp/nemo-trading-kelly.log` |
| Coinbase | `/tmp/nemo-trading.log` |

---

## When to Use

### ✅ Use This Skill
- Hourly status checks
- Quick debugging
- Metrics extraction
- Before/after deployments

### ❌ Use Sub-Agents Instead
- Deep log analysis (patterns over days)
- Complex debugging
- Research tasks
- Strategy evaluation

---

## Integration with HEARTBEAT.md

Update your cron reminder to use this skill:

```bash
# Before (spawns agent)
sessions_spawn({ task: "Monitor bot..." })

# After (runs skill)
~/.nemo/workspace/skills/trading-monitor/trading-monitor.sh
```

**Savings**: $0.004 per check → $0

---

## Future Enhancements

- [ ] JSON output mode for programmatic use
- [ ] Webhook alerts on errors
- [ ] Historical metrics tracking
- [ ] Grafana/Prometheus integration
- [ ] Dashboard auto-refresh

---

**Status**: ✅ Operational  
**Last Tested**: 2026-02-27 02:11 MST  
**Test Result**: Bot running, 11 trades, 0 errors (last hour)
