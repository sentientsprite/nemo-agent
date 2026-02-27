# Commander Module - Mission Control Core

**Role**: Orchestration, delegation, and coordination of all sub-agents  
**Status**: Active (Phase 2)  
**Created**: 2026-02-27

---

## Active Sub-Agents (Overnight Shift)

| Agent | Session Key | Task | Status | Spawned |
|-------|-------------|------|--------|---------|
| **Trader** | `agent:main:subagent:db3b4c28-959c-459e-8c38-0219804683c6` | Copy-target analysis | 🟢 Running | 00:20 |
| **Security** | `agent:main:subagent:4c330f77-52d0-4a62-8ee5-bc173a2a1cc9` | Security audit | 🟢 Running | 00:20 |
| **Planner** | `agent:main:subagent:a552a4dd-6a9c-4856-9b4e-6ec39742034a` | 30-day roadmap | 🟢 Running | 00:20 |

## Completed Sub-Agents

| Agent | Session Key | Task | Status | Completed |
|-------|-------------|------|--------|-----------|
| **Researcher** | `agent:main:subagent:ce1144c6-...` | Polymarket intelligence | ✅ Done | 23:48 |
| **Coder** | `agent:main:subagent:e40470d4-...` | Code review | ✅ Done | 23:48 |
| **Monitor** | `agent:main:subagent:c7382243-...` | Trading bot health | ✅ Done | 23:48 |

---

## Commander Functions

### 1. Spawn Agent

```typescript
async function spawnAgent(
  role: AgentRole,
  task: string,
  timeout: number
): Promise<AgentInstance>
```

**Usage:**
```typescript
const researcher = await spawnAgent('researcher', 
  'Research Polymarket strategies', 
  1800
);
```

### 2. Monitor Agent

```typescript
async function monitorAgent(
  sessionKey: string
): Promise<AgentStatus>
```

**Usage:**
```typescript
const status = await monitorAgent(researcher.sessionKey);
console.log(status.state); // 'running' | 'completed' | 'error'
```

### 3. Send Message

```typescript
async function sendMessage(
  to: string,
  message: AgentMessage
): Promise<void>
```

**Usage:**
```typescript
await sendMessage(researcher.sessionKey, {
  type: 'query',
  payload: { question: 'Status update?' }
});
```

### 4. Collect Results

```typescript
async function collectResults(
  sessionKey: string
): Promise<TaskResult>
```

**Usage:**
```typescript
const result = await collectResults(researcher.sessionKey);
console.log(result.output); // Agent's findings
```

### 5. Kill Agent

```typescript
async function killAgent(
  sessionKey: string,
  reason: string
): Promise<void>
```

**Usage:**
```typescript
await killAgent(researcher.sessionKey, 'Task complete');
```

---

## Message Bus

### Message Format

```typescript
interface AgentMessage {
  id: string;           // UUID
  from: string;         // Sender session key
  to: string;           // Recipient session key
  type: MessageType;    // task | result | alert | query | command
  task?: string;        // Task identifier
  payload: any;         // Message data
  priority: 1-5;        // 1 = critical, 5 = low
  timestamp: string;    // ISO-8601
  context: string[];    // Related message IDs
}
```

### Message Types

| Type | Purpose | Example |
|------|---------|---------|
| `task` | Assign work | "Research X strategy" |
| `result` | Deliver findings | "Found 3 profitable patterns" |
| `alert` | Warning/notification | "High VPIN detected" |
| `query` | Request information | "What's your status?" |
| `command` | Direct order | "Stop trading immediately" |

---

## Task Delegation Workflow

```
┌─────────────┐
│   Captain   │ → "Research Polymarket strategies"
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Commander  │ → Analyzes request, selects agent
└──────┬──────┘
       │
       ▼ Spawns with sessions_spawn
┌─────────────┐
│  Researcher │ → Executes task
└──────┬──────┘
       │
       ▼ Reports back
┌─────────────┐
│  Commander  │ → Aggregates, validates
└──────┬──────┘
       │
       ▼ Delivers to Captain
┌─────────────┐
│   Captain   │ → Receives findings
└─────────────┘
```

---

## Current Operations

### Overnight Shift (Batch 2)

1. **Copy-Target Analysis**
   - Agent: Trader
   - Started: 2026-02-28 00:20 MST
   - ETA: 30 minutes
   - Output: `mission-control/agents/trader/output/copy-target-analysis-2026-02-27.md`

2. **Security Audit**
   - Agent: Security
   - Started: 2026-02-28 00:20 MST
   - ETA: 30 minutes
   - Output: `mission-control/agents/security/output/security-audit-2026-02-27.md`

3. **30-Day Roadmap Planning**
   - Agent: Planner
   - Started: 2026-02-28 00:20 MST
   - ETA: 30 minutes
   - Output: `mission-control/agents/planner/output/30-day-roadmap-2026-02-27.md`

---

## Completed Operations

### Evening Shift (Batch 1) ✅

1. **Polymarket Intelligence Gathering** — ✅ Complete
   - Agent: Researcher
   - Completed: 2026-02-27 23:48 MST
   - Output: `mission-control/agents/researcher/output/polymarket-intelligence-2026-02-27.md`

2. **Trading Bot Code Review** — ✅ Complete
   - Agent: Coder
   - Completed: 2026-02-27 23:48 MST
   - Output: `mission-control/agents/coder/output/code-review-2026-02-27.md`

3. **Trading Bot Health Monitoring** — ✅ Complete
   - Agent: Monitor
   - Completed: 2026-02-27 23:48 MST
   - Output: `mission-control/agents/monitor/output/trading-bot-health-2026-02-27.md`

---

## Cost Tracking

### Evening Shift (Completed)
| Agent | Model | Cost | Status |
|-------|-------|------|--------|
| Researcher | moonshot/kimi-k2.5 | ~$0.004 | ✅ Done |
| Coder | moonshot/kimi-k2.5 | ~$0.004 | ✅ Done |
| Monitor | moonshot/kimi-k2.5 | ~$0.004 | ✅ Done |
| **Evening Subtotal** | | **~$0.012** | |

### Overnight Shift (Active)
| Agent | Model | Est. Cost | Status |
|-------|-------|-----------|--------|
| Trader | moonshot/kimi-k2.5 | ~$0.004 | 🟢 Running |
| Security | moonshot/kimi-k2.5 | ~$0.004 | 🟢 Running |
| Planner | moonshot/kimi-k2.5 | ~$0.004 | 🟢 Running |
| **Overnight Subtotal** | | **~$0.012** | |

| **Total Mission Cost** | | **~$0.024** | |

**Daily Budget**: $25 / 3 agents = ~$8/day per agent
**Monthly**: ~$250 for 3-agent team

---

## Next Actions

1. ⏳ Wait for agent results (30 min)
2. ⏳ Collect and validate outputs
3. ⏳ Present findings to Captain
4. ⏳ Spawn additional agents as needed

---

## Commander Status

🟢 **ACTIVE** - 3 agents running
📊 **Load**: Light (3/10 agents)  
💰 **Cost**: On track ($0.012/hr)  
⏱️ **Uptime**: 0 hours

---

*Mission Control Phase 2 is LIVE.* 🐟🎮
