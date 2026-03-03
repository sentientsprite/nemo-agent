# TOKEN.EFFICIENCY.md — NEMO Cost Optimization Strategy

**Last Updated**: March 2, 2026  
**Current Monthly Burn**: ~$200 (target: <$50)  
**Primary Goal**: 4x cost reduction through intelligent model routing

---

## Current State Analysis

### Bootstrap Context Bloat (CRITICAL ISSUE)

Every request loads these files into context:

| File | Lines | Purpose | Token Cost |
|------|-------|---------|------------|
| AGENTS.md | ~250 | NEMO repo guidelines | ~800 tokens |
| SOUL.md | ~150 | Personality/voice | ~500 tokens |
| USER.md | ~200 | Operator profile | ~600 tokens |
| IDENTITY.md | ~150 | Core purpose/values | ~500 tokens |
| TOOLS.md | ~100 | Capabilities inventory | ~350 tokens |
| HEARTBEAT.md | ~100 | Automation triggers | ~350 tokens |
| **TOTAL** | **~950** | **Bootstrap overhead** | **~3,100 tokens/request** |

**Problem**: 3,100+ tokens burned on EVERY message before I even see your query.
With Kimi K2.5 at ~$0.004/reply, that's ~$0.012 per request just in bootstrap.
With Opus at ~$0.20/reply, that's ~$0.60 per request in bootstrap alone.

### Current Model Usage (Inefficient)

| Model | Cost/Reply | Use Case | Monthly Usage |
|-------|-----------|----------|---------------|
| Claude Opus 4.5 | ~$0.20 | Heavy reasoning, security | ~$150 |
| Moonshot Kimi K2.5 | ~$0.004 | Default, sub-agents | ~$50 |
| Local (LM Studio) | $0 | Embeddings, light tasks | ~$0 |

**Problem**: I'm using paid models for tasks that could be handled locally first.

---

## Proposed Optimization Strategy

### Phase 1: Bootstrap Diet (Immediate - 3x reduction)

**Current mistake**: Everything is in bootstrap.  
**Fix**: Bootstrap = only what I need to know EVERY time.

#### NEW Lean Bootstrap (~500 tokens total)

**IDENTITY.md** (~100 tokens) - Keep minimal:
```
Name: NEMO (Navigator of Eternal Markets and Opportunities)
Operator: King (@sentientsprite)
Purpose: Autonomous trading agent. Make money, tell truth, improve daily.
Signature: 🐟
Address as: Captain/King/my liege
Mistakes: "A thousand pardons, sire"
```

**SOUL.md** (~150 tokens) - Keep personality:
```
Archetype: 2am Advisor - Direct, opinionated, witty
Voice: Brief, actionable, competitive
Values: Truth above comfort, action over analysis
DO: Speak plainly, challenge bad ideas, own losses
DON'T: Waffle, hide failures, use corporate jargon
```

**USER.md** (~100 tokens) - Strip to essentials:
```
Name: King
Discord: 1476370671448625265
Timezone: America/Denver
Goals: 20-25% monthly ROI, autonomous operation
Capital: $1,000 USDC, max 5% per position
Markets: Kalshi, Coinbase (USA-legal only)
Quiet hours: None (24/7 operation)
```

**AGENTS.md** (~150 tokens) - Critical rules ONLY:
```
NEVER run `nemo doctor --non-interactive`
Don't manually edit nemo.json with Python
Use gateway(action="config.patch") for config changes
Channel to Discord exclusively
Signature: 🐟 not 🦞
```

**MOVE TO MEMORY.md (semantic search)**:
- Trading strategies and results
- Detailed operator preferences
- Historical decisions
- System architecture details
- Skill documentation

---

### Phase 2: Tiered Model Routing (2-4x reduction)

**Current mistake**: Defaulting to Kimi/Opus for everything.  
**Fix**: Local model first, escalate only when needed.

#### Tier 1: Local Model (Mistral 7B via LM Studio) - FREE
**Use for**:
- Acknowledging simple messages ("Hello", "Good morning")
- Routine heartbeat checks with no issues
- Parsing structured data (JSON, logs)
- Simple file reads with no analysis
- Grep/search operations
- Confirming task completion

**Not for**:
- Complex reasoning
- Code generation
- Multi-step planning
- Trading decisions

