# Commander Module - Mission Control Core

**Role**: Orchestration, delegation, and coordination of all sub-agents  
**Status**: Active (Phase 2)  
**Created**: 2026-02-27

---

## Active Sub-Agents

| Agent | Session Key | Task | Status | Spawned |
|-------|-------------|------|--------|---------|
| **Researcher** | `agent:main:subagent:ce1144c6-3b07-4495-93ca-54877f76729f` | Polymarket intelligence | 🟢 Running | 23:45 |
| **Coder** | `agent:main:subagent:e40470d4-e586-42df-8371-82fa3f18b221` | Code review | 🟢 Running | 23:45 |
| **Monitor** | `agent:main:subagent:c7382243-29b9-4970-8e15-c7b10e632737` | Trading bot health | 🟢 Running | 23:45 |

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

### Active Tasks

1. **Polymarket Intelligence Gathering**
   - Agent: Researcher
   - Started: 2026-02-27 23:45 MST
   - ETA: 30 minutes
   - Output: `mission-control/agents/researcher/output/polymarket-intelligence-2026-02-27.md`

2. **Trading Bot Code Review**
   - Agent: Coder
   - Started: 2026-02-27 23:45 MST
   - ETA: 30 minutes
   - Output: `mission-control/agents/coder/output/code-review-2026-02-27.md`

3. **Trading Bot Health Monitoring**
   - Agent: Monitor
   - Started: 2026-02-27 23:45 MST
   - Duration: 30 minutes (6 checks)
   - Output: `mission-control/agents/monitor/output/trading-bot-health-2026-02-27.md`

---

## Cost Tracking

| Agent | Model | Est. Cost | Runtime |
|-------|-------|-----------|---------|
| Researcher | moonshot/kimi-k2.5 | ~$0.004 | 30 min |
| Coder | moonshot/kimi-k2.5 | ~$0.004 | 30 min |
| Monitor | moonshot/kimi-k2.5 | ~$0.004 | 30 min |
| **Total** | | **~$0.012** | |

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
