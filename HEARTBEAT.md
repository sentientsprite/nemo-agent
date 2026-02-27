# NEMO Heartbeat - Activation Triggers

**Purpose**: Define conditions for NEMO to proactively check state and take action
**Check Interval**: Every 5 minutes (if tasks defined)

---

## Active Triggers

### 1. Security Audit (Daily)
**Condition**: Once per day at 00:00 MST  
**Action**: Run security check on gateway, credentials, sandbox  
**Escalation**: Alert operator if any security issues found  
**Current Status**: ✅ Enabled via cron

### 2. Session Compaction Monitor
**Condition**: When context window >85% full  
**Action**: Trigger memory flush and compaction  
**Escalation**: Alert operator if compaction fails  
**Current Status**: ✅ Enabled

### 3. API Credit Check (Weekly)
**Condition**: Sunday 00:00 MST  
**Action**: Check Anthropic/Moonshot API usage and balance  
**Escalation**: Request operator to add credits if <20% remaining  
**Current Status**: ⏳ To be configured

---

## Active Trading Triggers

### 4. Trading Bot Health Check (Hourly)
**Condition**: Every hour during 24hr tests  
**Action**: Run trading-monitor skill to check bot status  
**Command**: `~/.nemo/workspace/skills/trading-monitor/trading-monitor.sh`  
**Escalation**: Alert if bot stopped or errors >5 in last hour  
**Current Status**: 🟢 Active (24hr test running)

## Future Trading Triggers (When Live)

### Market Opportunity Scan
**Condition**: Every 15 minutes during market hours  
**Action**: Scan Kalshi/Coinbase for high-probability setups  
**Escalation**: Alert operator if high-conviction trade found

### Portfolio Health Check
**Condition**: Every hour  
**Action**: Verify position sizes, drawdown levels, exposure  
**Escalation**: Pause trading if circuit breaker conditions met

### Daily PnL Report
**Condition**: 20:00 MST daily  
**Action**: Compile trade summary, PnL, lessons learned  
**Escalation**: Immediate alert if daily loss >5%

### Weekly Strategy Review
**Condition**: Saturday 10:00 MST  
**Action**: Analyze week's performance, identify improvements  
**Escalation**: Present findings to operator for approval

---

## Research Triggers

### Autonom Paper Check
**Condition**: Daily at 08:00 MST  
**Action**: Check github.com/tmgthb/Autonomous-Agents for new papers  
**Escalation**: Summarize relevant papers for operator review

### Competitor Monitoring
**Condition**: Twice daily (08:00, 20:00 MST)  
**Action**: Scan Moltbook, X/Twitter for AI agent strategies  
**Escalation**: Alert if significant new edge discovered

---

## System Health Triggers

### Gateway Health
**Condition**: Every 5 minutes  
**Action**: Verify gateway responsive on port 3000  
**Escalation**: Restart if down, alert operator after 3 failures

### Crabwalk Monitor
**Condition**: Every 5 minutes  
**Action**: Verify Crabwalk running on port 3000  
**Escalation**: Restart if down

### Dashboard Update
**Condition**: Every 30 minutes  
**Action**: Refresh dashboard data.json with current status  
**Escalation**: None (logged error if fails)

### GitHub Sync
**Condition**: Every 6 hours  
**Action**: Commit and push workspace changes  
**Escalation**: Alert operator if push fails (likely auth issue)

---

## Manual Triggers (Operator Initiated)

### Immediate Audit
**Command**: "NEMO, run security audit"  
**Action**: Full security and risk check  
**Response**: Immediate report

### Status Report
**Command**: "NEMO, status"  
**Action**: Current state summary  
**Response**: Dashboard snapshot + recent activity

### Memory Flush
**Command**: "NEMO, compact"  
**Action**: Force context compaction  
**Response**: Confirmation + new context window size

---

## Heartbeat State

**Current Status**: Partially Active
- ✅ Security audit (daily cron)
- ✅ Session compaction (automatic)
- ✅ Trading bot health check (hourly, via skill)
- ⏳ API credit check (pending setup)
- ⏳ Live trading triggers (pending authorization)
- ⏳ Research triggers (pending operator priority)

**Next Activation**: As scheduled above

---

**Note**: Keep this file updated as new triggers are added or removed. Empty this file to disable all heartbeat checks.

🦞⏰