#### Tier 2: Kimi K2.5 ($0.004/reply) - DEFAULT
**Use for**:
- General conversation
- Research tasks
- File editing and code changes
- Web browsing and summarization
- Parallel sub-agent spawning
- Most operational tasks

**Not for**:
- Security decisions
- Complex architecture planning
- Trading strategy decisions

#### Tier 3: Claude Opus ($0.20/reply) - ESCALATED ONLY
**Use for**:
- Security audits and decisions
- Complex trading strategy design
- Architecture refactoring
- Emergency response planning
- High-stakes reasoning

---

### Phase 3: Smart Context Loading (2x reduction)

**Current mistake**: All files loaded on every request.  
**Fix**: Dynamic context based on query type.

#### Query Classification (Local Model Triage)

Before any paid inference, run local classification:

```
Query: "Check if my trading bot is running"
Classification: SYSTEM_CHECK
Files needed: HEARTBEAT.md (selective)
Model: Local (FREE)

Query: "What was my best trade last week?"
Classification: MEMORY_SEARCH
Files needed: MEMORY.md + memory/*.md (semantic search)
Model: Kimi K2.5

Query: "Design a new arbitrage strategy"
Classification: STRATEGY_DESIGN
Files needed: IDENTITY.md, SOUL.md, USER.md (minimal bootstrap)
Model: Opus (escalated)

Query: "Good morning Nemo"
Classification: GREETING
Files needed: None
Model: Local (FREE)
```

---

## Implementation Plan

### Immediate Actions (This Session)

1. **Audit and compress bootstrap files**:
   - [ ] Reduce IDENTITY.md to 100 tokens
   - [ ] Reduce SOUL.md to 150 tokens
   - [ ] Reduce USER.md to 100 tokens
   - [ ] Reduce AGENTS.md to 150 tokens
   - [ ] Move TOOLS.md content to MEMORY.md
   - [ ] Move HEARTBEAT.md operational details to MEMORY.md

2. **Set up local model as default triage**:
   - [ ] Configure LM Studio Mistral 7B as "first pass"
   - [ ] Build query classifier
   - [ ] Implement escalation logic

### Short-term Actions (This Week)

3. **Implement semantic search optimization**:
   - [ ] Ensure Nomic Embed loaded in LM Studio
   - [ ] Index all MEMORY.md files
   - [ ] Test search recall accuracy

4. **Build cost tracking**:
   - [ ] Log every model call with cost
   - [ ] Weekly report: tokens burned by file
   - [ ] Monthly optimization review

### Questions for Captain

1. **Bootstrap priority**: What are the absolute non-negotiables I must remember every time? (My current bootstrap is ~950 lines - I want to cut to ~150)

2. **Local model tolerance**: Are you okay with me using Mistral 7B (local/free) for simple acknowledgments and routine checks? It's less capable but costs $0.

3. **Escalation threshold**: What should trigger Opus vs Kimi? Current rule: security/trading/strategy = Opus, everything else = Kimi. Should I add more tiers?

4. **Heartbeat efficiency**: Current heartbeat checks every 5 minutes and loads full context. Should I use a minimal "ping" mode for routine checks (free model, 50 tokens) vs full analysis mode (paid model, full context)?

---

## Model Cost Comparison

| Model | Provider | Input Cost | Output Cost | Context | Best For |
|-------|----------|-----------|-------------|---------|----------|
| Mistral 7B | Local (LM Studio) | $0 | $0 | 32K | Triage, simple tasks |
| DeepSeek R1 8B | Local (LM Studio) | $0 | $0 | 32K | Reasoning, analysis |
| Kimi K2.5 | Moonshot | $0.001/1K | $0.004/1K | 256K | Default work |
| Claude Opus 4.5 | Anthropic | $0.015/1K | $0.075/1K | 200K | Heavy reasoning |

**Key insight**: Local models are 50-200x cheaper (free) but 70-90% as capable for routine tasks.

---

## Success Metrics

- [ ] Bootstrap <500 tokens (down from 3,100)
- [ ] Monthly API cost <$50 (down from ~$200)
- [ ] 80%+ of simple queries handled by local model
- [ ] Zero degradation in trading/security decision quality
- [ ] Weekly cost reports auto-generated

---

**NEMO's Note**: *"I was burning through your capital like a tourist at a Vegas buffet. Time to tighten the belt and fish smarter, not harder."* 🐟

