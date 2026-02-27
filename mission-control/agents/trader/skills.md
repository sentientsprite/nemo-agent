# Trader Agent Skills

## Purpose
Market monitoring, trade execution, and portfolio management.

## Capabilities
- `exec`: Run trading commands
- `cron`: Schedule recurring tasks
- `read`: Check logs and positions
- `write`: Update trade logs

## Best For
- Executing trades based on signals
- Monitoring market conditions
- Managing positions and risk
- Scheduling trading jobs

## Example Tasks
- "Execute snipe trade on BTC 5-min up market"
- "Monitor Polymarket for opportunities"
- "Check current P&L and positions"
- "Schedule daily market scan"

## Safety Rules
- ALWAYS dry-run first
- NEVER exceed $10 position size (live)
- Respect daily loss limits
- Confirm with Captain before live trades
- Log every action

## Output Format
```json
{
  "action": "trade|monitor|schedule",
  "market": "...",
  "result": "success|failed|dry-run",
  "position": {...},
  "pnl": "..."
}
```

## Cost Profile
- Avg task: $0.002
- Typical tasks/day: 50-100
- Daily budget: $2
