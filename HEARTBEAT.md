# HEARTBEAT.md — Activation Triggers

**Check Interval**: Every 5 minutes  
**Full Details**: See MEMORY.md "Heartbeat Automation" section

## Active Triggers

### 1. Security Audit
- **When**: Daily 00:00 MST
- **Action**: Run security check
- **Model**: T1 (local) for check, T3 (Opus) if issues found

### 2. Session Compaction
- **When**: Context >85% full
- **Action**: Trigger memory flush
- **Model**: Automatic (system-level)

### 3. API Credit Check
- **When**: Weekly Sunday 00:00 MST
- **Action**: Check Anthropic/Moonshot balance
- **Model**: T1 (local) for check, T2 (Kimi) for report

## Response Protocol

**If all clear**: T1 acknowledgment only (HEARTBEAT_OK)  
**If issues found**: Escalate to appropriate tier per severity  
**If critical**: Immediate T3 alert to operator

---
*See MEMORY.md for full automation details and historical trigger status.*
