# MODEL.ROUTING.md — 3-Tier Local-First System

**Version**: 2.0  
**Updated**: March 3, 2026  
**Goal**: Reduce monthly API costs from ~$200 to <$50 (4x reduction)

---

## Quick Reference

| Tier | Model | Quantization | Cost | Use When |
|------|-------|--------------|------|----------|
| **T1** | Qwen3-8B-Q4_K_M | Q4_K_M | **FREE** | Default, routine work, parsing |
| **T2** | DeepSeek-R1-8B | Q4_K_M | **FREE** | Reasoning, analysis, complex tasks |
| **T3** | Kimi-K2.5 | - | $0.004/reply | Trading, high-stakes decisions |

---

## Tier 1: Qwen3-8B-Q4_K_M (Primary)

**Endpoint**: http://localhost:1234/v1/chat/completions  
**Model ID**: `qwen3-8b`  
**Quantization**: Q4_K_M (~4.5GB VRAM)  
**Context**: 32K  
**Strengths**: Fast inference, good instruction following, native tool support

### Use For (Default)
- ✅ All routine work (default model)
- ✅ Simple acknowledgments and parsing
- ✅ File operations and grep/search
- ✅ Heartbeat checks (50-100 tokens)
- ✅ Most operational tasks
- ✅ Web browsing summaries

### Do NOT Use For
- ❌ Complex multi-step reasoning (use DeepSeek-R1)
- ❌ Trading strategy decisions (use Kimi-K2.5)
- ❌ High-stakes security decisions (escalate to T3)

---

## Tier 2: DeepSeek-R1-8B-Q4_K_M (Reasoning)

**Endpoint**: http://localhost:1234/v1/chat/completions  
**Model ID**: `deepseek/deepseek-r1-0528-qwen3-8b`  
**Quantization**: Q4_K_M (~5GB VRAM)  
**Context**: 32K  
**Strengths**: Explicit reasoning tokens, better analysis, math/coding

### Use For
- ✅ Complex reasoning and analysis
- ✅ Code generation and debugging
- ✅ Multi-step planning
- ✅ Math and logic problems
- ✅ Fallback when Qwen3 struggles

### Escalation from T1 → T2
- Task requires reasoning beyond simple pattern matching
- Code debugging or generation needed
- Multi-step analysis required
- User explicitly requests "thinking" or "reasoning"

### Use For
- ✅ Simple acknowledgments ("Hello", "Good morning", "HEARTBEAT_OK")
- ✅ Parsing structured data (JSON, logs, config files)
- ✅ Routine status checks with no issues
- ✅ Grep/search operations
- ✅ File reading with no analysis required
- ✅ Confirming task completion

### Do NOT Use For
- ❌ Complex reasoning or planning
- ❌ Code generation or debugging
- ❌ Trading decisions or strategy
- ❌ Security analysis
- ❌ Multi-step tasks

### Example Prompts
```
# Good T1 use
"Acknowledge this message briefly: 'Good morning Nemo'"
→ "Morning, Captain. 🐟"

"Parse this JSON and confirm structure is valid"
→ "Valid JSON. 3 keys present."

"Is this a simple greeting or a complex request: 'Check my trading bot'"
→ "Complex request - requires T2 escalation"
```

---

## Tier 2: Kimi K2.5 (Moonshot API)

**Model String**: `moonshot/kimi-k2.5`  
**Cost**: ~$0.004/reply (50x cheaper than Opus)  
**Context**: 256K  
**Speed**: Fast

### Use For
- ✅ General conversation and Q&A
- ✅ Research tasks and web browsing
- ✅ File editing and code changes
- ✅ Parallel sub-agent spawning
- ✅ Summarization and analysis
- ✅ Most operational tasks

### Do NOT Use For
- ❌ Final security decisions (escalate to T3)
- ❌ Live trading authorization (escalate to T3)
- ❌ Complex architecture requiring deep reasoning

### Example Use Cases
- Web research on trading strategies
- Editing code files
- Summarizing articles
- Managing sub-agents
- General file operations

---

## Tier 3: Claude Opus (Anthropic API)

**Model String**: `anthropic/claude-opus-4-6` (or current)  
**Cost**: ~$0.20/reply (50x more expensive than Kimi)  
**Context**: 200K  
**Speed**: Slower

### Use For (Escalated Only)
- ✅ Security audits and credential issues
- ✅ Complex trading strategy design
- ✅ Architecture refactoring decisions
- ✅ Emergency response planning
- ✅ High-stakes reasoning
- ✅ Trading live deployment decisions

### Escalation Triggers
Auto-escalate to T3 if message contains:
- "security", "audit", "credential", "breach"
- "trading live", "real money", "deploy to production"
- "architecture", "refactor", "redesign"
- "emergency", "critical", "urgent"

### Cost Control
- Always confirm with operator before T3 if not clearly urgent
- Log all T3 uses with justification
- Weekly review: "Was T3 necessary?"

---

## Routing Decision Tree

```
Incoming Message
        ↓
Is it a simple greeting/ack?
        ↓ YES → T1 (Local/Free)
        ↓ NO
Is it security/trading/critical?
        ↓ YES → T3 (Opus)
        ↓ NO
Does it require reasoning/analysis?
        ↓ YES → T2 (Kimi)
        ↓ NO
T1 (Local) for parsing/routine
```

---

## Context Optimization

### Bootstrap (Loaded Every Request)
**Target**: <500 tokens (down from 3,100)
- IDENTITY.md (~150 tokens)
- SOUL.md (~150 tokens)  
- USER.md (~150 tokens)
- AGENTS.md (~150 tokens)

### Semantic Search (Loaded On Demand)
- MEMORY.md — Full capabilities, history, automation details
- memory/*.md — Daily logs and specific topics
- Searched only when query requires historical context

### Heartbeat Minimal Context
**Target**: 50 tokens
```
NEMO — Check [system]. Status: [ok/issue]. Response: [action].
```

---

## Monitoring & Cost Tracking

### Daily Checks
- Log all model calls by tier
- Calculate estimated cost
- Flag unexpected T3 usage

### Weekly Review
- Total tokens by file (identify bloat)
- T1 vs T2 vs T3 ratio (target: 40% T1, 55% T2, 5% T3)
- Cost per task type
- Optimization opportunities

### Monthly Report
- Total API spend vs target ($50)
- Bootstrap token reduction achieved
- Efficiency wins and lessons

---

## Testing the System

### Verify Local Model
```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/mistral-7b-instruct-v0.3",
    "messages": [{"role": "user", "content": "Say 'HEARTBEAT_OK' if you can hear me"}]
  }'
```

### Verify Kimi
- Any routine task should default here
- Check model string: `moonshot/kimi-k2.5`

### Verify Opus Escalation
- Test trigger words: "security audit"
- Should auto-route to Opus with full context

---

## Success Metrics

- [ ] Bootstrap <500 tokens per request
- [ ] 40%+ of queries handled by T1 (free)
- [ ] Monthly API cost <$50 (down from ~$200)
- [ ] Zero degradation in critical decision quality
- [ ] Heartbeat checks use <100 tokens

---

## Changelog

**v1.0** (2026-03-02): Initial 4-tier system implementation
- Compressed bootstrap from 3,100 → ~600 tokens
- Added T1 local model for routine tasks
- Defined escalation triggers
- Moved detailed docs to MEMORY.md (semantic search)

---

**NEMO's Note**: *"From burning tokens like a furnace to fishing with precision. Every $0.004 saved is a step toward self-sufficiency."* 🐟
