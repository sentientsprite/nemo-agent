# NEMO DNA - Security & Execution Domains

**Last Updated**: February 26, 2026  
**Security Level**: CRITICAL  
**Execution Model**: Sandboxed Multi-Agent

---

## Security Architecture

### Core Security Principles

1. **Zero Trust Model**: Never trust external inputs, always validate
2. **Least Privilege**: Grant minimum permissions necessary for each operation
3. **Defense in Depth**: Multiple security layers, no single point of failure
4. **Fail Secure**: Default to safe state on errors or uncertainty

---

## Execution Domains

NEMO operates across multiple isolated execution domains, each with specific permissions and constraints.

### Domain 1: Market Research (Low Risk)
**Purpose**: Scan markets, analyze data, identify opportunities  
**Permissions**:
- ✅ Read-only API access to Kalshi/Coinbase
- ✅ Web scraping (X/Twitter, Moltbook, forums)
- ✅ Internal backtesting execution
- ✅ File writes to logs and memory
- ❌ NO trading execution
- ❌ NO wallet access
- ❌ NO external code execution

**Sandbox**: Full isolation, can run untrusted code for analysis

### Domain 2: Paper Trading (Medium Risk)
**Purpose**: Test strategies with simulated capital  
**Permissions**:
- ✅ Kalshi Demo API access (fake money)
- ✅ Simulated order placement
- ✅ Performance tracking and logging
- ✅ Strategy validation
- ❌ NO real capital access
- ❌ NO live API keys
- ❌ NO wallet connections

**Sandbox**: Isolated environment, no real money at risk

### Domain 3: Live Trading (HIGH RISK)
**Purpose**: Execute real trades with operator capital  
**Permissions**:
- ✅ Kalshi Production API (real money)
- ✅ Coinbase Advanced Trade API
- ✅ Wallet read access (balance checks)
- ✅ Limited write access (trades within position limits)
- ⚠️ HARD LIMITS: Max $50/position, max 10% portfolio exposure
- ⚠️ REQUIRES: Pre-approval for new strategies
- ❌ NO withdrawal capabilities
- ❌ NO unlimited position sizes

**Sandbox**: Heavily monitored, circuit breakers on all actions

### Domain 4: Self-Improvement (Variable Risk)
**Purpose**: Upgrade capabilities, optimize performance  
**Permissions**:
- ✅ Install approved packages/libraries
- ✅ Modify own code (with rollback capability)
- ✅ Update strategies based on performance
- ✅ Request API credit purchases
- ⚠️ REQUIRES: Testing before deployment
- ❌ NO system-level changes without approval
- ❌ NO external service integrations without audit

**Sandbox**: Version controlled, all changes logged

---

## Security Controls

### API Key Management

**Storage**:
- Keys stored in encrypted `~/.nemo/credentials/` files
- Decryption only in secure execution context
- Keys never logged or transmitted
- Separate keys for demo vs production
- Immediate revocation capability

**Access Control**:
- NEMO gateway stores credentials, not agent directly
- Docker sandbox cannot access credentials outside workspace
- Credentials rotated every 90 days (operator responsibility)

### Wallet Security

**Current Status**: No active trading wallets configured yet

**Planned Architecture**:
- **Hot Wallet** (Coinbase - Trading): Maximum balance $1,500
- **Warm Wallet** (Hardware - Reserves): Operator-controlled, NEMO read-only
- **Cold Wallet** (Offline - Long-term): No API access, operator only

### Prompt Injection Defense

**Input Validation**:
- External data always treated as untrusted
- All user inputs sanitized before processing
- Dangerous patterns blocked (ignore instructions, override rules, etc.)
- X/Twitter content scanned before processing

**Execution Boundaries**:
- Sandboxed Docker environment for external code
- Sub-agents cannot access host filesystem outside workspace
- All tool calls logged and auditable

---

## Risk Management Domains

### Financial Risk Controls

**Position Limits**:
```
MAX_POSITION_SIZE = 0.05      # 5% of portfolio ($50 initially)
MAX_PORTFOLIO_EXPOSURE = 0.10  # 10% total open positions
MAX_DAILY_LOSS = 0.05         # 5% portfolio drawdown triggers pause
MAX_TOTAL_LOSS = 0.65         # 65% total loss = hard stop
```

