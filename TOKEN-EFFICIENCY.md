# TOKEN-EFFICIENCY.md — Cost Optimization Rules

## 🎯 Philosophy: FREE FIRST

**Until trading bot is profitable:** LM Studio (free) → Kimi ($0.004) → Opus ($$$)

## Smart Router Implementation

**File:** `utils/smart_router.py`

```python
from utils.smart_router import smart_complete

# Auto-routes to cheapest capable model
result = smart_complete("Your prompt here")
```

### Routing Logic
```
Task Input
    ↓
[Analyzer] — Estimates tokens, complexity, urgency
    ↓
    ├─> Simple + <4K tokens + Not urgent → LM Studio (FREE)
    │      └─> Timeout/fail? → Escalate to Kimi
    ├─> Complex OR >6K tokens OR Speed needed → Kimi ($0.004)
    │      └─> Security/final review? → Escalate to Opus
    └─> Security audit / Strategy decisions → Opus ($$$)
```

## Model Routing Table

| Priority | Task Type | Model | Cost | Auto-Select? |
|----------|-----------|-------|------|--------------|
| 1st | Simple coding, summaries, analysis | **LM Studio** | **FREE** | ✅ Yes |
| 2nd | Complex logic, speed critical, >6K tokens | Kimi K2.5 | ~$0.004 | ✅ Yes |
| 3rd | Security, trading strategy, final review | Opus | $$$ | ✅ Yes |

## When to Use Each Model

### LM Studio (FREE) — Default for:
- File reading & summarization (<1000 lines)
- Simple code generation (<200 lines)
- Log analysis & grep queries
- Format conversion
- Basic calculations
- Status reports
- String manipulation

### Kimi K2.5 — Escalate for:
- Multi-step reasoning
- Context >6K tokens
- Speed-critical (user waiting)
- API integrations
- Complex data transformation

### Opus — Escalate for:
- Security audit findings
- Trading strategy decisions
- Architecture design
- Final code review
- Complex bug diagnosis

## Cost Savings Tracking

**Log:** `cost-savings.log`

```
[2026-02-28] Local handled: 45 tasks, saved ~$0.18
[2026-02-28] Escalated to Kimi: 12 tasks, cost $0.048
[2026-02-28] Total savings vs all-Kimi: $0.132
```

**Monthly Target:** <$20 until trading bot funds itself

## Force Model Override

User can force specific model:
- `@local` or `@lmstudio` — Force LM Studio
- `@kimi` — Force Kimi K2.5
- `@opus` — Force Opus
- `@think` or `@deep` — Auto-escalate to Opus

## Browser Efficiency Rules
- Always use `compact: true` for snapshots
- Keep `maxChars` between 800-1500
- Use `grep`/`head`/`tail` before full file reads
- Keep replies concise

## LM Studio (localhost:1234)
- **Status:** ✅ ONLINE (Mistral 7B loaded)
- **Cost:** FREE
- **Speed:** ~3-5s per request
- **Limit:** ~8K token context
- Models: Mistral 7B, DeepSeek R1 8B, Qwen3 VL 8B
- Embeddings: Nomic Embed Text v1.5 (always loaded)
