# Multi-Agent Mission Control (MAMC)

**Status:** Design Phase  
**Captain:** King (@sentientsprite)  
**Created:** 2026-02-26  
**Updated:** 2026-02-26

---

## Overview

Mission Control coordinates multiple specialized NEMO sub-agents working together as a unified team. Inspired by pbteja1998's 10-agent SiteGPT architecture (3.8M views), MAMC enables parallel task execution with centralized orchestration.

---

## Core Architecture

### 1. Agent Types

| Role | Purpose | Model | Priority |
|------|---------|-------|----------|
| **Commander** (NEMO main) | Orchestration, delegation, final decisions | Opus | Critical |
| **Researcher** | Information gathering, analysis | Kimi K2.5 | High |
| **Coder** | Code generation, debugging | Kimi K2.5 | High |
| **Trader** | Trading execution, market monitoring | Kimi K2.5 | High |
| **Analyst** | Data analysis, backtesting | Kimi K2.5 | Medium |
| **Security** | Audits, threat detection | Opus (heavy reasoning) | Critical |
| **Writer** | Documentation, reports | Kimi K2.5 | Low |
| **Monitor** | System health, alerts | Kimi K2.5 | Medium |
| **Planner** | Task breakdown, scheduling | Kimi K2.5 | Medium |
| **Learner** | Pattern recognition, improvement | Kimi K2.5 | Low |

### 2. Communication Protocol

```
┌─────────────┐
│  Commander  │ ← Main NEMO (you're talking to me)
└──────┬──────┘
       │ delegates via sessions_spawn
       ▼
┌─────────────────────────────────────────┐
│           Message Bus (JSON)            │
└─────────────────────────────────────────┘
       │
   ┌───┼───┬───┬───┬───┬───┬───┬───┬───┐
   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼
  [R] [C] [T] [A] [S] [W] [M] [P] [L]
  Research Coder  Trader  Security  etc
```

**Message Format:**
```json
{
  "id": "msg-uuid",
  "from": "commander",
  "to": "researcher",
  "type": "task|result|alert|query",
  "task": "analyze-polymarket-strategy",
  "payload": {...},
  "priority": 1-5,
  "deadline": "ISO-8601",
  "context": ["msg-uuid-1", "msg-uuid-2"]
}
```

### 3. Task Lifecycle

```
1. INTAKE → Commander receives request
2. ANALYSIS → Break down into sub-tasks
3. DELEGATION → Spawn agents via sessions_spawn
4. EXECUTION → Agents work in parallel
5. MONITORING → Track progress, handle blocks
6. AGGREGATION → Collect results
7. VALIDATION → Verify completeness/quality
8. RESPONSE → Deliver to Captain
```

---

## Implementation Phases

### Phase 1: Core Infrastructure ✅ COMPLETE
- [x] Design agent registry (JSON config)
- [x] Create message bus protocol
- [x] Build Commander delegation logic
- [x] Implement basic spawn/monitor/kill

### Phase 2: Specialized Agents 🟢 ACTIVE
- [x] Researcher agent (web search, analysis) - **SPAWNED**
- [x] Coder agent (code generation, review) - **SPAWNED**
- [x] Monitor agent (system health, alerts) - **SPAWNED**
- [ ] Trader agent (market monitoring, execution) - Pending
- [ ] Security agent (audit, hardening) - Pending

### Phase 3: Advanced Features ⏳ PENDING
- [ ] Inter-agent communication
- [ ] Shared memory/context
- [ ] Conflict resolution
- [ ] Load balancing
- [ ] Auto-scaling

### Phase 4: Optimization
- [ ] Cost tracking per agent
- [ ] Performance metrics
- [ ] Agent specialization tuning
- [ ] Failure recovery

---

## Agent Registry

```json
{
  "agents": {
    "researcher": {
      "model": "kimi-k2.5",
      "timeout": 300,
      "maxConcurrent": 3,
      "skills": ["web_search", "web_fetch", "memory_search"],
      "costLimit": "$5/day"
    },
    "coder": {
      "model": "kimi-k2.5",
      "timeout": 600,
      "maxConcurrent": 2,
      "skills": ["read", "write", "edit", "exec"],
      "costLimit": "$10/day"
    },
    "trader": {
      "model": "kimi-k2.5",
      "timeout": 60,
      "maxConcurrent": 1,
      "skills": ["exec", "cron"],
      "costLimit": "$2/day"
    }
  }
}
```

---

## Usage Examples

### Example 1: Research Trading Strategy
```
Captain: "Research Polymarket edge opportunities"

Commander:
  → Spawn Researcher: "Search X for profitable strategies"
  → Spawn Analyst: "Analyze fee structures"
  → Spawn Trader: "Check current market conditions"
  
Aggregator combines results → Summary to Captain
```

### Example 2: Build Feature
```
Captain: "Add Snipe strategy to trading bot"

Commander:
  → Spawn Planner: "Break down implementation steps"
  → Spawn Coder: "Implement strategy/snipe.py"
  → Spawn Security: "Audit for risks"
  → Spawn Tester: "Validate with dry-run"
  
Validation passes → Commit to GitHub → Report to Captain
```

### Example 3: Incident Response
```
Monitor: "Alert: Trading bot stopped"

Commander:
  → Spawn Security: "Check logs for intrusion"
  → Spawn Coder: "Diagnose crash cause"
  → Spawn Trader: "Assess position exposure"
  
Critical? → Alert Captain immediately
Routine? → Fix autonomously, report in daily summary
```

---

## Cost Model

| Agent | Model | Avg Task | Daily Budget |
|-------|-------|----------|--------------|
| Researcher | Kimi K2.5 | $0.004 | $5 |
| Coder | Kimi K2.5 | $0.01 | $10 |
| Trader | Kimi K2.5 | $0.002 | $2 |
| Security | Opus | $0.20 | $5 |
| Others | Kimi K2.5 | $0.005 | $3 |
| **Total** | | | **~$25/day** |

**Monthly estimate:** $750 (well within $200 trading profit target)

---

## File Structure

```
~/.nemo/workspace/mission-control/
├── README.md
├── config/
│   └── agents.json          # Agent registry
├── core/
│   ├── commander.ts         # Orchestration logic
│   ├── message-bus.ts       # Inter-agent communication
│   └── task-queue.ts        # Priority queue
├── agents/
│   ├── researcher/
│   │   ├── agent.ts
│   │   └── skills.md
│   ├── coder/
│   ├── trader/
│   ├── security/
│   └── ...
├── memory/
│   └── shared-context.jsonl # Cross-agent memory
└── logs/
    └── agent-activity.jsonl
```

---

## Integration with Existing Systems

- **Trading Bot:** Trader agent runs `trading/nemo-trading/`
- **Spryte Engine:** Coder agent builds on `@spryte/agent-core`
- **Dashboard:** Monitor agent updates `dashboard/data.json`
- **MEMORY.md:** All agents read/write to memory system
- **Cron:** Scheduler agent manages `HEARTBEAT.md` triggers

---

## Success Metrics

- [ ] 5+ specialized agents operational
- [ ] <5s task delegation latency
- [ ] 90%+ task completion rate
- [ ] <$25/day agent costs
- [ ] Zero cross-agent conflicts
- [ ] Captain satisfaction >8/10

---

## Next Steps

1. **Create agent registry** (config/agents.json)
2. **Build Commander module** (command delegation)
3. **Spawn first 3 agents** (Researcher, Coder, Trader)
4. **Test parallel task execution**
5. **Document learnings** in `memory/`

---

*"One agent is a tool. Ten agents is a team."* — pbteja1998 🐟
