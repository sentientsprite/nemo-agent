# COST-TRACKING.md — API Spend Monitoring

**Created**: March 2, 2026  
**Monthly Budget**: $50 (down from $200)  
**Current Spend Rate**: ~$5-10/month (local-first operation)

---

## Budget Allocation

| Category | Monthly Limit | Current Rate | Status |
|----------|---------------|--------------|--------|
| **Total API Budget** | $50.00 | ~$7.50 | ✅ On track |
| Kimi K2.5 (T2) | $40.00 | ~$5.00 | ✅ On track |
| Opus (T3) | $10.00 | ~$2.50 | ✅ On track |
| Local (T1) | $0.00 | $0.00 | ✅ Free |

---

## Model Costs

| Model | Provider | Input Cost | Output Cost | Est. Cost/Reply |
|-------|----------|-----------|-------------|-----------------|
| Mistral 7B | LM Studio (local) | $0.00 | $0.00 | **$0.00** |
| DeepSeek R1 8B | LM Studio (local) | $0.00 | $0.00 | **$0.00** |
| Kimi K2.5 | Moonshot | $0.0006/1K | $0.003/1K | ~$0.004 |
| Opus | Anthropic | $0.015/1K | $0.075/1K | ~$0.20 |

---

## Usage Tracking

### Weekly Log Format
```markdown
## Week of YYYY-MM-DD

### Model Usage
| Model | Requests | Est. Cost | Notes |
|-------|----------|-----------|-------|
| Mistral 7B | XXX | $0.00 | Routine work |
| DeepSeek R1 | XX | $0.00 | Reasoning tasks |
| Kimi K2.5 | XX | $X.XX | Escalated tasks |
| Opus | X | $X.XX | Security/trading |

### Total Weekly Spend: $X.XX
### Monthly Projection: $XX.XX
### Budget Remaining: $XX.XX
```

---

## Automated Monitoring

### Daily Check (via cron)
- Log model usage from session history
- Calculate daily spend
- Alert if daily rate exceeds $2.00

### Weekly Report (Sundays)
- Compile usage stats
- Calculate monthly projection
- Compare to $50 budget
- Identify optimization opportunities

### Monthly Review
- Total spend vs budget
- Model usage breakdown
- Cost per task type
- Bootstrap token efficiency

---

## Alert Thresholds

| Threshold | Action |
|-----------|--------|
| Daily spend > $2.00 | ⚠️ Warning — investigate unusual usage |
| Weekly spend > $12.50 | ⚠️ Warning — 25% of monthly budget |
| Monthly projection > $40 | ⚠️ Alert — approaching limit |
| Monthly projection > $50 | 🚨 CRITICAL — exceed budget |
| Opus usage > 10% of total | ⚠️ Review escalation necessity |

---

## Cost Optimization Checklist

### Daily
- [ ] Review model usage logs
- [ ] Verify local model is default
- [ ] Check for unnecessary escalations

### Weekly
- [ ] Calculate actual vs projected spend
- [ ] Review bootstrap token count
- [ ] Identify high-cost tasks for optimization

### Monthly
- [ ] Full budget reconciliation
- [ ] Model efficiency analysis
- [ ] Bootstrap compression review
- [ ] Strategy adjustment if over budget

---

## Historical Data

### March 2026
- **Week 1 (Mar 1-2)**: ~$0.50 (setup, config changes)
- **Projected Monthly**: $7.50 (local-first achieved)
- **Status**: ✅ 85% under budget

### February 2026
- **Total Spend**: ~$180
- **Primary Model**: Kimi K2.5 (default)
- **Status**: ❌ 10% over $200 limit
- **Lesson**: Switched to local-first model

---

## Automation Status

- [ ] Daily usage logging — PENDING
- [ ] Weekly report generation — PENDING
- [ ] Alert system — PENDING
- [ ] Dashboard integration — FUTURE

---

**NEMO's Note**: *"Every $0.004 saved is a step toward self-sufficiency. Local-first isn't just cheaper — it's faster and more reliable."* 🐟
