# SMART-ROUTER.md — Local-First Model Routing

## Philosophy
**FREE FIRST, PAY ONLY WHEN NECESSARY**

Until trading bot is profitable, every token counts.

## The Router Logic

```
USER REQUEST
    ↓
[Task Analyzer] — Estimates complexity, context size, speed needs
    ↓
    ├─→ Simple + <4K context + Not urgent? → LM Studio (FREE)
    │      └─→ Timeout 10s or fail? → Escalate to Kimi
    │
    ├─→ Complex OR >8K context OR Speed critical? → Kimi K2.5 ($0.004)
    │      └─→ Security/Architecture critical? → Escalate to Opus
    │
    └─→ Security audit / Final review / Complex strategy? → Opus ($$$)
```

## Task Classification Rules

### ALWAYS Try LM Studio First:
- File reading & summarization (<1000 lines)
- Simple code generation (<200 lines output)
- Log analysis & grep-style queries
- Format conversion (JSON, YAML, etc.)
- Basic math & calculations
- String manipulation
- Status checks & reporting

### ESCALATE to Kimi:
- Context >8K tokens (local model limit)
- Multi-step reasoning chains
- API integration code
- Speed-critical (user waiting)
- Complex data transformation
- Error diagnosis requiring broad context

### ESCALATE to Opus:
- Security audit findings review
- Trading strategy decisions
- Architecture design choices
- Complex bug diagnosis
- Final code review before production
- User explicitly requests "think hard" or "be thorough"

## Implementation

### Router Function
```javascript
async function smartRoute(task) {
  const analysis = analyzeTask(task);
  
  // Try FREE first
  if (analysis.estimatedTokens < 4000 && 
      analysis.complexity === 'low' && 
      !analysis.speedCritical) {
    try {
      const result = await tryLocalModel(task, {timeout: 10000});
      logCostSavings('LM Studio', analysis.estimatedTokens);
      return result;
    } catch (e) {
      logEscalation('Local failed, escalating to Kimi', e.message);
    }
  }
  
  // Try CHEAP next
  if (analysis.securityCritical || analysis.complexity === 'high') {
    return await callOpus(task);
  }
  
  return await callKimi(task);
}
```

## Cost Tracking

| Model | Cost/1K tokens | Typical Task | Monthly Budget |
|-------|---------------|--------------|----------------|
| LM Studio | $0.00 | 80% of tasks | $0 |
| Kimi K2.5 | $0.0006 | 18% of tasks | ~$5-10 |
| Opus | $0.015 | 2% of tasks | ~$5-10 |

**Target:** <$20/month until trading bot funds itself.

## Auto-Detection Criteria

### Try Local If:
- [ ] Input < 2000 tokens
- [ ] Expected output < 1000 tokens  
- [ ] No complex reasoning required
- [ ] Not security-sensitive
- [ ] User not actively waiting
- [ ] No API calls needed
- [ ] No multi-file coordination

### Escalate to Kimi If:
- [ ] Input > 4000 tokens
- [ ] Multi-step logic required
- [ ] Speed matters (interactive)
- [ ] Complex parsing/extraction
- [ ] Local model failed/timeout

### Escalate to Opus If:
- [ ] Security implications
- [ ] Financial risk assessment
- [ ] Complex architecture decisions
- [ ] Final code review
- [ ] User explicitly requests deep thinking

## Fallback Chain

```
LM Studio (10s timeout)
    ↓ FAIL
Kimi K2.5 (30s timeout)
    ↓ FAIL  
Opus (60s timeout)
    ↓ FAIL
Error to user + log for investigation
```

## Monitoring

Track in `cost-savings.log`:
```
[2026-02-28] LM Studio handled: 45 tasks, saved ~$0.18
[2026-02-28] Escalated to Kimi: 12 tasks, cost $0.048
[2026-02-28] Escalated to Opus: 2 tasks, cost $0.03
[2026-02-28] Total savings vs all-Kimi: $0.132
```

## Commands

### Test if Local is Available
```bash
curl -s http://localhost:1234/v1/models | jq '.data[].id'
```

### Force Escalation Override
User can force model with:
- `@local` or `@lmstudio` — Force local
- `@kimi` — Force Kimi  
- `@opus` — Force Opus
- `@think` or `@deep` — Auto-escalate to Opus

## Status

- [x] Router design complete
- [ ] LM Studio model loaded (waiting on user)
- [ ] Router implementation
- [ ] Cost tracking dashboard
- [ ] Auto-escalation testing
