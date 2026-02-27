# Multi-Agent Mission Control — Quick Start

**Status:** Phase 1 Complete 🐟  
**Location:** `~/.nemo/workspace/mission-control/`

---

## What Is This?

Mission Control coordinates multiple NEMO sub-agents working together. Instead of doing everything myself, I can delegate tasks to specialized agents:

- **Researcher** — Gathers intelligence, searches X/web
- **Coder** — Writes code, fixes bugs
- **Trader** — Monitors markets, executes trades
- **Analyst** — Crunches numbers, backtests
- **Security** — Audits everything (uses Opus)
- And 4 more...

---

## How To Use

### Option 1: Natural Language (Auto-Routing)
Just tell me what you want, and I'll route to the right agent:

```
Captain: "Research Polymarket fees"
→ Commander auto-routes to Researcher agent

Captain: "Fix the stop-loss bug"  
→ Commander auto-routes to Coder agent

Captain: "Execute snipe trade"
→ Commander auto-routes to Trader agent
```

### Option 2: Direct Delegation
Specify which agent to use:

```
Captain: "Delegate to security: Audit the trading bot"
→ Commander explicitly uses Security agent (Opus)
```

### Option 3: Parallel Tasks
Multiple agents work simultaneously:

```
Captain: "Research fees, analyze win rates, and update code"
→ All 3 agents run in parallel
→ Results combined into single report
```

---

## Current Capabilities

✅ **Agent Registry** — 9 specialized agents defined  
✅ **Commander Module** — Task routing and delegation  
✅ **Auto-Routing** — Keyword-based agent selection  
✅ **Cost Tracking** — Per-agent budget monitoring  

⏳ **Phase 2:** Live sub-agent spawning (next session)

---

## Example Commands

### Research Tasks
- "Research new Polymarket strategies on X"
- "Find documentation on Kalshi API"
- "Analyze competitor trading bots"

### Coding Tasks  
- "Add logging to the trading bot"
- "Fix the risk manager bug"
- "Implement a new strategy"

### Trading Tasks
- "Check current market conditions"
- "Execute a test trade"
- "Monitor P&L for today"

### Security Tasks
- "Audit the trading bot for vulnerabilities"
- "Review new code before commit"
- "Check for exposed secrets"

---

## Cost Budgets

| Agent | Daily Budget | Avg Task |
|-------|-------------|----------|
| Researcher | $5 | $0.004 |
| Coder | $10 | $0.01 |
| Trader | $2 | $0.002 |
| Security | $5 | $0.20 |
| **Total** | **~$25/day** | |

Monthly estimate: $750 (fits within trading profit target)

---

## Files

```
mission-control/
├── README.md              # Full architecture docs
├── config/
│   └── agents.json        # Agent definitions
├── core/
│   └── commander.py       # Orchestration logic
└── agents/
    ├── researcher/skills.md
    ├── coder/skills.md
    └── trader/skills.md
```

---

## Next Steps (Phase 2)

1. Spawn live Researcher agent
2. Spawn live Coder agent  
3. Spawn live Trader agent
4. Test parallel task execution
5. Build shared memory system

Want me to **spawn the first live agent** now, Captain? 🐟