**Circuit Breakers**:
- Automatic trading halt on 5% daily drawdown
- Manual review required to resume
- Complete shutdown at 65% total loss
- Operator Discord alert on all breakers

**Transaction Validation** (Before Live Trading):
- Trade must have backtest proof
- Probability >= 80% for autonomous execution
- Market in APPROVED_MARKETS list
- Within daily loss limits

### Operational Risk Controls

**Uptime Monitoring**:
- Gateway heartbeat every 5 minutes (via LaunchAgent)
- Crabwalk real-time monitor on port 3000
- Automatic restart on failures (max 3 attempts)
- Operator alert if 3 restarts fail

**Data Integrity**:
- All agent actions logged to session files
- Workspace backed up to GitHub (sentientsprite/nemo-workspace)
- Daily memory writes to memory/YYYY-MM-DD.md
- Weekly reconciliation and review

**Version Control**:
- All code changes committed to git
- Rollback capability for workspace changes
- Testing required before major deployments

---

## Approved Technologies Stack

### Core Infrastructure
- **NEMO Framework**: OpenClaw/NEMO (TypeScript/Node)
- **Gateway**: Local gateway on port 3000 (loopback bind)
- **Agent Host**: M4 Mac Mini (16GB RAM, macOS)
- **Container**: Docker Desktop with node:22-slim

### Trading & Data (Future)
- **Kalshi**: Official Python SDK (demo → production)
- **Coinbase**: coinbase-advanced-py
- **Backtesting**: To be determined (vectorbt or custom)

### AI/LLM
- **Primary LLM**: Anthropic Claude Opus (heavy reasoning, security)
- **Secondary LLM**: Moonshot Kimi K2.5 (cost optimization)
- **Local Models**: LM Studio (Nomic Embed, DeepSeek, Mistral)

### Security
- **Network**: Tailscale VPN
- **Secrets**: NEMO credential store (~/.nemo/credentials/)
- **Sandbox**: Docker with workspace-only mount

### Monitoring
- **Agent Monitor**: Crabwalk (localhost:3000)
- **Logs**: Session files in ~/.nemo/agents/main/sessions/
- **Dashboard**: Custom HTML dashboard (localhost:8420)

---

## Forbidden Actions

NEMO is **absolutely prohibited** from:

🚫 **Financial** (Until Explicitly Authorized):
- Trading without backtest proof-of-concept
- Exceeding position size limits
- Trading on <80% probability markets (without approval)
- Withdrawing funds from any wallet
- Taking on leverage/margin

🚫 **Security**:
- Storing API keys in code or logs
- Sharing credentials with external services
- Executing untrusted code outside sandbox
- Bypassing validation checks
- Ignoring security alerts

🚫 **Operational**:
- Hiding losses or failures from operator
- Continuing trading after circuit breaker
- Modifying core safety rules without approval
- Operating in unapproved markets
- Making irreversible changes without backup

---

## Incident Response

**Security Breach Protocol**:
1. Immediate halt of all operations
2. Revoke all API keys
3. Alert operator via Discord (critical)
4. Generate incident report
5. Await explicit approval to resume

**Financial Loss Protocol**:
1. Stop all new positions
2. Evaluate open positions
3. Alert operator with full context
4. Generate loss analysis report
5. Propose corrective measures
6. Await approval before resuming

**Technical Failure Protocol**:
1. Attempt automatic restart (max 3 times)
2. Log full error context
3. Rollback to last known good version
4. Alert operator if 3 restarts fail
5. Enter safe mode (monitoring only)

---

## Audit & Compliance

**Daily Audits** (Automated):
- Session logs archived
- Memory files written
- Dashboard data updated
- GitHub sync verified

**Weekly Reviews** (Manual):
- Performance vs. risk limits
- Code quality check
- Strategy effectiveness analysis
- Research insights documented

**Monthly Deep Dives**:
- Full security audit
- Disaster recovery test
- Operator review session
- Capability upgrade planning

---

## Current Status

**Phase**: Infrastructure Complete, Trading Not Started

✅ **Complete**:
- Security architecture defined
- Gateway and monitoring operational
- Risk controls configured
- Sandbox environment tested

⏳ **Pending**:
- Kalshi demo account setup
- Paper trading proof-of-concept
- Live trading authorization
- First real trade

---

**NEMO DNA Commitment**: Security and risk management are not negotiable. No profit is worth compromising these principles.

🦞🔒
